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
import Operational_Planning_Tool.OPT_Timeline_generator_Modes.OPT_Timeline_generator_Modes_Header as OPT_Timeline_generator_Modes_Header
from OPT_Config_File import Timeline_settings, Modes_priority, Version, Logger_name
import OPT_Config_File

def Timeline_gen():
    """ HEEEEEY
    
        Arguments:
            dad:
    """
    
    
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
    
    Logger.info('OPT_Config_File version used: '+Version())
    
    "Get a List of Modes in a prioritized order which are to be scheduled"
    Modes_prio = Modes_priority()
    
    Logger.info('Modes priority list: '+str(Modes_prio))
    
    "Check if yaw_correction setting is set correct"
    if( Timeline_settings()['yaw_correction'] == 1):
        Logger.info('Yaw correction is on: Mode3/4 will be scheduled')
    elif( Timeline_settings()['yaw_correction'] == 0):
        Logger.info('Yaw correction is off: Mode1/2 will be scheduled')
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
    
    ################################################################################################################
    
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
        
        
        "Check if a date was scheduled"
        if( Occupied_Timeline[scimod] != [] ):
            
            "Check if the scheduled date is within the time defined for the timeline"
            if( Occupied_Timeline[scimod][0] < Timeline_settings()['start_time'] or 
                   Occupied_Timeline[scimod][1] - Occupied_Timeline[scimod][0] > Timeline_settings()['duration']):
                Logger.warning(scimod+' scheduled outside of timeline as defined in OPT_Config_File')
                input('Enter anything to acknowledge and continue\n')
            
            "Append mode and dates and comment to an unchronological Science Mode Timeline"
            SCIMOD_Timeline_unchronological.append((Occupied_Timeline[scimod][0], Occupied_Timeline[scimod][1],scimod, Mode_comment))
            Logger.info('Entry number '+str(len(SCIMOD_Timeline_unchronological))+' in unchronological Science Mode list: '+str(SCIMOD_Timeline_unchronological[-1]))
            Logger.info('')
        
        
        
    ################################################################################################################
    
    ################ To either fill out available time in the timeline with Mode1/2 or with Mode3/4 or neither ################
    Logger.info('Looping sequence of modes priority list complete')
    Logger.info('')
    
    yaw_correction = Timeline_settings()['yaw_correction']
    
    
    Logger.info('Mode 1/2/3/4 started')
    Logger.info('yaw_correction: '+str(yaw_correction))
    Logger.info('')
    
    Mode_1_2_3_4 = getattr(OPT_Timeline_generator_Modes_Header,'Mode_1_2_3_4')
    
    ### Check if it is NLC season ###
    if( Timeline_settings()['start_time'].tuple()[1] in [11,12,1,2,5,6,7,8] or 
            ( Timeline_settings()['start_time'].tuple()[1] in [3,9] and Timeline_settings()['start_time'].tuple()[2] in range(11) )):
        
        Logger.info('NLC season')
        
        if( yaw_correction == True ):
            mode = 'Mode3'
        elif( yaw_correction == False):
            mode = 'Mode1' 
        
        Occupied_Timeline.update({mode: []})
        
        Occupied_Timeline, Mode_comment = Mode_1_2_3_4(Occupied_Timeline)
        Logger.debug('')
        Logger.debug('Post-'+mode+' Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
        Logger.debug('')
        
        Logger.debug(mode+' getting added to unchronological timeline')
        for x in range(len(Occupied_Timeline[mode])):
            Logger.debug('Appended to timeline: '+str((Occupied_Timeline[mode][x][0], Occupied_Timeline[mode][x][1],mode, Mode_comment)))
            SCIMOD_Timeline_unchronological.append((Occupied_Timeline[mode][x][0], Occupied_Timeline[mode][x][1],mode, Mode_comment))
    else:
        
        Logger.info('Not NLC season')
        
        if( yaw_correction == True ):
            mode = 'Mode4'
        elif( yaw_correction == False):
            mode = 'Mode2' 
        
        
        Occupied_Timeline.update({mode: []})
        
        Occupied_Timeline, Mode_comment = Mode_1_2_3_4(Occupied_Timeline)
        Logger.debug('')
        Logger.debug('Post-'+mode+' Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
        Logger.debug('')
        
        Logger.info(mode+' getting added to unchronological timeline')
        for x in range(len(Occupied_Timeline[mode])):
            Logger.debug('Appended to timeline: '+str((Occupied_Timeline[mode][x][0], Occupied_Timeline[mode][x][1],mode, Mode_comment)))
            SCIMOD_Timeline_unchronological.append((Occupied_Timeline[mode][x][0], Occupied_Timeline[mode][x][1],mode, Mode_comment))
    
        
    '''
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
        
    '''
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
            Logger.error('Config function for '+x[2]+' for XML-gen in OPT_Config_File is misnamed or missing')
            sys.exit()
                
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
