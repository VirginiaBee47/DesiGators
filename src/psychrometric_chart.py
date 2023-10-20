# -*- coding: utf-8 -*-
"""
Title: Psychrometric Chart
Author: Virginia Covert
Co-Authors: Alexander Weaver, Korynn Haetten, Stanley Moonjeli

Description: 
    A script to aid in psychrometric calculations. Designed for use in 
    DesiGators IPPD project sponsored by UF-FSHN dept.
    
Sponsor: Dr. Andrew MacIntosh
Coach: Dr. Philip Jackson

References:
    1 - https://journals.ametsoc.org/view/journals/apme/57/6/jamc-d-17-0334.1.xml
    2 - https://www.1728.org/relhum.htm
    X - https://www.caee.utexas.edu/prof/novoselac/classes/are383/handouts/f01_06si.pdf
"""

from math import exp
from exceptions import PointNotDefinedException

R_dry_air = 287.055  # [=] J/(kg * C)
R_water_vapor = 461.520  # [=] J/(kg * C)

psychrometric_properties = {'dry_bulb_temperature': None,
                            'wet_bulb_temperature': None,
                            'dew_point_temperature': None,
                            'total_pressure': None,
                            'humidity_ratio': None,
                            'relative_humidity': None,
                            'total_enthalpy': None,
                            'partial_pressure_vapor': None,
                            'specific_volume': None,
                            'specific_heat_capacity': None}


