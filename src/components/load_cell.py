from time import sleep
from numpy import polyfit
from os.path import exists

import hx711


class LoadCell(hx711.HX711):
    def __init__(self, data_pin: int, clock_pin: int, gain: int=128, channel: str='A', chamber: int=1, side: str='L', m: float=None, b: float=None):
        super().__init__(data_pin, clock_pin, gain, channel)

        if chamber not in [1, 2, 3, 4]:
            raise ValueError("Chamber parameter must be one of [1,2,3,4].")

        if str(side).upper() not in ['L', 'R']:
            raise ValueError("Side parameter must equal 'L' or 'R'")

        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.gain = gain
        self.channel = channel

        self.id = str(chamber) + str(side).upper()

        self.m = m
        self.b = b

    def tare(self, sample_size: int=25):
        readings = self.get_raw_data(sample_size)

        average_val = sum(readings) / len(readings)
        self.offset = average_val

    def take_measurement(self) -> float:
        measurement = sum(self.get_raw_data(3)) / 3
        return measurement

    def get_mass(self) -> float:
        measurement = self.take_measurement()
        mass = self.m * measurement + self.b
        return mass

    def calibrate(self) -> None:
        calibrating = True
        input("Ensure that 0 mass is on the scale, then press enter.")
        working_mass = 0

        calibration_data = [[],[]]

        for i in range(10):
            calibration_data[0].append(self.take_measurement())
            calibration_data[1].append(working_mass)

        while calibrating:
            working_mass_accepted = False

            while not working_mass_accepted:
                try:
                    working_mass = int(input("Add a known mass onto the scale.\nMass: "))
                    working_mass_accepted = True
                except Exception:
                    print("Not a valid mass...")

            print("Do not disturb the scale during meausurement...")
            for i in range(10):
                calibration_data[0].append(self.take_measurement())
                calibration_data[1].append(working_mass)

            if (ans := input("Do you wish to continue? [Y/N] ").lower()) == "n":
                calibrating = False
            elif ans == 'no':
                calibrating = False
            elif ans != 'y':
                print("Answer interpreted as \'yes\'")

        self.m, self.b = polyfit(calibration_data[0], calibration_data[1], 1)
        print("Regression Equation: y = %f*x = %f" % (self.m, self.b))


class LoadCellArray:
    def __init__(self, cells: list=None):
        # "cells" should be a list of LoadCell objects with their chambers and sides defined. __init__ will convert it
        # into the proper hierarchy.
        self.cells = [[],[],[],[]]

        if cells is not None:
            for cell in cells:
                # if...else... determines index within chamber list
                # last line inserts into proper chamber based on cell.id param
                if cell.id[1] == 'L':
                    index = 0
                else:
                    index = 1
                self.cells[int(cell.id[0]) - 1].insert(index, cell)

    def save_array(self) -> None:
        with open('cache/load_cells.txt', 'w') as file:
            for chamber in self.cells:
                for cell in chamber:
                    write_str = str(cell.data_pin) + ',' + str(cell.clock_pin) + ',' + str(cell.gain) + ',' + str(cell.channel) + ',' + str(cell.id) + ',' + str(cell.m) + ',' + str(cell.b) + '|'
                    file.write(write_str)
            file.close()

    def load_array(self) -> None:
        with open('cache/load_cells.txt', 'r') as file:
            data_string = file.read()
            file.close()

        cells = data_string.split('|')
        for i in range(len(cells)):
            cells[i] = cells[i].split(',')
            data_pin = int(cells[i][0])
            clock_pin = int(cells[i][1])
            gain = int(cells[i][2])
            channel = cells[i][3]
            chamber = int(cells[i][4][0])
            side = cells[i][4][1]
            if side == 'L':
                index = 0
            else:
                index = 1

            if cells[i][5] != "None":
                m = cells[i][5]
            else:
                m = None
            if cells[i][6] != "None":
                b = cells[i][6]
            else:
                b = None
            self.cells[chamber - 1].insert(index, LoadCell(data_pin, clock_pin, gain, channel, chamber, side, m, b))

    def take_measurement(self) -> list:
        data = [[],[],[],[]]

        chamber_num = 1
        for chamber in self.cells:
            for cell in chamber:
                mass = cell.take_measurement()
                data[chamber_num - 1].append(mass)
            chamber_num += 1

        print(data)
        return data


def main():
    cell1 = LoadCell(12, 23, chamber=1, side='R')
    cell2 = LoadCell(13, 23, chamber=1, side='L')

    load_cell_array = LoadCellArray([cell2, cell1])
    load_cell_array.save_array()

    while True:
        print(str(load_cell_array.take_measurement()))


if __name__ == '__main__':
    main()
