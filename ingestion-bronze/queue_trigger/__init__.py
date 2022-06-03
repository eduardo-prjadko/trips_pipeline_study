from datetime import datetime
import json
from json import JSONDecodeError
import logging
import os

import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobClient

from owned_exceptions import ExpectedKeysException


def check_expected_keys(message: dict, expected_keys: list) -> None:
    keys = list(message.keys())
    message_keys_check = [key in expected_keys for key in keys]
    if not all(message_keys_check):
        lacking_keys = [keys[index] for index, check in 
            enumerate(message_keys_check) if check is False]
        raise ExpectedKeysException(lacking_keys)

def upload_json_to_blob(
    data: dict, 
    conn_string:str, 
    container: str, 
    blob: str
) -> BlobClient:
    blob_service_client = BlobServiceClient.from_connection_string(conn_string)
    blob_client = blob_service_client.get_blob_client(
        container=container,
        blob=blob
    )
    blob_client.upload_blob(
        data=json.dumps(data),
        overwrite=True
    )
    return blob_client

def parse_datetime(date_str: str) -> datetime:
    parsed_datetime = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return parsed_datetime

def main(msg: func.QueueMessage) -> None:

    message = msg.get_body().decode('utf-8')

    try:
        message = json.loads(message)
    except JSONDecodeError:
        raise Exception('message is not json serializable.')
    
    expected_keys = [
        'region', 
        'origin_coord', 
        'destination_coord',
        'datetime',
        'datasource'
    ]
    check_expected_keys(message, expected_keys)

    trip_datetime = parse_datetime(message['datetime'])
    blob_conn_string = os.getenv('AzureWebJobsDATA_LAKE')
    ingestion_container = os.getenv('INGESTION_CONTAINER')
    blob_path = f'trips/{trip_datetime.year}/{trip_datetime.month:02}/{trip_datetime.day:02}'
    blob_name = f'{trip_datetime.isoformat()}.json'
    upload_json_to_blob(
        data=message,
        conn_string=blob_conn_string,
        container=ingestion_container,
        blob=f'{blob_path}/{blob_name}'
    )
    
