from datetime import datetime

import unittest
from data import SensorData, CompiledSensorData, FLOOD_FORMAT, RAIN_DATA_FORMAT, RAIN_ACCU_FORMAT, DataSource, RawData


class TestDataclass(unittest.TestCase):

    def test_write_to_csv(self):
        date = datetime(2020, 1, 1, 3)
        data_1 = SensorData(
            source=DataSource.DIGITAL_RAIN_GAUGE,
            unit='cm',
            date=date,
            data=[RawData(format=FLOOD_FORMAT, datum=None)],
        )
        data_2 = SensorData(
            source=DataSource.DIGITAL_RAIN_GAUGE,
            unit='mm',
            date=date,
            data=[RawData(format=RAIN_DATA_FORMAT, datum=None)],
        )
        payload = CompiledSensorData(data=[data_1, data_2]).get_csv_format(date)
        expected = [date, '#####', '######']
        self.assertEqual(expected, payload)


if __name__ == '__main__':
    unittest.main()