class PsychrometricProperties:
    def __init__(self, **kwargs):
        if 'dry_bulb_temperature' in kwargs.keys():
            self.dry_bulb_temperature = kwargs['dry_bulb_temperature']
        else:
            self.dry_bulb_temperature = None

        if 'wet_bulb_temperature' in kwargs.keys():
            self.wet_bulb_temperature = kwargs['wet_bulb_temperature']
        else:
            self.wet_bulb_temperature = None

        if 'dew_point_temperature' in kwargs.keys():
            self.dew_point_temperature = kwargs['dew_point_temperature']
        else:
            self.dew_point_temperature = None

        if 'total_pressure' in kwargs.keys():
            self.total_pressure = kwargs['total_pressure']
        else:
            self.total_pressure = None

        if 'humidity_ratio' in kwargs.keys():
            self.humidity_ratio = kwargs['humidity_ratio']
        else:
            self.humidity_ratio = None

        if 'relative_humidity' in kwargs.keys():
            self.relative_humidity = kwargs['relative_humidity']
        else:
            self.relative_humidity = None

        if 'total_enthalpy' in kwargs.keys():
            self.total_enthalpy = kwargs['total_enthalpy']
        else:
            self.total_enthalpy = None

        if 'partial_pressure_vapor' in kwargs.keys():
            self.partial_pressure_vapor = kwargs['partial_pressure_vapor']
        else:
            self.partial_pressure_vapor = None

        if 'density' in kwargs.keys():
            self.density = kwargs['density']
        else:
            self.density = None

        if 'specific_volume' in kwargs.keys():
            self.specific_volume = kwargs['specific_volume']
        else:
            self.specific_volume = None

        if 'specific_heat_capacity' in kwargs.keys():
            self.specific_heat_capacity = kwargs['specific_heat_capacity']
        else:
            self.specific_heat_capacity = None

        self.point_defined = self.check_defined()

        try:
            self.define_point()
        except PointNotDefinedException:
            print("Point could not be defined automatically. Input more information and then try again. Continuing...")
            raise

    def check_defined(self) -> bool:
        """Checks to see if the condition specified is fully defined.
        
        Function checks to see if there is enough information to fully define 
        the psychrometric properties of the point or if more must be supplied 
        to defind the point.

        Returns
        -------
        bool
            Whether or not the point is fully defined.

        """
        criterion_1, criterion_2 = False, False
        criterion_2_properties = [self.dry_bulb_temperature,
                                  self.wet_bulb_temperature,
                                  self.dew_point_temperature,
                                  self.humidity_ratio,
                                  self.relative_humidity,
                                  self.total_enthalpy,
                                  self.partial_pressure_vapor,
                                  self.specific_volume,
                                  self.specific_heat_capacity]

        if self.total_pressure is not None:
            criterion_1 = True

        if sum(x is not None for x in criterion_2_properties) >= 2:
            criterion_2 = True

        return criterion_1 and criterion_2

    def define_point(self) -> None:
        if not self.point_defined:
            raise PointNotDefinedException

        # Case reduction 1: specific heat capacity to humidity ratio
        if self.specific_heat_capacity is not None:
            self.humidity_ratio = find_humidity_ratio_from_cp(self.specific_heat_capacity)

        # Case reduction 2: dew point temperature to partial pressure of vapor
        if self.dew_point_temperature is not None:
            self.partial_pressure_vapor = find_p_water_vapor_from_dew_point(self.dew_point_temperature)

        # Case reduction 3a: partial pressure of vapor to humidity ratio
        if self.partial_pressure_vapor is not None:
            self.humidity_ratio = find_humidity_ratio(self.partial_pressure_vapor, self.total_pressure)

        # Case reduction 3b: humidity ratio to partial pressure of vapor
        elif self.humidity_ratio is not None:
            self.partial_pressure_vapor = find_p_water_vapor_from_humidity_ratio(self.humidity_ratio,
                                                                                 self.total_pressure)

        # Case 1: Dry Bulb and Wet Bulb Temps known
        if self.dry_bulb_temperature is not None and self.wet_bulb_temperature is not None:
            self.total_enthalpy = find_total_enthalpy(self.wet_bulb_temperature,
                                                      find_saturation_humidity_ratio(self.wet_bulb_temperature,
                                                                                     p_total=self.total_pressure))
            self.humidity_ratio = find_humidity_ratio_from_enthalpy_db(self.dry_bulb_temperature, self.total_enthalpy)
            self.partial_pressure_vapor = find_p_water_vapor_from_humidity_ratio(self.humidity_ratio,
                                                                                 self.total_pressure)
            self.relative_humidity = find_relative_humidity(self.partial_pressure_vapor, self.dry_bulb_temperature)
            self.dew_point_temperature = find_dew_point_temperature(self.partial_pressure_vapor)
            self.specific_volume = find_specific_volume(self.humidity_ratio, self.dry_bulb_temperature,
                                                        self.total_pressure)
            self.specific_heat_capacity = find_specific_heat(self.humidity_ratio)

        # Case 2: Dry Bulb and Humidity Ratio known
        elif self.dry_bulb_temperature is not None and self.humidity_ratio is not None:
            self.total_enthalpy = find_total_enthalpy(self.dry_bulb_temperature, self.humidity_ratio)
            self.wet_bulb_temperature = find_wet_bulb_temperature(self.total_enthalpy, self.dry_bulb_temperature)
            self.dew_point_temperature = find_dew_point_temperature(self.partial_pressure_vapor)
            self.relative_humidity = find_relative_humidity(self.partial_pressure_vapor, self.dry_bulb_temperature)
            self.specific_volume = find_specific_volume(self.humidity_ratio, self.dry_bulb_temperature,
                                                        self.total_pressure)
            self.specific_heat_capacity = find_specific_heat(self.humidity_ratio)

        # Case 3: Dry Bulb and Relative Humidity known
        elif self.dry_bulb_temperature is not None and self.relative_humidity is not None:
            self.partial_pressure_vapor = self.relative_humidity * find_p_saturation(self.dry_bulb_temperature)
            self.humidity_ratio = find_humidity_ratio_from_RH_temp(self.relative_humidity, self.dry_bulb_temperature,
                                                                   p_total=self.total_pressure)
            self.dew_point_temperature = find_dew_point_temperature(self.partial_pressure_vapor)
            self.total_enthalpy = find_total_enthalpy(self.dry_bulb_temperature, self.humidity_ratio)
            self.wet_bulb_temperature = find_wet_bulb_temperature(self.total_enthalpy, self.dry_bulb_temperature)
            self.specific_volume = find_specific_volume(self.humidity_ratio, self.dry_bulb_temperature,
                                                        self.total_pressure)
            self.specific_heat_capacity = find_specific_heat(self.humidity_ratio)

        # Case 4: Dry Bulb and Total Enthalpy known
        elif self.dry_bulb_temperature is not None and self.total_enthalpy is not None:
            self.humidity_ratio = find_humidity_ratio_from_enthalpy_db(self.dry_bulb_temperature, self.total_enthalpy)
            self.wet_bulb_temperature = find_wet_bulb_temperature(self.total_enthalpy, self.dry_bulb_temperature,
                                                                  self.total_pressure)
            self.partial_pressure_vapor = find_p_water_vapor_from_humidity_ratio(self.humidity_ratio,
                                                                                 self.total_pressure)
            self.dew_point_temperature = find_dew_point_temperature(self.partial_pressure_vapor)
            self.relative_humidity = find_relative_humidity(self.partial_pressure_vapor, self.dry_bulb_temperature)
            self.specific_heat_capacity = find_specific_heat(self.humidity_ratio)
            self.specific_volume = find_specific_volume(self.humidity_ratio, self.dry_bulb_temperature,
                                                        self.total_pressure)

        # Case 5: Dry Bulb and Specific Volume known
        elif self.dry_bulb_temperature is not None and self.specific_volume is not None:
            self.humidity_ratio = find_humidity_ratio_from_specific_vol_and_temp(self.specific_volume,
                                                                                 self.dry_bulb_temperature,
                                                                                 self.total_pressure)
            self.partial_pressure_vapor = find_p_water_vapor_from_humidity_ratio(self.humidity_ratio,
                                                                                 self.total_pressure)
            self.relative_humidity = find_relative_humidity(self.partial_pressure_vapor, self.dry_bulb_temperature)
            self.dew_point_temperature = find_dew_point_temperature(self.partial_pressure_vapor)
            self.specific_heat_capacity = find_specific_heat(self.humidity_ratio)
            self.total_enthalpy = find_total_enthalpy(self.dry_bulb_temperature, self.humidity_ratio)
            self.wet_bulb_temperature = find_wet_bulb_temperature(self.total_enthalpy, self.dry_bulb_temperature,
                                                                  self.total_pressure)

        # Case 6: Wet Bulb and Humidity Ratio known
        elif self.wet_bulb_temperature is not None and self.humidity_ratio is not None:
            # partial pressure of vapor is known because of case reduction
            self.total_enthalpy = find_total_enthalpy(self.wet_bulb_temperature,
                                                      find_saturation_humidity_ratio(self.wet_bulb_temperature,
                                                                                     self.total_pressure))
            self.dry_bulb_temperature = find_dry_bulb_temperature(self.total_enthalpy, self.humidity_ratio)
            self.dew_point_temperature = find_dew_point_temperature(self.partial_pressure_vapor)
            self.relative_humidity = find_relative_humidity(self.partial_pressure_vapor, self.dry_bulb_temperature)
            self.specific_volume = find_specific_volume(self.humidity_ratio, self.dry_bulb_temperature,
                                                        self.total_pressure)
            self.specific_heat_capacity = find_specific_heat(self.humidity_ratio)

        # Case 7: Wet Bulb and Relative Humidity known
        elif self.wet_bulb_temperature is not None and self.relative_humidity is not None:
            self.total_enthalpy = find_total_enthalpy(self.wet_bulb_temperature,
                                                      find_saturation_humidity_ratio(self.wet_bulb_temperature,
                                                                                     self.total_pressure))
            self.dry_bulb_temperature = find_dry_bulb_temperature_RH_enthalpy(self.relative_humidity, self.total_enthalpy, self.total_pressure)
            self.humidity_ratio = find_humidity_ratio_from_enthalpy_db(self.dry_bulb_temperature, self.total_enthalpy)
            self.partial_pressure_vapor = find_p_water_vapor_from_humidity_ratio(self.humidity_ratio, self.total_pressure)
            self.specific_volume = find_specific_volume(self.humidity_ratio, self.dry_bulb_temperature, self.total_pressure)
            self.specific_heat_capacity = find_specific_heat(self.humidity_ratio)
            self.dew_point_temperature = find_dew_point_temperature(self.partial_pressure_vapor)
        
        # Case 8: Wet Bulb and Total Enthalpy known
        elif self.wet_bulb_temperature is not None and self.total_enthalpy is not None:
            self.dry_bulb_temperature = find_dry_bulb_temperature_WB_enthalpy(self.wet_bulb_temperature, self.total_enthalpy, self.total_pressure)
            self.humidity_ratio = find_humidity_ratio_from_enthalpy_db(self.dry_bulb_temperature, self.total_enthalpy)
            self.partial_pressure_vapor = find_p_water_vapor_from_humidity_ratio(self.humidity_ratio, self.total_pressure)
            self.relative_humidity = find_relative_humidity(self.partial_pressure_vapor, self.dry_bulb_temperature)
            self.dew_point_temperature = find_dew_point_temperature(self.partial_pressure_vapor)
            self.specific_volume = find_specific_volume(self.humidity_ratio, self.dry_bulb_temperature, self.total_pressure)
            self.specific_heat_capacity = find_specific_heat(self.humidity_ratio)
            
        # Case 9: Wet Bulb and Specifc Volume known
        elif self.wet_bulb_temperature is not None and self.specific_volume is not None:
            pass


