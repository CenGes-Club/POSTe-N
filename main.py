import serial
from configs import parse_serial_config
from time import sleep
from commands import write_to_serial, AT
from crccheck.crc import Crc16Modbus
import csv
from struct import unpack
from datetime import datetime

from scratch.buzzer import notify_buzzer
from scratch.generics import get_last_n_rows_csv

## Paths
DATA_LOG_PATH = '/home/postekit/POSTe/data_log.csv'
EVENT_LOG_PATH = '/home/postekit/POSTe/event_log.csv'


# Miscelleneous Variables
# Datalog = True
# loop_time = 1
COUNT = 0


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


def get_drrg_data(initial_time):  # TODO: Prettify
    data = get_data_from_port(DRRG_PORT, DRRG_COMM_0)
    if len(data) == 37:  # TODO: Ask Boss James Why This is Specifically 37
        if do_crc_check(data) != 0:
            COUNT += 1  # TODO: This must be changed, pls
            return

        rain_data, accu_data = bytearray(0), bytearray(0)
        rain_temp, accu_temp = bytearray(4), bytearray(4)

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
        return csv_write[0:3]
    print("ERROR: No communication with DRRG!")
    return None


def get_dsg_data(initial_time):
    data = get_data_from_port(DSG_PORT, DSG_COMM_0)
    if data is None:
        print("ERROR: No communication with DSG!")
    if do_crc_check(data) != 0:
        return None

    data_int = int.from_bytes(data[4:5], "big")
    print("Water level: %d cm" % data_int)

    with open(DATA_LOG_PATH, 'a') as f:
        writer = csv.writer(f)
        csv_write = [initial_time, str(data_int), " cm", "DSG"]
        writer.writerow(csv_write)

    ###Warning Lights and Alarm
    notify_buzzer(data_int)
    ###

    return csv_write[0:1]


def send_data_to_lora(start_time):
    """ This should obtain the last n rows of data from the data log path
    and transform it into the 'specified' data format.
    :param start_time: `datetime` determines which row to start truncating from
    """  # TODO: Ask Boss James into how to transform the data
    data = get_last_n_rows_csv(DATA_LOG_PATH, 40)  # 40 rows should be the worst if race conditions happen
    ##
    # TODO: Process :param start_time:
    ##
    data_to_send = transform_data(data)
    write_to_serial(LORA_PORT, AT.MSG, data_to_send)


def transform_data(data): # TODO: Function Not Complete
    """This should transform `data` and turn it into LoRa compatible characters.
    :param data:`list[list[Any]]` A list of rows from the csv file.
    :return:
    """
    return data


def main():
    setup()
    print('Setup Finished')
    inc = 0
    start_time = datetime.now()  # this should fix race condition
    data_to_transmit = []
    while DSG_PORT.is_open and DSG_PORT.is_open:
        if inc == 10:  # after 10 minutes, send the data to LoRa
            send_data_to_lora(initial_time)
            inc = 0
            start_time = datetime.now()
            continue

        drrg_data = get_drrg_data(start_time)
        dsg_data = get_dsg_data(start_time)
        if drrg_data is not None and dsg_data is not None:
            # transmit the data here
            for
            pass
        else:
            if drrg_data is None:
                print("ERROR: No data with DRRG!")
            if dsg_data is None:
                print("ERROR: No data with DSG!")
        sleep(58)
        inc += 1


if __name__ == '__main__':
    main()
