# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 15:11:05 2018

Part of a program to automatically generate a mission timeline from parameters
defined in SCIMOD_DEFAULT_PARAMS. The timeline consists of
science modes and their start/end dates expressed as a list in chronological order

@author: David
"""

import ephem
from MATS_TIMELINE_SCIMOD_DEFAULT_PARAMS import Timeline_params, Logger_name

def Mode_1_2(Occupied_Timeline):
    
    Mode_1_2_initial_date = Mode_1_2_date_calculator(Occupied_Timeline)
    
    Occupied_Timeline, Mode_1_2_comment = Mode_1_2_date_select(Occupied_Timeline, Mode_1_2_initial_date)
    
    
    
    return Occupied_Timeline, Mode_1_2_comment



############################################################################################



def Mode_1_2_date_calculator(Occupied_Timeline):
    
    
    Mode_1_2_initial_date = Timeline_params()['start_time']
        
    
    return Mode_1_2_initial_date



############################################################################################



def Mode_1_2_date_select(Occupied_Timeline, Mode_1_2_initial_date):
#if(True):
    
    Occupied_values = []
    
    ## Extract all occupied dates and sort them in chronological order ##
    for Occupied_value in Occupied_Timeline.values():
        if( Occupied_value == []):
            continue
        else:
            Occupied_values.append(Occupied_value)
    Occupied_values.sort()
    
    
    Mode_1_2_dates = []
    
    Mode_1_2_minDuration = ephem.second*Timeline_params()['mode_separation']*2
    iterations = 0
    
    ## To fill in mode1 inbetween already schedueled modes
    for x in range(len(Occupied_values)):
        
        ## Check first if there is spacing between Mode_1_2_initial_date and the the first mode running
        if( x == 0 and Occupied_values[0][0] != Mode_1_2_initial_date):
            time_between_modes = Occupied_values[0][0] - Mode_1_2_initial_date 
            if(time_between_modes > Mode_1_2_minDuration ):
                Mode_1_2_date = Occupied_value[x][1]
                Mode_1_2_endDate = ephem.Date(Occupied_values[x+1][0] - ephem.second*Timeline_params()['mode_separation'])
                Mode_1_2_dates.append( (Mode_1_2_date, Mode_1_2_endDate) )
                iterations = iterations + 1
                
        ## For last, check if there is spacing in between end of the last mode and the end of the timeline
        elif( x == len(Occupied_values)-1 ):
            timeline_end = ephem.Date(Timeline_params()['start_time']+ephem.second*Timeline_params()['duration'])
            time_between_modes = timeline_end - Occupied_values[x][1] 
            if(time_between_modes > Mode_1_2_minDuration ):
                Mode_1_2_date = Occupied_values[x][1]
                Mode_1_2_endDate = ephem.Date(timeline_end - ephem.second*Timeline_params()['mode_separation'])
                Mode_1_2_dates.append( (Mode_1_2_date, Mode_1_2_endDate) )
                iterations = iterations + 1
                
        ## If there is no spacing, start filling in Mode_1_2_dates inbetween currently schedueled modes
        else:
            time_between_modes = Occupied_values[x+1][0] - Occupied_values[x][1] 
            if(time_between_modes > Mode_1_2_minDuration ):
                Mode_1_2_date = Occupied_values[x][1]
                Mode_1_2_endDate = ephem.Date(Occupied_values[x+1][0] - ephem.second*Timeline_params()['mode_separation'])
                Mode_1_2_dates.append( (Mode_1_2_date, Mode_1_2_endDate) )
                iterations = iterations + 1
                
            
    if( Timeline_params()['start_time'].tuple()[1] in [11,12,1,2,5,6,7,8] or 
        ( Timeline_params()['start_time'].tuple()[1] in [3,9] and Timeline_params()['start_time'].tuple()[2] in range(11) )):
        
        Occupied_Timeline['Mode1'] = Mode_1_2_dates
    else:
        Occupied_Timeline['Mode2'] = Mode_1_2_dates
        
    Mode_1_2_comment = 'Number of Modes inserted: ' + str(iterations)
    
    
    return Occupied_Timeline, Mode_1_2_comment