def find_p_saturation(air_temp: float) -> float:
    """Function to find the saturation vapor pressure of water at a given temperature.

    Equation follows that proposed in reference 1.    

    Parameters
    ----------
    air_temp : float
        Temperature supplied must be in [C].

    Returns
    -------
    float
        Answer provided in units of [Pa].

    """
    return exp(34.494 - (4924.99 / (air_temp + 237.1))) / (air_temp + 105) ** 1.57


def deriv_p_saturation(T: float) -> float:
    """Derivative of saturation vapor pressure equation
    
    Derivative of p_sat equation to be used in gradient descent calculations.

    Parameters
    ----------
    T : float
        Temperature at which the derivative is to be evaluated. Must be in 
        units of [C].

    Returns
    -------
    float
        Slope of p_saturation vs. T plot at a given T. Answer (technically) 
        given in units of [Pa/C].

    """
    numer = (T + 105) ** 1.57 * exp(34.494 - 4924.99 / (T + 237.1)) * 4924.99 / (T + 237.1) ** 2 - exp(
        34.494 - 4924.99 / (T + 237.1)) * 1.57 * (T + 105) ** 0.57
    denom = (T + 105) ** 3.14
    return numer / denom


def find_humidity_ratio(p_vapor: float, p_total: float = 101325) -> float:
    """Function to find the humidity ratio of air at a given partial vapor pressure of water and total pressure.

    Parameters
    ----------
    p_vapor : float
        Pressure should have units of [Pa].
    p_total : float, optional
        Pressure should have units of [Pa]. The default is 101325. 

    Returns
    -------
    float
        Answer provided in units of [kg water/kg dry air].

    """
    return 18.02 / 28.97 * p_vapor / (p_total - p_vapor)


