"""
Lora Specific Command Stuff
"""

from enum import Enum
import time


class AT(Enum):
    # Status Check
    AT = "AT"
    OK = "AT+OK"

    # One Way Commands
    MSG = "AT+MSG"

    # Commands that Send Acknowledgement Later
    JOIN = "AT+JOIN"
    CMSG = 'AT+CMSG'


def get_command(cmd):
    """
    :param cmd:`ATCmd`
    :return:`str`
    """
    return cmd.value


def write_to_serial(serial, command, arg=''):
    """ Writes the command to the serial port

    :param serial: `serial.Serial` object
    :param command: `string`
    :param arg: `string`
    :return:
    """
    cmd = get_command(command)
    if arg != '':
        cmd += '+' + arg
    cmd += '\n'
    serial.write(cmd.encode('ascii'))
