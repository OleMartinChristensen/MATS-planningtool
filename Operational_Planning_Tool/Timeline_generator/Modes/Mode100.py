# -*- coding: utf-8 -*-
"""Schedules the Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""

import ephem, sys, logging

from OPT_Config_File import Timeline_settings, Logger_name, Mode100_settings
from Operational_Planning_Tool.Library import scheduler

Logger = logging.getLogger(Logger_name())


def Mode100(Occupied_Timeline):
    """Core function for the scheduling of Mode100.
    
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
    """Subfunction, Returns the initially requested date (defined in Config_File.py) for the Mode to be scheduled.
    
    Returns:
        (ephem.Date): initial_date
    
    """
    
    
    if( Mode100_settings()['start_time'] != ephem.Date('0') ):
        initial_date = Mode100_settings()['start_time']
        Logger.info('Mode specific start_time used as initial date')
    else:
        Logger.info('Timeline start_time used as initial date')
        initial_date = Timeline_settings()['start_time']
    
    return initial_date



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, initial_date):
    """Subfunction, Checks if the initially requested date is available and post-pones it until available if occupied.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes together with their start and end time in a list. The list is empty if the Mode is unscheduled.
        initial_date (ephem.Date): The initially requested date for the Mode.
        
    Returns:
        (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode).
        (str): Comment regarding the result of the scheduling of the Mode.
    
    """
    
    
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