def find_saturation_humidity_ratio(air_temp: float, p_total: float = 101325) -> float:
    """Function to find the saturation humidity ratio of air at a given temperature.

    Parameters
    ----------
    air_temp : float
        Temperature supplied must be in [C].
    p_total : float, optional
        Pressure must have units of [Pa]. The default is 101325.

    Returns
    -------
    float
        Answer provided in units of [kg water/kg dry air].

    """
    return find_humidity_ratio(find_p_saturation(air_temp), p_total)


def find_total_enthalpy(air_temp: float, humidity_ratio: float) -> float:
    """Function to find the total enthalpy of an air/water mixture at a given temperature and humidity ratio.

    Parameters
    ----------
    air_temp : float
        Temperature supplied must be in [C].
    humidity_ratio : float
        Humidity ratio must be in [kg water/kg dry air].

    Returns
    -------
    float
        Answer provided in units of [kJ / kg dry air].

    """
    return (1.005 + 1.88 * humidity_ratio) * air_temp + 2501.4 * humidity_ratio


def find_humidity_ratio_from_RH_temp(relative_humidity: float, air_temp: float, p_total: float = 101325) -> float:
    """Function to find humidity ratio using relative humidity and temperature.
    
    This function is similar to 'find_humidity_ratio', but instead of using 
    parameters p_vapor and p_total, it uses values commonly returned from 
    relative humidity sensing elements.

    Parameters
    ----------
    relative_humidity : float
        Relative humidity of the air. This must be a unitless value between 0
        and 1 (not expressed as a percent).
    air_temp : float
        Temperature supplied must be in [C].
    p_total : float, optional
        Pressure must have units of [Pa]. The default is 101325.

    Returns
    -------
    float
        Answer provided in units of [kg water/kg dry air].

    Raises
    ------
    ValueError
        If the value passed for relative humidity is outside the expected 
        range [0,1]
    
    """
    if relative_humidity > 1 or relative_humidity < 0:
        raise ValueError(
            'The value passed for relative humidity (%f) is outside the accepted range [0,1].' % relative_humidity)

    p_vapor_calculated = relative_humidity * find_p_saturation(air_temp)
    return find_humidity_ratio(p_vapor_calculated, p_total)


