# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 10:35:32 2019

Template for a new Mode where 'X' is exchanged for the number or name of the mode. 
The Mode is scheduled at the start of the timeline as defined in OPT_Config_File.Timeline_settings

@author: David
"""


import ephem, sys, logging

from Operational_Planning_Tool._Library import scheduler
from OPT_Config_File import Timeline_settings, Logger_name

Logger = logging.getLogger(Logger_name())


def ModeX(Occupied_Timeline):
    
    initial_date = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, initial_date)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    
    
    
    if( ModeX_settings()['start_date'] != '0' ):
        initial_date = ephem.Date(ModeX_settings()['start_date'])
        Logger.info('Mode specific start_date used as initial date')
    else:
        Logger.info('Timeline start_date used as initial date')
        initial_date = ephem.Date(Timeline_settings()['start_date'])
    
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
    
    Occupied_Timeline[Mode_name].append((date,endDate))
    
    return Occupied_Timeline, comment
