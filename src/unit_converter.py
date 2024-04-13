"""
Units
----------------------------------------
Mass                    :   g,      kg,     lbm,    slug,   firkin
Volume                  :   ft³,    m³,     L,      mL,     butt,   hogsheads
Temperature             :
Pressure                :
Mass Flow Rate          :
Volumetric Flow Rate    :
Energy                  :
Power                   :
Specific Enthalpy       :
Specific Heat Capacity  :
"""


def convert_units(value_type: str, unit_a: str, unit_b: str, value_a: float) -> float:
    value_b = None
    if unit_a == unit_b:
        value_b = value_a
    elif value_type == 'Mass':
        if unit_a == 'g':
            if unit_b == 'kg':
                value_b = value_a / 1000
            elif unit_b == 'lbm':
                value_b = mass_kg_to_lbm(value_a / 1000)
            elif unit_b == 'slug':
                value_b = mass_kg_to_slug(value_a / 1000)
            elif unit_b == 'firkin':
                value_b = mass_kg_to_firkin(value_a / 1000)
        elif unit_a == 'kg':
            if unit_b == 'g':
                value_b = value_a * 1000
            elif unit_b == 'lbm':
                value_b = mass_kg_to_lbm(value_a)
            elif unit_b == 'slug':
                value_b = mass_kg_to_slug(value_a)
            elif unit_b == 'firkin':
                value_b = mass_kg_to_firkin(value_a)
        elif unit_a == 'lbm':
            if unit_b == 'g':
                value_b = mass_lbm_to_kg(value_a) * 1000
            elif unit_b == 'kg':
                value_b = mass_lbm_to_kg(value_a)
            elif unit_b == 'slug':
                value_b = mass_lbm_to_slug(value_a)
            elif unit_b == 'firkin':
                value_b = mass_lbm_to_firkin(value_a)
        elif unit_a == 'slug':
            if unit_b == 'g':
                value_b = mass_slug_to_kg(value_a) * 1000
            elif unit_b == 'kg':
                value_b = mass_slug_to_kg(value_a)
            elif unit_b == 'lbm':
                value_b = mass_slug_to_lbm(value_a)
            elif unit_b == 'firkin':
                value_b = mass_slug_to_firkin(value_a)
        elif unit_a == 'firkin':
            if unit_b == 'g':
                value_b = mass_firkin_to_kg(value_a) * 1000
            elif unit_b == 'kg':
                value_b = mass_firkin_to_kg(value_a)
            elif unit_b == 'lbm':
                value_b = mass_firkin_to_lbm(value_a)
            elif unit_b == 'slug':
                value_b = mass_firkin_to_slug(value_a)
    elif value_type == 'Volume':
        if unit_a == 'ft³':
            if unit_b == 'm³':
                value_b = vol_feet_cubed_to_meters_cubed(value_a)
            elif unit_b == 'L':
                value_b = vol_feet_cubed_to_meters_cubed(value_a) * 1000
            elif unit_b == 'mL':
                value_b = vol_feet_cubed_to_meters_cubed(value_a) * 1000000
        elif unit_a == 'm³':
            if unit_b == 'ft³':
                value_b = vol_meters_cubed_to_feet_cubed(value_a)
            elif unit_b == 'L':
                value_b = value_a * 1000
            elif unit_b == 'mL':
                value_b = value_a * 1000000
        elif unit_a == 'L':
            if unit_b == 'm³':
                value_b = value_a / 1000
            elif unit_b == 'ft³':
                value_b = vol_meters_cubed_to_feet_cubed(value_a / 1000)
            elif unit_b == 'mL':
                value_b = value_a * 1000
        elif unit_a == 'mL':
            if unit_b == 'm³':
                value_b = value_a / 1000000
            elif unit_b == 'ft³':
                value_b = vol_meters_cubed_to_feet_cubed(value_a / 1000000)
            elif unit_b == 'L':
                value_b = value_a / 1000
    elif value_type == 'Temperature':
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
    elif value_type == 'Pressure':
        if unit_a == 'Pa':
            if unit_b == 'psi':
                pass
            elif unit_b == 'mmHg':
                pass
            elif unit_b == 'atm':
                pass
            elif unit_b == 'bar':
                pass
            elif unit_b == 'torr':
                pass
        elif unit_a == 'psi':
            if unit_b == 'Pa':
                pass
            elif unit_b == 'mmHg':
                pass
            elif unit_b == 'atm':
                pass
            elif unit_b == 'bar':
                pass
            elif unit_b == 'torr':
                pass
        elif unit_a == 'mmHg':
            if unit_b == 'Pa':
                pass
            elif unit_b == 'psi':
                pass
            elif unit_b == 'atm':
                pass
            elif unit_b == 'bar':
                pass
            elif unit_b == 'torr':
                pass
        elif unit_a == 'atm':
            if unit_b == 'Pa':
                pass
            elif unit_b == 'psi':
                pass
            elif unit_b == 'mmHg':
                pass
            elif unit_b == 'bar':
                pass
            elif unit_b == 'torr':
                pass
        elif unit_a == 'bar':
            if unit_b == 'Pa':
                pass
            elif unit_b == 'psi':
                pass
            elif unit_b == 'mmHg':
                pass
            elif unit_b == 'atm':
                pass
            elif unit_b == 'torr':
                pass
        elif unit_a == 'torr':
            if unit_b == 'Pa':
                pass
            elif unit_b == 'psi':
                pass
            elif unit_b == 'mmHg':
                pass
            elif unit_b == 'atm':
                pass
            elif unit_b == 'bar':
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


def mass_kg_to_slug(kg: float) -> float:
    return kg / 14.59390


def mass_slug_to_kg(slug: float) -> float:
    return slug * 14.59390


def mass_lbm_to_slug(lbm: float) -> float:
    return lbm / 32.17405


def mass_slug_to_lbm(slug: float) -> float:
    return slug * 32.17405


def mass_kg_to_firkin(kg: float) -> float:
    return kg / 40.8233133


def mass_firkin_to_kg(firkin: float) -> float:
    return firkin * 40.8233133


def mass_lbm_to_firkin(lbm: float) -> float:
    return lbm / 90


def mass_firkin_to_lbm(firkin: float) -> float:
    return firkin * 90


def mass_slug_to_firkin(slug: float) -> float:
    return mass_kg_to_firkin(mass_slug_to_kg(slug))


def mass_firkin_to_slug(firkin: float) -> float:
    return mass_kg_to_slug(mass_firkin_to_kg(firkin))


def vol_meters_cubed_to_feet_cubed(cu_meters: float) -> float:
    return cu_meters * 35.3147


def vol_feet_cubed_to_meters_cubed(cu_feet: float) -> float:
    return cu_feet / 35.3147


def temp_f_to_c(f: float) -> float:
    return (f - 32) * 5/9


def temp_c_to_f(c: float) -> float:
    return (c * 9/5) + 32
