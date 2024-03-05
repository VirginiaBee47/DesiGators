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
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QScrollArea,
    QTabWidget,
    QFrame,
    QSpacerItem
)
from PyQt6.QtGui import (
    QAction,
    QFont
)

from exceptions import PointNotDefinedException, InvalidParamsException
from psychrometric_calc import PsychrometricProperties
from unit_converter import convert_units
from components.load_cell import LoadCellArray
from components.sht45 import RHTSensorArray, SHT45


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
        taken_reading = False
        print("Thread started.")

        while True:
            if not self.control['measure']:
                break
            elif self.control['read_signal'] and not taken_reading:
                print(readings := self._array.take_measurement())
                readings.insert(0, time())
                self.signals.result.emit(readings)
                sleep(0.5)
                self.signals.finished.emit()
                sleep(2)
                taken_reading = True
            elif not self.control['read_signal'] and taken_reading:
                taken_reading = False
        print("Thread completed.")


class RHTSignals(QObject):
    """Signals associated with the RHT updating worker. Works
    in the same way as the MassUpdater class.
    """

    finished = pyqtSignal()
    error = pyqtSignal()
    result = pyqtSignal(list)


class RHTUpdater(QRunnable):
    def __init__(self, _sensor_array: RHTSensorArray, control):
        super(RHTUpdater, self).__init__()

        self.control = control
        self.signals = RHTSignals()
        self._array = _sensor_array

    def run(self):
        taken_reading = False

        print("Thread started.")
        while True:
            if not self.control['measure']:
                break
            elif self.control['read_signal'] and not taken_reading:
                print(readings := self._array.take_measurement())
                self.signals.result.emit(readings)
                sleep(0.5)
                self.signals.finished.emit()
                sleep(1)
                taken_reading = True
            elif not self.control['read_signal'] and taken_reading:
                taken_reading = False
        print("Thread completed.")


class CoordinatorSignals(QObject):
    read = pyqtSignal()


class MeasurementCoordinator(QRunnable):
    def __init__(self, control, interval: int = 10):
        super(MeasurementCoordinator, self).__init__()
        self.signals = CoordinatorSignals()
        self.interval = interval
        self.control = control

    def run(self):
        while True:
            if not self.control['measure']:
                break
            else:
                sleep(self.interval)
                self.signals.read.emit()


class UnitConverterWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle("Unit Converter")

        self.parent = parent

        # Define row layouts (rows ordered top to bottom)
        row_one_layout = QHBoxLayout()
        row_two_layout = QHBoxLayout()
        row_three_layout = QHBoxLayout()

        # Building row one (row to include title/large label and value dropdown)
        header_label = QLabel("Heading")

        self.value_type_dropdown = QComboBox()
        self.value_type_dropdown.addItems(['Select a value type', 'Mass', 'Volume', 'Temperature', 'Pressure',
                                           'Mass Flow Rate', 'Volumetric Flow Rate', 'Energy', 'Power',
                                           'Specific Enthalpy', 'Specific Heat Capacity'])
        self.value_type_dropdown.currentIndexChanged.connect(self.value_type_dropdown_index_changed)

        row_one_layout.addWidget(header_label)
        row_one_layout.addWidget(self.value_type_dropdown)

        # Building row two (row to include two input boxes, two dropdowns, and flip button)
        self.known_value_line_edit = QLineEdit()

        self.known_value_dropdown = QComboBox()
        self.known_value_dropdown.addItem("Select a value type above")

        flip_button = QPushButton('\u21D4')
        flip_button.setFont(QFont('Times', 16))
        flip_button.clicked.connect(self.flip_clicked)

        self.calc_value_line_edit = QLineEdit()
        self.calc_value_line_edit.setReadOnly(True)

        self.calc_value_dropdown = QComboBox()
        self.calc_value_dropdown.addItem("Select a value type above")

        row_two_layout.addWidget(self.known_value_line_edit)
        row_two_layout.addWidget(self.known_value_dropdown)
        row_two_layout.addWidget(flip_button)
        row_two_layout.addWidget(self.calc_value_line_edit)
        row_two_layout.addWidget(self.calc_value_dropdown)

        # Building row three (row to include spacers and calculate button)
        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate_clicked)

        row_three_layout.addWidget(calculate_button)

        # Add together rows to make window layout
        layout = QVBoxLayout()
        layout.addLayout(row_one_layout)
        layout.addLayout(row_two_layout)
        layout.addLayout(row_three_layout)

        self.setLayout(layout)

    def calculate_clicked(self) -> None:
        value_type = self.value_type_dropdown.currentText()
        unit_a = self.known_value_dropdown.currentText()
        unit_b = self.calc_value_dropdown.currentText()
        try:
            value_a = float(self.known_value_line_edit.text())
        except ValueError as e:
            print(e)
            return

        value_b = convert_units(value_type, unit_a, unit_b, value_a)
        self.calc_value_line_edit.setText("{:.3f}".format(value_b))

    def value_type_dropdown_index_changed(self, index) -> list:
        units = None

        if self.value_type_dropdown.itemText(0) == 'Select a value type':
            self.value_type_dropdown.removeItem(0)
            index -= 1

        if index == 0:
            # Mass
            units = ['g', 'kg', 'lbm', 'slug', 'firkin']
        elif index == 1:
            # Volume
            units = ['ft³', 'm³', 'L', 'mL', 'butt', 'hogsheads']
        elif index == 2:
            # Temperature
            units = [chr(176) + 'C', chr(176) + 'F', 'K', chr(176) + 'R',]
        elif index == 3:
            # Pressure
            units = ['Pa', 'psi', 'mmHg', 'atm', 'bar', 'torr', 'beard-second-black-hole']
        elif index == 4:
            # Mass Flow Rate
            units = ['kg/s', 'lb/s']
        elif index == 5:
            # Volumetric Flow Rate
            units = ['SCFM', 'SCFH', 'SLPM', 'm³/h']
        elif index == 6:
            # Energy
            units = ['J', 'kJ', 'kWh', 'Btu', 'kcal', 'keV']
        elif index == 7:
            # Power
            units = ['W', 'kW', 'hp', 'dp', 'Btu/h', 'RT']
        elif index == 8:
            # Specific Enthalpy
            units = ['kJ/kg', 'Btu/lbm']
        elif index == 9:
            # Specific Heat Capacity
            units = ['kJ/kg\u00B7K', 'Btu/lbm\u00B7\u00B0R']

        self.known_value_dropdown.clear()
        self.known_value_dropdown.addItems(units)

        self.calc_value_dropdown.clear()
        self.calc_value_dropdown.addItems(units)

        return units

    def flip_clicked(self) -> None:
        calc_value = self.calc_value_line_edit.text()

        self.known_value_line_edit.setText(calc_value)
        self.calc_value_line_edit.setText("")

        known_unit_index = self.known_value_dropdown.currentIndex()
        calc_unit_index = self.calc_value_dropdown.currentIndex()
        self.known_value_dropdown.setCurrentIndex(calc_unit_index)
        self.calc_value_dropdown.setCurrentIndex(known_unit_index)

    def closeEvent(self, event):
        # Override the closeEvent method that exists and replace with controls editing to exit ongoing threads
        self.parent.controls['converter_shown'] = False
        event.accept()


class PsychrometricCalculatorWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle("Psychrometric Calculator")

        self.parent = parent

        params_layout = QVBoxLayout()

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

        output_controls_layout = QVBoxLayout()

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate_clicked)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_clicked)

        self.output_box = QLabel()
        self.output_box.setStyleSheet("border: 2px solid black;")

        output_controls_layout.addWidget(self.output_box)
        output_controls_layout.addWidget(calculate_button)
        output_controls_layout.addWidget(clear_button)

        layout = QHBoxLayout()
        layout.addLayout(params_layout, 75)
        layout.addLayout(output_controls_layout, 25)

        self.setLayout(layout)

    def calculate_clicked(self):
        self.output_box.setText("")

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

        psy_point = None
        try:
            psy_point = PsychrometricProperties(**params_dict)
        except PointNotDefinedException:
            self.output_box.setText("Not enough information provided.")
        except InvalidParamsException as exception:
            self.output_box.setText(exception.message)

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

            self.output_box.setText("Calculated!")

    def clear_clicked(self):
        for input_box in self.input_boxes:
            input_box.setText("")
        self.output_box.setText("Cleared!")

    def closeEvent(self, event):
        # Override the closeEvent method that exists and replace with controls editing to exit ongoing threads
        self.parent.controls['calc_shown'] = False
        event.accept()


class QChamberTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()

    def changeEvent(self, event):
        print(event)
        # self.widget()
        event.accept()

