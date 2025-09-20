"""
Dataclass for DSG and DRRG and the Payload Functions
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType, Optional


NULL_FORMAT = '#'


_DataFormat = NewType('_DataFormat', str)
FLOOD_FORMAT = _DataFormat("5.0")
RAIN_DATA_FORMAT = _DataFormat("4.2")
RAIN_ACCU_FORMAT = _DataFormat("4.17")


class DataSource(Enum):
    DIGITAL_RAIN_GAUGE = 'DRRG'  # data
    DIGITAL_STAFF_GAUGE = 'DSG'  # digital staff gauge


@dataclass
class RawData:
    format: _DataFormat
    datum: Optional[float]


@dataclass
class SensorData:
    source: DataSource
    unit: str  # TODO: Remove?
    date: datetime
    data: list[RawData]

    def append_data(self, datum: RawData):
        self.data.append(datum)

    def get_payload_format(self) -> str:
        payload = ''
        for element in self.data:  # `RawData`
            if element.datum is None:
                payload += get_null_format(NULL_FORMAT, element.format)
                continue
            payload += fill_zeroes(element.datum, element.format)
        return payload

    def get_datum(self) -> list[float]:
        return [raw_data.datum for raw_data in self.data]


@dataclass
class CompiledSensorData:
    data: list[SensorData] = None

    def append_data(self, datum: SensorData):
        self.data.append(datum)

    def get_full_payload(self, now) -> str:
        payload = ''
        for sensor_data in self.data:
            payload += sensor_data.get_payload_format()
        return now.strftime("%H%M") + payload

    def get_csv_format(self, now) -> list:
        data = [now]
        for sensor_data in self.data:
            data += sensor_data.get_datum()
        return data


def zeroth_function(zeroes: int, number: str, prefix: bool) -> str:
    missing_zeroes = zeroes - len(number) if len(number) <= zeroes else 0
    return '0' * missing_zeroes + number if prefix is True else number + '0' * missing_zeroes


def fill_zeroes(number: float, data_format: _DataFormat) -> str:
    """Generates a string where missing leading and trailing numbers are filled with zeroes.

    Args:
        number:
            The floating point number where the whole and decimal parts will be filled.
        data_format:
            data_format:
                `DataFormat`: The data format in the form "x.y" where:
                    - x is the number of whole number digits
                    - y is the number of decimal digits
    Returns:
        >>> fill_zeroes(1.3, _DataFormat("3.2"))
        '001.30'
    """
    n_leading, n_trailing = map(int, data_format.split("."))
    whole_numbers, decimals = str(round(number, n_trailing)).split(".")
    if int(decimals) == 0:
        decimals = ''

    # Adds the Leading Zeroes to the Whole Number
    whole_number = zeroth_function(n_leading, whole_numbers, True)
    decimal = zeroth_function(n_trailing, decimals, False)

    return whole_number + decimal

def get_null_format(null_format: str, data_format: _DataFormat) -> str:
    """
    Generate the payload's null format string in the case where data is absent.

    Args:
        null_format:
            The character string to used as the placeholder for null data.

        data_format:
            The data format in the form "x.y" where:
                - x is the number of whole number digits
                - y is the number of decimal digits

    Returns:
        str:
            A str representing the null formatted payload.
    Example:
        >>> get_null_format('#', _DataFormat("3.2"))
        '#####'
    """
    n_leading, n_trailing = map(int, data_format.split("."))
    return null_format * n_leading + null_format * n_trailing
