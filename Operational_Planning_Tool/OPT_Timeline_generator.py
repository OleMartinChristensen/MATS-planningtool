# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 14:57:28 2018

Part of a program to automatically generate a mission timeline from parameters
defined in OPT_Config_File. The timeline consists of
science modes together with their start/end dates, settings, and comments 
expressed as a list in chronological order.

Has a setable priority for the modes 
(except 1,2,3,4 which just fills out available time), 
which can be seen in the order of the modes in the list fetched from the 
function Modes_priority in the OPT_Config_File module. 
Modes either calculate appropriate dates (mode 120, 200..), or are 
planned at the timeline starting date. Every mode can also be planned at a user specified date
using the OPT_Config_File-

Depending on OPT_Config_File.Timeline_settings()['yaw_correction'], Mode1/2 or Mode3/4 is chosen, these modes will fill out time left available (mode 1,2,3,4).

If calculated starting dates for modes are occupied, they will be changed  
depending on a filtering process (mode 120, 200), or postponed until time is available (mode 130).

@author: David
"""

import json, logging, sys, time, os
from Operational_Planning_Tool.OPT_Timeline_generator_Modes.OPT_Timeline_generator_Mode_1_2 import Mode_1_2
'''
from OPT_Timeline_generator_Mode120 import Mode120
from OPT_Timeline_generator_Mode130 import Mode130
from OPT_Timeline_generator_Mode200 import Mode200
from OPT_Timeline_generator_Mode_User_Specified import Mode_User_Specified
'''
import Operational_Planning_Tool.OPT_Timeline_generator_Modes.OPT_Timeline_generator_Modes_Header as OPT_Timeline_generator_Modes_Header

from OPT_Config_File import Timeline_settings, Modes_priority, Version, Logger_name
import OPT_Config_File


def Timeline_gen():
#if __name__ == "__main__":
    
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    
    "Try to make a directory for logs if none is existing"
    try:
        os.mkdir('Logs_'+__name__)
    except:
        pass
    
    "Setup for Logger"
    Logger = logging.getLogger(Logger_name())
    timestr = time.strftime("%Y%m%d-%H%M%S")
    Handler = logging.FileHandler('Logs_'+__name__+'\\'+__name__+'_'+Version()+'_'+timestr+'.log', mode='a')
    formatter = logging.Formatter("%(levelname)-6s : %(message)-80s :: %(module)s :: %(funcName)s")
    Handler.setFormatter(formatter)
    Logger.addHandler(Handler)
    Logger.setLevel(logging.DEBUG)
    
    
    Logger.info('Start of program')
    
    Logger.info('Default_Params version used: '+Version())
    
    "Get a List of Modes in a prioritized order which are to be scheduled"
    Modes_prio = Modes_priority()
    
    Logger.info('Modes priority list: '+str(Modes_prio))
    
    "Check if yaw_correction setting is set correct"
    if( Timeline_settings()['yaw_correction'] == 1):
        Logger.info('Mode3/4 is to be scheduled')
    elif( Timeline_settings()['yaw_correction'] == 0):
        Logger.info('Mode1/2 is to be scheduled')
    else:
        Logger.error('OPT_Config_File.Timeline_settings()["yaw_correction"] is set wrong')
        sys.exit()
        
    
    
    SCIMOD_Timeline_unchronological = []
    
    Logger.info('Create "Occupied_Timeline" variable')
    Occupied_Timeline = {key:[] for key in Modes_prio}
    
    Logger.info('')
    Logger.info('Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
    Logger.info('')
    
    Logger.info('')
    Logger.info('Start of Loop through modes priority list')
    
    "Loop through the Modes to be ran and schedule each one in the priority order of which they appear in the list"
    for x in range(len(Modes_prio)):
        
        Logger.info('Iteration '+str(x+1)+' in Mode scheduling loop')
        
        scimod = Modes_prio[x]
        
        Logger.info('')
        Logger.info('Start of '+scimod)
        Logger.info('')
        
        "Call the function of the same name as the string in OPT_Config_File.Modes_priority"
        try:
            Mode_function = getattr(OPT_Timeline_generator_Modes_Header,scimod)
        except:
            Logger.error('Name of Mode in Modes_priority was not found in OPT_Timeline_generator_Modes_Header')
            sys.exit()
            
        Occupied_Timeline, Mode_comment = Mode_function(Occupied_Timeline)
        
        Logger.debug('')
        Logger.debug('Post-'+scimod+' Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
        Logger.debug('')
        
        if( Occupied_Timeline[scimod] != [] ):
            SCIMOD_Timeline_unchronological.append((Occupied_Timeline[scimod][0], Occupied_Timeline[scimod][1],scimod, Mode_comment))
            Logger.info('Entry number '+str(x+1)+' in unchronological Science Mode list: '+str(SCIMOD_Timeline_unchronological[x]))
            Logger.info('')
        
        '''
        if( 'Mode200' in scimod):
            
            Logger.info('')
            Logger.info('Start of '+scimod)
            Logger.info('')
            
            Occupied_Timeline, Mode_comment = Mode200(Occupied_Timeline)
            #Logger.debug('Post-Mode200 "Occupied_Timeline": '+str(Occupied_Timeline))
            
            Logger.debug('')
            Logger.debug('Post-'+scimod+' Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
            Logger.debug('')
            
            ################# Testing #############
            #Occupied_Timeline['Mode200'] = (ephem.Date(43364.03914351852), ephem.Date(43364.05303240741))
            #Occupied_Timeline['Mode1'] = (Timeline_settings()['start_time'], ephem.Date(Timeline_settings()['start_time']+ephem.second*3600))
            ################# Testing #############
            
            #if( Mode200_comment == 'Moon not visible' or Mode200_comment == 'No time available for Mode200'):
            if( Occupied_Timeline[scimod] != [] ):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline[scimod][0], Occupied_Timeline[scimod][1],scimod, Mode_comment))
                Logger.info('Entry number '+str(x+1)+' in unchronological Science Mode list: '+str(SCIMOD_Timeline_unchronological[x]))
                Logger.info('')
        
        if( 'Mode120' in scimod ):
            
            Logger.info('')
            Logger.info('Start of '+scimod)
            Logger.info('')
            
            Occupied_Timeline, Mode_comment = Mode120(Occupied_Timeline)
            
            Logger.debug('')
            Logger.debug('Post-'+scimod+' Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
            Logger.debug('')
            
            if( Occupied_Timeline[scimod] != [] ):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline[scimod][0], Occupied_Timeline[scimod][1],scimod, Mode_comment))
                Logger.info('Entry number '+str(x+1)+' in unchronological Science Mode list: '+str(SCIMOD_Timeline_unchronological[x]))
                Logger.info('')
            
            
        if( 'Mode130' in scimod):
            Logger.info('')
            Logger.info('Start of '+scimod)
            Logger.info('')
            
            Occupied_Timeline, Mode_comment = Mode130(Occupied_Timeline)
            
            Logger.debug('')
            Logger.debug('Post-'+scimod+' Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
            Logger.debug('')
            
            if( Occupied_Timeline[scimod] != [] ):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline[scimod][0], Occupied_Timeline[scimod][1],scimod, Mode_comment))
                Logger.info('Entry number '+str(x+1)+' in unchronological Science Mode list: '+str(SCIMOD_Timeline_unchronological[x]))
                Logger.info('')
            
        if( 'Mode_User_Specified' in scimod):
            Logger.info('')
            Logger.info('Start of '+scimod)
            Logger.info('')
            
            Occupied_Timeline, Mode_comment = Mode_User_Specified(Occupied_Timeline)
            
            Logger.debug('')
            Logger.debug('Post-'+scimod+' Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
            Logger.debug('')
            
            if( Occupied_Timeline[scimod] != [] ):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline[scimod][0], Occupied_Timeline[scimod][1],scimod, Mode_comment))
                Logger.info('Entry number '+str(x+1)+' in unchronological Science Mode list: '+str(SCIMOD_Timeline_unchronological[x]))
                Logger.info('')
        '''
        
    
    ################ To either fill out available time in the timeline with Mode1/2 or with Mode3/4 or neither ################
    Logger.info('Looping sequence of modes priority list complete')
    Logger.info('')
    
    Mode1_2_3_4_select = Timeline_settings()['yaw_correction']
    
    if( Mode1_2_3_4_select == 0):
        
        Logger.info('Mode 1/2 started')
        Logger.info('')
        
        ### Check if it is NLC season ###
        if( Timeline_settings()['start_time'].tuple()[1] in [11,12,1,2,5,6,7,8] or 
                ( Timeline_settings()['start_time'].tuple()[1] in [3,9] and Timeline_settings()['start_time'].tuple()[2] in range(11) )):
            
            Logger.info('NLC season')
            
            
            
            Occupied_Timeline.update({'Mode1': []})
            
            Occupied_Timeline, Mode1_comment = Mode_1_2(Occupied_Timeline)
            Logger.debug('')
            Logger.debug('Post-Mode1 Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
            Logger.debug('')
            
            Logger.debug('Add Mode1 to unchronological timeline')
            for x in range(len(Occupied_Timeline['Mode1'])):
                Logger.debug('Appended to timeline: '+str((Occupied_Timeline['Mode1'][x][0], Occupied_Timeline['Mode1'][x][1],'Mode1', Mode1_comment)))
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode1'][x][0], Occupied_Timeline['Mode1'][x][1],'Mode1', Mode1_comment))
        else:
            
            Logger.info('Not NLC season')
            
            Occupied_Timeline.update({'Mode2': []})
            Occupied_Timeline, Mode2_comment = Mode_1_2(Occupied_Timeline)
            Logger.debug('')
            Logger.debug('Post-Mode2 Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
            Logger.debug('')
            
            Logger.info('Add Mode2 to unchronological timeline')
            for x in range(len(Occupied_Timeline['Mode2'])):
                Logger.debug('Appended to timeline: '+str((Occupied_Timeline['Mode2'][x][0], Occupied_Timeline['Mode2'][x][1],'Mode2', Mode2_comment)))
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode2'][x][0], Occupied_Timeline['Mode2'][x][1],'Mode2', Mode2_comment))
        
        
        
    elif(Mode1_2_3_4_select == 1):
        
        Logger.info('Mode 3/4 clause entered')
        
        ### Check if it is NLC season ###
        if( Timeline_settings()['start_time'].tuple()[1] in [11,12,1,2,5,6,7,8] or 
                ( Timeline_settings()['start_time'].tuple()[1] in [3,9] and Timeline_settings()['start_time'].tuple()[2] in range(11) )):
            
            Logger.info('NLC season')
            
            Occupied_Timeline.update({'Mode3': []})
            Occupied_Timeline, Mode3_comment = Mode_3_4(Occupied_Timeline)
            Logger.debug('')
            Logger.debug('Post-Mode3 Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
            Logger.debug('')
            
            Logger.info('Add Mode3 to unchronological timeline')
            for x in range(len(Occupied_Timeline['Mode3'])):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode3'][x][0], Occupied_Timeline['Mode3'][x][1],'Mode3', Mode3_comment))
        else:
            
            Logger.info('Not NLC season')
            
            Occupied_Timeline.update({'Mode4': []})
            Occupied_Timeline, Mode4_comment = Mode_3_4(Occupied_Timeline)
            Logger.debug('')
            Logger.debug('Post-Mode4 Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
            Logger.debug('')
            
            Logger.info('Add Mode4 to unchronological timeline')
            for x in range(len(Occupied_Timeline['Mode4'])):
                SCIMOD_Timeline_unchronological.append((Occupied_Timeline['Mode4'][x][0], Occupied_Timeline['Mode4'][x][1],'Mode4', Mode4_comment))
        
    ################ END of To either fill out available time in the timeline with Mode1/2 or with Mode3/4 or neither ################
    
    
    
    SCIMOD_Timeline_unchronological.sort()
    
    Logger.info('')
    Logger.info('Unchronological timeline sorted')
    Logger.info('')
    
    SCIMOD_Timeline = []
    
    Logger.info("Create a science mode list in chronological order. The list contains Mode name, start date, enddate, params for XML-gen and comment")
    t=0
    "Create a science mode list in chronological order. The list contains Mode name, start date, enddate, params for XML-gen and comment"
    for x in SCIMOD_Timeline_unchronological:
        
        
        
        Logger.info(str(t+1)+' Timeline entry: '+str(x))
        
        
        Logger.info('Get the parameters for XML-gen from OPT_Config_File and add them to Science Mode timeline')
        try:
            Config_File = getattr(OPT_Config_File,x[2]+'_settings')
        except:
            Logger.error('Config function for '+x[2]+' for XML-gen in OPT_Config_File is misnamed')
            exit()
                
        #SCIMOD_Timeline.append([ x[2],str(x[0]), str(x[1]),{},x[3] ])
        
        SCIMOD_Timeline.append([ x[2],str(x[0]), str(x[1]),Config_File(),x[3] ])
        Logger.info(str(t+1)+' entry in Science Mode list: '+str(SCIMOD_Timeline[t]))
        Logger.info('')
        t= t+1
    
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
    
    Logger.info('Save mode timeline to file version: '+Version())
    
    try:
        os.mkdir('Output')
    except:
        pass
    
    SCIMOD_NAME = 'Output\\MATS_SCIMOD_TIMELINE_Version-'+Version()+'.json'
    with open(SCIMOD_NAME, "w") as write_file:
        json.dump(SCIMOD_Timeline, write_file, indent = 2)
    '''
    with open("MATS_SCIMOD_TIMELINE.json", "w") as write_file:
        json.dump(SCIMOD_Timeline, write_file, indent = 2)
    '''
