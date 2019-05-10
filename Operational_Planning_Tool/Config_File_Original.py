# -*- coding: utf-8 -*-
"""Contains settings for the Operational Planning Tool. The Config file used must be
named OPT_Config_File.py and be located in the working directoy of the user call.
    
"""

 
from Operational_Planning_Tool.Library import FreezeDuration_calculator

def Logger_name():
    '''Contains the name of the shared logger.
    
    Returns:
        (str): Logger_name
    
    '''
    
    Logger_name = "OPT_logger"
    
    return Logger_name


def Version():
    ''''Contains the version name of this Config_File.
    
    Returns:
        (str): version_name 
    
    '''
    version_name = 'Original'
    return version_name


def Modes_priority():
    '''Contain the Modes (except 1-4) planned to be schedueled as a list. Only one entry of each mode is allowed.
    
    'PWRTOGGLE',
    'CCDFlushBadColumns',
    'CCDBadColumn',
    'Mode130', 
    'Mode110', 
    'Mode100', 
    'Mode120', 
    'Mode121',
    'Mode122',
    'Mode130',  
    'Mode131',
    'Mode132', 
    'Mode200', 
    
    The order of which the Modes appear is also their priority order.
    The name must be equal to the name of the top function in the Timeline_generator.Modes.ModeX module, where X is any mode.
    
    Returns:
        (:obj:`list` of :obj:`str`): Modes_priority
    
    '''
    Modes_priority = [
            'PWRTOGGLE',
            'CCDFlushBadColumns',
            'CCDBadColumn',
            'Mode130', 
            'Mode200',
            'Mode120',
            'Mode121',
            'Mode110',
            'Mode100',
            'Mode132',
            'Mode122',
            'Mode131']
    return Modes_priority


def getTLE():
    '''Contains the TLE as two strings in a list.
    
    Returns:
        (:obj:`list` of :obj:`str`): First Element is the first TLE row and the second Element is the second row.
    
    '''
    TLE1 = '1 26702U 01007A   18231.91993126  .00000590  00000-0  00000-0 0  9994'
    TLE2= '2 26702 97.61000 65.95030 0000001 0.000001 359.9590 14.97700580100  4'
    #TLE1 = '1 26702U 01007A   09264.68474097 +.00000336 +00000-0 +35288-4 0  9993'
    #TLE2 = '2 26702 097.7067 283.5904 0004656 126.2204 233.9434 14.95755636467886'
    return [TLE1, TLE2]


def initialConditions():
    '''Contains the values for the initialConditions container in the XML-file.
    
    initialCondition container defined in "InnoSat Payload Timeline XML Definition" Document
    
    Returns:
        (:obj:`dict` of :obj:`dict` of :obj:`str`): InitialConditions 
    
    '''
    InitialConditions = { 'spacecraft': {'mode': 'Normal', 'acs': 'Normal'}, 'payload': { 'power': 'On' , 'mode': ''} }
    return InitialConditions


def Timeline_settings():
    '''Contains the settings related to the timeline as a whole as a dict.
    
    Keys:
        'start_date': Sets the starting date of the timeline as a str, (example: '2018/9/3 08:00:40')). \n
        'duration': Sets the duration in seconds of the timeline. (int) \n
        'leap_seconds': Sets the amount of leap seconds for GPS time to be used. (int) \n
        'GPS_epoch': Sets the epoch of the GPS time as a str, (example: '1980/1/6'). \n
        
        'Mode_1_2_3_4minDuration': Minimum amount of time needed (inbetween scheduled Modes) for the scheduling of Modes 1-4 [s]. \n
        'mode_separation': Time in seconds. Is used in Library.scheduler to postpone Modes and also as an extra term in the calculations of the duration of other modes to act as an prolonged buffer.
        Meaning that whenever mode_duration is calculated it is equal to an calculated estimation of the modes duration plus "mode_separation". (int) \n
        
        'CMD_duration': Sets the amount of time scheduled for PayloadCMDs. (int) \n
        'yaw_correction': If yaw correction will be used for the duration of the timeline. Decides if Mode1/2 or Mode3/4 are to be scheduled. Set to True for Mode3/4, set to False for Mode1/2. (bool) \n
        'command_separation': Minimum ammount of time inbetween scheduled commands [s]. (float) \n
        'pointing_stabilization': Extra time [s] scheduled for fixed pointing commands before new commands are allowed. (int) \n
        
        
    Returns:
        (dict): timeline_settings
    '''
    timeline_settings = {'start_date': '2018/9/3 08:00:40', 'duration': 1*4*3600, 
                       'leap_seconds': 18, 'GPS_epoch': '1980/1/6', 'Mode_1_2_3_4minDuration': 300, 'mode_separation': 120,
                       'CMD_duration': 60, 'yaw_correction': True, 'command_separation': 0.1, 'pointing_stabilization': 60, 
                       }
    return timeline_settings


