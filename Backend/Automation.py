from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search as playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
from yt_dlp import YoutubeDL

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = [
    "zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d",
    "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
    "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
client = Groq(api_key=GroqAPIKey)
message = []
SystemChatBot = [{"role": 'system', "content": f"Hello, I am {os.environ.get('Username', 'Coder')}, You're Code Helper. Let’s Start Coding."}]

def GoogleSearch(Topic):
    playonyt(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(['notepad.exe', File])

    def ContentWriteAI(Prompt):
        message.append({"role": "user", "content": Prompt})
        completion = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=SystemChatBot + message,
            max_tokens=2024,
            temperature=0.7,
            top_p=1,
            stream=True
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        answer = answer.replace("</s>", "")
        message.append({"role": "assistant", "content": answer})
        return answer

    Topic = Topic.replace("Content", "")
    ContentByAI = ContentWriteAI(Topic)
    FileName = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    os.makedirs("Data", exist_ok=True)
    with open(FileName, "w", encoding="utf-8") as f:
        f.write(ContentByAI)
    OpenNotepad(FileName)
    return True

def YoutubeSearch(Topic):
    Url = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url)
    return True

def PlayYoutube(Query):
    with YoutubeDL({'quiet': True}) as ydl:
        search_result = ydl.extract_info(f"ytsearch:{Query}", download=False)['entries'][0]
        video_url = search_result['webpage_url']
        webbrowser.open(video_url)
    return True
 
def OpenApp(AppName):
    try:
        # Try to open installed app
        appopen(AppName, match_closest=True, output=True, throw_error=True)
        print(f"Opened installed app: {AppName}")
        return
    except Exception:
        print(f"App '{AppName}' not found locally. Searching for official website...")

    # Prepare Google search URL with "official site" keyword
    query = f"{AppName} official site"
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": useragent}

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Google search results links are inside <a> tags in div with class 'tF2Cxc' or similar
        # Let's try to get top 3 links from organic results:
        links = []
        for g in soup.find_all('div', class_='tF2Cxc'):
            a_tag = g.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                # Filter out google redirects and safe URLs only
                if href.startswith("http") and "google.com" not in href:
                    links.append(href)
            if len(links) >= 3:
                break

        if links:
            # Open the first candidate link
            print(f"Opening likely official site: {links[0]}")
            webbrowser.open(links[0])
            return
    except Exception as e:
        print("Error during Google search or parsing:", e)

    # If all else fails, open generic google search page
    print(f"Could not find official site, opening search page for: {AppName}")
    webbrowser.open(f"https://www.google.com/search?q={AppName}")

 

def CloseApp(App):
    if "chrome" in App.lower():
        return True
    try:
        close(App, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

def System(Command):
    def mute():
        keyboard.press_and_release('volume mute')
    def unmute():
        keyboard.press_and_release('volume mute')
    def volume_up():
        keyboard.press_and_release('volume up')
    def volume_down():
        keyboard.press_and_release('volume down')
    if Command == "mute":
        mute()
    elif Command == "unmute":
        unmute()
    elif Command == "volume up":
        volume_up()
    elif Command == "volume down":
        volume_down()
    return True

async def TranslateAndExecute(Commands: list[str]):
    funcs = []
    for Command in Commands:
        if Command.startswith('open '):
            fun = asyncio.to_thread(OpenApp, Command.replace("open ", ""))
            funcs.append(fun)
        elif Command.startswith('general'):
            pass
        elif Command.startswith('realtime'):
            pass
        elif Command.startswith('close'):
            fun = asyncio.to_thread(CloseApp, Command.replace("close ", ""))
            funcs.append(fun)
        elif Command.startswith('play'):
            fun = asyncio.to_thread(PlayYoutube, Command.replace("play ", ""))
            funcs.append(fun)
        elif Command.startswith('content'):
            fun = asyncio.to_thread(Content, Command.replace("content ", ""))
            funcs.append(fun)
        elif Command.startswith('google search'):
            fun = asyncio.to_thread(GoogleSearch, Command.replace("google search ", ""))
            funcs.append(fun)
        elif Command.startswith('youtube search'):
            fun = asyncio.to_thread(YoutubeSearch, Command.replace("youtube search ", ""))
            funcs.append(fun)
        elif Command.startswith('system'):
            fun = asyncio.to_thread(System, Command.replace("system ", ""))
            funcs.append(fun)
        else:
            print(f"No function found for: {Command}")
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(Commands: list[str]):
    async for result in TranslateAndExecute(Commands):
        pass
    return True


if __name__ == "__main__":
    asyncio.run(Automation(['open facebook',"open teligram", "play russian banda", ]))