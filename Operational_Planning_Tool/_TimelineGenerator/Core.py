# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 14:57:28 2018



@author: David
"""

import json, logging, sys, time, os, ephem, importlib


from .Modes import Modes_Header
from OPT import _Globals, _Library

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())

def Timeline_generator():
    """The core function of the *Timeline_gen* program, part of Operational Planning Tool.
        
    Returns:
        None
        
    """
    
    ######## Try to Create a directory for storage of output files #######
    try:
        os.mkdir('Output')
    except:
        pass
    
    
    
    ############# Set up Logger #################################
    _Library.SetupLogger(OPT_Config_File.Logger_name())
    
    Logger.info('Start of program')
    
    Version = OPT_Config_File.Version()
    Logger.info('Configuration File used: '+_Globals.Config_File+', Version: '+Version)
    
    "Get a List of Modes and CMDs in a prioritized order which are to be scheduled"
    Scheduling_priority = OPT_Config_File.Scheduling_priority()
    Logger.info('Scheduling priority list: '+str(Scheduling_priority))
    
    "Get settings for the timeline"
    Timeline_settings = OPT_Config_File.Timeline_settings()
    _Globals.Timeline_settings = Timeline_settings
    Timeline_start_date = ephem.Date(Timeline_settings['start_date'])
    Logger.debug('Timeline_settings: '+str(Timeline_settings))
    
    "Check if yaw_correction setting is set correct"
    if( Timeline_settings['yaw_correction'] == True):
        Logger.info('Yaw correction is on')
    elif( Timeline_settings['yaw_correction'] == False):
        Logger.info('Yaw correction is off')
    else:
        Logger.error('OPT_Config_File.Timeline_settings["yaw_correction"] is set wrong')
        raise TypeError
        
    SCIMOD_Timeline_unchronological = []
    
    Logger.debug('Create "Occupied_Timeline" variable')
    Occupied_Timeline = {key:[] for key in Scheduling_priority}
    
    Logger.debug('')
    Logger.debug('Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
    Logger.debug('')
    
    Logger.info('')
    Logger.info('Start looping through modes priority list')
    
    
    
    ################################################################################################################
    
    "Loop through the Modes to be ran and schedule each one in the priority order of which they appear in the list"
    for x in range(len(Scheduling_priority)):
        
        Logger.info('')
        Logger.info('Iteration '+str(x+1)+' in Mode scheduling loop')
        
        scimod = Scheduling_priority[x]
        
        
        Logger.info('Start of '+scimod)
        Logger.info('')
        
        "Call the function of the same name as the string in Scheduling_priority"
        try:
            Mode_function = getattr(Modes_Header,scimod)
        except:
            Logger.error(scimod+' in Scheduling_priority was not found in Modes.Modes_Header')
            raise NameError
            
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
            Logger.debug('Entry number '+str(len(SCIMOD_Timeline_unchronological))+' in unchronological Science Mode list: '+str(SCIMOD_Timeline_unchronological[-1]))
            Logger.debug('')
        
    ################################################################################################################
    
    
    
    Logger.info('Looping sequence of modes priority list complete')
    Logger.info('')
    
    
    
    ##########################################################################################
    ########## Scheduling of operational science mode (Mode1,2 and possibly 5) ###################################
    
    
    Logger.info('Operational Science Mode scheduling')
    
    Mode1_2_5 = getattr(Modes_Header,'Mode1_2_5')
    
    
    if( Timeline_settings['Schedule_Mode5'] == True ):
        Logger.info("Timeline_settings['Schedule_Mode5'] == True")
        Logger.info('Schedule Mode5 as an operational science mode')
        
        mode = 'Mode5'
    ### Check if it is NLC season ###
    elif( Timeline_start_date.tuple()[1] in [11,12,1,2,5,6,7,8] or 
            ( Timeline_start_date.tuple()[1] in [3,9] and Timeline_start_date.tuple()[2] in range(11) )):
        
        Logger.info('NLC season (Mode1)')
        mode = 'Mode1' 
    else:
        
        Logger.info('Not NLC season (Mode2)')
        mode = 'Mode2'
            
        
    Occupied_Timeline.update({mode: []})
    
    Occupied_Timeline, Mode_comment = Mode1_2_5(Occupied_Timeline)
    Logger.debug('')
    Logger.debug('Post-'+mode+' Occupied_Timeline: \n'+"{" + "\n".join("        {}: {}".format(k, v) for k, v in Occupied_Timeline.items()) + "}")
    Logger.debug('')
    
    Logger.debug(mode+' getting added to unchronological timeline')
    for x in range(len(Occupied_Timeline[mode])):
        Logger.debug('Appended to timeline: '+str((Occupied_Timeline[mode][x][0], Occupied_Timeline[mode][x][1],mode, Mode_comment)))
        SCIMOD_Timeline_unchronological.append((Occupied_Timeline[mode][x][0], Occupied_Timeline[mode][x][1],mode, Mode_comment))
        
    
    ###########################################################################################
    ###########################################################################################
    
    
    #############################################################################################
    ################# Sort Planned Modes and create a Science Mode Timeline List ################
    
    SCIMOD_Timeline_unchronological.sort()
    Logger.debug('')
    Logger.debug('Unchronological timeline sorted')
    Logger.debug('')
    
    SCIMOD_Timeline = []
    SCIMOD_Timeline.append([ 'Timeline_settings','This Timeline was created using these settings from '+_Globals.Config_File,
                            'Note: These Timeline_settings and TLE will be used when converting into a XML', 
                            Timeline_settings, OPT_Config_File.getTLE()])
    
    Logger.debug("Create a science mode list in chronological order. The list contains Mode name, start date, enddate, params for XML-gen and comment")
    t=0
    "Create a science mode list in chronological order. The list contains Mode name, start date, enddate, params for XML-gen and comment"
    for x in SCIMOD_Timeline_unchronological:
        
        Logger.debug(str(t+1)+' Timeline entry: '+str(x))
        
        
        Logger.debug('Get the parameters for XML-gen from OPT_Config_File and add them to Science Mode timeline')
        try:
            Config_File = getattr(OPT_Config_File,x[2]+'_settings')()
        except AttributeError:
            
            if(  x[2] == 'Mode1' or x[2] == 'Mode2' or x[2] == 'Mode5' ):
                
                Config_File = getattr(OPT_Config_File,'Operational_Science_Mode_settings')()
                
            else:
                    Logger.error('No Config function for '+x[2])
                    Config_File = []
                    
            
                
        #SCIMOD_Timeline.append([ x[2],str(x[0]), str(x[1]),{},x[3] ])
        
        SCIMOD_Timeline.append([ x[2],str(x[0]), str(x[1]),Config_File,x[3] ])
        Logger.debug(str(t+1)+' entry in Science Mode list: '+str(SCIMOD_Timeline[t]))
        Logger.debug('')
        t= t+1
    
    ###########################################################################################
    
    
    
    
    try:
        os.mkdir('Output')
    except:
        pass
    SCIMOD_NAME = os.path.join('Output', 'Science_Mode_Timeline__'+_Globals.Config_File+'.json')
    Logger.info('Save mode timeline to file: '+SCIMOD_NAME)
    with open(SCIMOD_NAME, "w") as write_file:
        json.dump(SCIMOD_Timeline, write_file, indent = 2)
    