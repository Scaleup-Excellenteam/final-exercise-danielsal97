import os
import unittest
from test_helpers import TestHelpers
from explainer.pptxManagment import save_to_json

FILE_NAME = 'f4a40e7d.pptx'
FILE_PATH = os.path.join("../", FILE_NAME)
UPLOADS_PATH = '../shared_files/uploads'


class MyTestCase(unittest.TestCase):
    """Unit tests for various components of the application."""

    def setUp(self):
        """Set up test variables and processes."""
        self.helpers = TestHelpers()
        self.pptx_file = FILE_PATH
        self.text = "openai response"
        self.processes = []

    def tearDown(self):
        """Terminate and wait for all processes to end."""
        for proc in self.processes:
            self.helpers.terminate_subprocess(proc)
        self.helpers.delete_files_created_after(UPLOADS_PATH)

    def test_save_to_json(self):
        """Test the save_to_json function."""
        json_file = os.path.splitext(self.pptx_file)[0] + '.json'
        save_to_json(self.text, json_file)
        self.assertTrue(os.path.exists(json_file), "JSON file was not created.")
        os.remove(json_file)

    def test_start_web_API(self):
        """Test starting the web API."""
        process = self.helpers.start_subprocess(['python', '../web_api/app.py'])
        self.processes.append(process)
        self.assertNotEqual(process.pid, 0)

    def test_start_explainer(self):
        """Test starting the explainer process."""
        explainer_process = self.helpers.start_subprocess(['python', '../explainer/explainer.py'])
        self.processes.append(explainer_process)
        self.assertIsNotNone(explainer_process)

    def test_upload_file(self):
        """Test uploading a file using the client script."""
        explainer_process = self.helpers.start_subprocess(['python', '../client/client.py', 'upload', self.pptx_file])
        self.processes.append(explainer_process)
        explainer_process.wait()
        self.assertNotEqual(explainer_process.returncode, 200, "Upload process failed.")
        self.assertTrue(os.path.exists(self.pptx_file), "Uploaded file was not found in the expected directory.")


if __name__ == '__main__':
    unittest.main()