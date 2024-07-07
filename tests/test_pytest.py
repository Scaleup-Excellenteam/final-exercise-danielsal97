import datetime
import os
import pytest
import requests
from test_helpers import TestHelpers  # Import the TestHelpers class

# Constants
FILE_NAME = 'f4a40e7d.pptx'
FILE_PATH = os.path.join("../", FILE_NAME)
UPLOADS_PATH = '../shared_files/uploads'


@pytest.fixture(scope="module")
def helpers():
    """Fixture to provide an instance of TestHelpers."""
    return TestHelpers()


@pytest.fixture(scope="module")
def run_web_api(helpers):
    """Fixture to start the web API server before tests and stop it after."""
    process = helpers.start_subprocess(['python', '../web_api/app.py'])
    yield process
    helpers.terminate_subprocess(process)
    helpers.delete_files_created_after(UPLOADS_PATH)


@pytest.fixture(scope="module")
def run_explainer(helpers):
    """Fixture to start the explainer process before tests and stop it after."""
    process = helpers.start_subprocess(['python', '../client/client.py', 'upload', FILE_PATH])
    yield process
    helpers.terminate_subprocess(process)
    helpers.delete_files_created_after(UPLOADS_PATH)


def test_upload_returns_uid(helpers, run_web_api):
    """Test if the upload endpoint returns a UID."""
    response = helpers.upload_file(FILE_PATH)
    assert response.status_code == 201
    data = response.json()
    assert 'uid' in data
    uid = data['uid']
    assert isinstance(uid, str)


def test_upload_creates_file(helpers, run_web_api):
    """Test if the uploaded file is correctly created with a timestamp and UID."""
    response = helpers.upload_file(FILE_PATH)
    assert response.status_code == 201
    data = response.json()
    uid = data['uid']
    timestamp_format = "%Y-%m-%d_%H-%M-%S"
    expected_filename_prefix = datetime.datetime.now().strftime(timestamp_format) + f"_{uid}_{FILE_NAME}"

    # Check if the uploaded file is created in the uploads folder with the correct format
    files = os.listdir(UPLOADS_PATH)
    matching_files = [f for f in files if f.startswith(expected_filename_prefix)]
    assert len(matching_files) == 1
    uploaded_filename = matching_files[0]

    # Further validate that the filename contains the UID and the original filename
    assert uid in uploaded_filename
    assert FILE_NAME in uploaded_filename


def test_explainer_processes_new_files(run_explainer):
    """Test if the explainer process finishes successfully."""
    process = run_explainer
    process.wait()  # Ensure the process has finished
    assert process.returncode == 0  # Check if the process ended successfully


def test_uid_not_found(helpers, run_web_api):
    """Test if querying a nonexistent UID returns a 404 status."""
    response = requests.get('http://127.0.0.1:5000/status', params={'uid': 'nonexistent'})
    assert response.status_code == 404


def test_pending_status_after_upload(helpers, run_web_api):
    """Test if the status of a newly uploaded file is 'pending'."""
    response = helpers.upload_file(FILE_PATH)
    data = response.json()
    uid = data['uid']

    status_response = requests.get('http://127.0.0.1:5000/status', params={'uid': uid})
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data.get('status') == 'pending'


if __name__ == '__main__':
    pytest.main()