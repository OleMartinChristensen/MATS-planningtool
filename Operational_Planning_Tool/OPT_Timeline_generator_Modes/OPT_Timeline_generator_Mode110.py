# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 16:41:14 2019

@author: David
"""




import ephem, sys, logging
from OPT_Config_File import Mode110_settings, Timeline_settings, Logger_name




def Mode110(Occupied_Timeline):
    
    initial_date = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, initial_date)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    
    Logger = logging.getLogger(Logger_name())
    
    try:
        initial_date = Mode110_settings()['start_time']
        Logger.info('Mode start_time used as initial date')
    except:
        Logger.warning('!!Error raised in try statement!!')
        Logger.info('Timeline start_time used as initial date')
        initial_date = Timeline_settings()['start_time']
    
    return initial_date



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, initial_date):
    
    from Operational_Planning_Tool.OPT_library import scheduler
    
    date = initial_date
    endDate = ephem.Date(initial_date + ephem.second*Timeline_settings()['mode_separation'] +
                                 ephem.second*Mode110_settings()['mode_duration'])
    
    
    ############### Start of availability schedueler ##########################
    
    date, endDate, iterations = scheduler(Occupied_Timeline, date, endDate)
                
    ############### End of availability schedueler ##########################
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[Mode_name] = (date,endDate)
    
    return Occupied_Timeline, comment
