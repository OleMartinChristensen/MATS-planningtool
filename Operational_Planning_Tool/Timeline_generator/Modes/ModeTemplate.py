# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 10:35:32 2019

Template for a new Mode where 'X' is exchanged for the number or name of the mode. 
The Mode is scheduled at the start of the timeline as defined in OPT_Config_File.Timeline_settings

@author: David
"""


import ephem, sys, logging

from Operational_Planning_Tool.Library import scheduler
from OPT_Config_File import Timeline_settings, Logger_name

Logger = logging.getLogger(Logger_name())


def ModeX(Occupied_Timeline):
    
    initial_date = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, initial_date)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    
    
    
    try:
        initial_date = ModeX_settings()['start_time']
        Logger.info('Mode specific start_time used as initial date')
    except:
        Logger.warning('!!Error raised in try statement!! Could not use Mode specific start_time; Timeline start_time used as initial date')
        initial_date = Timeline_settings()['start_time']
    
    return initial_date



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, initial_date):
    
    
    
    date = initial_date
    
    try:
        Logger.info('Mode specific mode_duration used as initial date')
        endDate = ephem.Date(initial_date + ephem.second*Timeline_settings()['mode_separation'] +
                             ephem.second*ModeX_settings()['mode_duration'])
    except:
        Logger.info('Timeline mode_duration used as initial date')
        endDate = ephem.Date(initial_date + ephem.second*Timeline_settings()['mode_separation'] +
                             ephem.second*Timeline_settings()['mode_duration'])
    
    ############### Start of availability schedueler ##########################
    
    date, endDate, iterations = scheduler(Occupied_Timeline, date, endDate)
                
    ############### End of availability schedueler ##########################
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[Mode_name] = (date,endDate)
    
    return Occupied_Timeline, comment
