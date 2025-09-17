import serial
from configs import parse_serial_config, verify_unique_xml_value, parse_string_config
from time import sleep
from commands import write_to_serial, AT
from crccheck.crc import Crc16Modbus
from generics import write_to_csv
from struct import unpack
from datetime import datetime, timedelta
from data import SensorData, DataSource, RawData, RAIN_DATA_FORMAT, RAIN_ACCU_FORMAT, FLOOD_FORMAT, CompiledSensorData
from typing import Optional

from logs import rename_log_file, DATA_LOG_PATH


# Miscelleneous Variables
# Datalog = True
# loop_time = 1
# COUNT = 0


# Initialize Variables
DSG_PORT = serial.Serial(**parse_serial_config('config.xml', 'dsg'))
DRRG_PORT = serial.Serial(**parse_serial_config('config.xml', 'drrg'))
LORA_PORT = serial.Serial(**parse_serial_config('config.xml', 'lora'))


DSG_PORT.rs485_mode = serial.rs485.RS485Settings(
    rts_level_for_tx = False,
    rts_level_for_rx = False,
    delay_before_tx = 0.0,
    delay_before_rx = 0.0
)


## TODO: Move to config.py
#DRRG comm0 is read rain and accumulated rain values
DRRG_COMM_0 = b'\x01\x03\x00\x00\x00\x10\x44\x06'
#DSG comm0 is read water level
DSG_COMM_0 = b'\x01\x03\x00\x00\x00\x02\xC4\x0B'


### Functions for DSG and DRRG ###
def get_data_from_port(port, comm):
    port.write(comm)
    if port.in_waiting > 0:
        return port.readline()
    return None  # TODO: Do Error Handling Here


def do_crc_check(data):
    crc = Crc16Modbus()
    crc.process(data)
    return crc.final()


def setup():
    """Lora Node Join Network"""
    if not LORA_PORT.is_open:
        raise Exception("Lora Node is not open")  # Logging

    write_to_serial(LORA_PORT, AT.JOIN)
    sleep(10)  # 10 seconds to be safe

    while LORA_PORT.in_waiting != 0:
        if LORA_PORT.in_waiting:
            reply = LORA_PORT.readlines()
            print('LoRa Node: ',reply)
        else:
            print('No Reply from LoRa Node')


# TODO: Determine if nomadic error handling should be done
def get_drrg_data(initial_time) -> tuple[Optional[SensorData], bool]:
    """ Get DRRG Data
    Args:
        initial_time:
            time when the DRRG data was retrieved
    Returns:
        `tuple` of len 2 where the first element is the sensor data and
        the second element is whether or not the DRRG data was retrieved
    """
    raw_data = get_data_from_port(DRRG_PORT, DRRG_COMM_0)
    if len(raw_data) == 37:
        if do_crc_check(raw_data) != 0:
            return None, True

        rain_data, accu_data = bytearray(0), bytearray(0)
        rain_temp, accu_temp = bytearray(4), bytearray(4)  # TODO: Should this be called accu?

        rain_data += raw_data[27:31]

        rain_temp[0:1] = rain_data[2:3]
        rain_temp[2:3] = rain_data[0:1]

        [rain_data_f] = unpack('!f', rain_temp)  # shouldn't this be `float`?

        accu_data += raw_data[31:35]

        accu_temp[0:1] = accu_data[2:3]
        accu_temp[2:3] = accu_data[0:1]

        [accu_data_f] = unpack('!f', accu_temp)

        print("Rain Data:" + str(rain_data_f))
        print("Rain Accu:" + str(accu_data_f))

        data = SensorData(
            source=DataSource.DIGITAL_RAIN_GAUGE,
            unit='mm',
            date=initial_time,
            data=[
                RawData(format=RAIN_DATA_FORMAT, datum=rain_data_f),
                RawData(format=RAIN_ACCU_FORMAT, datum=accu_data_f)
            ]
        )

        return data, False
    print("ERROR: No communication with DRRG!")  # TODO: Log
    return None, True


def get_dsg_data(initial_time) -> tuple[Optional[SensorData], bool]:
    """Gets DSG Data
    Args:
        initial_time:
            time when the DSG data was retrieved
    Returns:
        `tuple` of len 2 where the first element is the sensor data and
        the second element is whether or not the DSG data was retrieved
    """
    data = get_data_from_port(DSG_PORT, DSG_COMM_0)
    if data is None:
        print("ERROR: No communication with DSG!")  # TODO: Log
        return None, True
    if do_crc_check(data) != 0:
        return None, True  # TODO: Log

    water_level = str(int.from_bytes(data[4:5], "big"))
    print("Water level: %s cm" % water_level)

    data = SensorData(
        source=DataSource.DIGITAL_RAIN_GAUGE,
        unit='cm',
        date=initial_time,
        data=[
            RawData(format=FLOOD_FORMAT, datum=water_level),
        ]
    )

    ###Warning Lights and Alarm
    # notify_buzzer(water_level)
    ###

    return data, False


def main():
    setup()
    print('Setup Finished')
    now = datetime.now()  # this should fix race condition

    # TODO: Fix condition where power out occurs before next midnight is checked, rena
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    while DSG_PORT.is_open and DSG_PORT.is_open:
        if now > next_midnight:
            rename_log_file(now)

        ### <-- This block is responsible for retrieving, logging, and transmitting data.
        drrg_data, has_error_1  = get_drrg_data(now)
        dsg_data, has_error_2 = get_dsg_data(now)
        write_to_csv(DATA_LOG_PATH, drrg_data.get_csv_format())
        write_to_csv(DATA_LOG_PATH, dsg_data.get_csv_format())
        payload = CompiledSensorData(data=[drrg_data, dsg_data]).get_full_payload()
        write_to_serial(LORA_PORT, AT.CMSG, payload)
        ### <--

        # TODO: Next Block Should be Responsible for Reading the Buffer for any CMSG ACK or ERRORs

        sleep(60)
        now = datetime.now()


if __name__ == '__main__':
    main()
