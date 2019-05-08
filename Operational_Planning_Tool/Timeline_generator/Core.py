# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 14:57:28 2018

The Timeline_generator part of the Operational_Planning_Tool which purpose is to automatically generate a
mission timeline from settings defined in the OPT_Config_File. The timeline consists of
science modes together with their planned start/end dates, settings, and comments 
expressed as a list in chronological order. 

Timeline_generator has a setable priority for the scheduling of modes, 
which can be seen in the order of the modes in the list fetched from the 
function Modes_priority in the Config_File module.

For each mode, one at a time, an appropriate date is calculated, or the
a predetermined date is already set in the Config_File. A dictionary (Occupied_Timeline) keeps track of the planned runtime of all Modes, 
this to prevent colliding scheduling. 

Depending on Config_File.Timeline_settings()['yaw_correction'], Mode1/2 or Mode3/4 is chosen, 
these modes will fill out time left available after the scheduling of the rest of the modes, 
set in Config_File.Modes_priority.

If calculated starting dates for modes are occupied, they will be changed  
depending on a specialized filtering process (mode 120, 200...), or postponed until time is available (mode 130, 131...).

@author: David
"""

import json, logging, sys, time, os, ephem
from .Modes import Modes_Header
import OPT_Config_File

Logger = logging.getLogger(OPT_Config_File.Logger_name())

def Timeline_generator():
    """The core function of the Timeline_gen program.
        
    Returns:
        None
        
    """
    
    
    
    
    "Try to make a directory for logs if none is existing"
    try:
        os.mkdir('Logs_'+__name__)
    except:
        pass
    
    ######## Try to Create a directory for storage of output files #######
    try:
        os.mkdir('Output')
    except:
        pass
    
    ############# Set up Logger #################################
    
    "Remove all previous handlers of the logger"
    for handler in Logger.handlers[:]:
        Logger.removeHandler(handler)
    
    #logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    Handler = logging.FileHandler('Logs_'+__name__+'\\'+__name__+'_'+OPT_Config_File.Version()+'_'+timestr+'.log', mode='a')
    formatter = logging.Formatter("%(levelname)-6s : %(message)-80s :: %(module)s :: %(funcName)s")
    Handler.setFormatter(formatter)
    Logger.addHandler(Handler)
    Logger.setLevel(logging.DEBUG)
    
    
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.WARNING)
    streamHandler.setFormatter(formatter)
    Logger.addHandler(streamHandler)
    
    
    ############# Set up Logger #################################
    
    Logger.info('Start of program')
    
    Version = OPT_Config_File.Version()
    Logger.info('OPT_Config_File version used: '+Version)
    
    "Get a List of Modes in a prioritized order which are to be scheduled"
    Modes_priority = OPT_Config_File.Modes_priority()
    Logger.info('Modes priority list: '+str(Modes_priority))
    
    "Get settings for the timeline"
    Timeline_settings = OPT_Config_File.Timeline_settings()
    Timeline_start_date = ephem.Date(Timeline_settings['start_date'])
    Logger.info('Timeline_settings: '+str(Timeline_settings))
    
    "Check if yaw_correction setting is set correct"
    if( Timeline_settings['yaw_correction'] == 1):
        Logger.info('Yaw correction is on: Mode3/4 will be scheduled')
    elif( Timeline_settings['yaw_correction'] == 0):
        Logger.info('Yaw correction is off: Mode1/2 will be scheduled')
    else:
        Logger.error('OPT_Config_File.Timeline_settings["yaw_correction"] is set wrong')
        sys.exit()
        
    SCIMOD_Timeline_unchronological = []
    
    Logger.info('Create "Occupied_Timeline" variable')
    Occupied_Timeline = {key:[] for key in Modes_priority}
    
    Logger.info('')
    Logger.info('Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
    Logger.info('')
    
    Logger.info('')
    Logger.info('Start looping through modes priority list')
    
    
    
    ################################################################################################################
    
    "Loop through the Modes to be ran and schedule each one in the priority order of which they appear in the list"
    for x in range(len(Modes_priority)):
        
        Logger.info('Iteration '+str(x+1)+' in Mode scheduling loop')
        
        scimod = Modes_priority[x]
        
        Logger.info('')
        Logger.info('Start of '+scimod)
        Logger.info('')
        
        "Call the function of the same name as the string in OPT_Config_File.Modes_priority"
        try:
            Mode_function = getattr(Modes_Header,scimod)
        except:
            Logger.error(scimod+' in Modes_priority was not found in OPT_Timeline_generator_Modes_Header')
            sys.exit()
            
        Occupied_Timeline, Mode_comment = Mode_function(Occupied_Timeline)
        
        Logger.debug('')
        Logger.debug('Post-'+scimod+' Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
        Logger.debug('')
        
        
        "Check if a date was scheduled"
        if( Occupied_Timeline[scimod] != [] ):
            
            scheduled_instances = len(Occupied_Timeline[scimod])
            
            "Check if the scheduled date is within the time defined for the timeline"
            if( Occupied_Timeline[scimod][scheduled_instances-1][0] < Timeline_start_date or 
                   Occupied_Timeline[scimod][scheduled_instances-1][0] > (Timeline_start_date+ephem.second*Timeline_settings['duration']) or
                   Occupied_Timeline[scimod][scheduled_instances-1][1] - Occupied_Timeline[scimod][scheduled_instances-1][0] > Timeline_settings['duration']):
                Logger.warning(scimod+' scheduled outside of timeline as defined in OPT_Config_File')
                
                #input('Enter anything to acknowledge and continue\n')
            
            "Append mode and dates and comment to an unchronological Science Mode Timeline"
            SCIMOD_Timeline_unchronological.append((Occupied_Timeline[scimod][scheduled_instances-1][0], Occupied_Timeline[scimod][scheduled_instances-1][1],scimod, Mode_comment))
            Logger.info('Entry number '+str(len(SCIMOD_Timeline_unchronological))+' in unchronological Science Mode list: '+str(SCIMOD_Timeline_unchronological[-1]))
            Logger.info('')
        
    ################################################################################################################
    
    
    
    Logger.info('Looping sequence of modes priority list complete')
    Logger.info('')
    
    
    
    ##########################################################################################
    ################################ Scheduling of Mode1-4 ###################################
    
    yaw_correction = Timeline_settings['yaw_correction']
    Logger.info('Mode 1/2/3/4 started')
    Logger.info('yaw_correction: '+str(yaw_correction))
    Logger.info('')
    
    Mode_1_2_3_4 = getattr(Modes_Header,'Mode_1_2_3_4')
    
    ### Check if it is NLC season ###
    if( Timeline_start_date.tuple()[1] in [11,12,1,2,5,6,7,8] or 
            ( Timeline_start_date.tuple()[1] in [3,9] and Timeline_start_date.tuple()[2] in range(11) )):
        
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
    
    ###########################################################################################
    ###########################################################################################
    
    
    #############################################################################################
    ################# Sort Planned Modes and create a Science Mode Timeline List ################
    
    SCIMOD_Timeline_unchronological.sort()
    Logger.info('')
    Logger.info('Unchronological timeline sorted')
    Logger.info('')
    
    SCIMOD_Timeline = []
    SCIMOD_Timeline.append([ 'Timeline_settings','This Timeline was created using these settings', Timeline_settings, 'Note: These settings are not actually used when generating an XML, the ones in OPT_Config_File are' ])
    
    Logger.info("Create a science mode list in chronological order. The list contains Mode name, start date, enddate, params for XML-gen and comment")
    t=0
    "Create a science mode list in chronological order. The list contains Mode name, start date, enddate, params for XML-gen and comment"
    for x in SCIMOD_Timeline_unchronological:
        
        Logger.info(str(t+1)+' Timeline entry: '+str(x))
        
        
        Logger.info('Get the parameters for XML-gen from OPT_Config_File and add them to Science Mode timeline')
        try:
            Config_File = getattr(OPT_Config_File,x[2]+'_settings')()
        except:
            Logger.warning('No Config function for '+x[2])
            Config_File = []
            
                
        #SCIMOD_Timeline.append([ x[2],str(x[0]), str(x[1]),{},x[3] ])
        
        SCIMOD_Timeline.append([ x[2],str(x[0]), str(x[1]),Config_File,x[3] ])
        Logger.info(str(t+1)+' entry in Science Mode list: '+str(SCIMOD_Timeline[t]))
        Logger.info('')
        t= t+1
    
    ###########################################################################################
    
    
    
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
    
    
    
    Logger.info('Save mode timeline to file version: '+Version)
    
    
    try:
        os.mkdir('Output')
    except:
        pass
    
    SCIMOD_NAME = 'Output\\Science_Mode_Timeline_Version_'+Version+'.json'
    print('Save mode timeline to file: '+SCIMOD_NAME)
    with open(SCIMOD_NAME, "w") as write_file:
        json.dump(SCIMOD_Timeline, write_file, indent = 2)
    