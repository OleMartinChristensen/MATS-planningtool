# -*- coding: utf-8 -*-
"""Schedules the active Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""


import ephem, sys, logging, importlib

from Operational_Planning_Tool._Library import scheduler
from Operational_Planning_Tool import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def Mode201(Occupied_Timeline):
    
    initial_date = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, initial_date)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    
    
    
    if( Mode201_settings()['start_date'] != '0' ):
        initial_date = ephem.Date(Mode201_settings()['start_date'])
        Logger.info('Mode specific start_date used as initial date')
    else:
        Logger.info('Timeline start_date used as initial date')
        initial_date = ephem.Date(OPT_Config_File.Timeline_settings()['start_date'])
    
    return initial_date



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, initial_date):
    
    
    
    date = initial_date
    
    try:
        Logger.info('Mode specific mode_duration used as initial date')
        endDate = ephem.Date(initial_date + ephem.second*OPT_Config_File.Timeline_settings()['mode_separation'] + 
                             ephem.second*Mode201_settings()['mode_duration'])
    except:
        Logger.info('Timeline mode_duration used as initial date')
        endDate = ephem.Date(initial_date + ephem.second*OPT_Config_File.Timeline_settings()['mode_separation'] +
                             ephem.second*OPT_Config_File.Timeline_settings()['mode_duration'])
    
    ############### Start of availability schedueler ##########################
    
    date, endDate, iterations = scheduler(Occupied_Timeline, date, endDate)
                
    ############### End of availability schedueler ##########################
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[Mode_name].append((date,endDate))
    
    return Occupied_Timeline, comment
