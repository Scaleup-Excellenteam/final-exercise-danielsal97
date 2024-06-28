import os
import unittest
from pptxManagment import save_to_json


class MyTestCase(unittest.TestCase):
    """
    Set up the test environment.
    """
    def setUp(self):
        self.file_name = 'f4a40e7d.json'
        self.text = "openai response"

    """
    Test the 'save_to_json' function.
    """
    def test_something(self):
        json_file = os.path.splitext(self.file_name)[0] + '.json'
        save_to_json(self.text, self.file_name)
        self.assertTrue(os.path.exists(json_file), " JSON file was not created.")
        os.remove(json_file)


if __name__ == '__main__':
    unittest.main()