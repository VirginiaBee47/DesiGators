def convert_units(value_type: str, unit_a: str, unit_b: str, value_a: float) -> float:
    value_b = None
    if unit_a == unit_b:
        value_b = value_a
    elif value_type == 'Mass':
        if unit_a == 'g':
            if unit_b == 'kg':
                value_b = value_a/1000
            elif unit_b == 'lbm':
                value_b = mass_kg_to_lbm(value_a/1000)
        elif unit_a == 'kg':
            if unit_b == 'g':
                value_b = value_a*1000
            elif unit_b == 'lbm':
                value_b = mass_kg_to_lbm(value_a)
        elif unit_a == 'lbm':
            if unit_b == 'g':
                value_b = mass_lbm_to_kg(value_a)*1000
            elif unit_b == 'kg':
                value_b = mass_lbm_to_kg(value_a)
    elif value_type == 'Volume':
        if unit_a == 'ft³':
            pass
        elif unit_a == 'm³':
            pass
        elif unit_a == 'L':
            pass
        elif unit_a == 'mL':
            pass
    elif value_type == 'Temperature':
        if unit_a == chr(176) + 'C':
            pass
        elif unit_a == chr(176) + 'F':
            pass
        elif unit_a == 'K':
            pass
        elif unit_a == chr(176) + 'R':
            pass
    elif value_type == 'Pressure':
        if unit_a == 'Pa':
            pass
        elif unit_a == 'psi':
            pass
        elif unit_a == 'mmHg':
            pass
        elif unit_a == 'atm':
            pass
        elif unit_a == 'bar':
            pass
        elif unit_a == 'torr':
            pass
    elif value_type == 'Mass Flow Rate':
        if unit_a == 'kg/s':
            pass
        elif unit_b == 'lb/s':
            pass
    elif value_type == 'Volumetric Flow Rate':
        if unit_a == 'SCFM':
            pass
        elif unit_a == 'SCFH':
            pass
        elif unit_a == 'SLPM':
            pass
        elif unit_a == 'm³/h':
            pass
    elif value_type == 'Energy':
        if unit_a == 'J':
            pass
        elif unit_a == 'kJ':
            pass
        elif unit_a == 'kWh':
            pass
        elif unit_a == 'Btu':
            pass
        elif unit_a == 'kcal':
            pass
        elif unit_a == 'keV':
            pass
    elif value_type == 'Power':
        if unit_a == 'W':
            pass
        elif unit_a == 'kW':
            pass
        elif unit_a == 'hp':
            pass
        elif unit_a == 'Btu/h':
            pass
        elif unit_a == 'RT':
            pass
    elif value_type == 'Specific Enthalpy':
        if unit_a == 'kJ/kg':
            pass
        elif unit_a == 'Btu/lbm':
            pass
    elif value_type == 'Specific Heat Capacity':
        if unit_a == 'kJ/kg\u00B7K':
            pass
        elif unit_a == 'Btu/lbm\u00B7\u00B0R':
            pass
    return value_b


def mass_kg_to_lbm(kg: float) -> float:
    return kg * 2.20462262185


def mass_lbm_to_kg(lbm: float) -> float:
    return lbm / 2.20462262185