def find_humidity_ratio_from_enthalpy_db(air_temp: float, enthalpy: float) -> float:
    """Function to find humidity ratio using enthalpy and dry bulb temp.
    
    This function is particularly useful when wet bulb temperature is known
    since it is a quick way to find the total enthalpy.

    Parameters
    ----------
    air_temp : float
        Specifically refers to dry bulb temperature. Must be reported in [C].
    enthalpy : float
        Total enthalpy of the air/water mix. Must be in units of [kJ/kg dry air].

    Returns
    -------
    float
        Answer provided in units of [kg water/kg dry air].

    """
    return (enthalpy - 1.005 * air_temp) / (1.88 * air_temp + 2501.4)


def find_p_water_vapor_from_humidity_ratio(humidity_ratio: float, p_total: float = 101325) -> float:
    """Function to find the partial pressure of vapor given humidity ratio.
    
    This function calculates the partial pressure of water vapor given a
    certain humidity ratio and ambient total pressure.    

    Parameters
    ----------
    humidity_ratio : float
        Must be in units of [kg water/kg dry air].
    p_total : float, optional
        Pressure must have units of [Pa]. The default is 101325.

    Returns
    -------
    float
        Answer provided in units of [Pa].

    """
    return 28.97 * humidity_ratio * p_total / (18.02 + 28.97 * humidity_ratio)


def find_relative_humidity(p_vapor: float, air_temp: float) -> float:
    """Function to find the relative humidity of the air.
    
    This function is particularly useful for applications of known partial 
    pressure of water vapor. If this value is not yet known, refer to other 
    equations first.

    Parameters
    ----------
    p_vapor : float
        Partial pressure of water vapor in the air. Must be in units of [Pa].
    air_temp : float
        Dry Bulb temperature of the ambient air. Must be in units of [C].

    Returns
    -------
    float
        Answer provided as a decimal representation of % relative humidity.

    """
    if (rh := (p_vapor / find_p_saturation(air_temp))) > 1:
        raise ValueError("Calculated relative humidity (%f) is too high for the given air temperature." % rh)
    else:
        return rh


def find_p_water_vapor_from_dew_point(dew_point_temperature: float) -> float:
    """Function to find the partial pressure of water vapor at a dew point

    Parameters
    ----------
    dew_point_temperature : float
        Known dew point temperature. Must be given in [C].

    Returns
    -------
    float
        Partial pressure of water vapor in the air/water vapor mixture. Answer 
        provided in units of [Pa].

    """
    return find_p_saturation(dew_point_temperature)


def find_dew_point_temperature(p_vapor: float, precision: int = 5, trial_temp: float = 50) -> float:
    """Function to use gradient descent to find dew point temperature.
    
    This function works in conjunction with t_dew_point_step to use gradient 
    descent to find dew point temperature. To avoid the Lambert-W function in
    solving the p_saturation equation for temperature, an iterative solution is
    utilized. A temperature is guessed and then p_sat at the guessed
    temperatuer is referenced to the known partial pressure of water vapor.
    Then, using t_dew_point_step, the next guess is calculated until the
    difference between the previous guess and next iteration is less than the
    specified decimal presision (10 ** -precision).

    Parameters
    ----------
    p_vapor : float
        Partial pressure of water vapor in the air. Must be in units of [Pa].
    precision : int, optional
        Denotes the requested presicion of answer. The default is 5. Avoid 
        precisions above 10 to reduce script runtime.
    trial_temp : float, optional
        Initial guess for dew point temperature. Must be in units of [C]. The 
        default is 50.

    Returns
    -------
    float
        Answer provided is dew point temperature in units of [C].

    """
    t_next = t_dew_point_step(trial_temp, p_vapor)

    while abs(t_next - trial_temp) > 10 ** (-precision):
        trial_temp = t_next
        t_next = t_dew_point_step(trial_temp, p_vapor)

    return trial_temp


