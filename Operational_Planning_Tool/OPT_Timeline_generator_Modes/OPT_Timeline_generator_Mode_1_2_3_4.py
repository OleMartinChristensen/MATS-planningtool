# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 15:11:05 2018

Part of a program to automatically generate a mission timeline from parameters
defined in SCIMOD_DEFAULT_PARAMS. The timeline consists of
science modes and their start/end dates expressed as a list in chronological order

@author: David
"""

import ephem
from OPT_Config_File import Timeline_settings, Logger_name

def Mode_1_2_3_4(Occupied_Timeline):
    
    Mode_1_2_3_4initial_date = Mode_1_2_3_4date_calculator()
    
    Occupied_Timeline, Mode_1_2_3_4comment = Mode_1_2_3_4date_select(Occupied_Timeline, Mode_1_2_3_4initial_date)
    
    
    
    return Occupied_Timeline, Mode_1_2_3_4comment



############################################################################################



def Mode_1_2_3_4date_calculator():
    
    
    Mode_1_2_3_4initial_date = Timeline_settings()['start_time']
        
    
    return Mode_1_2_3_4initial_date



############################################################################################



def Mode_1_2_3_4date_select(Occupied_Timeline, Mode_1_2_3_4initial_date):
#if(True):
    
    settings = Timeline_settings()
    
    Occupied_values = []
    
    ## Extract all scheduled modes with actual occupied dates and sort them in chronological order. Skip the ones which are empty or entirely scheduled before Mode_1_2_3_4initial_date ##
    for Occupied_value in Occupied_Timeline.values():
        if( Occupied_value == [] ):
            continue
        elif( Occupied_value[0] < Mode_1_2_3_4initial_date and Occupied_value[1] < Mode_1_2_3_4initial_date):
            continue
        else:
            Occupied_values.append(Occupied_value)
    Occupied_values.sort()
    
    
    Mode_1_2_3_4dates = []
    
    "The least amount of time that needs to be available for mode1/2 to be scheduled"
    Mode_1_2_3_4minDuration = ephem.second*settings['mode_separation']*2
    iterations = 0
    
    ## To fill in mode1/2 inbetween already schedueled modes. The amount of iterations is equal to 
    ## the number of modes scheduled plus 1 as there is a possibility for mode1/2 to be scheduled 
    ## before and after the already scheduled modes
    for x in range(len(Occupied_values)+1):
        
        ## For first iteration; Check if there is spacing between Mode_1_2_3_4initial_date and the the first mode running
        if( x == 0 and Occupied_values[0][0] != Mode_1_2_3_4initial_date):
            time_between_modes = Occupied_values[0][0] - Mode_1_2_3_4initial_date 
            if(time_between_modes > Mode_1_2_3_4minDuration ):
                Mode_1_2_3_4date = Mode_1_2_3_4initial_date
                
                #Mode_1_2_3_4date = Occupied_values[x][1]
                Mode_1_2_3_4endDate = ephem.Date(Occupied_values[x][0] - ephem.second*settings['mode_separation'])
                Mode_1_2_3_4dates.append( (Mode_1_2_3_4date, Mode_1_2_3_4endDate) )
                iterations = iterations + 1
                
        ## For last iteration; Check if there is spacing in between end of the last mode and the end of the timeline
        elif( x == len(Occupied_values) ):
            timeline_end = ephem.Date(settings['start_time']+ephem.second*settings['duration'])
            time_between_modes = timeline_end - Occupied_values[-1][1] 
            if(time_between_modes > Mode_1_2_3_4minDuration ):
                Mode_1_2_3_4date = Occupied_values[-1][1]
                Mode_1_2_3_4endDate = ephem.Date(timeline_end - ephem.second*settings['mode_separation'])
                Mode_1_2_3_4dates.append( (Mode_1_2_3_4date, Mode_1_2_3_4endDate) )
                iterations = iterations + 1
                
        ## For all other iterations; Start filling in Mode_1_2_3_4dates inbetween currently schedueled modes
        elif( x != 0 and x != len(Occupied_values) ):
            time_between_modes = Occupied_values[x][0] - Occupied_values[x-1][1] 
            if(time_between_modes > Mode_1_2_3_4minDuration ):
                Mode_1_2_3_4date = Occupied_values[x-1][1]
                Mode_1_2_3_4endDate = ephem.Date(Occupied_values[x][0] - ephem.second*settings['mode_separation'])
                Mode_1_2_3_4dates.append( (Mode_1_2_3_4date, Mode_1_2_3_4endDate) )
                iterations = iterations + 1
                
            
    if( settings['start_time'].tuple()[1] in [11,12,1,2,5,6,7,8] or 
        ( settings['start_time'].tuple()[1] in [3,9] and settings['start_time'].tuple()[2] in range(11) )):
        
        if( settings['yaw_correction'] == True):
            Occupied_Timeline['Mode3'] = Mode_1_2_3_4dates
        elif(settings['yaw_correction'] == False):
            Occupied_Timeline['Mode1'] = Mode_1_2_3_4dates
            
    else:
        if( settings['yaw_correction'] == True):
            Occupied_Timeline['Mode4'] = Mode_1_2_3_4dates
        elif(settings['yaw_correction'] == False):
            Occupied_Timeline['Mode2'] = Mode_1_2_3_4dates
        
    Mode_1_2_3_4comment = 'Number of Modes inserted: ' + str(iterations)
    
    
    return Occupied_Timeline, Mode_1_2_3_4comment