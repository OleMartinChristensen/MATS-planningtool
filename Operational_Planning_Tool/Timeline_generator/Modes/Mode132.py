# -*- coding: utf-8 -*-
"""Schedules the active Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""

import ephem, sys, logging

from Operational_Planning_Tool.Library import scheduler
from OPT_Config_File import Mode132_settings, Timeline_settings, Logger_name

Logger = logging.getLogger(Logger_name())


def Mode132(Occupied_Timeline):
    """Core function for the scheduling of Mode132.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes with entries equal to their start and end time as a list.
        
    Returns:
        (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode).
        (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    initial_date = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, initial_date)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    
    
    
    if( Mode132_settings()['start_time'] != ephem.Date('0') ):
        initial_date = Mode132_settings()['start_time']
        Logger.info('Mode specific start_time used as initial date')
    else:
        Logger.info('Timeline start_time used as initial date')
        initial_date = Timeline_settings()['start_time']
    
    return initial_date



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, initial_date):
    
    
    
    settings = Mode132_settings()
    
    date = initial_date
    duration = settings['session_duration']*len(settings['ExpTimes'])+Timeline_settings()['mode_separation']
    endDate = ephem.Date(initial_date + ephem.second*duration)
    
    
    ############### Start of availability schedueler ##########################
    
    date, endDate, iterations = scheduler(Occupied_Timeline, date, endDate)
                
    ############### End of availability schedueler ##########################
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[Mode_name] = (date,endDate)
    
    return Occupied_Timeline, comment



'''
import ephem, sys
from OPT_Config_File import Mode130_settings, Timeline_settings, Logger_name



def Mode130(Occupied_Timeline):
    
    Mode130_initial_date = Mode130_date_calculator()
    
    Occupied_Timeline, Mode130_comment = Mode130_date_select(Occupied_Timeline, Mode130_initial_date)
    
    
    
    return Occupied_Timeline, Mode130_comment
    


##################################################################################################
##################################################################################################



def Mode130_date_calculator():
    
    Mode130_initial_date = Timeline_settings()['start_time']
    
    return Mode130_initial_date



##################################################################################################
##################################################################################################



def Mode130_date_select(Occupied_Timeline, Mode130_initial_date):
    
    
    Mode130_date = Mode130_initial_date
    Mode130_endDate = ephem.Date(Mode130_initial_date + ephem.second*Timeline_settings()['mode_separation'] +
                                 ephem.second*Mode130_settings()['mode_duration'])
    
    
    ############### Start of availability schedueler ##########################
    
    iterations = 0
    restart = True
    ## Checks if date is available and postpones starting date of mode until available
    while( restart == True):
        restart = False
        
        for busy_dates in Occupied_Timeline.values():
            if( busy_dates == []):
                continue
            else:
                if( busy_dates[0] <= Mode130_date < busy_dates[1] or 
                       busy_dates[0] < Mode130_endDate <= busy_dates[1]):
                    
                    Mode130_date = ephem.Date(Mode130_date + ephem.second*Timeline_settings()['mode_separation']*2)
                    Mode130_endDate = ephem.Date(Mode130_endDate + ephem.second*Timeline_settings()['mode_separation']*2)
                    
                    iterations = iterations + 1
                    restart = True
                    break
                
    ############### End of availability schedueler ##########################
    
    Mode130_comment = 'Number of times date postponed: ' + str(iterations)
    
    
    
    Occupied_Timeline['Mode130'] = (Mode130_date,Mode130_endDate)
    
    return Occupied_Timeline, Mode130_comment
'''