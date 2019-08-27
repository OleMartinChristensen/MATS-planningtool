# -*- coding: utf-8 -*-
"""Schedules the active Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""

import ephem, sys, logging, importlib

from Operational_Planning_Tool._Library import scheduler
from Operational_Planning_Tool import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def Mode132(Occupied_Timeline):
    """Core function for the scheduling of Mode132.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes with entries equal to their start and end time as a list.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    initial_date = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, initial_date)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    """Subfunction, Returns the requested initial date for the Mode to be scheduled.
    
    Returns:
        (ephem.Date): initial_date
    
    """
    
    
    if( OPT_Config_File.Mode132_settings()['start_date'] != '0' ):
        initial_date = ephem.Date(OPT_Config_File.Mode132_settings()['start_date'])
        Logger.info('Mode specific start_date used as initial date')
    else:
        Logger.info('Timeline start_date used as initial date')
        initial_date = ephem.Date(OPT_Config_File.Timeline_settings()['start_date'])
    
    return initial_date



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, initial_date):
    """Subfunction, Checks if the requested initial date is available and post-pones it until available if occupied.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes together with their start and end time in a list. The list is empty if the Mode is unscheduled.
        initial_date (ephem.Date): The initially requested date for the Mode.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    
    settings = OPT_Config_File.Mode132_settings()
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    if( len(settings['Exp_Times_UV']) <= len(settings['Exp_Times_IR'])):
        duration = settings['session_duration']*len(settings['Exp_Times_UV'])+Timeline_settings['mode_separation']+Timeline_settings['pointing_stabilization']
    elif( len(settings['Exp_Times_IR']) < len(settings['Exp_Times_UV']) ):
        duration = settings['session_duration']*len(settings['Exp_Times_IR'])+Timeline_settings['mode_separation']+Timeline_settings['pointing_stabilization']
    
    date = initial_date
    endDate = ephem.Date(initial_date + ephem.second*duration)
    
    
    ############### Start of availability schedueler ##########################
    
    date, endDate, iterations = scheduler(Occupied_Timeline, date, endDate)
                
    ############### End of availability schedueler ##########################
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[Mode_name].append((date,endDate))
    
    return Occupied_Timeline, comment


