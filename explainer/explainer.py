import asyncio
import os
import time
import logging

import pptxManagment
import openaiAgent

# Configuration
UPLOAD_FOLDER = '../shared_files/uploads'
OUTPUT_FOLDER = '../shared_files/outputs'
CHECK_INTERVAL = 1  # Interval in seconds to check for new files
LOG_FILE = 'explainer.log'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add file handler to the logger
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


async def process_file(file_path, output_path):
    """
    Process the uploaded file using pptxManagement and openaiAgent.

    Args:
        file_path (str): The path to the file to process.
        output_path (str): The path to save the processed output.
    """
    try:
        key = openaiAgent.get_key()
        await pptxManagment.read_pptx_file(file_path, key, output_path)
        logger.info(f"Processing of {file_path} completed.")
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")


def explainer_directory(directory):
    """
    explainers the specified directory for new files and processes them.

    Args:
        directory (str): The path to the directory to explainer.
    """
    # Get a set of files currently in the directory
    previous_files = set(os.listdir(directory))
    logger.info(f"upload directory: {directory}")

    while True:
        try:
            current_files = set(os.listdir(directory))
            new_files = current_files - previous_files

            if new_files:
                for file_name in new_files:
                    logger.info(f"New file detected: {file_name}")
                    logger.info("Process is started")
                    file_path = os.path.join(directory, file_name)
                    output_path = os.path.join(OUTPUT_FOLDER, file_name)
                    asyncio.run(process_file(file_path, output_path))
                    logger.info("Process ended")
            previous_files = current_files
        except Exception as e:
            logger.error(f"Error explainering directory {directory}: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    explainer_directory(UPLOAD_FOLDER)