def Mode1_settings():
    '''Contain settings related to Mode1 as a dict.
    
    Keys:
        'lat': Sets in degrees the latitude (+ and -) that the LP crosses that causes NLC mode to swith on/off. (int) \n
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'log_timestep': Sets the frequency of data being logged [s]. (int)
        
    Returns:
        (dict): settings
    
    '''
    settings = {'lat': 45, 'pointing_altitude': 92000, 'log_timestep': 800}
    return settings


def Mode2_settings():
    '''Contain settings related to Mode2 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'log_timestep': Sets the frequency of data being logged [s]. (int)
        
    Returns:
        (dict): settings
        
    '''
    settings = {'pointing_altitude': 92000, 'log_timestep': 800}
    return settings


def Mode3_settings():
    '''Contain settings related to Mode3 as a dict.
    
    Keys:
        'lat': Sets in degrees the latitude (+ and -) that when the LP crosses causes NLC mode to swith on/off. (int) \n
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'log_timestep': Sets the frequency of data being logged [s]. (int)
        
    Returns:
        (dict): settings
    
    '''
    settings = {'lat': 45, 'pointing_altitude': 92000, 'log_timestep': 800}
    return settings


def Mode4_settings():
    '''Contain settings related to Mode4 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'log_timestep': Sets the frequency of data being logged [s]. (int)
        
    Returns:
        (dict): settings
        
    '''
    settings = {'pointing_altitude': 92000, 'log_timestep': 800}
    return settings


def Mode100_settings():
    '''Contain settings related to Mode100 as a dict.
    
    Keys:
        'pointing_altitude_from': Sets in meters the starting altitude. (int) \n
        'pointing_altitude_to': Sets in meters the ending altitude. (int) \n
        'pointing_altitude_interval': Sets in meters the interval size of each succesive pointing. (int) \n
        'pointing_duration': Sets the time [s] from attitude stabilization until next pointing command. (int) \n
        'ExpTimeUV': Sets the exposuretime of the UV CCDs. \n
        'ExpTimeIR': Sets the exposuretime of the IR CCDs. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
        
    Returns:
        (dict): settings
            
    '''
    settings = {'pointing_altitude_from': 10000, 'pointing_altitude_to': 150000, 
                'pointing_altitude_interval': 5000, 'pointing_duration': 20, 'ExpTimeUV': 3000, 'ExpTimeIR': 5000, 'start_date': '0'}
    return settings


def Mode110_settings():
    '''Contain settings related to Mode110 as a dict.
    
    Keys:
        'pointing_altitude_from': Sets in meters the starting altitude of the sweep. (int) \n
        'pointing_altitude_to': Sets in meters the ending altitude of the sweep. (int) \n
        'sweep_rate': Sets in meters rate of the sweep. (int) \n
        'sweep_start': Sets in seconds the time from start of the Mode to when the sweep starts. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (dict): settings
        
    '''
    settings = {'pointing_altitude_from': 10000, 'pointing_altitude_to': 150000, 'sweep_rate': 500, 'sweep_start': 120, 'start_date': '0'}
    return settings


