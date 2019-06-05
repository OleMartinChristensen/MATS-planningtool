# -*- coding: utf-8 -*-
"""Schedules the active Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""

import importlib

from Operational_Planning_Tool import _Globals
from .Mode121_122_123 import date_calculator, date_select

OPT_Config_File = importlib.import_module(_Globals.Config_File)

def Mode122(Occupied_Timeline):
    """Core function for the scheduling of Mode121.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes with entries equal to their start and end time as a list.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    Settings = OPT_Config_File.Mode122_settings()
    
    date_magnitude_array = date_calculator(Settings)
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, date_magnitude_array, Settings)
    
    
    return Occupied_Timeline, comment