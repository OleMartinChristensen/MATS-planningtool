# -*- coding: utf-8 -*-
"""Contains functions that return settings for the Operational Planning Tool. The Config file used is set 
by calling *Operational_Planning_Tool.Set_ConfigFile()* and must be visible in *sys.path*.
    
"""

from pylab import pi, arccos
from Operational_Planning_Tool import _Globals


def Logger_name():
    '''Contains the name of the shared logger.
    
    Returns:
        (str): Logger_name
    
    '''
    
    Logger_name = "OPT_logger"
    
    return Logger_name


def Version():
    ''''Contains the version ID of this Configuration File.
    
    Returns:
        (str): version_name 
    
    '''
    version_name = 'Original'
    return version_name


def Scheduling_priority():
    '''Contain the Modes (except Operational Science Modes: Mode1,2,5) and available CMDs planned to be schedueled as a list using the Timeline_gen.
    
    Available choices are: \n
    
    'PWRTOGGLE',
    'CCDFlushBadColumns',
    'CCDBadColumn',
    'PM',
    'CCDBIAS', 
    'Mode100', 
    'Mode110', 
    'Mode120', 
    'Mode121', 
    'Mode122', 
    'Mode123', 
    'Mode124', 
    'Mode131', 
    'Mode132', 
    'Mode133', 
    'Mode130', 
    'Mode160'
     
    The order of which the Modes appear is also their priority order (top-down).
    The name must be a function imported in the *_Timeline_generator.Modes.Modes_Header* module.
    
    Returns:
        (:obj:`list` of :obj:`str`): Modes_priority
    
    '''
    Modes_priority = [
            'PWRTOGGLE',
            'CCDFlushBadColumns',
            'CCDBadColumn',
            'PM',
            'Mode130', 
            'Mode124',
            'Mode120',
            'Mode123',
            'Mode121',
            'Mode110',
            'Mode100',
            'Mode132',
            'Mode122',
            'Mode131',
            'Mode160']
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
    
    "OHB TLE"
    #TLE1 = '1 54321U 19100G   20172.75043981 0.00000000  00000-0  75180-4 0  0014'
    #TLE2 = '2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010'
    
    "OHB TLE timeshifted by 2 sec"
    TLE1 = '1 54321U 19100G   20172.75041666 0.00000000  00000-0  75180-4 0  0012'
    TLE2 = '2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010'
    
    
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
        
        'Mode1_2_5_minDuration': Minimum amount of time needed (inbetween scheduled Modes) for the scheduling of Modes 1-6 [s]. \n
        'mode_separation': Time in seconds for an added buffer inbetween schedules Modes and PayloadCMDs in the Science Mode Timeline when determining their duration. 
        Is also used in Library.scheduler to postpone Modes if their scheduled date is occupied. (int) \n
        'CMD_duration': Sets the amount of time scheduled for separate PayloadCMDs using *Timeline_gen*. (int) \n
        
        'yaw_correction': If yaw correction will be used for the duration of the timeline. (bool) \n
        'yaw_amplitude': Amplitude of the yaw function (float). \n
        'yaw_phase': Phase of the yaw function (float). \n
        'Schedule_Mode5': Set to *True* if mode 5 will be used and scheduled as the operational science mode, set to *False* for Mode1-2. (bool)
        'LP_pointing_altitude': Sets altitude of LP in meters for the timeline. (int) \n
        
        'command_separation': Minimum ammount of time inbetween scheduled commands [s]. (float) \n
        'pointing_stabilization': Extra time [s] scheduled after fixed pointing commands (TC_acfLimbPointingAltitudeOffset) before new commands are allowed. (int) \n
        'CCDSYNC_ExtraOffset': Extra offset time [ms] that is added to an estimated ReadoutTime when calculating arguments for the CCD Synchronize CMD. (int) \n
        'CCDSYNC_ExtraIntervalTime': Extra time [ms] that is added to the calculated Exposure Interval Time when calculating arguments for the CCD Synchronize CMD. (int) \n
        
    Returns:
        (:obj:`dict`): timeline_settings
    '''
    timeline_settings = {'start_date': _Globals.StartTime, 'duration': 1*4*3600, 
                       'leap_seconds': 18, 'GPS_epoch': '1980/1/6', 'Mode1_2_5_minDuration': 300, 'mode_separation': 60,
                       'CMD_duration': 30, 'yaw_correction': True, 'yaw_amplitude': -3.8, 'yaw_phase': -20, 'Schedule_Mode5': False, 'LP_pointing_altitude': 92500, 
                       'command_separation': 1, 'pointing_stabilization': 60, 'CCDSYNC_ExtraOffset': 50, 'CCDSYNC_ExtraIntervalTime': 200}
    
    
    return timeline_settings


def Mode1_2_settings():
    '''Contain settings related to Mode1, 2 as a dict.
    
    Keys:
        'lat': Sets in degrees the latitude (+ and -) that the LP crosses that causes the UV exposure to swith on/off (applies to Mode1). (int) \n
        'log_timestep': Sets the frequency of data being logged [s]. (int) \n
        'timestep': Sets the timestep [s] of the XML generator simulation of Mode1-2. (int)
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'lat': 45, 'log_timestep': 800, 'timestep': 5}
    return settings


