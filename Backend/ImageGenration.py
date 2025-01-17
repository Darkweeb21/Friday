import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
import os
from time import sleep

# Load environment variables at the start
load_dotenv()


def setup_data_file():
    """Create necessary directories and data file if they don't exist"""
    # Create directory structure with the new path
    data_dir = r"Frontend\Files"
    os.makedirs(data_dir, exist_ok=True)

    # Create ImageGeneration.data file if it doesn't exist
    data_file_path = os.path.join(data_dir, "ImageGeneration.data")
    if not os.path.exists(data_file_path):
        with open(data_file_path, "w") as f:
            f.write(",False")  # Initialize with empty prompt and False status
    return data_file_path


def get_api_key():
    """Retrieve API key from environment variables"""
    api_key = os.getenv('HuggingFaceAPIKey')
    if not api_key:
        raise ValueError("HuggingFaceAPIKey not found in .env file")
    return api_key


def open_images(prompt: str) -> None:
    """Open generated images using PIL"""
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError as e:
            print(f"Unable to open {image_path}: {e}")


# API configuration
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_api_key()}"}


async def query(payload: dict) -> bytes:
    """Send request to Hugging Face API"""
    response = await asyncio.to_thread(
        requests.post,
        API_URL,
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")
    return response.content


async def generate_images(prompt: str) -> None:
    """Generate multiple images asynchronously"""
    tasks = []
    for i in range(5):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    try:
        image_bytes_list = await asyncio.gather(*tasks)
        folder_path = r"Data"
        os.makedirs(folder_path, exist_ok=True)

        for i, image_bytes in enumerate(image_bytes_list):
            filename = f"{prompt.replace(' ', '_')}{i + 1}.jpg"
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "wb") as f:
                f.write(image_bytes)
    except Exception as e:
        print(f"Error generating images: {e}")
        raise


def GenerateImages(prompt: str) -> bool:
    """Main function to generate and display images"""
    try:
        asyncio.run(generate_images(prompt))
        open_images(prompt)
        return True
    except Exception as e:
        print(f"Error in GenerateImages: {e}")
        return False


def main():
    # Setup the data file with the new path
    data_file_path = setup_data_file()

    while True:
        try:
            with open(data_file_path, "r") as f:
                data = f.read().strip()

            if not data:
                print("Empty data file")
                sleep(1)
                continue

            prompt, status = data.split(",")

            if status.lower() == "true":
                print("Generating Images.....")
                success = GenerateImages(prompt=prompt)

                with open(data_file_path, "w") as f:
                    f.write(f"{prompt},False")

                if success:
                    break
            else:
                sleep(1)

        except FileNotFoundError:
            print("ImageGeneration.data file not found, recreating...")
            setup_data_file()
            sleep(1)
        except ValueError as e:
            print(f"Invalid data format in file: {e}")
            sleep(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sleep(1)


if __name__ == "__main__":
    main()
