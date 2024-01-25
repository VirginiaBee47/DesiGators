import argparse
import openpyxl

from time import sleep, time
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, CrcCalculator
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_sht4x.device import Sht4xDevice

parser = argparse.ArgumentParser()
parser.add_argument('--i2c-port', '-p', default='/dev/i2c-1')
args = parser.parse_args()

i2c_transceiver = LinuxI2cTransceiver(args.i2c_port)


def close_i2c_transceiver():
    i2c_transceiver.close()


class Sht45(Sht4xDevice):
    def __init__(self, address, chamber: int = 1, side: str = 'I'):
        _channel = I2cChannel(I2cConnection(i2c_transceiver),
                              slave_address=address,
                              crc=CrcCalculator(8, 0x31, 0xff, 0x0))
        super().__init__(_channel)

        if chamber not in [1, 2, 3, 4]:
            raise ValueError("Chamber parameter must be one of [1,2,3,4].")

        if str(side).upper() not in ['I', 'O']:
            raise ValueError("Side parameter must equal 'I' or 'O'.")

        self.id = str(chamber) + str(side).upper()

    def take_measurement(self, precision: str = 'H'):
        if str(precision).upper() not in ['H', 'M', 'L']:
            raise ValueError("Precision parameter must equal 'H', 'M', or 'L'.")

        if precision == 'H':
            (a_temperature, a_humidity) = self.measure_high_precision()
        elif precision == 'M':
            (a_temperature, a_humidity) = self.measure_medium_precision()
        else:
            (a_temperature, a_humidity) = self.measure_lowest_precision()

        return a_temperature.value, a_humidity.value


class RHTSensorArray():
    def __init__(self, sensors: list=None):
        # "cells" should be a list of LoadCell objects with their chambers and sides defined. __init__ will convert it
        # into the proper hierarchy.
        self.sensors = [[],[],[],[]]

        if sensors is not None:
            for sensor in sensors:
                # if...else... determines index within chamber list
                # last line inserts into proper chamber based on cell.id param
                if sensor.id[1] == 'I':
                    index = 0
                else:
                    index = 1
                self.sensors[int(sensor.id[0]) - 1].insert(index, sensor)

    def take_measurement(self) -> list:
        data = []

        chamber_num = 1
        for chamber in self.sensors:
            for sensor in chamber:
                temp, humidity = sensor.take_measurement()
                data.append((temp, humidity))
            chamber_num += 1

        return data


def save_rht_vals(rht_vals):
    path = '/home/admin/Documents/Drying Data/RHT'

    name = 'autosave ' + str(time()) + '.xlsx'

    sheet = openpyxl.Workbook()

    for i in len(rht_vals):
        sheet['Sheet1']['A' + str(i + 1)] = rht_vals[i][0]
        sheet['Sheet1']['B' + str(i + 1)] = rht_vals[i][1]
        sheet['Sheet1']['C' + str(i + 1)] = rht_vals[i][2]
        sheet['Sheet1']['D' + str(i + 1)] = rht_vals[i][3]
        sheet['Sheet1']['E' + str(i + 1)] = rht_vals[i][4]
        sheet['Sheet1']['F' + str(i + 1)] = rht_vals[i][5]
        sheet['Sheet1']['G' + str(i + 1)] = rht_vals[i][6]
        sheet['Sheet1']['H' + str(i + 1)] = rht_vals[i][7]
        sheet['Sheet1']['I' + str(i + 1)] = rht_vals[i][8]

    sheet.save(path + name)

    return name
