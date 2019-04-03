# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 15:39:18 2019

@author: David
"""

import ephem, sys, logging
from OPT_Config_File import Timeline_settings, Logger_name, Mode100_settings



def Mode100(Occupied_Timeline):
    
    initial_date = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, initial_date)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    
    Logger = logging.getLogger(Logger_name())
    
    try:
        initial_date = Mode100_settings()['start_time']
        Logger.info('Mode specific start_time used as initial date')
    except:
        Logger.warning('!!Error raised in try statement!!')
        Logger.info('Timeline start_time used as initial date')
        initial_date = Timeline_settings()['start_time']
    
    return initial_date



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, initial_date):
    
    from Operational_Planning_Tool.OPT_library import scheduler
    
    settings = Mode100_settings()
    
    date = initial_date
    
    number_of_altitudes = round( (settings['pointing_altitude_to'] - settings['pointing_altitude_from']) / settings['pointing_altitude_interval'] + 1 )
    
    duration = (settings['pointing_duration'] + Timeline_settings()['pointing_stabilization']) * number_of_altitudes
    
    endDate = ephem.Date(initial_date + ephem.second*(Timeline_settings()['mode_separation'] + duration) )
    
    '''
    try:
        Logger.info('Mode specific mode_duration used as initial date')
        endDate = ephem.Date(initial_date + ephem.second*Timeline_settings()['mode_separation'] +
                             ephem.second*Mode100_settings()['mode_duration'])
    except:
        Logger.info('Timeline mode_duration used as initial date')
        endDate = ephem.Date(initial_date + ephem.second*Timeline_settings()['mode_separation'] +
                             ephem.second*Timeline_settings()['mode_duration'])
    '''
    
    ############### Start of availability schedueler ##########################
    
    date, endDate, iterations = scheduler(Occupied_Timeline, date, endDate)
                
    ############### End of availability schedueler ##########################
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[Mode_name] = (date,endDate)
    
    return Occupied_Timeline, comment
