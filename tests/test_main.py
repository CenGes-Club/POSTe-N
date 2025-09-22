import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import main
from data import DataSource


class TestMain(unittest.TestCase):

    def test_get_data_from_port_line_mode(self):
        mock_port = MagicMock()
        mock_port.readline.return_value = b'1234'
        result = main.get_data_from_port(mock_port, b'cmd', line_mode=True)
        mock_port.write.assert_called_once_with(b'cmd')
        self.assertEqual(result, b'1234')

    def test_get_data_from_port_non_line_mode(self):
        mock_port = MagicMock()
        mock_port.read.return_value = b'abcd'
        mock_port.in_waiting = 4
        result = main.get_data_from_port(mock_port, b'cmd', line_mode=False)
        mock_port.write.assert_called_once_with(b'cmd')
        mock_port.read.assert_called_once_with(4)
        self.assertEqual(result, b'abcd')

    def test_do_crc_check_valid(self):
        data = b'\x01\x03\x00\x00'  # CRC library will compute something
        crc_value = main.do_crc_check(data)
        self.assertIsInstance(crc_value, int)

    @patch("main.write_to_serial")
    def test_setup_raises_if_port_closed(self, mock_write):
        mock_lora = MagicMock()
        mock_lora.is_open = False

        with self.assertRaises(Exception):
            main.setup(mock_lora)

        mock_write.assert_not_called()

    @patch("main.write_to_serial")
    def test_setup_sends_join_when_open(self, mock_write):
        mock_lora = MagicMock()
        mock_lora.is_open = True
        mock_lora.in_waiting = 0  # no reply branch

        main.setup(mock_lora)

        mock_write.assert_called_once_with(mock_lora, main.AT.JOIN)

    @patch("main.get_data_from_port")
    @patch("main.do_crc_check", return_value=0)
    def test_get_drrg_data_success(self, mock_crc, mock_port):
        # Contract: returns SensorData with 2 data points and has_error=False
        mock_port.return_value = bytes(37)  # correct length

        now = datetime.now()
        data, has_error = main.get_drrg_data(now, port=MagicMock())

        self.assertFalse(has_error)
        self.assertEqual(data.source, DataSource.DIGITAL_RAIN_GAUGE)
        self.assertEqual(len(data.data), 2)

    @patch("main.get_data_from_port", return_value=bytes(10))  # too short
    def test_get_drrg_data_no_comm(self, mock_port):
        now = datetime.now()
        data, has_error = main.get_drrg_data(now, port=MagicMock())

        self.assertTrue(has_error)
        self.assertEqual(len(data.data), 2)
        self.assertIsNone(data.data[0].datum)
        self.assertIsNone(data.data[1].datum)

    @patch("main.get_data_from_port", return_value=bytes(37))
    @patch("main.do_crc_check", return_value=123)  # CRC fails
    def test_get_drrg_data_crc_fail(self, mock_crc, mock_port):
        now = datetime.now()
        data, has_error = main.get_drrg_data(now, port=MagicMock())

        self.assertTrue(has_error)
        self.assertIsNone(data.data[0].datum)

    @patch("main.get_data_from_port")
    @patch("main.do_crc_check", return_value=0)
    def test_get_dsg_data_success(self, mock_crc, mock_port):
        mock_port.return_value = b'\x00' * 5  # at least 5 bytes
        now = datetime.now()
        data, has_error = main.get_dsg_data(now, port=MagicMock())

        self.assertFalse(has_error)
        self.assertEqual(data.source, DataSource.DIGITAL_STAFF_GAUGE)
        self.assertEqual(len(data.data), 1)

    @patch("main.get_data_from_port", return_value=b'')
    def test_get_dsg_data_no_data(self, mock_port):
        now = datetime.now()
        data, has_error = main.get_dsg_data(now, port=MagicMock())

        self.assertTrue(has_error)
        self.assertIsNone(data.data[0].datum)

    def test_get_next_midnight(self):
        now = datetime(2025, 9, 22, 10, 30, 15)
        midnight = main.get_next_midnight(now)
        self.assertEqual(midnight, datetime(2025, 9, 23, 0, 0, 0))


if __name__ == '__main__':
    unittest.main()