"""
Raise Exceptions will be Automatically Logged to .log file here.
"""
from datetime import datetime, timedelta
import os
from configs import parse_string_config


DATA_LOG_PATH = parse_string_config('config.xml', 'datalogpath')
EVENT_LOG_PATH = parse_string_config('config.xml', 'eventlogpath')


def rename_log_file(now: datetime) -> None:
    previous_day: str = (now - timedelta(days=1)).strftime("%m-%d")  # format should be 'mm-dd'
    # TODO: Try statement for the rename function so no comparison by > or <, but within < x < instead.
    os.rename(DATA_LOG_PATH, DATA_LOG_PATH + '_' + previous_day)  # TODO: Consult with this Format
    os.rename(EVENT_LOG_PATH, EVENT_LOG_PATH + '_' + previous_day)
