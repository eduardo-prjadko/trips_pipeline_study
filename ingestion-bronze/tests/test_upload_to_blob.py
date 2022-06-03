import os

import pytest

from queue_trigger import upload_json_to_blob


@pytest.fixture
def data():
    return {'example': 'data'}

@pytest.fixture
def conn_string():
    return os.getenv('CONN_STRING')

@pytest.fixture
def container():
    return os.getenv('CONTAINER')

@pytest.fixture
def blob():
    return os.getenv('BLOB')

def test_upload_json_to_blob(data, conn_string, container, blob):
    blob = upload_json_to_blob(
        data=data,
        conn_string=conn_string,
        container=container,
        blob=blob
    )

    assert blob.exists()

    blob.delete_blob()

