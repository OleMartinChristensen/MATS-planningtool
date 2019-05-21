# -*- coding: utf-8 -*-
"""Creates the base of the XML-tree and calculates initial values such as the 
start and end time and also duration of the timeline. Then goes through the 
supplied Science Mode Timeline List chronologically and calls for the corresponding function. \n

Mode/Test/CMD specific settings given in the Science Mode Timeline List will overirde the use of the same settings stated in OPT_Config_File.

"""

from lxml import etree
import ephem, logging, sys, time, os, json

from OPT_Config_File import Timeline_settings, initialConditions, Logger_name, Version
from .Modes_and_Tests import MODES, Tests, SeparateCmds

Logger = logging.getLogger(Logger_name())


def XML_generator(SCIMOD_Path):
    """The core function of the XML_gen program.
    
    Arguments:
        SCIMOD_Path (str): A string containing the path to the Science Mode Timeline json file.
    Returns:
        None
        
    """
    
    ######## Try to Create a directory for storage of Logs #######
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
    Handler = logging.FileHandler('Logs_'+__name__+'\\'+__name__+'_'+Version()+'_'+timestr+'.log', mode='a')
    formatter = logging.Formatter("%(levelname)6s : %(message)-80s :: %(module)s :: %(funcName)s")
    Handler.setFormatter(formatter)
    Logger.addHandler(Handler)
    Logger.setLevel(logging.DEBUG)
    
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.INFO)
    streamHandler.setFormatter(formatter)
    Logger.addHandler(streamHandler)
    ############# Set up Logger ##########################
    
    
    Logger.info('Start of Program')
    Logger.info('')
    Logger.info('OPT_Config_File version used: '+Version())
    Logger.info('')
    
    
    ################# Read Science Mode Timeline json file ############
    with open(SCIMOD_Path, "r") as read_file:
        SCIMOD= json.load(read_file)
    ################# Read Science Mode Timeline json file ############
    
    
    ################ Get settings for Timeline from Config module ############
    timeline_duration = Timeline_settings()['duration']
    Logger.info('timeline_duration: '+str(timeline_duration))
    
    timeline_start = ephem.Date(Timeline_settings()['start_date'])
    Logger.info('timeline_start: '+str(timeline_start))
    
    
    ########    Call function to create XML-tree basis ##########################
    Logger.info('Call function XML_Initial_Basis_Creator')
    Logger.info('')
    root = XML_Initial_Basis_Creator(timeline_start,timeline_duration, SCIMOD_Path)
    
    ######## Loop through SCIMOD TIMELINE lIST, selecting one mode at a time #####
    Logger.info('Loop through Science Mode Timeline List')
    
    for x in range(len(SCIMOD)):
        Logger.info('')
        Logger.info('Iteration number: '+str(x+1))
        
        "Skip the first entry if it only contains Timeline_settings used for the creation of the Science Mode Timeline"
        if( str(SCIMOD[x][0]) == 'Timeline_settings' ):
            continue
        
        Logger.info(str(SCIMOD[x][0]))
        Logger.debug('Start Date: '+str(SCIMOD[x][1]))
        Logger.debug('End Date: '+str(SCIMOD[x][2]))
        
        mode_duration = round((ephem.Date(SCIMOD[x][2]) - ephem.Date(SCIMOD[x][1]) ) *24*3600)
        relativeTime = round((ephem.Date(SCIMOD[x][1])-ephem.Date(timeline_start))*24*3600)
        Logger.debug('mode_duration: '+str(mode_duration))
        Logger.debug('relativeTime: '+str(relativeTime))
        
        if( relativeTime >= timeline_duration ):
            Logger.warning('relativeTime is exceeding timeline_duration!!!')
            #warning = input('Enter anything to continue or enter 1 to stop\n')
            #if( warning == '1'):
            #    sys.exit()
                
        if( ephem.Date(SCIMOD[x][1]) < timeline_start or mode_duration+relativeTime > timeline_duration):
            Logger.warning(str(SCIMOD[x][0])+', is not scheduled within the boundaries of the timeline!!!')
            #warning = input('Enter anything to continue or enter 1 to stop\n')
            #if( warning == '1'):
            #    sys.exit()
        
        Logger.debug('Call XML_generator_select')
        XML_generator_select(root=root, duration=mode_duration, relativeTime=relativeTime, mode=SCIMOD[x][0], date=ephem.Date(SCIMOD[x][1]), params=SCIMOD[x][3])
        
    
    ### Rewrite path string to allow it to be in the name of the generated XML command file ###
    SCIMOD_Path = SCIMOD_Path.replace('Output/','_from_')
    SCIMOD_Path = SCIMOD_Path.replace('.json','')
    
    ### Write finished XML-tree with all commands to a file #######
    MATS_COMMANDS = 'Output\\MATS_COMMANDS__Version_'+Version()+'__'+SCIMOD_Path+'.xml'
    Logger.info('Write XML-tree to: '+MATS_COMMANDS)
    f = open(MATS_COMMANDS, 'w')
    f.write(etree.tostring(root, pretty_print=True, encoding = 'unicode'))
    f.close()
    
    logging.shutdown()



################### XML-tree basis creator ####################################

def XML_Initial_Basis_Creator(timeline_start,timeline_duration, SCIMOD_Path):
    '''Subfunction, Construct Basis of XML document and adds the description container.
    
    Arguments: 
        earliestStartingDate (ephem.Date): Earliest Starting date of the Timeline. On the form of the ephem.Date class.
        latestStartingDate (ephem.Date): Latest Starting date of the Timeline. On the form of the ephem.Date class.
        timeline_duration (int): Duration of the timeline [s] as a integer class.
        SCIMOD_Path (str): The path as a string to the Science Mode Timeline .json file used in this run.
    '''
    
    earliestStartingDate = ephem.Date(timeline_start-ephem.second).datetime().strftime("%Y-%m-%dT%H:%M:%S")
    latestStartingDate = ephem.Date(timeline_start).datetime().strftime("%Y-%m-%dT%H:%M:%S")
    
    
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



####################### Mode selecter ###################################

def XML_generator_select(mode, root, date, duration, relativeTime, params):
    '''Subfunction, Selects corresponding mode, test or CMD function in the package *Modes_and_Tests* from the variable *mode*.
    
    Arguments: 
        mode (str): The name of the of the mode or test as a string. The name in the XML_generator_name function in OPT_XML_generator_MODES
        root (lxml.etree.Element): XML tree structure. Main container object for the ElementTree API.
        date (ephem.Date) = Starting date of the Mode. On the form of the ephem.Date class.
        duration (int) = The duration of the mode [s] as an integer class.
        relativeTime (int) = The starting time of the mode with regard to the start of the timeline [s] as an integer class
        params (dict) = Dictionary containing the parameters of the Mode, CMD, or Test given in the Science_Mode_Timeline.
    
    Returns:
        None
    '''
    
    
    try:
        Mode_Test_SeparateCmd_func = getattr(MODES,'XML_generator_'+mode)
    except AttributeError:
        try:
            Mode_Test_SeparateCmd_func = getattr(Tests,'XML_generator_'+mode)
        except AttributeError:
            try:
                Mode_Test_SeparateCmd_func = getattr(SeparateCmds,'XML_generator_'+mode)
            except AttributeError:
                Logger.error('No XML-generator is defined for '+mode)
                sys.exit()
    
    "Check if no parameters are given"
    if(len(params.keys()) == 0):
        Mode_Test_SeparateCmd_func(root, date, duration, relativeTime)
    else:
        Mode_Test_SeparateCmd_func(root, date, duration, relativeTime, params = params)

####################### End of Mode selecter #############################

