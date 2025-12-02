from datetime import datetime

import unittest
from data import SensorData, CompiledSensorData, FLOOD_FMT, RAIN_FMT, RAIN_ACCU_FMT, DataSource, RawData


class TestDataclass(unittest.TestCase):

    def test_write_to_csv(self):
        date = datetime(2020, 1, 1, 3)
        data_1 = SensorData(
            source=DataSource.DIGITAL_RAIN_GAUGE,
            unit='cm',
            date=date,
            data=[RawData(format=FLOOD_FMT, datum=None)],
        )
        data_2 = SensorData(
            source=DataSource.DIGITAL_RAIN_GAUGE,
            unit='mm',
            date=date,
            data=[RawData(format=RAIN_FMT, datum=None)],
        )
        payload = CompiledSensorData(data=[data_1, data_2]).get_csv_format(date)
        expected = [date, None, None]
        self.assertEqual(expected, payload)


if __name__ == '__main__':
    unittest.main()
