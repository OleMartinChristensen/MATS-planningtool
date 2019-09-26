"""Schedules *Operational Science Modes* wherever time is available as defined by the *Occupied_Timeline* dictionary.

Part of *Timeline_gen*, as part of OPT. *Operational Science Modes* is always scheduled after the rest of the planned Modes have been scheduled. Result is saved in the Occupied_Timeline dictionary.

"""

import ephem, logging, importlib

from OPT import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def Mode1_2_5(Occupied_Timeline):
    """Core function for the scheduling of *Operational Science Modes* (Mode 1, 2, and 5).
    
    Which Mode that will be scheduled depends on *Timeline_settings['Choose_Operational_Science_Mode']*.
    These Modes, called *Operational Science Modes*, are always scheduled last, and wherever time is available. Only one *Operational Science Mode* is scheduled for each timeline.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list): Dictionary with keys equal to planned and scheduled Modes with entries equal to with their start and end time as a list of duples.
        
    Returns:
        (tuple): tuple containing:
            
            **Occupied_Timeline** (*dict*): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            **Comment** (*str*): Comment regarding the result of scheduling of the mode.
    
    """
    
    "Earliest possible date an Operational Science Mode is scheduled"
    initial_date = ephem.Date(OPT_Config_File.Timeline_settings()['start_date'])
    
    settings = OPT_Config_File.Timeline_settings()
    
    Occupied_values = []
    
    "Extract all scheduled modes with their scheduled dates and sort them in chronological order. Skip the ones which are empty or entirely scheduled before initial_date"
    for Occupied_value in Occupied_Timeline.values():
        if( Occupied_value == [] ):
            continue
        
        for date in Occupied_value:
        
            if( date[0] < initial_date and date[1] < initial_date):
                continue
                
            else:
                Occupied_values.append(date)
    
    Occupied_values.sort()
    
    dates = []
    
    "The least amount of time that needs to be available for mode1/2 to be scheduled"
    minDuration = ephem.second*settings['Mode1_2_5_minDuration']
    iterations = 0
    
    ## To fill in modes inbetween already schedueled modes. The amount of iterations is equal to 
    ## the number of modes scheduled plus 1 as there is a possibility for the modes to be scheduled 
    ## at the start and end of the timeline.
    for x in range(len(Occupied_values)+1):
        
        ## For first iteration; Check if there is spacing between initial_date and the the first mode running
        if( x == 0 and Occupied_values[0][0] != initial_date):
            time_between_modes = Occupied_values[0][0] - initial_date 
            if(time_between_modes > minDuration ):
                date = initial_date
                
                endDate = ephem.Date(Occupied_values[x][0] - ephem.second*settings['mode_separation'])
                dates.append( (date, endDate) )
                iterations = iterations + 1
                
        ## For last iteration; Check if there is spacing in between end of the last mode and the end of the timeline
        elif( x == len(Occupied_values) ):
            timeline_end = ephem.Date( ephem.Date(settings['start_date'])+ephem.second*settings['duration'])
            time_between_modes = timeline_end - Occupied_values[-1][1] 
            if(time_between_modes > minDuration ):
                date = Occupied_values[-1][1]
                endDate = ephem.Date(timeline_end - ephem.second*settings['mode_separation'])
                dates.append( (date, endDate) )
                iterations = iterations + 1
                
        ## For all other iterations; Start scheduling Mode1,2,5 inbetween already schedueled modes and CMDs
        elif( x != 0 and x != len(Occupied_values) ):
            time_between_modes = Occupied_values[x][0] - Occupied_values[x-1][1] 
            if(time_between_modes > minDuration ):
                date = Occupied_values[x-1][1]
                endDate = ephem.Date(Occupied_values[x][0] - ephem.second*settings['mode_separation'])
                dates.append( (date, endDate) )
                iterations = iterations + 1
                
    
    
    if( 'Mode1' in Occupied_Timeline ):
        Occupied_Timeline['Mode1'] = dates
    elif( 'Mode2' in Occupied_Timeline  ):
        Occupied_Timeline['Mode2'] = dates
    elif( 'Mode5' in Occupied_Timeline  ):
        Occupied_Timeline['Mode5'] = dates
        
    """
    if( settings['Choose_Operational_Science_Mode'] == 0 ):
        if( settings['Schedule_Mode5'] == True):
            Occupied_Timeline['Mode5'] = dates
            
        elif( ephem.Date(settings['start_date']).tuple()[1] in [11,12,1,2,5,6,7,8] or 
             ( ephem.Date(settings['start_date']).tuple()[1] in [3,9] and ephem.Date(settings['start_date']).tuple()[2] in range(11) )):
            
            Occupied_Timeline['Mode1'] = dates
            
        else:
            Occupied_Timeline['Mode2'] = dates
            
    elif( settings['Choose_Operational_Science_Mode'] == 1 ):
        Occupied_Timeline['Mode1'] = dates
    elif( settings['Choose_Operational_Science_Mode'] == 2 ):
        Occupied_Timeline['Mode2'] = dates
    elif( settings['Choose_Operational_Science_Mode'] == 5 ):
        Occupied_Timeline['Mode5'] = dates
    """
    comment = 'Number of Modes inserted: ' + str(iterations)
    
    
    return Occupied_Timeline, comment