def Mode120_settings():
    '''Contain settings related to Mode120 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'V_offset': Sets the V-offset of the star (when pointing towards pointing_altitude) for when the attitude freeze command is scheduled. (int) \n
        'H_offset': Sets the maximum H-offset angle from the optical axis (angle away from orbital plane) in degrees that determines if stars are available. (int) \n
        'Vmag': Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2'). \n
        'timestep': Sets timestep used in simulation [s]. (int) \n
        'log_timestep': Sets the frequency of data being logged [s]. (int) \n
        'automatic': Sets if the mode date is to be calculated or user provided. True for calculated or False for user provided. (bool) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). Note! only applies if automatic is set to False. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated. (int) \n
        'LP_pointing_altitude': Sets altitude of LP in meters. (int) \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freezes. (int) \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with LP_pointing_altitude. (int)
    
    Returns:
        (dict): settings
    
    '''
    settings = {'pointing_altitude': 227000, 'V_offset': 0, 'H_offset': 2.5, 'Vmag': '<2', 'timestep': 2,'log_timestep': 3600, 
                      'automatic': True, 'date': '2019', 'mode_duration': 0, 'LP_pointing_altitude': 92000, 'freeze_start': 300, 
                      'freeze_duration': 0}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( settings['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings


def Mode121_settings():
    '''Contain settings related to Mode121 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'H_FOV': Sets full Horizontal FOV of the Limb instrument in degrees. \n
        'V_FOV': Sets full Vertical FOV of the Limb instrument in degrees. \n
        'Vmag': Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2'). \n
        'timestep': sets timestep used in simulation [s]. \n
        'log_timestep': Sets the frequency of data being logged [s]. \n
        'automatic': Sets if the mode date is to be calculated or user provided. True for calculated or False for user provided. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). Note! only applies if automatic is set to False. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated. \n
        'LP_pointing_altitude': Sets altitude of LP in meters. \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freezes. \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with LP_pointing_altitude.
    
    Returns:
        (dict): settings
    
    '''
    settings = {'pointing_altitude': 227000, 'H_FOV': 5.67, 'V_FOV': 0.91, 'Vmag': '<4', 'timestep': 5,'log_timestep': 3600, 
                      'automatic': True, 'start_date': '2019', 'mode_duration': 0, 'LP_pointing_altitude': 92000, 'freeze_start': 300, 
                      'freeze_duration': 0}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( settings['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings


def Mode122_settings():
    '''Contain settings related to Mode122 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'H_FOV': Sets full Horizontal FOV of the Limb instrument in degrees. \n
        'V_FOV': Sets full Vertical FOV of the Limb instrument in degrees. \n
        'Vmag': Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2'). \n
        'timestep': sets timestep used in simulation [s]. \n
        'log_timestep': Sets the frequency of data being logged [s]. \n
        'automatic': Sets if the mode date is to be calculated or user provided. True for calculated or False for user provided. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). Note! only applies if automatic is set to False. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated. \n
        'ExpTimes': Sets exposure times [s] as a integer list and the exposure intervall (ExpInt = ExpTime + 1). \n
        'LP_pointing_altitude': Sets altitude of LP in meters. \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freezes. \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with LP_pointing_altitude.
    
    Returns:
        (dict): settings
        
    '''
    settings = {'pointing_altitude': 227000, 'H_FOV': 5.67, 'V_FOV': 0.91, 'Vmag': '<4', 'timestep': 5,'log_timestep': 3600, 
                      'automatic': True, 'start_date': '2019', 'mode_duration': 0, 'LP_pointing_altitude': 92000, 'freeze_start': 300, 
                      'freeze_duration': 0, 'ExpTimes': [1000, 3000, 5000, 10000, 20000], 'session_duration': 120}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( settings['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings


def Mode130_settings():
    '''Contain settings related to Mode130 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (dict): settings
        
    '''
    settings = {'pointing_altitude': 200000, 'mode_duration': 900, 'start_date': '2018/9/3 12:00:40'}
    return settings


def Mode131_settings():
    '''Contain settings related to Mode131 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (dict): settings
    
    '''
    settings = {'pointing_altitude': 200000, 'mode_duration': 900, 'start_date': '2018/9/3 12:00:40'}
    return settings


def Mode132_settings():
    '''Contain settings related to Mode132 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used. \n
        'ExpTimes': Sets exposure times [s] as a integer list and the exposure intervall (ExpInt = ExpTime + 1). \n
        'session_duration': Sets the duration [s] of each session using the different exposure times in ExpTimes.
    
    Returns:
        (dict): settings
    
    '''
    settings = {'pointing_altitude': 200000, 'start_date': '2018/9/3 12:00:40', 'ExpTimes': [1000, 3000, 5000, 10000, 20000], 'session_duration': 120}
    return settings


def Mode200_settings():
    '''Contain settings related to Mode200 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'V_offset': Sets the V-offset of the Moon (when pointing towards pointing_altitude) for when the attitude freeze command is scheduled. \n
        'H_offset': Sets the maximum H-offset angle from the optical axis in degrees that determines if the Moon is available. \n
        'timestep': Sets in seconds the timestep of the simulation when larger timeskips (Moon determined far out of sight) are not made. \n
        'log_timestep': Sets the frequency of data being logged [s]. \n
        'automatic': Sets if the mode date is to be calculated or user provided. True for calculated or False for user provided. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). Note! only applies if automatic is set to False. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated. \n
        'LP_pointing_altitude': Sets altitude of LP in meters. \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freeze command is scheduled. \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with LP_pointing_altitude.
    
    Returns:
        (dict): settings
    
    '''
    settings = {'pointing_altitude': 227000, 'V_offset': 0, 'H_offset': 3+2.5, 'timestep': 2, 'log_timestep': 1200, 
                      'automatic': 1, 'date': '2019', 'mode_duration': 0, 'LP_pointing_altitude': 92000, 'freeze_start': 300, 'freeze_duration': 0}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( settings['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings

"""
def Mode201_settings():
    '''Contain settings related to Mode201 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (dict): settings
    
    '''
    settings = {'pointing_altitude': 70000, 'mode_duration': 600, 'start_date': '0'}
    return settings



def Mode203_settings():
    '''Contain settings related to Mode203 as a dict.
    
    Keys:
        'pitch': Sets the pitch axis maneuver.
        
    Returns:
        settings (dict)
    
    '''
    settings = {'pitch': 180}
    return settings
"""


def PWRTOGGLE_settings():
    '''Contain default parameters related to PWRTOGGLE when treated as a standalone CMD as a dict.
    
    Keys:
        'CONST': Magic Constant 
        
    Returns:
        (dict): parameters
    
    '''
    parameters = {'CONST': 165}
    return parameters

def CCDFlushBadColumns_settings():
    '''Contain default parameters related to CCDFlushBadColumns when treated as a standalone CMD as a dict.
    
    Keys:
        'CCDSEL': CCD select, 1 bit for each CCD (1..127).
        
    Returns:
        (dict): parameters
    
    '''
    parameters = {'CCDSEL': 1}
    return parameters

def CCDBadColumn_settings():
    '''Contain default parameters related to CCDBadColumn when treated as a standalone CMD as a dict.
    
    Keys:
        'CCDSEL': CCD select, 1 bit for each CCD (1..127). \n
        'NBC': Number of uint16 in BC as a uint16. Big Endian. Maximum number is 63. \n
        'BC': Bad Column as a uint16 (4..2047). Several uint16 cam be combined to select multiple columns. 
        
    Returns:
        (dict): parameters
    
    '''
    parameters = {'CCDSEL': 1, 'NBC': 0, 'BC': 0}
    return parameters

def PM_settings():
    '''Contain default parameters related to PM as a dict.
    
    Keys:
        'TEXPMS': Exposure time [ms] for the photometer (int) \n
        'TEXPIMS': Exposure intervall time [ms] for the photometer (int)
        
    Returns:
        (dict): parameters
    
    '''
    parameters = {'TEXPMS': 1000, 'TEXPIMS': 3000}
    return parameters