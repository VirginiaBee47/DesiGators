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
    1 - https://www.caee.utexas.edu/prof/novoselac/classes/are383/handouts/f01_06si.pdf
"""

from math import exp

R_dry_air = 287.055 # [=] J/(kg * C)
R_water_vapor = 461.520 # [=] J/(kg * C)

def find_p_saturation(air_temp: float) -> float:
    """Function to find the saturation vapor pressure of water at a given temperature.

    Parameters
    ----------
    air_temp : float
        Temperature supplied must be in [C].

    Returns
    -------
    float
        Answer provided in units of [Pa].

    """
    return(exp(77.3450 + 0.0057 * (air_temp + 273.15) - 7235 / (air_temp + 273.15)) / (air_temp + 273.15) ** 8.2)


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
