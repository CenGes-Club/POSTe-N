import serial
from configs import parse_serial_config, DRRG_COMM_0, DSG_COMM_0
from time import sleep
from commands import write_to_serial, AT
from crccheck.crc import Crc16Modbus
from generics import write_to_csv
from struct import unpack
from datetime import datetime, timedelta
from data import SensorData, DataSource, RawData, RAIN_DATA_FORMAT, RAIN_ACCU_FORMAT, FLOOD_FORMAT, CompiledSensorData
from typing import Optional
import RPi.GPIO as GPIO
from logs import rename_log_file, DATA_LOG_PATH


# GPIO Variables\Methods
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


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


DRRG_PORT.rs485_mode = serial.rs485.RS485Settings(
    rts_level_for_tx = False,
    rts_level_for_rx = False,
    delay_before_tx = 0.0,
    delay_before_rx = 0.0
)


### Functions for DSG and DRRG ###
# def get_data_from_port(port, comm) -> str:
#     port.write(comm)
#     if port.in_waiting > 0:
#         return port.readline()  # TODO: This method might not work for DSG, check original script.
#     return ''
def get_data_from_port(port, comm, line_mode):
    port.write(comm)
    if line_mode:
        return port.readline()
    else:
        return port.read(port.in_waiting)


def do_crc_check(data):
    crc = Crc16Modbus()
    crc.process(data)
    return crc.final()


def setup():
    """Lora Node Join Network"""
    if not LORA_PORT.is_open:
        raise Exception("Lora Node is not open")  # Logging

    write_to_serial(LORA_PORT, AT.JOIN)
    sleep(5)  # 10 seconds to be safe

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
    data = SensorData(
        source=DataSource.DIGITAL_RAIN_GAUGE,
        unit='mm',
        date=initial_time,
        data=[]
    )

    raw_data = get_data_from_port(DRRG_PORT, DRRG_COMM_0, line_mode=True)
    if len(raw_data) == 37:
        print("ERROR: No communication with DRRG!")
        return None, True
    if do_crc_check(raw_data) != 0:
        print("CRC Check Failed!")
        return None, True

    rain_data, accu_data = bytearray(0), bytearray(0)
    rain_temp, accu_temp = bytearray(4), bytearray(4)

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

    data.append_data(RawData(format=RAIN_DATA_FORMAT, datum=rain_data_f))
    data.append_data(RawData(format=RAIN_ACCU_FORMAT, datum=accu_data_f))
    return data, False


def get_dsg_data(initial_time) -> tuple[Optional[SensorData], bool]:
    """Gets DSG Data
    Args:
        initial_time:
            time when the DSG data was retrieved
    Returns:
        `tuple` of len 2 where the first element is the sensor data and
        the second element is whether or not the DSG data was retrieved
    """
    data = SensorData(
        source=DataSource.DIGITAL_RAIN_GAUGE,
        unit='cm',
        date=initial_time,
        data=[]
    )

    raw_data = get_data_from_port(DSG_PORT, DSG_COMM_0, line_mode=False)
    if len(raw_data) == 0:
        print("ERROR: No communication with DSG!")
        return None, True
    if do_crc_check(raw_data) != 0:
        print("CRC Check Failed!")
        return None, True

    water_level = float(int.from_bytes(raw_data[4:5], "big"))  # this is a horrible conversion, but it works
    print("Water level: %s cm" % water_level)

    data.append_data(RawData(format=FLOOD_FORMAT, datum=water_level))
    return data, False


def get_next_midnight(now: datetime) -> datetime:
    """Get next midnight
    Args:
        now:
        datetime when the data was retrieved
    """
    return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


def main():
    setup()
    print('Setup Finished')
    now = datetime.now()  # this should fix race condition

    # TODO: Fix condition where power out occurs before next midnight is checked, rena
    next_midnight = get_next_midnight(now)
    while DSG_PORT.is_open and DSG_PORT.is_open:
        if now > next_midnight:
            rename_log_file(now)
            next_midnight = get_next_midnight(now)

        ### <-- This block is responsible for retrieving, logging, and transmitting data.
        drrg_data, has_error_1  = get_drrg_data(now)  # TODO: Handle `None` for data
        dsg_data, has_error_2 = get_dsg_data(now)
        write_to_csv(DATA_LOG_PATH, drrg_data.get_csv_format())
        write_to_csv(DATA_LOG_PATH, dsg_data.get_csv_format())
        payload = now.strftime("%H%M") + CompiledSensorData(data=[drrg_data, dsg_data]).get_full_payload()
        write_to_serial(LORA_PORT, AT.CMSG, payload)
        ### <--

        # TODO: Next Block Should be Responsible for Reading the Buffer for any CMSG ACK or ERRORs

        sleep(60)
        now = datetime.now()

    DSG_PORT.close()
    DRRG_PORT.close()
    LORA_PORT.close()


if __name__ == '__main__':
    main()
