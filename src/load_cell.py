from time import sleep

import hx711


cell = hx711.HX711(12, 23)

cell.reset()
while True:
    measurements = cell.get_raw_data()

    for measurement in measurements:
        print("Measurement: " + str(measurement))

    sleep(2.5)