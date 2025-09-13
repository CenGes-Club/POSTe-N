"""
The package that handles data transformation of the Payload.
"""
from typing import NewType


DataFormat = NewType('DataFormat', str)

FLOOD_FORMAT = DataFormat("5.0")
RAIN_DATA_FORMAT = DataFormat("4.2")
RAIN_ACCU_FORMAT = DataFormat("4.17")


def get_zeroes_from(data_format: DataFormat) -> tuple[str, str]:
    n_leading, n_trailing = data_format.split(".")
    return str('0' * int(n_leading)), str('0' * int(n_trailing))


def zeroth_function(zeroes: str, number: str, prefix: bool) -> str:
    missing_zeroes = len(zeroes) - len(number) if len(number) <= len(zeroes) else 0
    return '0' * missing_zeroes + number if prefix is True else number + '0' * missing_zeroes


def fill_zeroes(data: float, data_format: DataFormat) -> str:
    leading_zeroes, trailing_zeroes = get_zeroes_from(data_format)
    whole_numbers, decimals = str(data).split(".")

    ## Adds the Leading Zeroes to the Whole Number
    whole_number = zeroth_function(leading_zeroes, whole_numbers, True)
    decimal = zeroth_function(trailing_zeroes, decimals, False)

    return whole_number + decimal
