import datetime
import subprocess
import time
import os
import requests

class TestHelpers:
    def __init__(self):
        self.start_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    @staticmethod
    def start_subprocess(command):
        """Start a subprocess with the given command and return the process."""
        process = subprocess.Popen(command)
        time.sleep(2)  # Wait for the process to start
        return process

    @staticmethod
    def terminate_subprocess(process):
        """Terminate the given subprocess and wait for it to finish."""
        process.terminate()
        process.wait()

    @staticmethod
    def upload_file(file_path):
        """Helper function to upload a file to the web API."""
        with open(file_path, 'rb') as file:
            response = requests.post('http://127.0.0.1:5000/upload', files={'file': file})
        return response

    def delete_files_created_after(self, uploads_path):
        """Delete all files in the uploads directory created after the given timestamp."""
        for file in os.listdir(uploads_path):
            file_path = os.path.join(uploads_path, file)
            file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            if file_creation_time > datetime.datetime.strptime(self.start_timestamp, "%Y-%m-%d_%H-%M-%S"):
                os.remove(file_path)