def t_dew_point_step(t_prev: float, p_vapor: float) -> float:
    """Function to find the optimal step for dew point temperature calculation
    
    This function uses a square difference and derivative function to find the
    optimal next step in temperature for dew point calculation. Because the
    step size is proportional to the slope of the squared difference function,
    the steps get smaller as the guess approaches the actual value for dew 
    point temperature.
    
    Works in conjuction with find_dew_point_temperature function.

    Parameters
    ----------
    t_prev : float
        Previous guess for dew point temperature. Must be in units of [C].
    p_vapor : float
        Known value for partial pressure of water vapor. Must be in units of 
        [Pa].

    Returns
    -------
    float
        Optimized next guess for dew point temperature. Provided in units of 
        [C].

    """
    difference_squared = (find_p_saturation(t_prev) - p_vapor) ** 2
    gradient = ((9849.88 * exp(68.998 - 9849.88 / (t_prev + 237.1)) * (t_prev + 105) ** 3.14) / (
            t_prev + 237.1) ** 2 - 3.14 * exp(68.998 - 9849.88 / (t_prev + 237.1)) * (t_prev + 105) ** 2.14) / (
                       t_prev + 105) ** 6.28 - 2 * p_vapor * (
                       (4924.99 * exp(34.494 - 4924.99 / (t_prev + 237.1)) * (t_prev + 105) ** 1.57) / (
                       t_prev + 237.1) ** 2 - 1.57 * exp(34.494 - 4924.99 / (t_prev + 237.1)) * (
                               t_prev + 105) ** 0.57) / (t_prev + 105) ** 3.14
    return t_prev - difference_squared / gradient


def t_dry_bulb_step(t_prev: float, relative_humidity: float, total_enthalpy: float,
                    total_pressure: float = 101325) -> float:
    """Function to find the optimal step for dry bulb temperature calculation
    
    This function uses a square difference and derivative function to find the
    optimal next step in temperature for dry bulb temperature calculation. 
    Because the step size is proportional to the slope of the squared 
    difference function, the steps get smaller as the guess approaches the 
    actual value for dry bulb temperature.

    Parameters
    ----------
    t_prev : float
        Previous guess for dew point temperature. Must be in units of [C].
    relative_humidity : float
        Relative humidity provided as a decimal on the interval [0,1].
    total_enthalpy : float
        Total enthalpy of the air/water vapor mix in units of [kJ/kg dry air].
    total_pressure : float, optional
        Sum of partial pressures in ambient environment. Pressure must have 
        units of [Pa]. The default is 101325.

    Returns
    -------
    float
        Optimized next guess for dew point temperature. Provided in units of 
        [C].

    """
    difference_squared = (1.005 * t_prev + (1.88 * t_prev + 2501.4) * relative_humidity * find_p_saturation(t_prev) / (
                total_pressure - relative_humidity * find_p_saturation(t_prev)) - total_enthalpy) ** 2
    gradient = 2 * (1.005 * t_prev + (1.88 * t_prev + 2501.4) * relative_humidity * find_p_saturation(t_prev) / (
                total_pressure - relative_humidity * find_p_saturation(t_prev)) - total_enthalpy) * (
                           1.005 + (1.88 * t_prev + 2501.4) * relative_humidity * total_pressure * deriv_p_saturation(
                       t_prev) / (total_pressure - relative_humidity * find_p_saturation(
                       t_prev)) ** 2 + 1.88 * relative_humidity * find_p_saturation(t_prev) / (
                                       total_pressure - relative_humidity * find_p_saturation(t_prev)))

    return t_prev - difference_squared / gradient


