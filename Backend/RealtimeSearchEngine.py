from duckduckgo_search import DDGS
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey", "")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

chatlog_path = r"Data\ChatLog.json"
os.makedirs("Data", exist_ok=True)
if not os.path.exists(chatlog_path):
    with open(chatlog_path, "w") as f:
        dump([], f)

def DuckDuckGoSearch(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
        Answer = f"The search results for '{query}' are:\n [start]\n"
        for r in results:
            Answer += f"Title: {r.get('title')}\nDescription: {r.get('body')}\nURL: {r.get('href')}\n\n"
        Answer += "[end]"
        return Answer

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"},
]

def information():
    now = datetime.datetime.now()
    return (
        f"use this real time information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )

def RealtimeSearchEngine(promt):
    global SystemChatBot
    with open(chatlog_path, "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": promt})
    SystemChatBot.append({"role": "system", "content": DuckDuckGoSearch(promt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(chatlog_path, "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer)

if __name__ == "__main__":
    while True:
        promt = input("Enter your query: ")
        print(RealtimeSearchEngine(promt))
