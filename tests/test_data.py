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
        self.data2.append_data(RawData(FLOOD_FORMAT, None))

        expected_null_format = '#####'
        the_time = datetime(1, 1, 1, hour=12, minute=30)
        payload = self.compiled_data.get_full_payload(the_time)
        expected_payload = '1230' + expected_1 + expected_1 + expected_2 + expected_null_format
        print("\n\nExpected Payload: ", expected_payload)

        self.assertEqual(expected_payload, payload)

    def test_scientific_notation_small_numbers(self):
        """Test that very small numbers (that would produce scientific notation) are handled correctly."""
        # Test case from the issue: 68739512313e-06
        n = 0.000068739512313
        expected = '000000'  # Rounds to 0.00 with 2 decimal places
        self.data1.append_data(RawData(RAIN_DATA_FORMAT, n))
        self.assertEqual(expected, self.data1.get_payload_format())

    def test_scientific_notation_edge_cases(self):
        """Test various scientific notation edge cases."""
        from data import fill_zeroes, _DataFormat
        
        # Very small number
        result = fill_zeroes(1e-6, _DataFormat("4.2"))
        self.assertEqual(result, "000000")
        
        # Small number with scientific notation
        result = fill_zeroes(1.234e-5, _DataFormat("4.2"))
        self.assertEqual(result, "000000")
        
        # Normal numbers should still work
        result = fill_zeroes(1.3, _DataFormat("3.2"))
        self.assertEqual(result, "00130")


if __name__ == '__main__':
    unittest.main()
