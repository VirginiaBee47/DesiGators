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

R_dry_air = 287.055 # [=] J/(kg * C)
R_water_vapor = 461.520 # [=] J/(kg * C)

psychrometric_properties = {'dry_bulb_temperature' : None,
                            'wet_bulb_temperature' : None,
                            'dew_point_temperature' : None,
                            'total_pressure' : None,
                            'humidity_ratio' : None,
                            'relative_humidity' : None,
                            'total_enthalpy' : None,
                            'partial_pressure_vapor' : None,
                            'specific_volume' : None}


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
                
        self.point_defined = self.check_defined()
        
        try:
            self.define_point()
        except PointNotDefinedException:
            print("Point could not be defined automatically. Input more information and then try again. Continuing...")
            
            
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
                                  self.specific_volume]
        
        if self.total_pressure is not None:
            criterion_1 = True
            
        if sum(x is not None for x in criterion_2_properties) >= 2:
            criterion_2 = True
            
        return criterion_1 and criterion_2
    
    
    def define_point(self) -> None:
        if not self.point_defined:
            raise PointNotDefinedException
        
        # Case 1: Dry Bulb and Wet Bulb Temps known
        if self.dry_bulb_temperature is not None and self.wet_bulb_temperature is not None:
            self.total_enthalpy = find_total_enthalpy(self.wet_bulb_temperature, find_saturation_humidity_ratio(self.wet_bulb_temperature, p_total=self.total_pressure))
            self.humidity_ratio = find_humidity_ratio_from_enthalpy_db(self.dry_bulb_temperature, self.total_enthalpy)
            self.partial_pressure_vapor = find_p_water_vapor_from_humidity_ratio(self.humidity_ratio, self.total_pressure)
            self.relative_humidity = find_relative_humidity(self.partial_pressure_vapor, self.dry_bulb_temperature)
            self.dew_point_temperature = find_dew_point_temperature(self.partial_pressure_vapor)
            
            
            

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
    return(exp(34.494 - (4924.99 / (air_temp + 237.1))) / (air_temp + 105) ** 1.57)


def find_humidity_ratio(p_vapor: float, p_total: float=101325) -> float:
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
    return(18.02 / 28.97 * p_vapor / (p_total - p_vapor))


def find_saturation_humidity_ratio(air_temp: float, p_total: float=101325) -> float:
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
    return(find_humidity_ratio(find_p_saturation(air_temp), p_total))


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
    return((1.005 + 1.88 * humidity_ratio) * air_temp + 2501.4 * humidity_ratio)


def find_humidity_ratio_from_RH_temp(relative_humidity: float, air_temp: float, p_total: float=101325) -> float:
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
        raise ValueError('The value passed for relative humidity (%f) is outside the accepted range [0,1].' % relative_humidity)
    
    p_vapor_calculated = relative_humidity * find_p_saturation(air_temp)
    return(find_humidity_ratio(p_vapor_calculated, p_total))


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
    return((enthalpy - 1.005 * air_temp) / (1.88 * air_temp + 2501.4))


def find_p_water_vapor_from_humidity_ratio(humidity_ratio: float, p_total: float=101325) -> float:
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
    return(28.97 * humidity_ratio * p_total / (18.02 + 28.97 * humidity_ratio))


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
    return None
    

def find_dew_point_temperature(p_vapor: float, precision: int=5, trial_temp: float=50) -> float:
    t_next = t_dew_point_step(trial_temp, p_vapor)
    
    while abs(t_next - trial_temp) > 10 ** (-1 * precision):
        print(str(t_next))
        trial_temp = t_next
        t_next = t_dew_point_step(trial_temp, p_vapor)
        
    return trial_temp


def t_dew_point_step(t_prev: float, p_vapor: float) -> float:
    difference_squared = (find_p_saturation(t_prev) - p_vapor) ** 2
    gradient = ((9849.88 * exp(68.998 - 9849.88/(t_prev + 237.1)) * (t_prev + 105) ** 3.14)/(t_prev + 237.1) ** 2 - 3.14 * exp(68.998 - 9849.88/(t_prev + 237.1)) * (t_prev + 105) ** 2.14)/(t_prev + 105) ** 6.28 - 2 * p_vapor * ((4924.99 * exp(34.494 - 4924.99/(t_prev + 237.1)) * (t_prev + 105) ** 1.57)/(t_prev + 237.1) ** 2 - 1.57 * exp(34.494 - 4924.99/(t_prev + 237.1)) * (t_prev + 105) ** 0.57)/(t_prev + 105) ** 3.14
    return (t_prev - difference_squared / gradient)