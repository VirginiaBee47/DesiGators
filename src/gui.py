import sys
import os
import numpy as np

from time import sleep, time
from PyQt6.QtCore import (
    Qt,
    QRunnable,
    QThreadPool,
    QObject,
    pyqtSignal
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QPushButton,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout
)
#from pyqtgraph import PlotWidget, plot

from exceptions import PointNotDefinedException, InvalidParamsException
from psychrometric_chart import PsychrometricProperties
from components.load_cell import LoadCell, LoadCellArray


class QInputBox(QLineEdit):
    def __init__(self, property_name, *args, **kwargs):
        super(QLineEdit, self).__init__(*args, **kwargs)

        self.property_name = property_name


class MassSignals(QObject):
    """Signals associated with mass updating worker
    finished signal has no associated type

    result signal is a list of all the masses in LoadCellArray order
    """

    finished = pyqtSignal()
    error = pyqtSignal()
    result = pyqtSignal(list)


class MassUpdater(QRunnable):
    """Runnable Updater for Mass Readouts"""

    def __init__(self, _cell_array: LoadCellArray, control):
        super(MassUpdater, self).__init__()

        self.control = control
        self.signals = MassSignals()
        self._array = _cell_array

    def run(self):
        print("Thread started.")
        print(self.control)
        while True:
            if not self.control['measure_mass']:
                break
            else:
                print("Reading...")
                print(self._array.cells)
                print(readings := self._array.take_measurement())
                readings.insert(0,time())
                self.signals.result.emit(readings)
                sleep(0.5)
                self.signals.finished.emit()
                sleep(3)
        print("Thread completed.")


class AppWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(AppWindow, self).__init__(*args, **kwargs)

        self.mass_data = None
        self.collection_start_time = None

        self.setWindowTitle("Psychrometric Calculator")
        layout = QHBoxLayout()

        # Create the parameter rows
        param_row_layouts_list = [pressure_layout := QHBoxLayout(),
                                  dry_bulb_layout := QHBoxLayout(),
                                  wet_bulb_layout := QHBoxLayout(),
                                  dew_point_layout := QHBoxLayout(),
                                  relative_humidity_layout := QHBoxLayout(),
                                  humidity_ratio_layout := QHBoxLayout(),
                                  partial_pressure_layout := QHBoxLayout(),
                                  total_enthalpy_layout := QHBoxLayout(),
                                  specific_heat_layout := QHBoxLayout(),
                                  specific_volume_layout := QHBoxLayout()]

        # Create 2 main columns
        params_layout = QVBoxLayout()
        dialogue_plot_layout = QHBoxLayout()
        output_calc_layout = QVBoxLayout()

        param_widgets_list = []
        unit_widgets_list = []

        # List all the psychrometric parameters in order (this order must be maintained)
        params = ['Total Pressure',
                  'Dry Bulb Temp',
                  'Wet Bulb Temp',
                  'Dew Point',
                  'Relative Humidity',
                  'Humidity Ratio',
                  'Partial Vapor Pressure',
                  'Total Enthalpy',
                  'Specific Heat',
                  'Specific Volume']

        # List all the units of the corresponding psychrometric parameters
        units = ['Pa',
                 chr(176) + 'C',
                 chr(176) + 'C',
                 chr(176) + 'C',
                 '%',
                 'kg water/kg dry air',
                 'Pa',
                 'kJ/kg dry air',
                 'kJ/kg*K',
                 'm^3/kg']

        # Create param labels
        for label in params:
            label_widget = QLabel(label)
            param_widgets_list.append(label_widget)

        # Create unit labels
        for label in units:
            label_widget = QLabel(label)
            unit_widgets_list.append(label_widget)

        # Create input boxes for each param
        self.total_pressure_input = QInputBox('total_pressure')
        self.dry_bulb_input = QInputBox('dry_bulb_temperature')
        self.wet_bulb_input = QInputBox('wet_bulb_temperature')
        self.dew_point_input = QInputBox('dew_point_temperature')
        self.relative_humidity_input = QInputBox('relative_humidity')
        self.humidity_ratio_input = QInputBox('humidity_ratio')
        self.vapor_pressure_input = QInputBox('partial_pressure_vapor')
        self.enthalpy_input = QInputBox('total_enthalpy')
        self.specific_heat_input = QInputBox('specific_heat_capacity')
        self.specific_vol_input = QInputBox('specific_volume')

        self.input_boxes = [self.total_pressure_input,
                            self.dry_bulb_input,
                            self.wet_bulb_input,
                            self.dew_point_input,
                            self.relative_humidity_input,
                            self.humidity_ratio_input,
                            self.vapor_pressure_input,
                            self.enthalpy_input,
                            self.specific_heat_input,
                            self.specific_vol_input]

        # Create row layouts for each parameter
        for i in range(len(param_row_layouts_list)):
            # Add 1. parameter name QLabel, 2. parameter QLineEdit, 3. parameter units QLabel
            param_widgets_list[i].setFixedWidth(130)
            param_row_layouts_list[i].addWidget(param_widgets_list[i])
            self.input_boxes[i].setFixedWidth(100)
            param_row_layouts_list[i].addWidget(self.input_boxes[i])
            unit_widgets_list[i].setFixedWidth(120)
            param_row_layouts_list[i].addWidget(unit_widgets_list[i])

            # Add parameter row to column on the left
            params_layout.addLayout(param_row_layouts_list[i])

        # Create output_calc_layout (layout including dialogue box for errors, plot, and button to calculate)
        self.dialogue_box = QLabel()
        self.dialogue_box.setStyleSheet("border: 1px solid black;")

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate_clicked)

        #self.mass_plot = PlotWidget()

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_clicked)

        measure_button = QPushButton("Start/Stop Measurement")
        measure_button.clicked.connect(self.measurement_clicked)

        # Defining the load cell array to be passed into the updater object
        self.load_cell_array = LoadCellArray()
        self.load_cell_array.load_array()

        button_layout = QHBoxLayout()
        button_layout.addWidget(calculate_button, 2)
        button_layout.addWidget(clear_button, 2)
        button_layout.addWidget(measure_button, 2)

        dialogue_plot_layout.addWidget(self.dialogue_box, 50)
        #dialogue_plot_layout.addWidget(self.mass_plot)

        output_calc_layout.addLayout(dialogue_plot_layout, 75)
        output_calc_layout.addLayout(button_layout, 25)

        layout.addLayout(params_layout)
        layout.addLayout(output_calc_layout)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.threadpool = QThreadPool()

        self.controls = {'measure_mass': False}

    def clear_clicked(self) -> None:
        for input_box in self.input_boxes:
            input_box.setText("")

        if not self.controls['measure_mass']:
            self.dialogue_box.setText("Cleared!")

    def calculate_clicked(self) -> None:
        if not self.controls['measure_mass']:
            self.dialogue_box.setText("")

        params_dict = {'dry_bulb_temperature': None,
                       'wet_bulb_temperature': None,
                       'dew_point_temperature': None,
                       'total_pressure': None,
                       'humidity_ratio': None,
                       'relative_humidity': None,
                       'total_enthalpy': None,
                       'partial_pressure_vapor': None,
                       'specific_volume': None,
                       'specific_heat_capacity': None}

        for input_box in self.input_boxes:
            if input_box.text() != "":
                if input_box.property_name == 'relative_humidity':
                    params_dict['relative_humidity'] = float(input_box.text()) / 100
                else:
                    params_dict[input_box.property_name] = float(input_box.text())

        # For debugging:
        print(params_dict)

        psy_point = None
        try:
            psy_point = PsychrometricProperties(**params_dict)
        except PointNotDefinedException:
            self.dialogue_box.setText("Not enough information provided.")
        except InvalidParamsException as exception:
            self.dialogue_box.setText(exception.message)

        if psy_point is not None:
            for input_box in self.input_boxes:
                if input_box.text() == "":
                    if input_box.property_name == 'dry_bulb_temperature':
                        input_box.setText(str(round(psy_point.dry_bulb_temperature, 2)))
                    elif input_box.property_name == 'wet_bulb_temperature':
                        input_box.setText(str(round(psy_point.wet_bulb_temperature, 2)))
                    elif input_box.property_name == 'dew_point_temperature':
                        input_box.setText(str(round(psy_point.dew_point_temperature, 2)))
                    elif input_box.property_name == 'total_pressure':
                        input_box.setText(str(round(psy_point.total_pressure, 2)))
                    elif input_box.property_name == 'humidity_ratio':
                        input_box.setText(str(round(psy_point.humidity_ratio, 5)))
                    elif input_box.property_name == 'relative_humidity':
                        input_box.setText(str(round(psy_point.relative_humidity * 100, 2)))
                    elif input_box.property_name == 'total_enthalpy':
                        input_box.setText(str(round(psy_point.total_enthalpy, 3)))
                    elif input_box.property_name == 'partial_pressure_vapor':
                        input_box.setText(str(round(psy_point.partial_pressure_vapor, 2)))
                    elif input_box.property_name == 'specific_volume':
                        input_box.setText(str(round(psy_point.specific_volume, 2)))
                    elif input_box.property_name == 'specific_heat_capacity':
                        input_box.setText(str(round(psy_point.specific_heat_capacity, 2)))

            if not self.controls['measure_mass']:
                self.dialogue_box.setText("Calculated!")

    def show_new_masses(self, masses: list) -> None:
        print("show masses now")
        print(masses)
        masses.pop(0)
        mass_string = '\n'.join(["Load Cell %i: %f" % (i + 1, masses[i]) for i in range(len(masses))])
        self.dialogue_box.setText(mass_string)

    def update_plot(self):
        # This function needs a lot of work
        # plot updating should occur in this function
        x_axis = self.mass_data
        y_axis = self.mass_data
        #self.mass_plot.plotItem()

    def store_masses(self, data: list) -> None:
        print('store_masses_called')
        current_time = data.pop(0)
        self.mass_data =  np.append(self.mass_data, [current_time - self.collection_start_time, *data])
        print(self.mass_data)

    def measurement_handling(self) -> None:
        handler = MassUpdater(self.load_cell_array, self.controls)
        handler.signals.result.connect(self.show_new_masses)
        handler.signals.result.connect(self.store_masses)
        handler.signals.finished.connect(self.update_plot)

        self.threadpool.start(handler)

    def measurement_clicked(self) -> None:
        if not self.controls['measure_mass']:
            self.controls['measure_mass'] = True
            self.collection_start_time = int(time())
            self.mass_data = np.zeros((8, 1))
            self.measurement_handling()
        else:
            self.controls['measure_mass'] = False
            file_name = str(self.collection_start_time) + '_mass_data.csv'
            headings = ''.join(["mass %i," % num for num in range(np.shape(self.mass_data)[0])])
            print(self.mass_data)
            np.savetxt(file_name, self.mass_data, header=headings)
            self.mass_data = None

    def closeEvent(self, event):
        # Override the closeEvent method that exists and replace with controls editing to exit ongoing threads
        self.controls['measure_mass'] = False
        event.accept()


def main() -> None:
    psy_chart_app = QApplication(sys.argv)

    window = AppWindow()
    window.show()

    psy_chart_app.exec()


if __name__ == '__main__':
    main()
