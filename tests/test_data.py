import unittest
from datetime import datetime
from data import SensorData, DataSource, FLOOD_FORMAT, RawData, CompiledSensorData, RAIN_DATA_FORMAT


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.data1 = SensorData(
            source=DataSource.DIGITAL_RAIN_GAUGE,
            unit='cm',
            date=datetime(1, 1, 1, hour=1, minute=2),
            data=[]
        )
        self.data2 = SensorData(
            source=DataSource.DIGITAL_STAFF_GAUGE,
            unit='mm',
            date=datetime(1, 1, 1, hour=1, minute=2),
            data=[]
        )
        self.compiled_data = CompiledSensorData(data=[self.data1, self.data2])

    def test_flood_data(self):
        n = float(1200)
        expected = '01200'
        self.data1.append_data(RawData(FLOOD_FORMAT, n))
        self.assertEqual(expected, self.data1.get_payload_format())

    def test_rain_data(self):
        n = 1234.2
        expected = "123420"
        self.data2.append_data(RawData(RAIN_DATA_FORMAT, n))
        self.assertEqual(expected, self.data2.get_payload_format())

    def test_time_data(self):
        expected_time = '0102'
        self.assertEqual(expected_time, self.data1.date.strftime("%H%M"))

    def test_full_payload(self):
        n = float(1200)
        expected_1 = '01200'
        self.data1.append_data(RawData(FLOOD_FORMAT, n))
        self.data1.append_data(RawData(FLOOD_FORMAT, n))
        n = 1234.2
        expected_2 = "123420"
        self.data2.append_data(RawData(RAIN_DATA_FORMAT, n))
        payload = self.compiled_data.get_full_payload()
        self.assertEqual(payload, expected_1 + expected_1 + expected_2)


if __name__ == '__main__':
    unittest.main()
