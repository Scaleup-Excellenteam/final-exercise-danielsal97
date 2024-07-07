import argparse
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HTTPClient:
    """
    A simple HTTP client for sending GET and POST requests.
    """

    def __init__(self, base_url):
        """
        Initialize the HTTP client with a base URL.

        :param base_url: The base URL for the HTTP requests.
        """
        self.base_url = base_url

    def get(self, endpoint, params=None):
        """
        Send a GET request to the specified endpoint.

        :param endpoint: The endpoint to send the GET request to.
        :param params: The query parameters for the GET request.
        :return: The response from the server as a JSON object, or None if an error occurred.
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        return self._process_response(response)

    def post(self, endpoint, data=None, json=None, files=None):
        """
        Send a POST request to the specified endpoint.

        :param endpoint: The endpoint to send the POST request to.
        :param data: The form data to send in the POST request.
        :param json: The JSON data to send in the POST request.
        :param files: The files to send in the POST request.
        :return: The response from the server as a JSON object, or None if an error occurred.
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, data=data, json=json, files=files)
        return self._process_response(response)

    def _process_response(self, response):
        """
        Process the HTTP response, raising errors if the status code indicates a failure.

        :param response: The response object returned by the requests library.
        :return: The JSON content of the response if successful, or None if an error occurred.
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error occurred: {err}")
        except Exception as err:
            logger.error(f"Other error occurred: {err}")


def parse_arguments():
    """
    Parse command-line arguments.

    :return: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Upload a file to the server or check status")
    parser.add_argument('operation', choices=['upload', 'status'], help='Operation to perform: upload or status')
    parser.add_argument('path', type=str, help='Path to the file to be uploaded or UID to check status')
    parser.add_argument('--server', type=str, default='http://127.0.0.1:5000', help='Base URL of the server')
    return parser.parse_args()


def upload_file(client, file_path):
    """
    Upload a file to the server.

    :param client: The HTTP client to use for the request.
    :param file_path: The path to the file to be uploaded.
    """
    if not os.path.exists(file_path):
        logger.error(f"File '{file_path}' does not exist.")
        return

    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = client.post('upload', files=files)
        if response:
            logger.info(f"Upload Response: {response}")
            uid = response.get('uid')
            if uid:
                logger.info(f"File uploaded successfully with UID: {uid}")
            else:
                logger.warning("No UID returned from the upload response.")
        else:
            logger.error("Failed to upload file.")


def check_status(client, uid):
    """
    Check the status of an uploaded file.

    :param client: The HTTP client to use for the request.
    :param uid: The UID of the uploaded file to check the status of.
    """
    response = client.get("status", params={'uid': uid})
    if response:
        logger.info(f"Status Response: {response}")
    else:
        logger.error(f"Failed to retrieve status for UID: {uid}")


def main():
    """
    Main function to parse arguments and perform the requested operation.
    """
    args = parse_arguments()
    client = HTTPClient(args.server)

    if args.operation == 'upload':
        upload_file(client, args.path)
    elif args.operation == 'status':
        check_status(client, args.path)


if __name__ == "__main__":
    main()