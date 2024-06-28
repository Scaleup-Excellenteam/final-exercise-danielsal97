
from dotenv import load_dotenv
import asyncio
import os
from pptxManagment import choose_file, read_pptx_file

def get_key():
    load_dotenv()
    env_key = os.getenv('OPENAI_API_KEY')
    if not env_key:
        print("API key not found. Please set it in the .env file.")
        exit(1)
    return env_key


if __name__ == '__main__':
    key = get_key()
    file_path = choose_file()
    asyncio.run(read_pptx_file(file_path, key))