def find_dry_bulb_temperature_RH_enthalpy(relative_humidity: float, total_enthalpy: float,
                                          total_pressure: float = 101325, precision: int = 5,
                                          trial_temp: float = 50) -> float:
    """Function to use gradient descent to find dry bulb temperature.
    
    This function works in conjunction with t_dry_bulb_step to use gradient 
    descent to find dry bulb temperature. To avoid the Lambert-W function in
    solving the p_saturation equation for temperature, an iterative solution is
    utilized. A temperature is guessed and then the difference between the 
    calculated value of total enthalpy and the actual known value is computed. 
    Then, using t_dry_bulb_step, the next guess is calculated until the
    difference between the previous guess and next iteration is less than the
    specified decimal presision (10 ** -precision).
    

    Parameters
    ----------
    relative_humidity : float
        Relative humidity provided as a decimal on the interval [0,1].
    total_enthalpy : float
        Total enthalpy of the air/water vapor mix in units of [kJ/kg dry air].
    total_pressure : float, optional
        Sum of partial pressures in ambient environment. Pressure must have 
        units of [Pa]. The default is 101325.
    precision : int, optional
        Denotes the requested presicion of answer. The default is 5. Avoid 
        precisions above 10 to reduce script runtime.
    trial_temp : float, optional
         Initial guess for dew point temperature. Must be in units of [C]. The 
        default is 50.

    Returns
    -------
    float
        Answer provided is dry bulb temperature in units of [C].

    """
    t_next = t_dry_bulb_step(trial_temp, relative_humidity, total_enthalpy, total_pressure)

    while abs(t_next - trial_temp) > 10 ** (-precision):
        trial_temp = t_next
        t_next = t_dry_bulb_step(trial_temp, relative_humidity, total_enthalpy, total_pressure)

    return trial_temp


def find_humidity_ratio_from_cp(specific_heat_capacity: float) -> float:
    """Function to find the humidity ratio given specific heat capacity.
    
    *NOTE* Heat capacities of air (1.005 kJ/kg dry air.K) and water vapour 
    (1.88 kJ/kg water vapour.K) assumed constant over pressure and temperature

    Parameters
    ----------
    specific_heat_capacity : float
        Known specific heat capacity of the air. Must be in units of [kJ/kg].

    Returns
    -------
    float
        Humidity ratio of the air provided in [kg water/kg dry air].

    """
    return (specific_heat_capacity - 1.005) / 1.88


def find_specific_heat(humidity_ratio: float) -> float:
    """Function to find the specific heat of the air.
    
    *NOTE* Heat capacities of air (1.005 kJ/kg dry air.K) and water vapour 
    (1.88 kJ/kg water vapour.K) assumed constant over pressure and temperature
    

    Parameters
    ----------
    humidity_ratio : float
        Humidity ratio of the air provided in [kg water/kg dry air].

    Returns
    -------
    float
        Specific heat capacity of the air. Must be in units of [kJ/kg].

    """
    return 1.005 + 1.88 * humidity_ratio


def find_specific_volume(humidity_ratio: float, air_temp: float, total_pressure: float = 101325) -> float:
    """Function to find the volume per kg of air/water vapor mix.
    
    This function uses a derivation of the ideal gas law (PV=mRT) to solve for
    ~specific~ volume, or the volume occupied by one kilogram of gas at the 
    given pressure.    
    
    Parameters
    ----------
    humidity_ratio : float
        Humidity ratio of the air provided in [kg water/kg dry air].
    air_temp : float
        Air temperature (dry_bulb). Must be supplied in [C] because unit 
        conversion will be performed later.
    total_pressure : float, optional
        Sum of partial pressures of dry air and water vaopr mixed with it to 
        make 1 kg. Must be in units of [Pa]. The default is 101325.

    Returns
    -------
    float
        Specific volume of air/water vapor mixture at a given ambient pressure.
        Answer given in units of [m^3/kg].

    """
    temp_K = air_temp + 273.15
    R_a = R_dry_air / total_pressure
    R_w = R_water_vapor / total_pressure

    return (R_a + R_w * humidity_ratio) * temp_K