class ChamberTabPage(QWidget):
    def __init__(self, mainwindow, num):
        super().__init__()
        self.mainwindow = mainwindow  # Figure out if this import is necessary
        self.num = num

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Create two main columns
        left_layout = QVBoxLayout()  # left_layout contains two plots (mass on top and psychro on bottom)
        right_layout = QVBoxLayout()  # right_layout contains three boxes controls on top, then current operating
                                      # conditions, then log with warnings/errors

        # Define left_layout
        left_layout.addWidget(QLabel('Mass Plot Here'))
        left_layout.addWidget(QLabel('Psychro Plot Here'))

        # Define right_layout
            # Define and add controls box
        controls_box = QWidget()
        controls_box.setObjectName('controls_box')
        controls_box.setStyleSheet("QWidget#controls_box {border: 2px solid black;}")
        controls_box_layout = QVBoxLayout()
        controls_box.setLayout(controls_box_layout)

        heater_control_layout = QHBoxLayout()
        heater_control_layout.setSpacing(5)
        heater_control_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        heater_checkbox = QCheckBox()
        heater_label = QLabel('Heater On')
        heater_control_layout.addWidget(heater_checkbox)
        heater_control_layout.addWidget(heater_label)

        record_control_layout = QHBoxLayout()
        record_control_layout.setSpacing(5)
        record_control_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.record_checkbox = QCheckBox()
        self.record_checkbox.stateChanged.connect(self.record_checked)
        record_label = QLabel('Recording')
        record_control_layout.addWidget(self.record_checkbox)
        record_control_layout.addWidget(record_label)

        controls_box_layout.addLayout(heater_control_layout)
        controls_box_layout.addLayout(record_control_layout)

        right_layout.addWidget(controls_box)

            # Define and add operating conditions box
        conditions_box = QWidget()
        conditions_box.setObjectName('conditions_box')
        conditions_box.setStyleSheet("QWidget#conditions_box {border: 2px solid black;}")
        conditions_box_layout = QHBoxLayout()
        conditions_box.setLayout(conditions_box_layout)

        conditions_1 = QLabel('Operating Conditions 1')
        conditions_box_layout.addWidget(conditions_1)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setLineWidth(2)
        conditions_box_layout.addWidget(separator)
        conditions_2 = QLabel('Operating Conditions 2')
        conditions_box_layout.addWidget(conditions_2)

        right_layout.addWidget(conditions_box)

            # Define and add log box
        log_box = QScrollArea()
        log_box.setObjectName('log_box')
        log_box.setStyleSheet("QWidget#log_box {border: 2px solid black;}")
        log_label = QLabel('Log Goes Here')
        log_box.setWidget(log_label)

        right_layout.addWidget(log_box)

        # Add both layouts together
        layout.addLayout(left_layout, 3)
        layout.addLayout(right_layout, 1)

    def record_checked(self, checked: bool) -> None:
        self.mainwindow.controls['measure'] = checked
        self.mainwindow.measurement_clicked()


class AppWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(AppWindow, self).__init__(*args, **kwargs)

        self.mass_data = None
        self.rht_data = None
        self.collection_start_time = None

        self.setWindowTitle("Desiccator Controller")
        layout = QHBoxLayout()

        show_calculator = QAction("&Calculator", self)
        show_calculator.setStatusTip("Display Psychrometric Calculator")
        show_calculator.triggered.connect(self.show_calculator_clicked)

        show_converter = QAction("&Unit Converter", self)
        show_converter.setStatusTip("Display Unit Converter")
        show_converter.triggered.connect(self.show_converter_clicked)

        open_qr_code = QAction("Display &QR Code", self)
        open_qr_code.setStatusTip("Show QR code linking to newest SOP")
        open_qr_code.triggered.connect(self.open_qr_code)

        menu = self.menuBar()
        menu_menubar = menu.addMenu("&Menu")
        menu_menubar.addAction(show_calculator)
        menu_menubar.addAction(show_converter)

        help_menubar = menu.addMenu("&Help")
        help_menubar.addAction(open_qr_code)

        # Create 2 main columns
        output_calc_layout = QVBoxLayout()

        # Create output_calc_layout (layout including dialogue box for errors, plot, and button to calculate)
        self.dialogue_box = QLabel()
        self.dialogue_box.setStyleSheet("border: 2px solid black;")

        self.mass_box = QLabel()
        self.mass_box.setStyleSheet("border: 1px solid black;")

        self.rht_box = QLabel()
        self.rht_box.setStyleSheet("border: 1px solid black;")

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_clicked)

        measure_button = QPushButton("Start/Stop Measurement")
        measure_button.clicked.connect(self.measurement_clicked)

        # Defining the load cell array to be passed into the updater object
        self.load_cell_array = LoadCellArray()
        self.load_cell_array.load_array()

        self.rht_sensor_array = RHTSensorArray([SHT45(3), SHT45(6)])

        button_layout = QHBoxLayout()
        button_layout.addWidget(clear_button, 2)
        button_layout.addWidget(measure_button, 2)

        output_calc_layout.addWidget(self.dialogue_box, 10)
        output_calc_layout.addWidget(self.mass_box, 40)
        output_calc_layout.addWidget(self.rht_box, 40)
        output_calc_layout.addLayout(button_layout, 10)

        # Test tabs below buttons
        self.tabs = QChamberTabWidget(self)

        # Play around with declaring tabs in self or each chamber tab individually or both
        self.chamber_1_tab = ChamberTabPage(self, 1)
        self.chamber_2_tab = ChamberTabPage(self, 2)

        self.tabs.addTab(self.chamber_1_tab, 'Chamber 1')
        self.tabs.addTab(self.chamber_2_tab, 'Chamber 2')
        output_calc_layout.addWidget(self.tabs)

        layout.addLayout(output_calc_layout)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.threadpool = QThreadPool()

        self.controls = {'measure': False,
                         'calc_shown': False,
                         'converter_shown': False,
                         'read_signal': False}

    def clear_clicked(self) -> None:
        if not self.controls['measure']:
            self.dialogue_box.setText("Cleared!")

    def show_new_masses(self, masses: list) -> None:
        masses.pop(0)
        mass_string = '\n'.join(["Load Cell %i: %f" % (i + 1, masses[i]) for i in range(len(masses))])
        self.mass_box.setText(mass_string)

    def show_new_rht(self, rhts: list) -> None:
        rht_string = '\n'.join(["Sensor %i - %f C\t %f" % (i + 1, rhts[i][0], rhts[i][1]) for i in range(len(rhts))])
        self.rht_box.setText(rht_string)

    def store_masses(self, data: list) -> None:
        current_time = data.pop(0)
        self.mass_data = np.append(self.mass_data, [[current_time - self.collection_start_time, *data]], axis=0)
        print(self.mass_data)

    def store_rht(self, data: list) -> None:
        self.rht_data = np.append(self.rht_data, [[x for t in data for x in t]], axis=0)
        print(self.rht_data)

    def emit_read_pulse(self) -> None:
        self.controls['read_signal'] = True
        sleep(1)
        self.controls['read_signal'] = False

    def measurement_handling(self) -> None:
        coordinator = MeasurementCoordinator(self.controls)
        coordinator.signals.read.connect(self.emit_read_pulse)

        mass_handler = MassUpdater(self.load_cell_array, self.controls)
        mass_handler.signals.result.connect(self.show_new_masses)
        mass_handler.signals.result.connect(self.store_masses)

        rht_handler = RHTUpdater(self.rht_sensor_array, self.controls)
        rht_handler.signals.result.connect(self.show_new_rht)
        rht_handler.signals.result.connect(self.store_rht)

        self.threadpool.start(mass_handler)
        self.threadpool.start(rht_handler)
        self.threadpool.start(coordinator)

    def measurement_clicked(self) -> str:
        if self.controls['measure']:
            self.collection_start_time = int(time())
            self.mass_data = np.zeros((1, int(1 + self.load_cell_array.num_cells)))
            self.rht_data = np.zeros((1, int(2 * self.rht_sensor_array.num_sensors)))
            self.measurement_handling()
        else:
            # Add either auto-saving or a save-only button that doesn't stop data collection
            file_name = str(self.collection_start_time) + '_data.csv'
            headings = 'time, ' + ', '.join(
                ["mass %i" % (num + 1) for num in range(self.load_cell_array.num_cells)]) + ', ' + ', '.join(
                "temp %i, rh %i" % (num + 1, num + 1) for num in range(self.rht_sensor_array.num_sensors))
            self.mass_data = np.delete(self.mass_data, 0, 0)
            self.rht_data = np.delete(self.rht_data, 0, 0)

            data_to_save = np.append(self.mass_data, self.rht_data, axis=1)
            np.savetxt(file_name, data_to_save, header=headings, delimiter=', ', fmt='%1.4f')
            self.mass_data = None
            self.rht_data = None

            return file_name

    def show_calculator_clicked(self) -> None:
        if not self.controls['calc_shown']:
            # then show the calc
            self.controls['calc_shown'] = True
            self.calc_window = PsychrometricCalculatorWindow(self)
            self.calc_window.show()
        else:
            self.dialogue_box.setText("Calculator already shown.")

    def show_converter_clicked(self) -> None:
        if not self.controls['converter_shown']:
            self.controls['converter_shown'] = True
            self.converter_window = UnitConverterWindow(self)
            self.converter_window.show()
        else:
            self.dialogue_box.setText("Unit converter already shown.")

    def open_qr_code(self) -> None:
        path_to_img = '~/Pictures/Main_GUI.png'
        os.system(path_to_img)

    def closeEvent(self, event):
        # Override the closeEvent method that exists and replace with controls editing to exit ongoing threads
        self.controls['measure'] = False
        event.accept()


def main() -> None:
    psy_chart_app = QApplication(sys.argv)

    window = AppWindow()
    window.show()

    psy_chart_app.exec()


if __name__ == '__main__':
    main()
