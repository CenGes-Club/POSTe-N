"""
Lora Specific Command Stuff
"""
from typing import final, Union

import serial
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

from logs import EventType


class AT(Enum):
    # Status Check
    AT = "AT"
    OK = "AT+OK"

    # One Way Commands
    MSG = "AT+MSG"

    # Commands that Send Acknowledgement Later
    JOIN = "AT+JOIN"
    CMSG = 'AT+CMSG'


@dataclass
class ReplyFormat:
    start: str
    end: str
    type: EventType


CMSG_AWK_REPLY_OK = ReplyFormat('ACK Received', 'Done', EventType.CMSG_OK)


def get_command(cmd):
    """
    :param cmd:`ATCmd`
    :return:`str`
    """
    return cmd.value


def write_to_serial(port, command, arg=None):
    """ Writes the command to the serial port

    :param port: `serial.Serial` object
    :param command: `string`
    :param arg: `string`
    :return:
    """
    cmd = get_command(command)
    if arg is not None:
        cmd += '=' + '"' + arg + '"'
    cmd += '\n'
    port.write(cmd.encode('ascii'))


@dataclass
class SerialMessage:
    lines: list[str]
    timestamp: datetime = field(default_factory=datetime.now)


class MessageHandler(ABC):
    def __init__(self, reply_format: ReplyFormat):
        self.start_marker = reply_format.start
        self.end_marker = reply_format.end

    @final
    def can_handle(self, line: str) -> bool:
        """Check if this handler should start collecting"""
        return line.startswith(self.start_marker)

    @final
    def feed(self, line: str, buffer: list[str]) -> tuple[bool, Union[SerialMessage, None]]:
        """Collect lines until end marker is reached"""
        buffer.append(line)
        if line.startswith(self.end_marker):
            msg = SerialMessage(buffer.copy())
            buffer.clear()
            return True, msg
        return False, None

    @abstractmethod
    def process(self, msg: SerialMessage):
        ...


class CMessageOkHandler(MessageHandler):
    def __init__(self):
        super().__init__(CMSG_AWK_REPLY_OK)

    def process(self, msg: SerialMessage):
        print("\n\nReply Received From CMSG:\n", msg.lines)
        print("\n\n")


class SerialDispatcher:
    def __init__(self, port: serial.Serial, handlers=None):
        self.port = port
        self.handlers = handlers or []
        self.buffer = []
        self.active_handler: Union[MessageHandler, None] = None

    def run(self):
        while True:  # this uses the `command` oop principle
            if self.port.in_waiting:
                line = self.port.readline().decode().strip()  # decode and strip might be unnecessary

                if self.active_handler is None:
                    # look for a handler that matches this line
                    for handler in self.handlers:
                        if handler.can_handle(line):
                            self.active_handler = handler
                            self.buffer = [line]
                            break
                else:
                    # continue collecting for the active handler
                    done, msg = self.active_handler.feed(line, self.buffer)
                    if done:
                        self.active_handler.process(msg)
                        self.active_handler = None