def find_humidity_ratio_from_specific_vol_and_temp(specific_volume: float, air_temp: float,
                                                   total_pressure: float = 101325) -> float:
    """Function to find the humidity ratio of air/water vapor mixture.

    This function uses a derivation of the ideal gas law (PV=mRT) to solve for
    humidity ratio from specific volume.

    Parameters
    ----------
    specific_volume : float
        Specific volume of air/water vapor mixture at a given ambient pressure.
        Provided in units of [m^3/kg].
    air_temp : float
        Air temperature (dry_bulb). Must be supplied in [C] because unit
        conversion will be performed later.
    total_pressure : float, optional
        Sum of partial pressures of dry air and water vaopr mixed with it to
        make 1 kg. Must be in units of [Pa]. The default is 101325.

    Returns
    -------
    float
        Humidity ratio of the air in units of [kg water/kg dry air].
    """
    temp_K = air_temp + 273.15
    R_a = R_dry_air / total_pressure
    R_w = R_water_vapor / total_pressure

    return (specific_volume / temp_K - R_a) / R_w


def find_dry_bulb_temperature(enthalpy: float, humidity_ratio: float) -> float:
    """Function to find the dry bulb temperature.

    This function uses a rearranged version of the total enthalpy equation to
    find the dry bulb temperature of a psychrometric mix (not usually the
    case). Because the total enthalpy of the air at dry bulb temperature and
    actual humidity ratio is equal to the total enthalpy of the air at wet
    bulb temperature and saturated humidity ratio, the total enthalpy of the
    latter case can be calculated first and then used to find the dry bulb
    temperature given the known humidity ratio. Humidity ratio can be
    calculated in this script from any number of parameters which contain
    information about the moisture content of the air.

    Parameters
    ----------
    enthalpy : float
        Total enthalpy of the air/water vapor mix reported in [kJ/kg dry air].
    humidity_ratio : float
        Humidity ratio of the air provided in [kg water/kg dry air].

    Returns
    -------
    float
        Air temperature (dry bulb) provided in units of [C] referenced to
        0 C.
    """
    return (enthalpy - 2501.4 * humidity_ratio) / (1.005 + 1.88 * humidity_ratio)


def find_wet_bulb_temperature(enthalpy: float, air_temp: float, total_pressure: float = 101325) -> float:
    """Function to find the wet bulb temperature.
    
    This function uses the equation for total enthalpy solved for temperature.
    Then, the humidity ratio is given as the saturation humidity ratio for that
    dry bulb temperature. This means that the point you select from the chart
    has the same enthalpy as your air but is at 100% RH where temperature will
    be equal to wet bulb temperature (adiabatic saturation temperature). The 
    main assumption here is that the adiabatic saturation lines are parallel to
    wet bulb temperature lines, which is not exactly the case due to some
    error.

    Parameters
    ----------
    enthalpy : float
        Total enthalpy of the air/water vapor mix reported in [kJ/kg dry air].
    air_temp : float
        Dry bulb temperature of the air given in [C].
    total_pressure : float, optional
        Sum of partial pressures of dry air and water vaopr mixed with it to 
        make 1 kg. Must be in units of [Pa]. The default is 101325.

    Returns
    -------
    float
        Air temperature (wet bulb) provided in units of [C] referenced to
        0 C.

    """
    humidity_ratio_saturation = find_saturation_humidity_ratio(air_temp, p_total=total_pressure)
    return (enthalpy - 2501.4 * humidity_ratio_saturation) / (1.005 + 1.88 * humidity_ratio_saturation)


def find_dry_bulb_temperature_WB_enthalpy(wet_bulb_temp: float, enthalpy: float, total_pressure: float=101325, precision: int=5, trial_temp: float=50) -> float:
    saturation_vapor_pressure = total_pressure * 28.97 * (enthalpy - 1.005 * wet_bulb_temp) / (28.97 * (enthalpy - 1.005 * wet_bulb_temp) + 18.02 * (1.88 * wet_bulb_temp + 2501.4))
    return find_dew_point_temperature(saturation_vapor_pressure, precision, trial_temp)