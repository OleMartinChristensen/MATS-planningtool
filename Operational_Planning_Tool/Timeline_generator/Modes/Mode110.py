# -*- coding: utf-8 -*-
"""Schedules the active Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""




import ephem, sys, logging

from Operational_Planning_Tool.Library import scheduler
from OPT_Config_File import Mode110_settings, Timeline_settings, Logger_name

Logger = logging.getLogger(Logger_name())


def Mode110(Occupied_Timeline):
    """Core function for the scheduling of Mode110.
    
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
    
    
    
    if( Mode110_settings()['start_time'] != ephem.Date('0') ):
        initial_date = Mode110_settings()['start_time']
        Logger.info('Mode specific start_time used as initial date')
    else:
        Logger.info('Timeline start_time used as initial date')
        initial_date = Timeline_settings()['start_time']
    
    return initial_date



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, initial_date):
    
    
    
    settings = Mode110_settings()
    
    date = initial_date
    
    duration = round(Timeline_settings()['pointing_stabilization'] + settings['sweep_start'] + round((settings['pointing_altitude_to'] - settings['pointing_altitude_from']) / settings['sweep_rate']) )
    
    endDate = ephem.Date(initial_date + ephem.second * (duration + Timeline_settings()['mode_separation']))
    
    
    ############### Start of availability schedueler ##########################
    
    date, endDate, iterations = scheduler(Occupied_Timeline, date, endDate)
                
    ############### End of availability schedueler ##########################
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[Mode_name] = (date,endDate)
    
    return Occupied_Timeline, comment
