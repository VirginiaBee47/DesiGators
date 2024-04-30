unit_equivalents = {'Mass': {'g': 1,
                             'kg': 1000,
                             'lbm': 453.59237,
                             'slug': 14593.903,
                             'firkin': 25401.17272},
                    'Volume': {'ft³': 1,
                               'm³': 35.31466672149,
                               'L': 0.03531466672149,
                               'mL': 0.00003531466672149,
                               'butt': 16.8570836,
                               'hogsheads': 8.42854179},
                    'Temperature': {'K': 1,
                                    'R': 5/9},
                    'Pressure': {'Pa': 1,
                                 'psi': 6894.76,
                                 'mmHg': 133.3223684,
                                 'atm': 101325.03982073,
                                 'bar': 100000,
                                 'torr': 133.3223684211},
                    'Mass Flow Rate': {'kg/s': 1,
                                       'kg/min': 0.01666666666,
                                       'lb/s': 0.45359237,
                                       'lb/min': 0.00755987283},
                    'Volumetric Flow Rate': {'SCFM': 1,
                                             'SCFH': 1/60,
                                             'SLPM': 0.035314666213,
                                             'm³/h': 0.58857777022},
                    'Energy': {'J': 1,
                               'kJ': 1000,
                               'kWh': 3600000,
                               'Btu': 1055.06,
                               'kcal': 4184,
                               'MeV': .00000000000016022},
                    'Power': {'W': 1,
                              'kW': 1000,
                              'hp': 745.69987158,
                              'Btu/h': 0.2930710702,
                              'RT': 3516.8528421},
                    'Specific Enthalpy': {'kJ/kg': 1,
                                          'Btu/lbm': 2.3244444444,
                                          'kcal/kg': 4.184},
                    'Specific Heat Capacity': {'kJ/kg\u00B7K': 1,
                                               'Btu/lbm\u00B7\u00B0R': 4.186,
                                               'kcal/kg\u00B7K': 4.186}}


def convert_units(value_type: str, unit_a: str, unit_b: str, value_a: float) -> float:
    value_b = None
    if value_type == 'Temperature':
        if unit_a == chr(176) + 'C':
            if unit_b == chr(176) + 'F':
                value_b = temp_c_to_f(value_a)
            elif unit_b == 'K':
                value_b = value_a + 273.15
            elif unit_b == chr(176) + 'R':
                value_b = temp_c_to_f(value_a) + 459.67
        elif unit_a == chr(176) + 'F':
            if unit_b == chr(176) + 'C':
                value_b = temp_f_to_c(value_a)
            elif unit_b == 'K':
                value_b = temp_f_to_c(value_a) + 273.15
            elif unit_b == chr(176) + 'R':
                value_b = value_a + 459.67
        elif unit_a == 'K':
            if unit_b == chr(176) + 'C':
                value_b = value_a - 273.15
            elif unit_b == chr(176) + 'F':
                value_b = temp_c_to_f(value_a - 273.15)
            elif unit_b == chr(176) + 'R':
                value_b = temp_c_to_f(value_a - 273.15) + 459.67
        elif unit_a == chr(176) + 'R':
            if unit_b == chr(176) + 'C':
                value_b = temp_f_to_c(value_a - 459.67)
            elif unit_b == chr(176) + 'F':
                value_b = value_a - 459.67
            elif unit_b == 'K':
                value_b = temp_f_to_c(value_a - 459.67) + 273.15
    else:
        value_b = value_a * unit_equivalents[value_type][unit_a] / unit_equivalents[value_type][unit_b]
    return value_b


def temp_f_to_c(f: float) -> float:
    return (f - 32) * 5/9


def temp_c_to_f(c: float) -> float:
    return (c * 9/5) + 32
