"""
Dataclass for DSG and DRRG and the Payload Functions
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType


DataFormat = NewType('DataFormat', str)
FLOOD_FORMAT = DataFormat("5.0")  # TODO: Reconfirm if this is right. There should be no decimals right?
RAIN_DATA_FORMAT = DataFormat("4.2")
RAIN_ACCU_FORMAT = DataFormat("4.17")


class DataSource(Enum):  # TODO: Check for naming convention
    digital_rain_gauge = 'DRRG' # data
    digital_staff_gauge = 'DSG' # digital staff gauge


@dataclass
class RawData:
    format: DataFormat
    datum: float


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
        for element in self.data:
            payload += fill_zeroes(element.datum, element.format)
        return payload

    def get_csv_format(self) -> list:
        return [self.date] + self.data + [self.source.value]


@dataclass
class CompiledSensorData:
    data: list[SensorData] = None

    def append_data(self, datum: SensorData):
        self.data.append(datum)

    def get_full_payload(self) -> str:
        payload = ''
        for sensor_data in self.data:
            payload += sensor_data.get_payload_format()
        return payload


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
