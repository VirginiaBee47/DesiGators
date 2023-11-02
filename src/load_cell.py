from time import sleep

import hx711


class LoadCell(hx711.HX711):
    def __init__(self, data_pin: int, clock_pin: int, gain: int=128, channel: str='A'):
        super().__init__(data_pin, clock_pin, gain, channel)
        self.offset = 0

    def tare(self, sample_size: int=25):
        readings = self.get_raw_data(sample_size)

        average_val = sum(readings) / len(readings)
        self.offset = average_val

    def take_measurement(self) -> float:
        measurement = sum(self.get_raw_data(3)) / 3
        measurement -= self.offset
        return measurement


def main():
    cell = LoadCell(12, 23)
    sleep(1)
    print("Taring Load Cell...")
    cell.tare()
    print("Load cell offset: %i" % cell.offset)
    sleep(1)
    while True:
        print(str(cell.take_measurement()))
        sleep(2)


if __name__ == '__main__':
    main()