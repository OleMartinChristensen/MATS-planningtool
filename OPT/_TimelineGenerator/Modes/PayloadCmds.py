# -*- coding: utf-8 -*-
"""Schedules the PayloadCMDs at the start of the timeline and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes with entries equal to their start and end time as a list.
        
    Returns:
        (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode).
        (str): Comment regarding the result of scheduling of the mode.
    
"""

import logging, sys, importlib
import ephem

from OPT._Library import scheduler
from OPT import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def CMD_scheduler(Occupied_Timeline):
    
    Logger.info('Timeline start_time used as initial date')
    initial_date = ephem.Date(OPT_Config_File.Timeline_settings()['start_date'])
    duration = OPT_Config_File.Timeline_settings()['CMD_duration']
    endDate = ephem.Date(initial_date + ephem.second*(OPT_Config_File.Timeline_settings()['mode_separation'] + duration) )
    
    ############### Start of availability schedueler ##########################
    
    date, endDate, iterations = scheduler(Occupied_Timeline, initial_date, endDate)
                
    ############### End of availability schedueler ##########################
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the function, which is defined as the name of the CMD"
    CMD_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[CMD_name].append((date,endDate))
    
    return Occupied_Timeline, comment


def PWRTOGGLE(Occupied_Timeline):
    
    Occupied_Timeline, comment = CMD_scheduler(Occupied_Timeline)
    
    return Occupied_Timeline, comment

    
def CCDBadColumn(Occupied_Timeline):
    
    Occupied_Timeline, comment = CMD_scheduler(Occupied_Timeline)
    
    return Occupied_Timeline, comment
    
def CCDFlushBadColumns(Occupied_Timeline):
    
    Occupied_Timeline, comment = CMD_scheduler(Occupied_Timeline)
    
    return Occupied_Timeline, comment


def PM(Occupied_Timeline):
    
    Occupied_Timeline, comment = CMD_scheduler(Occupied_Timeline)
    
    return Occupied_Timeline, comment
    

def CCDBIAS(Occupied_Timeline):
    
    Occupied_Timeline, comment = CMD_scheduler(Occupied_Timeline)
    
    return Occupied_Timeline, comment
    

"""
def HTR(Occupied_Timeline):
    
    Occupied_Timeline, comment = CMD_scheduler(Occupied_Timeline)
    
    return Occupied_Timeline, comment
"""