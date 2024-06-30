import os
import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import main
from pptxManagment import read_pptx_file

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
EXPLAINER_LOG_DIR = 'logs/explainer'
os.makedirs(EXPLAINER_LOG_DIR, exist_ok=True)

# Configure logging for Explainer
explainer_handler = TimedRotatingFileHandler(os.path.join(EXPLAINER_LOG_DIR, 'explainer.log'), when='midnight',
                                             backupCount=5)
explainer_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
explainer_handler.setLevel(logging.INFO)
explainer_logger = logging.getLogger('explainer')
explainer_logger.addHandler(explainer_handler)
explainer_logger.setLevel(logging.INFO)


def find_file_by_uid(uid):
    """
    Find the file in the upload folder that contains the given UID in its name.

    :param uid: Unique identifier for the file
    :return: The filename if found, None otherwise
    """
    files = [f for f in os.listdir(UPLOAD_FOLDER) if uid in f]
    if not files:
        explainer_logger.error(f"File with UID {uid} not found.")  # Log error
        return None
    return files[0]


def get_file_paths(file, uid):
    """
    Generate the upload and output paths for the given file and UID.

    :param file: The filename
    :param uid: Unique identifier for the file
    :return: A tuple containing the upload path and output path
    """
    upload_path = os.path.join(UPLOAD_FOLDER, file)
    output_path = os.path.join(OUTPUT_FOLDER, f"{uid}.json")
    return upload_path, output_path


async def convert_pptx_to_json(upload_path, output_path):
    """
    Process the PPTX file and save the output as a JSON file.

    :param upload_path: Path to the uploaded PPTX file
    :param output_path: Path to save the output JSON file
    :return: True if processing is successful, False otherwise
    """
    try:
        key = main.get_key()
        await read_pptx_file(upload_path, key, output_path)  # Await the async function
        explainer_logger.info(f"Finished processing file. Output saved to {output_path}")  # Log info
        return True
    except Exception as e:
        explainer_logger.error(f"Error processing file: {e}")  # Log error
        return False


async def process_file_async(uid):
    """
    Asynchronously process the file associated with the given UID.
    Reads the PPTX file, processes it, and saves the output as a JSON file.

    :param uid: Unique identifier for the file to be processed
    :return: Path to the output JSON file if processing is successful, None otherwise
    """
    file = find_file_by_uid(uid)
    if not file:
        return None

    upload_path, output_path = get_file_paths(file, uid)

    explainer_logger.debug(f"Processing file {file}...")  # Log debug
    explainer_logger.debug(f"Upload path: {upload_path}")  # Log debug
    explainer_logger.debug(f"Output path: {output_path}")  # Log debug

    if not os.path.exists(output_path):
        success = await convert_pptx_to_json(upload_path, output_path)
        if not success:
            return None
    else:
        explainer_logger.info(f"Output file {output_path} already exists.")  # Log info

    return output_path


def process_file(uid):
    """
    Synchronously process the file associated with the given UID by running the async processing function.

    :param uid: Unique identifier for the file to be processed
    :return: Path to the output JSON file if processing is successful, None otherwise
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    output_path = loop.run_until_complete(process_file_async(uid))
    return output_path
