# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 14:31:27 2018

Part of a program to automatically generate a mission timeline from parameters
defined in SCIMOD_DEFAULT_PARAMS. The timeline consists of
science modes and their start dates expressed as a list in chronological order

@author: David
"""


import ephem
from MATS_TIMELINE_SCIMOD_DEFAULT_PARAMS import Mode130_default, Timeline_params, Logger_name



def Mode130(Occupied_Timeline):
    
    Mode130_initial_date = Mode130_date_calculator(Occupied_Timeline)
    
    Occupied_Timeline, Mode130_comment = Mode130_date_select(Occupied_Timeline, Mode130_initial_date)
    
    
    
    return Occupied_Timeline, Mode130_comment
    


##################################################################################################
##################################################################################################



def Mode130_date_calculator(Occupied_Timeline):
    
    Mode130_initial_date = Timeline_params()['start_time']
    
    return Mode130_initial_date



##################################################################################################
##################################################################################################



def Mode130_date_select(Occupied_Timeline, Mode130_initial_date):
    
    
    Mode130_date = Mode130_initial_date
    Mode130_endDate = ephem.Date(Mode130_initial_date + ephem.second*Timeline_params()['mode_separation'] +
                                 ephem.second*Mode130_default()['mode_duration'])
    
    
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
                    
                    Mode130_date = ephem.Date(Mode130_date + ephem.second*Timeline_params()['mode_separation']*2)
                    Mode130_endDate = ephem.Date(Mode130_endDate + ephem.second*Timeline_params()['mode_separation']*2)
                    
                    iterations = iterations + 1
                    restart = True
                    break
                
    ############### End of availability schedueler ##########################
    
    Mode130_comment = 'Number of times date postponed: ' + str(iterations)
    
    
    
    Occupied_Timeline['Mode130'] = (Mode130_date,Mode130_endDate)
    
    return Occupied_Timeline, Mode130_comment