def Mode5_settings():
    '''Contain settings related to Mode5 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. If set to 0, Timeline_settings['LP_pointing_altitude'] will be used (int) 
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    
    settings = {'pointing_altitude': 110000}
    
    return settings



def Mode100_settings():
    '''Contain settings related to Mode100 as a dict.
    
    Keys:
        'pointing_altitude_from': Sets in meters the starting altitude. (int) \n
        'pointing_altitude_to': Sets in meters the ending altitude. (int) \n
        'pointing_altitude_interval': Sets in meters the interval size of each succesive pointing. (int) \n
        'pointing_duration': Sets the time [s] from attitude stabilization until next pointing command. (int) \n
        'Exp_Time_IR': Sets starting exposure time [ms] as a integer. \n
        'Exp_Time_UV': Sets starting exposure time [ms] as a integer. \n
        'ExpTime_step': Sets in ms the interval size of both ExpTimeUV and ExpTimeIR for each succesive pointing. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
        
    Returns:
        (:obj:`dict`): settings
            
    '''
    settings = {'pointing_altitude_from': 40000, 'pointing_altitude_to': 150000, 
                'pointing_altitude_interval': 5000, 'pointing_duration': 20, 'Exp_Time_UV': 1000, 
                'Exp_Time_IR': 1000, 'ExpTime_step': 500,  'start_date': '0'}
    return settings


def Mode110_settings():
    '''Contain settings related to Mode110 as a dict.
    
    Keys:
        'pointing_altitude_from': Sets in meters the starting altitude of the sweep. (int) \n
        'pointing_altitude_to': Sets in meters the ending altitude of the sweep. (int) \n
        'sweep_rate': Sets in meters rate of the sweep. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    '''
    settings = {'pointing_altitude_from': 40000, 'pointing_altitude_to': 150000, 'sweep_rate': 500, 'start_date': '0'}
    return settings


def Mode120_settings():
    '''Contain settings related to Mode120 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'V_offset': Sets the V-offset of the star (when pointing towards pointing_altitude) for when the attitude freeze command is scheduled. (int) \n
        'H_offset': Sets the maximum H-offset angle from the optical axis in degrees that determines if stars are available. (int) \n
        'Vmag': Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2'). \n
        'timestep': Sets timestep used in simulation [s]. (int) \n
        'log_timestep': Sets the frequency of data being logged [s]. (int) \n
        'automatic': Sets if the mode date is to be calculated or user provided. True for calculated or False for user provided. (bool) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). Note! only applies if automatic is set to False. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated. (int) \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freezes. (int) \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with *LP_pointing_altitude* (Normally around 50 s). (int) \n
        'SnapshotTime': Sets in seconds the time, from the start of the attitude freeze, to when the first Snapshot is taken. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. (int)
        
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 235000, 'V_offset': 0, 'H_offset': 2.5, 'Vmag': '<2', 'timestep': 2,'log_timestep': 3600, 
                      'automatic': True, 'start_date': '2019', 'mode_duration': 0, 'freeze_start': 120, 
                      'freeze_duration': 0, 'SnapshotTime': 3, 'SnapshotSpacing': 3}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( Timeline_settings()['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings


def Mode121_122_123_settings():
    '''Returns settings shared between Mode121-123 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'H_FOV': Sets full Horizontal FOV of the Limb instrument in degrees. \n
        'V_FOV': Sets full Vertical FOV of the Limb instrument in degrees. \n
        'Vmag': Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2'). \n
        'timestep': sets timestep used in simulation [s]. \n
        'TimeSkip': Sets the amount of days to skip ahead after one complete orbit is simulated. \n
        'log_timestep': Sets the frequency of data being logged [s]. \n
        'automatic': Sets if the mode date is to be calculated or user provided. True for calculated or False for user provided. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated. \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freezes. \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with *LP_pointing_altitude* (Normally around 50 s). \n
        'SnapshotTime': Sets in seconds the time, from the start of the attitude freeze, to when the first Snapshot is taken. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. (int)
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 235000, 'H_FOV': 5.67, 'V_FOV': 0.91, 'Vmag': '<4', 'timestep': 5, 'TimeSkip': 1, 'log_timestep': 3600, 
                      'automatic': True, 'mode_duration': 0, 'freeze_start': 120, 
                      'freeze_duration': 0, 'SnapshotTime': 2, 'SnapshotSpacing': 3}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( Timeline_settings()['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings


def Mode121_settings():
    '''Returns settings related to Mode121 as a dict.
    
    Keys:
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). Note! only applies if automatic is set to False. \n
    
    Returns:
        (:obj:`dict`): settings
    '''
    
    Settings = {'start_date': '2019'}
    CommonSettings = Mode121_122_123_settings()
    
    settings = {**CommonSettings, **Settings}
    
    return settings


def Mode122_settings():
    '''Returns settings related to Mode122 as a dict.
    
    Keys:
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). Note! only applies if automatic is set to False. \n
        'Exp_Time_IR': Sets exposure time [ms] of the IR CCDs. (int) \n
        'Exp_Time_UV': Sets exposure time [ms] of the UV CCDs. (int) \n
    
    Returns:
        (:obj:`dict`): settings
    '''
    
    Settings = {'start_date': '2019', 'Exp_Time_IR': 5000, 'Exp_Time_UV': 3000}
    CommonSettings = Mode121_122_123_settings()
    
    settings = {**CommonSettings, **Settings}
    
    return settings


def Mode123_settings():
    '''Returns settings related to Mode123 as a dict.
    
    Keys:
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). Note! only applies if automatic is set to False. \n
        'Exp_Time_IR': Sets exposure time [ms] of the IR CCDs. (int) \n
        'Exp_Time_UV': Sets exposure time [ms] of the UV CCDs. (int) \n
    
    Returns:
        (:obj:`dict`): settings
    '''
    
    Settings = {'start_date': '2019', 'Exp_Time_IR': 5000, 'Exp_Time_UV': 3000}
    CommonSettings = Mode121_122_123_settings()
    
    settings = {**CommonSettings, **Settings}
    
    return settings
    


def Mode124_settings():
    '''Contain settings related to Mode124 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'V_offset': Sets the V-offset of the Moon (when pointing towards pointing_altitude) for when the attitude freeze command is scheduled. \n
        'H_offset': Sets the maximum H-offset angle from the optical axis in degrees that determines if the Moon is available. \n
        'timestep': Sets in seconds the timestep of the simulation when larger timeskips (Moon determined far out of sight) are not made. \n
        'log_timestep': Sets the frequency of data being logged [s]. \n
        'automatic': Sets if the mode date is to be calculated or user provided. True for calculated or False for user provided. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). Note! only applies if automatic is set to False. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated. \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freeze command is scheduled. \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with LP_pointing_altitude. \n
        'SnapshotTime': Sets in seconds the time, from the start of the attitude freeze, to when the first Snapshot is taken. (int)
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. (int)
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 235000, 'V_offset': 0, 'H_offset': 3+2.5, 'timestep': 2, 'log_timestep': 1200, 
                      'automatic': True, 'start_date': '2019', 'mode_duration': 0, 'freeze_start': 120, 'freeze_duration': 0, 
                      'SnapshotTime': 2, 'SnapshotSpacing': 3}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( Timeline_settings()['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings


def Mode130_settings():
    '''Contain settings related to Mode130 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'SnapshotSpacing': Sets the scheduled duration of the Mode in seconds. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    '''
    settings = {'pointing_altitude': 235000, 'SnapshotSpacing': 2, 'start_date': '0'}
    return settings


def Mode131_settings():
    '''Contain settings related to Mode131 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'Exposure_Interval': Sets in ms the Exposure Interval Time of the Mode. Recommended to be at least 60000 to support FullReadout in Operational Mode. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    '''
    settings = {'pointing_altitude': 235000, 'Exposure_Interval': 60000, 'mode_duration': 120, 'start_date': '0'}
    return settings


def Mode132_settings():
    '''Contain settings related to Mode132 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used. \n
        'Exp_Times_IR': Sets exposure times [ms] as a list of integers. \n
        'Exp_Times_UV': Sets exposure times [ms] as a list of integers. \n
        'session_duration': Sets the duration [s] of each session using the different exposure times in *Exp_Times*.
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 235000, 'start_date': '0', 'Exp_Times_IR': [1000, 5000, 10000, 20000],
                'Exp_Times_UV': [1000, 5000, 10000, 20000], 'session_duration': 120}
    return settings


def Mode133_settings():
    '''Contain settings related to Mode133 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used. \n
        'Exp_Times_IR': Sets exposure times [ms] as a list of integers. \n
        'Exp_Times_UV': Sets exposure times [ms] as a list of integers. \n
        'session_duration': Sets the duration [s] of each session using the different exposure times in *Exp_Times_UV* and *Exp_Times_IR*.
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 235000, 'start_date': '0',  'Exp_Times_IR': [1000, 5000, 10000, 20000],
                'Exp_Times_UV': [1000, 5000, 10000, 20000], 'session_duration': 120}
    return settings

def Mode160_settings():
    '''Contain settings related to Mode160 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    '''
    settings = {'pointing_altitude': 110000, 'mode_duration': 900, 'start_date': '0'}
    return settings
    



"""
def Mode201_settings():
    '''Contain settings related to Mode201 as a dict.
    
    Keys:
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 70000, 'mode_duration': 600, 'start_date': '0'}
    return settings



def Mode203_settings():
    '''Contain settings related to Mode203 as a dict.
    
    Keys:
        'pitch': Sets the pitch axis maneuver.
        
    Returns:
        settings (:obj:`dict`)
    
    '''
    settings = {'pitch': 180}
    return settings
"""


def PWRTOGGLE_settings():
    '''Contain default parameters related to PWRTOGGLE when treated as a standalone CMD as a dict.
    
    Keys:
        'CONST': Magic Constant 
        
    Returns:
        (:obj:`dict`): parameters
    
    '''
    parameters = {'CONST': 165}
    return parameters

def CCDFlushBadColumns_settings():
    '''Contain default parameters related to CCDFlushBadColumns when treated as a standalone CMD as a dict.
    
    Keys:
        'CCDSEL': CCD select, 1 bit for each CCD (1..127).
        
    Returns:
        (:obj:`dict`): parameters
    
    '''
    parameters = {'CCDSEL': 1}
    return parameters

def CCDBadColumn_settings():
    '''Contain default parameters related to CCDBadColumn when treated as a standalone CMD as a dict.
    
    Keys:
        'CCDSEL': CCD select, 1 bit for each CCD (1..127). \n
        'NBC': Number of uint16 in BC as a uint16. Big Endian. Maximum number is 63. \n
        'BC': Bad Columns as a list of uint16 (4..2047).
        
    Returns:
        (:obj:`dict`): parameters
    
    '''
    parameters = {'CCDSEL': 1, 'NBC': 0, 'BC': []}
    return parameters

def PM_settings():
    '''Returns default parameters related to PM as a dict.
    
    Keys:
        'TEXPMS': Exposure time [ms] for the photometer (int) \n
        'TEXPIMS': Exposure interval time [ms] for the photometer (int)
        
    Returns:
        (:obj:`dict`): parameters
    
    '''
    parameters = {'TEXPMS': 1500, 'TEXPIMS': 2000}
    return parameters

def CCDBIAS_settings():
    '''Returns default parameters related to CCDBIAS as a dict.
    
    Keys:
        'CCDSEL': CCD select, 1 bit for each CCD (1..127). \n
        'VGATE': 8-bit value representing a Voltage (int) \n
        'VSUBST': 8-bit value representing a Voltage (int) \n
        'VRD': 8-bit value representing a Voltage (int) \n
        'VOD': 8-bit value representing a Voltage (int) \n
        
    Returns:
        (:obj:`dict`): parameters
    
    '''
    parameters = {'CCDSEL': 127, 'VGATE': 127, 'VSUBST': 127, 'VRD': 127, 'VOD': 127}
    return parameters



def CCD_macro_settings(CCDMacroSelect):
    
    CCD_settings = {'CCD_48': {}, 'CCD_9': {}, 'CCD_6': {}, 'CCD_64': {} }
    
    if( CCDMacroSelect == 'CustomBinning'):
        CCD_settings['CCD_48'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 0, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 0}
        
        CCD_settings['CCD_9'] = {'PWR': 1, 'WDW': 4, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 3, 'NROW': 170, 'NCSKIP': 0, 'NCBIN': 80, 'NCOL': 24, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_6'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 1500, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 50, 'NROW': 8, 'NCSKIP': 0, 'NCBIN': 50, 'NCOL': 32, 'NCBINFPGA': 0, 'SIGMODE': 1}
    
    
    elif( CCDMacroSelect == 'HighResUV'):
        CCD_settings['CCD_48'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 0}
        
        CCD_settings['CCD_9'] = {'PWR': 1, 'WDW': 4, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 3, 'NROW': 170, 'NCSKIP': 0, 'NCBIN': 80, 'NCOL': 24, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_6'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 1500, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 63, 'NROW': 8, 'NCSKIP': 0, 'NCBIN': 63, 'NCOL': 31, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    elif( CCDMacroSelect == 'HighResIR'):
        CCD_settings['CCD_48'] = {'PWR': 0, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 0, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 0}
        
        CCD_settings['CCD_9'] = {'PWR': 1, 'WDW': 4, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_6'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 1500, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 36, 'NROW': 14, 'NCSKIP': 0, 'NCBIN': 36, 'NCOL': 55, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    elif( CCDMacroSelect == 'BinnedCalibration'):
        CCD_settings['CCD_48'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 0, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 0}
        
        CCD_settings['CCD_9'] = {'PWR': 1, 'WDW': 4, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_6'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 0, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 36, 'NROW': 14, 'NCSKIP': 0, 'NCBIN': 36, 'NCOL': 55, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    elif( CCDMacroSelect == 'FullReadout'):
        CCD_settings['CCD_48'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 110, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2046, 'NCBINFPGA': 0, 'SIGMODE': 0}
        
        CCD_settings['CCD_9'] = {'PWR': 1, 'WDW': 4, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2046, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_6'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 110, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2046, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 0, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2046, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    elif( CCDMacroSelect == 'LowPixel'):
        CCD_settings['CCD_48'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 110, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 0}
        
        CCD_settings['CCD_9'] = {'PWR': 1, 'WDW': 4, 'JPEGQ': 90, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_6'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 110, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCD_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'TEXPMS': 1500, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    return CCD_settings
        
        

#################################################################################
#################################################################################

def FreezeDuration_calculator(pointing_altitude1, pointing_altitude2):
    '''Function that calculates the angle between two tangential altitudes and then calculates
    the time it takes for orbital position angle of a satellite in a circular orbit to change by the same amount.
    
    Arguments:
        pointing_altitude1 (int): First tangential pointing altitude in m
        pointing_altitude2 (int): Second tangential pointing altitude in m
        
    Returns:
        (int): FreezeDuration, Time [s] it takes for the satellites orbital position angle to change 
        by the same amount as the angle between the two tangential pointing altitudes as seen from the satellite.
    '''
    
    TLE2 = getTLE()[1] #Orbits per day
    U = 398600.4418 #Earth gravitational parameter
    MATS_P = 24*3600/float(TLE2[52:63]) #Orbital Period of MATS [s]
    MATS_p = ((MATS_P/2/pi)**2*U)**(1/3) #Semi-major axis of MATS assuming circular orbit [km]
    R_mean = 6371 #Mean Earth radius [km]
    pitch1 = arccos((R_mean+pointing_altitude1/1000)/(MATS_p))/pi*180
    pitch2 = arccos((R_mean+pointing_altitude2/1000 )/(MATS_p))/pi*180
    pitch_angle_difference = abs(pitch1 - pitch2)
    
    #The time it takes for the orbital position angle to change by the same amount as
    #the angle between the pointing axes
    FreezeDuration = round(MATS_P*(pitch_angle_difference)/360,1)
    
    return FreezeDuration
