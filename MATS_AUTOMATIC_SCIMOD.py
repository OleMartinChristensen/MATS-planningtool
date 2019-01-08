# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 14:57:28 2018

Part of a program to automatically generate a mission timeline from parameters
defined in MATS_TIMELINE_SCIMOD_DEFAULT_PARAMS. The timeline consists of
science modes together with their start/end dates and comments 
expressed as a list in chronological order.

Main function to be called by user. Has a setable priority for the modes 
(except 1,2,3,4 which just fills out available time), 
which can be seen in the order of the modes in the list fetched from the 
function Modes_priority in the DEFAULT_PARAMS module. 
Modes either calculate appropriate dates (mode 120, 200..), or are 
planned at the timeline starting date.

Depending on if Mode1/2 or Mode3/4 is chosen, these modes will fill out time left available (mode 1,2,3,4).

If calculated starting dates for modes are occupied, they will be changed to either 
the next best (mode 120, 121), or postponed until time is available (mode 130).

@author: David
"""

import json
import logging
from MATS_AUTOMATIC_SCIMOD_Mode_1_2 import Mode_1_2
from MATS_AUTOMATIC_SCIMOD_Mode120 import Mode120
from MATS_AUTOMATIC_SCIMOD_Mode130 import Mode130
from MATS_AUTOMATIC_SCIMOD_Mode200 import Mode200
from MATS_TIMELINE_SCIMOD_DEFAULT_PARAMS import Timeline_params, Modes_priority


#def MATS_Automatic_SCIMOD():
if __name__ == "__main__":
    
    
    
    Logger = logging.getLogger(__name__)
    Handler = logging.FileHandler('MATS_AUTOMATIC_SCIMOD_LOG.log', mode='w')
    Logger.addHandler(Handler)
    Logger.setLevel(logging.INFO)
    
    
    Logger.warning('2')
    
    Modes_prio = Modes_priority()
    
    SCIMOD_Timeline_unchronological = []
    
    Occupied_Timeline = {key:[] for key in Modes_prio}
    
    
    "Loop through the Modes to be ran and schedule each one in the priority order of which they appear in the list"
    for x in range(len(Modes_prio)):
        
        scimod = Modes_prio[x]
        
        if( 'Mode200' in scimod):
            
            Occupied_Timeline, Mode200_comment = Mode200(Occupied_Timeline)
            #Occupied_Timeline['Mode200'] = (ephem.Date(43364.03914351852), ephem.Date(43364.05303240741))
            #Occupied_Timeline['Mode1'] = (Timeline_params()['start_time'], ephem.Date(Timeline_params()['start_time']+ephem.second*3600))
            
            if( Mode200_comment == 'Moon not visible' or Mode200_comment == 'No time available for Mode200'):
                print(Mode200_comment)
            else:
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode200'][0], Occupied_Timeline['Mode200'][1],'Mode200', Mode200_comment))
            
        
        if( 'Mode120' in scimod ):
            Occupied_Timeline, Mode120_comment = Mode120(Occupied_Timeline)
            
            if( Mode120_comment == 'Stars not visible' or Mode120_comment == 'No time available for Mode120'):
                print(Mode120_comment)
            else:
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode120'][0], Occupied_Timeline['Mode120'][1],'Mode120', Mode120_comment))
            
        if( 'Mode130' in scimod):
            Occupied_Timeline, Mode130_comment = Mode130(Occupied_Timeline)
            
            SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode130'][0], Occupied_Timeline['Mode130'][1],'Mode130', Mode130_comment))
            
        #if():
        
        
        
    ################ To either fill out available time in the timeline with Mode1/2 or with Mode3/4 or neither ################
    
    while(True):
        Mode1_2_3_4_select = input('Do you want to use Mode1/2 (input 1 or 2) or Mode3/4 (input 3 or 4)? Type 0 for none: ')
        if( Mode1_2_3_4_select != '1' and Mode1_2_3_4_select != '2' and Mode1_2_3_4_select != '3' and Mode1_2_3_4_select != '4' and Mode1_2_3_4_select != '0' ):
            print('Wrong input, please try again')
        else:
            break
    
    
    if( Mode1_2_3_4_select == '1' or Mode1_2_3_4_select == '2'):
        
        ### Check if it is NLC season ###
        if( Timeline_params()['start_time'].tuple()[1] in [11,12,1,2,5,6,7,8] or 
                ( Timeline_params()['start_time'].tuple()[1] in [3,9] and Timeline_params()['start_time'].tuple()[2] in range(11) )):
            
            Occupied_Timeline.update({'Mode1': []})
            Occupied_Timeline, Mode1_comment = Mode_1_2(Occupied_Timeline)
            
            for x in range(len(Occupied_Timeline['Mode1'])):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode1'][x][0], Occupied_Timeline['Mode1'][x][1],'Mode1', Mode1_comment))
        else:
            
            Occupied_Timeline.update({'Mode2': []})
            Occupied_Timeline, Mode2_comment = Mode_1_2(Occupied_Timeline)
            
            for x in range(len(Occupied_Timeline['Mode2'])):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode2'][x][0], Occupied_Timeline['Mode2'][x][1],'Mode2', Mode2_comment))
        
    elif(Mode1_2_3_4_select == '3' or Mode1_2_3_4_select == '4'):
        
        ### Check if it is NLC season ###
        if( Timeline_params()['start_time'].tuple()[1] in [11,12,1,2,5,6,7,8] or 
                ( Timeline_params()['start_time'].tuple()[1] in [3,9] and Timeline_params()['start_time'].tuple()[2] in range(11) )):
            
            Occupied_Timeline.update({'Mode3': []})
            Occupied_Timeline, Mode3_comment = Mode_3_4(Occupied_Timeline)
            
            for x in range(len(Occupied_Timeline['Mode3'])):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode3'][x][0], Occupied_Timeline['Mode3'][x][1],'Mode3', Mode3_comment))
        else:
            
            Occupied_Timeline.update({'Mode4': []})
            Occupied_Timeline, Mode4_comment = Mode_3_4(Occupied_Timeline)
            
            for x in range(len(Occupied_Timeline['Mode4'])):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode4'][x][0], Occupied_Timeline['Mode4'][x][1],'Mode4', Mode4_comment))
        
    ################ END of To either fill out available time in the timeline with Mode1/2 or with Mode3/4 or neither ################
    
    
    SCIMOD_Timeline_unchronological.sort()
    SCIMOD_Timeline = []
    "Create a science mode list in chronological order. The list contains Mode name, start date, enddate, empty optional params and comment"
    for x in SCIMOD_Timeline_unchronological:
        SCIMOD_Timeline.append([ x[2],str(x[0]), str(x[1]),{},x[3] ])
    
    '''
    date1 = '2018/8/23 22:00:00'
    date2 = '2018/8/24 10:30:00'
    date3 = '2018/8/24 14:30:00'
    date4 = '2018/8/24 16:30:00'
    date5 = '2018/8/24 18:30:00'
    date6 = '2018/8/24 21:30:00'
    
    
    SCIMOD_Timeline.append(['Mode200',str(Mode200_date),{},Mode200_comment])
    SCIMOD_Timeline.append(['Mode120',str(Mode120_date),{},'Star: '+Mode120_comment[:-1]])
    '''
    '''
    #SCIMOD_Timeline.append(['Mode130',Mode130_date,{}])
    SCIMOD_Timeline.append(['Mode1',date1,date2,{'lat': 30}])
    SCIMOD_Timeline.append(['Mode1',date2,date3,{}])
    SCIMOD_Timeline.append(['Mode2',date3,date4,{'pointing_altitude': 93000}])
    SCIMOD_Timeline.append(['Mode120',date4,date5,{'pointing_altitude': 93000, 'freeze_duration': 500}])
    SCIMOD_Timeline.append(['Mode120',date5,date6,{'freeze_start': 35}])
    '''
            
    with open("MATS_SCIMOD_TIMELINE.json", "w") as write_file:
        json.dump(SCIMOD_Timeline, write_file, indent = 2)
        
