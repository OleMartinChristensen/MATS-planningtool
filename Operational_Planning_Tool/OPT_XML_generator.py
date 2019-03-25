# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 15:43:21 2018

Creates the base of the XML-tree and calculates initial values such as the 
start and end time and also duration of the timeline. Then goes through the 
supplied Science Mode Timeline List chronologically and calls for the corresponding function.



@author: David
"""

from lxml import etree
from OPT_Config_File import Timeline_settings, initialConditions, Logger_name, Version

import ephem, logging, sys, time, os, json


def XML_generator(SCIMOD_Path):
    
    
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    
    try:
        os.mkdir('Logs_'+__name__)
    except:
        pass
    
    
    Logger = logging.getLogger(Logger_name())
    timestr = time.strftime("%Y%m%d-%H%M%S")
    Handler = logging.FileHandler('Logs_'+__name__+'\\'+__name__+'_'+Version()+'_'+timestr+'.log', mode='a')
    formatter = logging.Formatter("%(levelname)6s : %(message)-80s :: %(module)s :: %(funcName)s")
    Handler.setFormatter(formatter)
    Logger.addHandler(Handler)
    Logger.setLevel(logging.DEBUG)
    
    Logger.info('Start of Program')
    Logger.info('')
    Logger.info('OPT_Config_File version used: '+Version())
    Logger.info('')
    
    with open(SCIMOD_Path, "r") as read_file:
        SCIMOD= json.load(read_file)
    
    timeline_duration = Timeline_settings()['duration']
    Logger.info('timeline_duration: '+str(timeline_duration))
    
    timeline_start = Timeline_settings()['start_time']
    Logger.info('timeline_start: '+str(timeline_start))
    
    #earliestStartingDate = str(ephem.Date(timeline_start-ephem.second)).replace(' ','T')
    #latestStartingDate = str(timeline_start).replace(' ','T')
    
    earliestStartingDate = ephem.Date(timeline_start-ephem.second).datetime().strftime("%Y-%m-%dT%H:%M:%S")
    latestStartingDate = ephem.Date(timeline_start).datetime().strftime("%Y-%m-%dT%H:%M:%S")
    
    Logger.debug('earliestStartingDate: '+str(earliestStartingDate))
    Logger.debug('latestStartingDate: '+str(latestStartingDate))
    Logger.info('')
    
    #earliestStartingDate = earliestStartingDate.replace('/','-')
    #latestStartingDate = latestStartingDate.replace('/','-')
    
    
    ########    Call function to create XML-tree basis ##########################
    Logger.info('Call function XML_Initial_Basis_Creator')
    Logger.info('')
    root = XML_Initial_Basis_Creator(earliestStartingDate,latestStartingDate,timeline_duration, SCIMOD_Path)
    
    ######## Loop through SCIMOD TIMELINE lIST, selecting one mode at a time #####
    Logger.info('Loop through Science Mode Timeline List')
    
    for x in range(len(SCIMOD)):
        Logger.info('')
        Logger.info('Iteration number: '+str(x+1))
        
        Logger.info(str(SCIMOD[x][0]))
        Logger.info('Start Date: '+str(SCIMOD[x][1]))
        Logger.info('End Date: '+str(SCIMOD[x][2]))
        
        mode_duration = int((ephem.Date(SCIMOD[x][2]) - ephem.Date(SCIMOD[x][1]) ) *24*3600)
        relativeTime = int((ephem.Date(SCIMOD[x][1])-ephem.Date(timeline_start))*24*3600)
        Logger.info('mode_duration: '+str(mode_duration))
        Logger.info('relativeTime: '+str(relativeTime))
        
        if( relativeTime >= timeline_duration ):
            Logger.warning('relativeTime is exceeding timeline_duration!!!')
            warning = input('Enter anything to continue or enter 1 to stop\n')
            if( warning == '1'):
                sys.exit()
                
        if( ephem.Date(SCIMOD[x][1]) < timeline_start or mode_duration+relativeTime > timeline_duration):
            Logger.warning('Mode: '+str(SCIMOD[x][0])+', is not scheduled within the boundaries of the timeline!!!')
            warning = input('Enter anything to continue or enter 1 to stop\n')
            if( warning == '1'):
                sys.exit()
        
        Logger.info('Call XML_generator_select')
        XML_generator_select(root=root, duration=mode_duration, relativeTime=relativeTime, mode=SCIMOD[x][0], date=ephem.Date(SCIMOD[x][1]), params=SCIMOD[x][3])
        
    #print(etree.tostring(root, pretty_print=True, encoding = 'unicode'))
    
    ### Write finished XML-tree to a file ###
    try:
        os.mkdir('Output')
    except:
        pass
    
    "Rewrite path string to allow it to be in the name of the generated XML command file"
    SCIMOD_Path = SCIMOD_Path.replace('/','_in_')
    SCIMOD_Path = SCIMOD_Path.replace('.json','')
    
    MATS_COMMANDS = 'Output\\MATS_COMMANDS_'+Version()+'__'+SCIMOD_Path+'.xml'
    Logger.info('Write XML-tree to: '+MATS_COMMANDS)
    f = open(MATS_COMMANDS, 'w')
    f.write(etree.tostring(root, pretty_print=True, encoding = 'unicode'))
    f.close()



################### XML-tree basis creator ####################################

def XML_Initial_Basis_Creator(earliestStartingDate,latestStartingDate,timeline_duration, SCIMOD_Path):
    '''Construct Basis of XML document and adds the description container.
    Input: 
        earliestStartingDate: Earliest Starting date of the Timeline. On the form of the ephem.Date class.
        latestStartingDate: Latest Starting date of the Timeline. On the form of the ephem.Date class.
        timeline_duration: Duration of the timeline [s] as a integer class.
        SCIMOD_Path: The path as a string to the Science Mode Timeline .json file used in this run.
    '''
    
    
    
    root = etree.Element('InnoSatTimeline', originator='OHB', sdbVersion='9.5.99.2')
    
    
    root.append(etree.Element('description'))
    
    
    etree.SubElement(root[0], 'timelineID', procedureIdentifier = "", descriptiveName = "", version = "1.0")
    
    etree.SubElement(root[0], 'changeLog')
    etree.SubElement(root[0][1], 'changeLogItem', version = "1.1", date = "2019-01-17", author = "David Skånberg")
    root[0][1][0].text = "Created Document"
    
    
    etree.SubElement(root[0], 'initialConditions')
    etree.SubElement(root[0][2], 'spacecraft', mode = initialConditions()['spacecraft']['mode'], acs = initialConditions()['spacecraft']['acs'])
    etree.SubElement(root[0][2], 'payload', power = initialConditions()['payload']['power'], mode = initialConditions()['payload']['mode'])
    
    
    etree.SubElement(root[0], 'validity')
    etree.SubElement(root[0][3], 'earliestStartingDate')
    root[0][3][0].text = earliestStartingDate
    etree.SubElement(root[0][3], 'latestStartingDate')
    root[0][3][1].text = latestStartingDate
    etree.SubElement(root[0][3], 'scenarioDuration')
    root[0][3][2].text = str(timeline_duration)
    
    etree.SubElement(root[0], 'comment')
    root[0][4].text = "This command sequence is an Innosat timeline \nScience Mode Timeline used to generate: "+SCIMOD_Path
    
    
    root.append(etree.Element('listOfCommands'))
    
    return root
    
####################### End of XML-tree basis creator #############################

'''
####################### Mode selecter #############################

def XML_generator_select(root,duration,relativeTime,mode,date,params):
    "Selects corresponding function from received science mode"
    
    from Operational_Planning_Tool.OPT_XML_generator_MODES import XML_generator_Mode1, XML_generator_Mode2, XML_generator_Mode120, XML_generator_Mode130, XML_generator_Mode200, XML_generator_Mode_User_Specified
    
    Mode_dict = {'Mode1': XML_generator_Mode1, 'Mode2': XML_generator_Mode2, 'Mode120': XML_generator_Mode120, 
             'Mode130': XML_generator_Mode130, 'Mode200': XML_generator_Mode200, 'Mode_User_Specified': XML_generator_Mode_User_Specified}

    
    #If no optional paramters are given
    if(len(params.keys()) == 0):
        
        Mode_dict[mode](root, date, duration, relativeTime)
        
    else:
        
        Mode_dict[mode](root, date, duration, relativeTime, params = params)
    
    
####################### End of Mode selecter #############################
'''

def XML_generator_select(mode, root, date, duration, relativeTime, params):
    '''Selects corresponding function from received science mode.
    Input: 
        mode: The name of the of the mode as a string. The name in the XML_generator_name function in OPT_XML_generator_MODES
        root: XML tree structure. Main container object for the ElementTree API. lxml.etree.Element class
        date = Starting date of the Mode. On the form of the ephem.Date class.
        duration = The duration of the mode [s] as an integer class.
        relativeTime = The starting time of the mode with regard to the start of the timeline [s] as an integer class
        params = Dictionary containing the parameters of the mode.
    Output:
        None
    '''
    
    import Operational_Planning_Tool.OPT_XML_generator_MODES as OPT_XML_generator_MODES
    
    Logger = logging.getLogger(Logger_name())
    
    #Mode_dict = {'Mode1': XML_generator_Mode1, 'Mode2': XML_generator_Mode2, 'Mode120': XML_generator_Mode120, 
    #         'Mode130': XML_generator_Mode130, 'Mode200': XML_generator_Mode200, 'Mode_User_Specified': XML_generator_Mode_User_Specified}
    
    
    
    #Check if no parameters are given
    if(len(params.keys()) == 0):
        
        try:
            Mode_func = getattr(OPT_XML_generator_MODES,'XML_generator_'+mode)
        except:
            Logger.error('No XML-generator Mode is defined for the scheduled Mode')
            sys.exit()
            
        Mode_func(root, date, duration, relativeTime)
        #Mode_dict[mode](root, date, duration, relativeTime)
        
    else:
        try:
            Mode_func = getattr(OPT_XML_generator_MODES,'XML_generator_'+mode)
        except:
            Logger.error('No XML-generator Mode is defined for the scheduled Mode')
            sys.exit()
        
        Mode_func(root, date, duration, relativeTime, params = params)
        #Mode_dict[mode](root, date, duration, relativeTime, params = params)
