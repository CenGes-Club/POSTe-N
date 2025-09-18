from data import FLOOD_FORMAT, RAIN_DATA_FORMAT, RAIN_ACCU_FORMAT, fill_zeroes, get_null_format
import unittest


class TestDataFormatter(unittest.TestCase):
    def test_flood_format(self):
        n = float(12.12344)
        expected = "00012"
        self.assertEqual(expected, fill_zeroes(n, FLOOD_FORMAT))

    def test_accu_format(self):
        n = 0.00012
        expected = "0000" + "00012000000000000"
        self.assertEqual(expected, fill_zeroes(n, RAIN_ACCU_FORMAT))

    def test_rain_data_format(self):
        n = 1234.2
        expected = "123420"
        self.assertEqual(expected, fill_zeroes(n, RAIN_DATA_FORMAT))
        n = 1234.56
        expected = "123456"
        self.assertEqual(expected, fill_zeroes(n, RAIN_DATA_FORMAT))

    def test_null_format_for_rain_data(self):
        null_format = "#"
        expected = "######"
        self.assertEqual(expected, get_null_format(null_format, RAIN_DATA_FORMAT))

    def test_null_format_for_flood_data(self):
        null_format = "#"
        expected = "#####"
        self.assertEqual(expected, get_null_format(null_format, FLOOD_FORMAT))


if __name__ == "__main__":
    unittest.main()
