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


def zeroth_function(leading_zeroes: str, number: list[str]) -> str:
    formatted_number = ''
    i = 0
    for _ in leading_zeroes:
        if i < len(number):
            formatted_number += number[i]
            i += 1
        else:
            formatted_number += '0'
    return formatted_number


def fill_zeroes(data: float, data_format: DataFormat) -> str:
    leading_zeroes, trailing_zeroes = get_zeroes_from(data_format)
    whole_numbers, decimals = str(data).split(".")

    ## Adds the Leading Zeroes to the Whole Number
    whole_number = zeroth_function(leading_zeroes, list(reversed(whole_numbers)))
    decimal = zeroth_function(trailing_zeroes, list(decimals))

    return whole_number[::-1] + decimal
