import logging

import pytest

from owned_exceptions import ExpectedKeysException
from queue_trigger import check_expected_keys


@pytest.fixture
def message():
    return {'expected': 'key', 'not_expected': 'key'}

def test_check_expected_keys_raise_exception(message):
    with pytest.raises(ExpectedKeysException) as exception_info:
        check_expected_keys(message, ['expected'])
    
    logging.debug(exception_info)

def test_check_expected_keys_no_exception(message):
    message = {'expected': 'key', 'not_expected': 'key'}
    check_expected_keys(message, ['expected', 'not_expected'])
