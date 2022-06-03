from datetime import datetime
import logging

import pytest

from queue_trigger import parse_datetime


def test_right_date_str():
    parsed_datetime = parse_datetime('2022-06-02 22:30:40')

    assert isinstance(parsed_datetime, datetime)

def test_wrong_date_str():
    with pytest.raises(ValueError) as exception_info:
        parse_datetime('2022-06-02 22:30')

    logging.debug(exception_info)
