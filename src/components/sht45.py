install = True
try:
    import board
    import adafruit_tca9548a as mux_mod
    import adafruit_sht4x as sht_mod
except ImportError or ModuleNotFoundError as err:
    print(err)
    install = False

if install:
    i2c = board.I2C()

    tca = mux_mod.TCA9548A(i2c)

channel_assignments = {0: (1, 'I'),
                       1: (1, 'O'),
                       2: (2, 'I'),
                       3: (2, 'O'),
                       4: (3, 'I'),
                       5: (3, 'O'),
                       6: (4, 'I'),
                       7: (4, 'O')}

if install:
    class SHT45(sht_mod.SHT4x):
        def __init__(self, channel):
            super().__init__(tca[channel])
            chamber, side = channel_assignments[channel]
            self.id = str(chamber) + str(side).upper()

        def take_measurement(self, precision: str = 'H'):
            if str(precision).upper() not in ['H', 'M', 'L']:
                raise ValueError("Precision parameter must equal 'H', 'M', or 'L'.")

            if precision == 'H':
                self.mode = 0xFD
            elif precision == 'M':
                self.mode = 0xF6
            else:
                self.mode = 0xE0

            return self.temperature, self.relative_humidity
else:
    class SHT45():
        pass

class RHTSensorArray:
    def __init__(self, sensors: list = None):
        # "cells" should be a list of SHT45 objects with their chambers and sides defined. __init__ will convert it
        # into the proper hierarchy.
        self.sensors = [[], [], [], []]
        self.num_sensors = 0

        if sensors is not None:
            for sensor in sensors:
                # if...else... determines index within chamber list
                # last line inserts into proper chamber based on cell.id param
                if sensor.id[1] == 'I':
                    index = 0
                else:
                    index = 1
                self.sensors[int(sensor.id[0]) - 1].insert(index, sensor)

        for chamber in self.sensors:
            for sensor in chamber:
                self.num_sensors += 1

    def take_measurement(self) -> list:
        data = []

        chamber_num = 1
        for chamber in self.sensors:
            for sensor in chamber:
                temp, humidity = sensor.take_measurement()
                data.append((temp, humidity))
            chamber_num += 1

        return data
