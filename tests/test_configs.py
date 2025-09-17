import unittest
import tempfile
import os
from configs import parse_serial_config, parse_string_config
import serial
from xml.etree import ElementTree


# Sample XML config string
CONFIG_XML = """<?xml version="1.0"?>
<config>
    <rpi>
        <baudrate>5432</baudrate>
        <parity>PARITY_NONE</parity>
        <bytesize>EIGHTBITS</bytesize>
        <stopbits>STOPBITS_ONE</stopbits>
    </rpi>
    <datalog>/home/postekit/POSTe/data_log.csv</datalog>
</config>
"""

class TestConfigReader(unittest.TestCase):

    def setUp(self):
        # Create a temporary XML file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        self.temp_file.write(CONFIG_XML.encode("utf-8"))
        self.temp_file.close()

    def tearDown(self):
        # Clean up the temporary file
        os.remove(self.temp_file.name)

    def test_read_config_no_errors(self):
        try:
            config = parse_serial_config(self.temp_file.name, 'rpi')
            # Basic assertions
            self.assertEqual(config["baudrate"], 5432)
            self.assertEqual(config["parity"], serial.PARITY_NONE)
            self.assertEqual(config["stopbits"], serial.STOPBITS_ONE)
        except Exception as e:
            self.fail(f"read_config raised an exception unexpectedly: {e}")

    def test_read_string_config(self):
        try:
            path = parse_string_config(self.temp_file.name, 'datalog')
            self.assertEqual('/home/postekit/POSTe/data_log.csv', path)
        except Exception as e:
            self.fail(f"read_config raised an exception unexpectedly: {e}")


if __name__ == "__main__":
    unittest.main()
