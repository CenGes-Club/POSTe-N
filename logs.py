"""
Raise Exceptions will be Automatically Logged to .log file here.
"""
from enum import Enum, auto

from datetime import datetime, timedelta
import os
from configs import parse_string_config


DATA_LOG_PATH = parse_string_config('config.xml', 'datalogpath')
EVENT_LOG_PATH = parse_string_config('config.xml', 'eventlogpath')


class EventType(Enum):  # TODO: This enum might be pointless
    CMSG_OK = auto()
    CMSG_NOK = auto()


def rename_log_file(now: datetime) -> None:
    previous_day: str = (now - timedelta(days=1)).strftime("%m-%d-%y")  # format should be 'mm-dd'
    os.rename(DATA_LOG_PATH, DATA_LOG_PATH[:-4] + '_' + previous_day + DATA_LOG_PATH[-4:])
    os.rename(EVENT_LOG_PATH, EVENT_LOG_PATH[:-4] + '_' + previous_day + EVENT_LOG_PATH[-4:])
