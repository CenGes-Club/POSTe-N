import serial
from configs import parse_serial_config, verify_unique_xml_value
from time import sleep
from commands import write_to_serial, AT
from crccheck.crc import Crc16Modbus
import csv
from struct import unpack
from datetime import datetime


## Paths
DATA_LOG_PATH = '/home/postekit/POSTe/data_log.csv'
EVENT_LOG_PATH = '/home/postekit/POSTe/event_log.csv'


# Miscelleneous Variables
# Datalog = True
# loop_time = 1
COUNT = 0


# Initialize Variables
DSG_PORT = serial.Serial(**parse_serial_config('config.xml', 'dsg', verify_unique_xml_value))
DRRG_PORT = serial.Serial(**parse_serial_config('config.xml', 'drrg', verify_unique_xml_value))
LORA_PORT = serial.Serial(**parse_serial_config('config.xml', 'lora', verify_unique_xml_value))


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


def get_drrg_data(initial_time):  # TODO: Prettify
    """

    Args:
        initial_time:

    Returns:
        `tuple` of len 2
    """
    data = get_data_from_port(DRRG_PORT, DRRG_COMM_0)
    if len(data) == 37:  # TODO: Ask Boss James Why This is Specifically 37
        if do_crc_check(data) != 0:
            COUNT += 1  # TODO: This must be changed, pls
            return list(), True

        rain_data, accu_data = bytearray(0), bytearray(0)
        rain_temp, accu_temp = bytearray(4), bytearray(4)  # TODO: Should this be called accu?

        ##-> TODO: This could be turned into a function, but...
        rain_data += data[27:31]

        rain_temp[0:1] = rain_data[2:3]
        rain_temp[2:3] = rain_data[0:1]

        [rain_data_f] = unpack('!f', rain_temp)

        accu_data += data[31:35]

        accu_temp[0:1] = accu_data[2:3]
        accu_temp[2:3] = accu_data[0:1]

        [accu_data_f] = unpack('!f', accu_temp)
        ##<-

        print("Rain Data:" + str(rain_data_f))
        print("Rain Accu:" + str(accu_data_f))

        with open(DATA_LOG_PATH, 'a') as f:
            writer = csv.writer(f)
            csv_write = [initial_time, str(rain_data_f), str(accu_data_f), "DRRG"]
            writer.writerow(csv_write)
        return csv_write[1:3], False
    print("ERROR: No communication with DRRG!")
    return list(), True


def get_dsg_data(initial_time):
    """


    Args:
        initial_time:

    Returns:
        `tuple` of len 1
    """
    data = get_data_from_port(DSG_PORT, DSG_COMM_0)
    if data is None:
        print("ERROR: No communication with DSG!")
    if do_crc_check(data) != 0:
        return list(), True

    water_level = int.from_bytes(data[4:5], "big")
    print("Water level: %d cm" % water_level)

    with open(DATA_LOG_PATH, 'a') as f:
        writer = csv.writer(f)
        csv_write = [initial_time, str(water_level), " cm", "DSG"]
        writer.writerow(csv_write)

    ###Warning Lights and Alarm
    notify_buzzer(water_level)
    ###

    return csv_write[1:2], False


def send_data_to_lora(start_time, data):
    """ This should obtain the last n rows of data from the data log path
    and transform it into the 'specified' data format.
    :param start_time: `datetime` determines which row to start truncating from
    """  # TODO: Ask Boss James into how to transform the data
    data = get_last_n_rows_csv(DATA_LOG_PATH, 40)  # 40 rows should be the worst if race conditions happen
    ##
    # TODO: Process :param start_time:
    ##
    data_to_send = transform_data(*data)
    write_to_serial(LORA_PORT, AT.MSG, data_to_send)


def transform_data(rain_data, rain_accu, water_level): # TODO: Function Not Complete
    """This should transform `data` and turn it into LoRa compatible characters.
    :param rain_data:`float`
    :param rain_accu:`float`
    :param water_level:`float`
    :return:
    """
    return


def main():
    setup()
    print('Setup Finished')
    inc = 0
    start_time = datetime.now()  # this should fix race condition
    data_to_transmit = []
    while DSG_PORT.is_open and DSG_PORT.is_open:

        drrg_data, has_error_1  = get_drrg_data(start_time)
        dsg_data, has_error_2 = get_dsg_data(start_time)

        sleep(60)
        inc += 1
        start_time = datetime.now()


if __name__ == '__main__':
    main()
