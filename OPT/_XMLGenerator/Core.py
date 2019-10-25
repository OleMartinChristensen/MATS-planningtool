# -*- coding: utf-8 -*-
"""Creates the base of the XML-tree and calculates initial values such as the 
start and end time and also duration of the timeline. Then goes through the 
supplied Science Mode Timeline List chronologically and calls for the corresponding function in one of the modules located in the *Modes_and_Tests* package. \n

Any settings given in the *Science Mode Timeline* file will overide the use of the same settings stated in set *Configuration File*.

"""

from lxml import etree
import ephem, logging, sys, time, os, json, importlib, datetime

from OPT import _Globals, _Library
OPT_Config_File = importlib.import_module(_Globals.Config_File)
#from OPT_Config_File import Timeline_settings, initialConditions, Logger_name, Version
from .Modes_and_Tests import MODES, Tests, SeparateCmds

Logger = logging.getLogger(OPT_Config_File.Logger_name())


def XML_generator(SCIMOD_Path):
    """The core function of the XML_gen program.
    
    Reads a *Science Mode Timeline* .json file. Then chronologically goes though the *Science Mode Timeline*, calling for the *XML_generator_select* function.
    Any settings stated in the *Science Mode Timeline* will override any similar ones given in the set *Configuration File*.
    Also calls for XML_Initial_Basis_Creator to setup a XML tree which will be used to write CMDs to.
    
    Arguments:
        SCIMOD_Path (str): A string containing the path to the Science Mode Timeline .json file.
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
    
    
    Logger.info('Start of Program')
    Logger.info('')
    Version = OPT_Config_File.Version()
    Logger.info('Configuration File used: '+_Globals.Config_File+', Version: '+Version)
    Logger.info('')
    
    
    ################# Read Science Mode Timeline json file ############
    with open(SCIMOD_Path, "r") as read_file:
        SCIMOD= json.load(read_file)
    ################# Read Science Mode Timeline json file ############
    
    Logger.info('Science Mode Timeline Used: '+SCIMOD_Path)
    
    "Check if there are Timeline_settings given in the Science Mode Timeline"
    if( str(SCIMOD[0][0]) == 'Timeline_settings' ):
        Timeline_settings_from_Timeline = SCIMOD[0][3]
        Timeline_settings = _Library.params_checker( Timeline_settings_from_Timeline, OPT_Config_File.Timeline_settings())
        Logger.info('Timeline_settings found in Science Mode Timeline. Using them')
        
        TLE_from_Timeline = SCIMOD[0][4]
        TLE_from_configFile =  OPT_Config_File.getTLE()
        
        if( TLE_from_Timeline[0] != TLE_from_configFile[0] or TLE_from_Timeline[1] != TLE_from_configFile[1] ):
            Logger.error('Mismatch between TLE in Science Mode Timeline and in ConfigFile. Check your chosen ConfigFile and maybe rerun OPT.Timeline_gen. Exiting...')
            raise ValueError
    else:
        Logger.info('Timeline_settings not found in Science Mode Timeline. Using the ones in the chosen ConfigFile')
        Timeline_settings = OPT_Config_File.Timeline_settings()
        
    "Save the Timeline_settings to be used in a Global variable"
    _Globals.Timeline_settings = Timeline_settings
    
    ################ Get settings for Timeline from Config module ############
    timeline_duration = Timeline_settings['duration']
    Logger.info('timeline_duration: '+str(timeline_duration))
    
    timeline_start = ephem.Date(Timeline_settings['start_date'])
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
        Logger.info(str(SCIMOD[x][0]))
        
        "Skip the first entry if it only contains Timeline_settings"
        if( str(SCIMOD[x][0]) == 'Timeline_settings' ):
            continue
        
        Logger.debug('Start Date: '+str(SCIMOD[x][1]))
        Logger.debug('End Date: '+str(SCIMOD[x][2]))
        
        mode_duration = round((ephem.Date(SCIMOD[x][2]) - ephem.Date(SCIMOD[x][1]) ) *24*3600)
        relativeTime = round((ephem.Date(SCIMOD[x][1])-ephem.Date(timeline_start))*24*3600)
        Logger.debug('mode_duration: '+str(mode_duration))
        Logger.debug('relativeTime: '+str(relativeTime))
        
        if( relativeTime >= timeline_duration ):
            Logger.warning('relativeTime is exceeding timeline_duration!!!')
            raise ValueError
            
                
        if( ephem.Date(SCIMOD[x][1]) < timeline_start or mode_duration+relativeTime > timeline_duration):
            Logger.warning(str(SCIMOD[x][0])+', is not scheduled within the boundaries of the timeline!!!')
            raise ValueError
            
        
        Logger.debug('Call XML_generator_select')
        XML_generator_select(root=root, duration=mode_duration, relativeTime=relativeTime, name=SCIMOD[x][0], date=ephem.Date(SCIMOD[x][1]), params=SCIMOD[x][3])
        
    
    ### Rewrite path string to allow it to be in the name of the generated XML command file ###
    SCIMOD_Path = SCIMOD_Path.replace('\\','_')
    SCIMOD_Path = SCIMOD_Path.replace('/','_')
    SCIMOD_Path = SCIMOD_Path.replace('.json','')
    
    ### Write finished XML-tree with all commands to a file #######
    XML_TIMELINE = os.path.join('Output','XML_TIMELINE__'+'FROM__'+SCIMOD_Path+'.xml')
    Logger.info('Write XML-tree to: '+XML_TIMELINE)
    f = open(XML_TIMELINE, 'w')
    f.write(etree.tostring(root, pretty_print=True, encoding = 'unicode'))
    f.close()
    
    statinfo = os.stat(XML_TIMELINE)
    SizeOfXML = statinfo.st_size
    DataLimitInBytes = 20*10**6
    if( SizeOfXML > DataLimitInBytes ):
        input('Size of XML Timeline file exceeds allowed datalimit (20Mb). Press enter to acknowledge')
    
    logging.shutdown()



################### XML-tree basis creator ####################################

def XML_Initial_Basis_Creator(timeline_start,timeline_duration, SCIMOD_Path):
    '''Subfunction, Construct Basis of XML document and adds the description container.
    
    Arguments: 
        timeline_start (ephem.Date): Starting date of the Timeline. On the form of the ephem.Date class.
        timeline_duration (int): Duration of the timeline [s].
        SCIMOD_Path (str): The path as a string to the Science Mode Timeline .json file used in this run.
    
    Returns:
        (lxml.etree.Element): The basis of the XML tree created with lxml.
    
    '''
    
    TimelineStart_Tuple = timeline_start.tuple()
    
    "Because of rounding errors in ephem.Date 0 seconds might be 59.9999... causing error. Add half a second here to fix this error."
    if( int(round(TimelineStart_Tuple[5])) == 60 ):
        TimelineStart_Tuple = ephem.Date( timeline_start + ephem.second/2 ).tuple()
    
    TimelineStart_datetime = datetime.datetime( TimelineStart_Tuple[0], TimelineStart_Tuple[1], TimelineStart_Tuple[2], 
                      TimelineStart_Tuple[3], TimelineStart_Tuple[4], int(round(TimelineStart_Tuple[5])) )
    
    StartingDate = TimelineStart_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    
    
    #earliestStartingDate = ephem.Date(timeline_start).datetime().strftime("%Y-%m-%dT%H:%M:%S")
    #latestStartingDate = ephem.Date(timeline_start).datetime().strftime("%Y-%m-%dT%H:%M:%S")
    
    root = etree.Element('InnoSatTimeline', originator='OHB', sdbVersion='9.5.99.2')
    
    
    root.append(etree.Element('description'))
    
    
    etree.SubElement(root[0], 'timelineID', procedureIdentifier = "", descriptiveName = "", version = "1.0")
    
    etree.SubElement(root[0], 'changeLog')
    etree.SubElement(root[0][1], 'changeLogItem', version = "1.1", date = "2019-01-17", author = "David Skanberg")
    root[0][1][0].text = "Created Document"
    
    
    etree.SubElement(root[0], 'validity')
    etree.SubElement(root[0][2], 'startingDate')
    root[0][2][0].text = StartingDate
    etree.SubElement(root[0][2], 'scenarioDuration')
    root[0][2][1].text = str(timeline_duration)
    
    etree.SubElement(root[0], 'comment')
    root[0][3].text = "This command sequence is an Innosat timeline. Science Mode Timeline used to generate: "+SCIMOD_Path+', Configuration File used: '+_Globals.Config_File
    
    
    root.append(etree.Element('listOfCommands'))
    
    return root
    
####################### End of XML-tree basis creator #############################



####################### Mode selecter ###################################

def XML_generator_select(name, root, date, duration, relativeTime, params):
    '''Subfunction, Selects corresponding mode, test or CMD function in the package *Modes_and_Tests* from the variable *mode*.
    
    Calls for any function named *X* in the modules *MODES*, *SeparateCmds*, and *Tests*, where X is the string in the input *name*.
    
    Arguments: 
        name (str): The name of the of the mode or test as a string. The name in the XML_generator_name function in OPT_XML_generator_MODES
        root (lxml.etree.Element): XML tree structure. Main container object for the ElementTree API.
        date (ephem.Date) = Starting date of the Mode. On the form of the ephem.Date class.
        duration (int) = The duration of the mode [s] as an integer class.
        relativeTime (int) = The starting time of the mode with regard to the start of the timeline [s] as an integer class
        params (dict) = Dictionary containing the parameters of the Mode, CMD, or Test given in the Science_Mode_Timeline. 
    
    Returns:
        None
    '''
    
    
    try:
        Mode_Test_SeparateCmd_func = getattr(MODES,name)
    except AttributeError:
        try:
            Mode_Test_SeparateCmd_func = getattr(Tests,name)
        except AttributeError:
            try:
                Mode_Test_SeparateCmd_func = getattr(SeparateCmds,name)
            except AttributeError:
                Logger.error('No XML-generator is defined for '+name)
                raise AttributeError
    
    "Check if no parameters are given"
    if(len(params.keys()) == 0):
        Mode_Test_SeparateCmd_func(root, date, duration, relativeTime)
    else:
        Mode_Test_SeparateCmd_func(root, date, duration, relativeTime, params = params)
        
    
####################### End of Mode selecter #############################

