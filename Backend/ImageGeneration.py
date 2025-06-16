import asyncio
from random import randint
from PIL import Image
from dotenv import get_key
from time import sleep
import requests
import os

def open_image(promt):
    folder_path = r'Data'
    promt = promt.replace(" ", "_")
    files = [f"{promt}{i}.jpg" for i in range(1, 5)]
    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening Image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

API_URL = 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0'
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"API Error: {response.status_code} {response.text}")
        return None
    return response.content

async def generate_images(promt: str):
    tasks = []
    for _ in range(4):
        prompt_text = f"{promt}, quality 4k, sharpness maximum, ultra high detail, high resolution"
        payload = {
            "inputs": prompt_text,
            "options": {"seed": randint(0, 1000000)}
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
    image_bytes_list = await asyncio.gather(*tasks)
    os.makedirs("Data", exist_ok=True)
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            with open(os.path.join("Data", f"{promt.replace(' ', '_')}{i+1}.jpg"), "wb") as f:
                f.write(image_bytes)
        else:
            print(f"Image {i+1} was not generated due to an error.")

def GenerateImage(promt: str):
    asyncio.run(generate_images(promt))
    open_image(promt)

while True:
    try:
        with open(r'Frontend\Files\ImageGeneration.data', "r") as f:
            Data = f.read()
            Promt, Status = Data.strip().split(",")
        if Status == "True":
            print("Generating Image....")
            GenerateImage(Promt)
            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
            break
        else:
            sleep(1)
    except Exception as e:
        print(e)
