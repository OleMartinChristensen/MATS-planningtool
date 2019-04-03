# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 15:00:40 2019

@author: David
"""

def Timeline_analyzer(science_mode_timeline_path, date):
    '''
    
    '''
    
    
    import ephem, json, os
    
    if(os.path.isfile(science_mode_timeline_path) == False):
        raise NameError('No such file exist...')
    else:
        
        ################# Read Science Mode Timeline json file ############
        with open(science_mode_timeline_path, "r") as read_file:
            Mode_Timeline = json.load(read_file)
        ################# Read Science Mode Timeline json file ############
        
        date = ephem.Date(date)
        
        for x in range(len(Mode_Timeline)):
            start_date = ephem.Date(Mode_Timeline[x][1])
            end_date = ephem.Date(Mode_Timeline[x][2])
            
            if( x != len(Mode_Timeline)-1 ):
                next_start_date = ephem.Date(Mode_Timeline[x+1][1])
            
            if( date >= start_date and (date < end_date or date < next_start_date) ):
                Mode = Mode_Timeline[x][0]
                Parameters = Mode_Timeline[x][3]
                break
            elif( x == len(Mode_Timeline)-1 ):
                raise ValueError('No mode scheduled during that date')
                
        return Mode, Parameters