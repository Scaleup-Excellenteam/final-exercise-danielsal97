import os
import asyncio
import main
from pptxManagment import read_pptx_file

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'


async def process_file_async(uid):
    files = [f for f in os.listdir(UPLOAD_FOLDER) if uid in f]
    if not files:
        print(f"File with UID {uid} not found.")
        return None

    file = files[0]
    upload_path = os.path.join(UPLOAD_FOLDER, file)
    output_path = os.path.join(OUTPUT_FOLDER, f"{uid}.json")

    print(f"Processing file {file}...")  # Debugging statement
    print(f"Upload path: {upload_path}")  # Debugging statement
    print(f"Output path: {output_path}")  # Debugging statement

    if not os.path.exists(output_path):
        try:
            key = main.get_key()
            await read_pptx_file(upload_path, key, output_path)  # Await the async function
            print(f"Finished processing file {file}. Output saved to {output_path}")  # Debugging statement
        except Exception as e:
            print(f"Error processing file {file}: {e}")  # Debugging statement
            return None
    else:
        print(f"Output file {output_path} already exists.")  # Debugging statement

    return output_path


def process_file(uid):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    output_path = loop.run_until_complete(process_file_async(uid))
    return output_path
