import logging

import pytest

from owned_exceptions import ExpectedKeysException


def test_expected_keys_exception():
    with pytest.raises(ExpectedKeysException) as except_info:
        raise ExpectedKeysException(['exception', 'test'])
    
    logging.debug(except_info)