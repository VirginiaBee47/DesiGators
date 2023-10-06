# -*- coding: utf-8 -*-
"""
Title: Exceptions
Author: Virginia Covert
Co-Authors: Alexander Weaver, Korynn Haetten, Stanley Moonjeli

Description: 
    New exception definitions relevant to the project.

Sponsor: Dr. Andrew MacIntosh
Coach: Dr. Philip Jackson
"""

class PointNotDefinedException(Exception):
    """Exception raised for lack of information to fully define point on psychrometric chart.
    
    Parameters
    ----------
    message : str
        Message to be printed to the console regarding the exception.
    """
    def __init__(self, message="Not enough information provided to fully define the point."):
        self.message = message
        super().__init__(self.message)
    