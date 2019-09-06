# -*- coding: utf-8 -*-
"""Schedules the Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""

import ephem, sys, logging, importlib

from Operational_Planning_Tool._Library import scheduler
from Operational_Planning_Tool import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def Mode100(Occupied_Timeline):
    """Core function for the scheduling of Mode100.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes with entries equal to their start and end time as a list.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    initialDate, endDate = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, initialDate, endDate)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    """Subfunction, Returns the requested initial date and a end for the Mode to be scheduled.
    
    Returns:
        (tuple): tuple containing:
            (ephem.Date): initialDate
            (ephem.Date): endDate
    
    """
    
    Timeline_settings = OPT_Config_File.Timeline_settings()
    Settings = OPT_Config_File.Mode100_settings()
    
    if( Settings['start_date'] != '0' ):
        initialDate = ephem.Date(Settings['start_date'])
        Logger.info('Mode specific start_date used as initial date')
    else:
        Logger.info('Timeline start_date used as initial date')
        initialDate = ephem.Date(Timeline_settings['start_date'])
    
    number_of_CMDs = 6
    number_of_altitudes = int( (Settings['pointing_altitude_to'] - Settings['pointing_altitude_from']) / Settings['pointing_altitude_interval'] + 1 )
    
    duration = (Settings['pointing_duration'] + Timeline_settings['pointing_stabilization'] + number_of_CMDs) * number_of_altitudes
    
    endDate = ephem.Date(initialDate + ephem.second*(Timeline_settings['mode_separation'] + duration) )
    
    
    return initialDate, endDate



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, initialDate, endDate):
    """Subfunction, Checks if the requested initial date is available and post-pones it until available if occupied.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes together with their start and end time in a list. The list is empty if the Mode is unscheduled.
        initialDate (ephem.Date): The initially requested date for the Mode.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    
    
    ############### Start of availability schedueler ##########################
    
    date, endDate, iterations = scheduler(Occupied_Timeline, initialDate, endDate)
                
    ############### End of availability schedueler ##########################
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[Mode_name].append((date,endDate))
    
    return Occupied_Timeline, comment
