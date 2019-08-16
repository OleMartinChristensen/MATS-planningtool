# -*- coding: utf-8 -*-
"""Schedules Mode1-6 wherever time is available as defined by the *Occupied_Timeline* dictionary, and *Timeline_settings* from the *Configuration File*.

Part of Timeline_generator, as part of OPT. This part is run after the rest of the planned Modes have been scheduled. Result is saved in the Occupied_Timeline variable.

"""

import ephem, logging, importlib

from Operational_Planning_Tool import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def Mode_1_2_3_4_5_6(Occupied_Timeline):
    """Core function for the scheduling of Mode1-6.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes with entries equal to with their start and end time as a list.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    Mode_1_2_3_4_5_6initial_date = Mode_1_2_3_4_5_6date_calculator()
    
    Occupied_Timeline, Mode_1_2_3_4_5_6comment = Mode_1_2_3_4_5_6date_select(Occupied_Timeline, Mode_1_2_3_4_5_6initial_date)
    
    
    
    return Occupied_Timeline, Mode_1_2_3_4_5_6comment



############################################################################################



def Mode_1_2_3_4_5_6date_calculator():
    """Sets the earliest date possible for Mode1-6 to be scheduled.
    
    Returns:
        (ephem.Date): Mode_1_2_3_4_5_6initial_date
    
    """
    
    Mode_1_2_3_4_5_6initial_date = ephem.Date(OPT_Config_File.Timeline_settings()['start_date'])
        
    
    return Mode_1_2_3_4_5_6initial_date



############################################################################################



def Mode_1_2_3_4_5_6date_select(Occupied_Timeline, Mode_1_2_3_4_5_6initial_date):
    """Schedules Mode1-6 anywhere in the planned timeline (defined in Timeline_settings) depending on the Occupied_Timeline dictionary.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes together with their start and end time as a list. The list is empty if the Mode is unscheduled.
        Mode_1_2_3_4_5_6initial_date (ephem.Date): Earliest possible date for Mode1-6 to be scheduled.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    settings = OPT_Config_File.Timeline_settings()
    
    Occupied_values = []
    
    ## Extract all scheduled modes with actual occupied dates and sort them in chronological order. Skip the ones which are empty or entirely scheduled before Mode_1_2_3_4_5_6initial_date ##
    for Occupied_value in Occupied_Timeline.values():
        if( Occupied_value == [] ):
            continue
        
        for date in Occupied_value:
        
            if( date[0] < Mode_1_2_3_4_5_6initial_date and date[1] < Mode_1_2_3_4_5_6initial_date):
                continue
                
            else:
                Occupied_values.append(date)
    
    Occupied_values.sort()
    
    Mode_1_2_3_4_5_6dates = []
    
    "The least amount of time that needs to be available for mode1/2 to be scheduled"
    Mode_1_2_3_4_5_6minDuration = ephem.second*settings['Mode_1_2_3_4_5_6minDuration']
    iterations = 0
    
    ## To fill in modes inbetween already schedueled modes. The amount of iterations is equal to 
    ## the number of modes scheduled plus 1 as there is a possibility for the modes to be scheduled 
    ## at the start and end of the timeline.
    for x in range(len(Occupied_values)+1):
        
        ## For first iteration; Check if there is spacing between Mode_1_2_3_4_5_6initial_date and the the first mode running
        if( x == 0 and Occupied_values[0][0] != Mode_1_2_3_4_5_6initial_date):
            time_between_modes = Occupied_values[0][0] - Mode_1_2_3_4_5_6initial_date 
            if(time_between_modes > Mode_1_2_3_4_5_6minDuration ):
                Mode_1_2_3_4_5_6date = Mode_1_2_3_4_5_6initial_date
                
                Mode_1_2_3_4_5_6endDate = ephem.Date(Occupied_values[x][0] - ephem.second*settings['mode_separation'])
                Mode_1_2_3_4_5_6dates.append( (Mode_1_2_3_4_5_6date, Mode_1_2_3_4_5_6endDate) )
                iterations = iterations + 1
                
        ## For last iteration; Check if there is spacing in between end of the last mode and the end of the timeline
        elif( x == len(Occupied_values) ):
            timeline_end = ephem.Date( ephem.Date(settings['start_date'])+ephem.second*settings['duration'])
            time_between_modes = timeline_end - Occupied_values[-1][1] 
            if(time_between_modes > Mode_1_2_3_4_5_6minDuration ):
                Mode_1_2_3_4_5_6date = Occupied_values[-1][1]
                Mode_1_2_3_4_5_6endDate = ephem.Date(timeline_end - ephem.second*settings['mode_separation'])
                Mode_1_2_3_4_5_6dates.append( (Mode_1_2_3_4_5_6date, Mode_1_2_3_4_5_6endDate) )
                iterations = iterations + 1
                
        ## For all other iterations; Start filling in Mode_1_2_3_4_5_6dates inbetween currently schedueled modes
        elif( x != 0 and x != len(Occupied_values) ):
            time_between_modes = Occupied_values[x][0] - Occupied_values[x-1][1] 
            if(time_between_modes > Mode_1_2_3_4_5_6minDuration ):
                Mode_1_2_3_4_5_6date = Occupied_values[x-1][1]
                Mode_1_2_3_4_5_6endDate = ephem.Date(Occupied_values[x][0] - ephem.second*settings['mode_separation'])
                Mode_1_2_3_4_5_6dates.append( (Mode_1_2_3_4_5_6date, Mode_1_2_3_4_5_6endDate) )
                iterations = iterations + 1
                
            
    if( settings['Custom_Mode'] == True):
        if( settings['yaw_correction'] == True):
            Occupied_Timeline['Mode6'] = Mode_1_2_3_4_5_6dates
        elif( settings['yaw_correction'] == False):
            Occupied_Timeline['Mode5'] = Mode_1_2_3_4_5_6dates
            
    elif( ephem.Date(settings['start_date']).tuple()[1] in [11,12,1,2,5,6,7,8] or 
        ( ephem.Date(settings['start_date']).tuple()[1] in [3,9] and ephem.Date(settings['start_date']).tuple()[2] in range(11) )):
        
        #if( settings['Custom_Mode'] == True):
        #    Occupied_Timeline['Mode5'] = Mode_1_2_3_4_5_6dates
        if( settings['yaw_correction'] == True):
            Occupied_Timeline['Mode3'] = Mode_1_2_3_4_5_6dates
        elif(settings['yaw_correction'] == False):
            Occupied_Timeline['Mode1'] = Mode_1_2_3_4_5_6dates
            
    else:
        #if( settings['Custom_Mode'] == True):
        #    Occupied_Timeline['Mode6'] = Mode_1_2_3_4_5_6dates
        if( settings['yaw_correction'] == True):
            Occupied_Timeline['Mode4'] = Mode_1_2_3_4_5_6dates
        elif(settings['yaw_correction'] == False):
            Occupied_Timeline['Mode2'] = Mode_1_2_3_4_5_6dates
        
    Mode_1_2_3_4_5_6comment = 'Number of Modes inserted: ' + str(iterations)
    
    
    return Occupied_Timeline, Mode_1_2_3_4_5_6comment