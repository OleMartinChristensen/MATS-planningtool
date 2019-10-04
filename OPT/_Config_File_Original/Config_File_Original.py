# -*- coding: utf-8 -*-
"""Contains functions that return settings for the Operational Planning Tool. A ConfigFile must be chosen
by calling *OPT.Set_ConfigFile()* and must be visible in *sys.path*.
    
"""


from OPT import _Globals, _Library


def Logger_name():
    '''Returns the name of the shared logger.
    
    Returns:
        (str): Logger_name
    
    '''
    
    Logger_name = "OPT_logger"
    
    return Logger_name


def Version():
    ''''Returns the version ID of this Configuration File.
    
    The version ID should only be changed when the default *Configuration File*, _ConfigFile in OPT, is changed.
    
    Returns:
        (str): version_name 
    
    '''
    version_ID = 'Original'
    return version_ID


def Scheduling_priority():
    '''Returns the Modes (except *Operational Science Modes* (Mode 1,2,5)) and CMDs planned to be schedueled in a *Science Mode Timeline* using *Timeline_gen*.
    
    **Available choices are:** \n
    
        - 'PWRTOGGLE',
        - 'ArgEnableYawComp',
        - 'CCDFlushBadColumns',
        - 'CCDBadColumn',
        - 'PM',
        - 'HTR',
        - 'CCDBIAS', 
        - 'Mode100', 
        - 'Mode110', 
        - 'Mode120', 
        - 'Mode121', 
        - 'Mode122', 
        - 'Mode123', 
        - 'Mode124', 
        - 'Mode131', 
        - 'Mode132', 
        - 'Mode133', 
        - 'Mode130', 
        - 'Mode134'
     
    The order of which the Modes/CMDs appear is also their priority order (top-down).
    The name must be equal to the name of a function imported in the *_Timeline_generator.Modes.Modes_Header* module.
    
    Returns:
        (:obj:`list` of :obj:`str`): Modes_priority
    
    '''
    Modes_priority = [
            'PWRTOGGLE',
            'ArgEnableYawComp',
            'CCDFlushBadColumns',
            'CCDBadColumn',
            'CCDBIAS',
            'PM',
            'Mode130', 
            'Mode124',
            'Mode120',
            'Mode123',
            'Mode121',
            'Mode110',
            'Mode100',
            'Mode132',
            'Mode133',
            'Mode122',
            'Mode131',
            'Mode134']
    
    return Modes_priority


def getTLE():
    '''Returns the TLE as two strings in a list.
    
    Returns:
        (:obj:`list` of :obj:`str`): First Element is the first TLE row, and the second Element is the second row.
    
    '''
    TLE1 = '1 26702U 01007A   18231.91993126  .00000590  00000-0  00000-0 0  9994'
    TLE2= '2 26702 97.61000 65.95030 0000001 0.000001 359.9590 14.97700580100  4'
    #TLE1 = '1 26702U 01007A   09264.68474097 +.00000336 +00000-0 +35288-4 0  9993'
    #TLE2 = '2 26702 097.7067 283.5904 0004656 126.2204 233.9434 14.95755636467886'
    
    "OHB TLE"
    TLE1 = '1 54321U 19100G   20172.75043981 0.00000000  00000-0  75180-4 0  0014'
    TLE2 = '2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010'
    
    "OHB TLE timeshifted by 2 sec"
    #TLE1 = '1 54321U 19100G   20172.75041666 0.00000000  00000-0  75180-4 0  0012'
    #TLE2 = '2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010'
    
    
    return [TLE1, TLE2]




def Timeline_settings():
    '''Returns settings related to a *Science Mode Timeline* as a whole.
    
    **Keys:**
        'start_date': Is usually set to *_Globals.StartTime*, where *_Globals.StartTime* is set by running *Set_ConfigFile*. Sets the starting date of the timeline (str), (example: '2018/9/3 08:00:40').  \n
        'duration': Sets the duration [s] of the timeline. Will drastically change the runtime of *Timeline_gen*. A runtime of around 15 min is estimated for a duration of 1 week (int) \n
        'leapSeconds': Sets the amount of leap seconds for GPS time conversion. MUST BE UPDATED EACH TIME A LEAP SECOND IS ADDED TO UTC (int). \n
        'GPS_epoch': Sets the epoch of the GPS time as a str, (example: '1980/1/6'). This should not be changed! \n
        
        'Mode1_2_5_minDuration': Minimum amount of available time needed, inbetween scheduled Modes/CMDs in a *Science Mode Timeline*, for the scheduling of *Operational Science Modes* when running *Timeline_gen* [s]. \n
        'mode_separation': Time in seconds for an added buffer when determining the duration of a Mode/CMD to make sure that CMDs from different Modes does not collide with each other. Must be larger than the number of CMDs in any macro multiplied by Timeline_settings['command_separation']. (int) \n
        'CMD_duration': Sets the amount of time scheduled for separate PayloadCMDs when using *Timeline_gen*. Should be large enough to allow any separate CMD to finish processing.  (int) \n
        
        'yaw_correction': Determines if yaw correction shall be used for the duration of the timeline. Mainly impacts simulations of MATS's pointing as when I am writing this there is no actual CMD to enable yaw-correction. (bool) \n
        'yaw_amplitude': Amplitude of the yaw function (float). \n
        'yaw_phase': Phase of the yaw function (float). \n
        'Choose_Operational_Science_Mode': Set to 1, 2, or 5 to choose either Mode1, Mode2, or Mode5 as the *Operational Science Mode*. Set to 0 to schedule either Mode1 or Mode2 depending of the time of the year.
        'LP_pointing_altitude': Sets altitude of LP in meters for the timeline. Used to set the pointing altitude of *Operational Science Modes* and to calculate the duration of attitude freezes (because attitude freezes last until the pointing altitude is once again set to this value).  (int) \n
        
        'CMD_separation': Changes the separation in time [s] between commands that are scheduled in *XML_gen*. If set too large without increasing Timeline_settings['mode_separation'], it is possible that not enough time is scheduled for the duration of Modes, causing Modes to overlap in time. (float) \n
        'pointing_stabilization': The maximum time it takes for an attitude change to stabilize [s]. Used before scheduling certain Commands in *XML_gen* to make sure that the attitude has been stabilized after running *TC_acfLimbPointingAltitudeOffset*. Also impact the estimated duration of Science Modes in *Timeline_gen*. (int) \n
        'CCDSYNC_ExtraOffset': Extra offset time [ms] that is added to an estimated ReadoutTime when calculating TEXPIOFS for the CCD Synchronize CMD. (int) \n
        'CCDSYNC_ExtraIntervalTime': Extra time [ms] that is added to the calculated Exposure Interval Time (for example when calculating arguments for the CCD Synchronize CMD or nadir TEXPIMS). (int) \n
        
    Returns:
        (:obj:`dict`): Timeline_settings
    '''
    Timeline_settings = {'start_date': _Globals.StartTime, 'duration': 1*4*3600, 
                       'leapSeconds': 18, 'GPS_epoch': '1980/1/6', 'Mode1_2_5_minDuration': 300, 'mode_separation': 15,
                       'CMD_duration': 30, 'yaw_correction': True, 'yaw_amplitude': -3.8, 'yaw_phase': -20, 
                       'Choose_Operational_Science_Mode': 0, 'LP_pointing_altitude': 92500, 
                       'CMD_separation': 1, 'pointing_stabilization': 60, 'CCDSYNC_ExtraOffset': 50, 'CCDSYNC_ExtraIntervalTime': 200}
    
    
    return Timeline_settings


def Operational_Science_Mode_settings():
    '''Returns settings related to Operational Science Modes (Mode1, 2, and 5).
    
    **Keys:**
        'lat': Applies only to Mode1! Sets in degrees the latitude (+ and -) that the LP crosses that causes the UV exposure to swith on/off. (int) \n
        'log_timestep': Sets the frequency of data being logged [s] for Mode1-2. Only determines how much of simulated data is logged for debugging purposes. (int) \n
        'timestep': Sets the timestep [s] of the XML generator simulation of Mode1-2. Will impact accuracy of command generation but also drastically changes the runtime of XML-gen. (int) \n
        'Choose_CCDMacro': Applies only to Mode5! Sets the CCD macro to be used by Mode5. Used as input to *CCD_macro_settings* (str).
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'lat': 45, 'log_timestep': 800, 'timestep': 8, 'Choose_CCDMacro': 'CustomBinning'}
    return settings

"""
def Mode5_settings():
    '''Returns settings related to Mode5.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. If set to 0, Timeline_settings['LP_pointing_altitude'] will be used (int) 
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    
    settings = {'pointing_altitude': 110000}
    
    return settings

"""

def Mode100_settings():
    '''Returns settings related to Mode100.
    
    **Keys in returned dict:**
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
    '''Returns settings related to Mode110.
    
    **Keys in returned dict:**
        'pointing_altitude_from': Sets in meters the starting altitude of the sweep. (int) \n
        'pointing_altitude_to': Sets in meters the ending altitude of the sweep. (int) \n
        'sweep_rate': Sets the rate of the sweep in m/s. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline_settings['start_date'] will be used.
        'Exp_Time_IR': Sets exposure time [ms] of the IR CCDs. (int) \n
        'Exp_Time_UV': Sets exposure time [ms] of the UV CCDs. (int) \n
        
    Returns:
        (:obj:`dict`): settings
        
    '''
    settings = {'pointing_altitude_from': 40000, 'pointing_altitude_to': 150000, 'sweep_rate': 500, 'start_date': '0', 
                'Exp_Time_IR': 5000, 'Exp_Time_UV': 3000}
    return settings


def Mode120_settings():
    '''Returns settings related to Mode120.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'V_offset': Used only in *Timeline_gen*. Sets the Vertical-offset angle (position in FOV) in degrees for the star, when the attitude freeze command is scheduled. (int) \n
        'H_offset': Used only in *Timeline_gen*. Sets the maximum Horizontal-offset angle in degrees that determines if stars are visible. (int) \n
        'Vmag': Used only in *Timeline_gen*. Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2'). \n
        'timestep': Used only in *Timeline_gen*. Sets timestep used in scheduling simulation [s]. Will impact scheduling accuracy. (int) \n
        'TimeSkip': Used only in *Timeline_gen*. Set the amount of seconds to skip ahead after one complete orbit is simulated. Will drastically change the runtime of the simulation. (int) \n
        'log_timestep': Sets the timestep of data being logged [s]. Only determines how much of simulated data is logged for debugging purposes.. (int) \n
        'automatic': Used only in *Timeline_gen*. Sets if 'start_date' will be calculated or user provided. True for calculated and False for user provided. (bool) \n
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freezes. (int) \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with *Timeline_settings['LP_pointing_altitude']* (Normally around 50 s). (int) \n
        'SnapshotTime': Sets in seconds the time, from the start of the attitude freeze, to when the first Snapshot is taken. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. (int)
        
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 230000, 'V_offset': 0, 'H_offset': 2.5, 'Vmag': '<2', 'timestep': 2, 'TimeSkip': 3600*4, 'log_timestep': 3600, 
                      'automatic': True, 'start_date': '0', 'freeze_start': 120, 
                      'freeze_duration': 0, 'SnapshotTime': 3, 'SnapshotSpacing': 3}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = _Library.FreezeDuration_calculator( Timeline_settings()['LP_pointing_altitude'], settings['pointing_altitude'], getTLE()[1])
    
    return settings


def Mode121_122_123_settings():
    '''Returns settings shared between Mode121-123.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'H_FOV': Used only in *Timeline_gen*. Sets full Horizontal FOV of the Limb instrument in degrees. Used to determine if stars are visible. (float) \n
        'V_FOV': Used only in *Timeline_gen*. Sets full Vertical FOV of the Limb instrument in degrees. Used to determine if stars are visible. (float) \n
        'Vmag': Used only in *Timeline_gen*. Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2'). \n
        'timestep': Used only in *Timeline_gen*. Set timestep used in scheduling simulation [s]. Will impact scheduling accuracy. (int) \n
        'TimeSkip': Used only in *Timeline_gen*. Set the amount of seconds to skip ahead after one complete orbit is simulated. Will drastically change the runtime of the simulation. (float) \n
        'log_timestep': Sets the timestep of data being logged [s]. Only determines how much of simulated data is logged for debugging purposes. (int) \n
        'freeze_start': Sets in seconds, the time from start of the Mode to when the attitude freezes. (int) \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with *Timeline_settings['LP_pointing_altitude']* (Normally around 50 s). (int) \n
        'SnapshotTime': Sets in seconds the time, from the start of the attitude freeze, to when the first Snapshot is taken. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. (int)
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 230000, 'H_FOV': 5.67, 'V_FOV': 0.91, 'Vmag': '<4', 'timestep': 5, 'TimeSkip': 3600*4, 'log_timestep': 3600, 
                      'freeze_start': 120, 
                      'freeze_duration': 0, 'SnapshotTime': 2, 'SnapshotSpacing': 3}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = _Library.FreezeDuration_calculator( Timeline_settings()['LP_pointing_altitude'], settings['pointing_altitude'], getTLE()[1])
    
    
    return settings


def Mode121_settings():
    '''Returns settings related to Mode121.
    
    **Keys in returned dict:**
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'automatic': Used only in *Timeline_gen*. Sets if 'start_date' will be calculated or user provided. True for calculated and False for user provided. (bool) \n
        
    Returns:
        (:obj:`dict`): settings
    '''
    
    Settings = {'start_date': '0', 'automatic': True}
    CommonSettings = Mode121_122_123_settings()
    
    settings = {**CommonSettings, **Settings}
    
    return settings


def Mode122_settings():
    '''Returns settings related to Mode122.
    
    **Keys in returned dict:**
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'automatic': Used only in *Timeline_gen*. Sets if 'start_date' will be calculated or user provided. True for calculated and False for user provided. (bool) \n
        'Exp_Time_IR': Sets exposure time [ms] of the IR CCDs. (int) \n
        'Exp_Time_UV': Sets exposure time [ms] of the UV CCDs. (int) \n
    
    Returns:
        (:obj:`dict`): settings
    '''
    
    Settings = {'start_date': '0', 'automatic': True, 'Exp_Time_IR': 5000, 'Exp_Time_UV': 3000}
    CommonSettings = Mode121_122_123_settings()
    
    settings = {**CommonSettings, **Settings}
    
    return settings


def Mode123_settings():
    '''Returns settings related to Mode123.
    
    **Keys in returned dict:**
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'automatic': Used only in *Timeline_gen*. Sets if 'start_date' will be calculated or user provided. True for calculated and False for user provided. (bool) \n
        'Exp_Time_IR': Sets exposure time [ms] of the IR CCDs. (int) \n
        'Exp_Time_UV': Sets exposure time [ms] of the UV CCDs. (int) \n
    
    Returns:
        (:obj:`dict`): settings
    '''
    
    Settings = {'start_date': '0', 'automatic': True, 'Exp_Time_IR': 5000, 'Exp_Time_UV': 3000}
    CommonSettings = Mode121_122_123_settings()
    
    settings = {**CommonSettings, **Settings}
    
    return settings
    


def Mode124_settings():
    '''Returns settings related to Mode124.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'V_offset': Used only in *Timeline_gen*. Sets the Vertical-offset angle (position in FOV) in degrees for the star , when the attitude freeze command is scheduled. (float) \n
        'H_offset': Used only in *Timeline_gen*. Sets the maximum H-offset angle from the optical axis in degrees that determines if the Moon is available. (float) \n
        'timestep':  Used only in *Timeline_gen*. Sets in seconds the timestep during scheduling simulation [s]. Will impact scheduling accuracy. (int) \n
        'log_timestep': Sets the timestep of data being logged [s]. Only determines how much of simulated data is logged for debugging purposes. (int) \n
        'automatic':  Used only in *Timeline_gen*. Sets if the mode date is to be calculated or user provided. True for calculated or False for user provided. (bool) \n
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freeze command is scheduled. (int) \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with *Timeline_settings['LP_pointing_altitude']*. (int) \n
        'SnapshotTime': Sets in seconds the time, from the start of the attitude freeze, to when the first Snapshot is taken. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. (int)
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 230000, 'V_offset': 0, 'H_offset': 3+2.5, 'timestep': 2, 'log_timestep': 1200, 
                      'automatic': True, 'start_date': '0', 'freeze_start': 120, 'freeze_duration': 0, 
                      'SnapshotTime': 2, 'SnapshotSpacing': 3}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = _Library.FreezeDuration_calculator( Timeline_settings()['LP_pointing_altitude'], settings['pointing_altitude'], getTLE()[1])
    
    return settings


def Mode130_settings():
    '''Returns settings related to Mode130.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    '''
    settings = {'pointing_altitude': 230000, 'SnapshotSpacing': 2, 'start_date': '0'}
    return settings


def Mode131_settings():
    '''Returns settings related to Mode131.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    '''
    settings = {'pointing_altitude': 230000, 'mode_duration': 120, 'start_date': '0'}
    return settings


def Mode132_settings():
    '''Returns settings related to Mode132.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used. \n
        'Exp_Times_IR': Sets exposure times [ms] as a list of integers. Shall have equal length to 'Exp_Times_UV'.  \n
        'Exp_Times_UV': Sets exposure times [ms] as a list of integers. Shall have equal length to 'Exp_Times_IR'. \n
        'session_duration': Sets the duration [s] of each session using the different exposure times in *Exp_Times*. (int)
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 230000, 'start_date': '0', 'Exp_Times_IR': [1000, 5000, 10000, 20000],
                'Exp_Times_UV': [1000, 5000, 10000, 20000], 'session_duration': 120}
    return settings


def Mode133_settings():
    '''Returns settings related to Mode133.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used. \n
        'Exp_Times_IR': Sets exposure times [ms] as a list of integers. Shall have equal length to 'Exp_Times_UV'.  \n
        'Exp_Times_UV': Sets exposure times [ms] as a list of integers. Shall have equal length to 'Exp_Times_IR'. \n
        'session_duration': Sets the duration [s] of each session using the different exposure times in *Exp_Times_UV* and *Exp_Times_IR*. (int)
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 230000, 'start_date': '0',  'Exp_Times_IR': [1000, 5000, 10000, 20000],
                'Exp_Times_UV': [1000, 5000, 10000, 20000], 'session_duration': 120}
    return settings

def Mode134_settings():
    '''Returns settings related to Mode134.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    '''
    settings = {'pointing_altitude': 110000, 'mode_duration': 900, 'start_date': '0'}
    return settings
    



"""
def Mode201_settings():
    '''Returns settings related to Mode201.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline start_date will be used.
    
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'pointing_altitude': 70000, 'mode_duration': 600, 'start_date': '0'}
    return settings



def Mode203_settings():
    '''Returns settings related to Mode203.
    
    **Keys in returned dict:**
        'pitch': Sets the pitch axis maneuver.
        
    Returns:
        settings (:obj:`dict`)
    
    '''
    settings = {'pitch': 180}
    return settings
"""


def PWRTOGGLE_settings():
    '''Returns settings related to the PWRTOGGLE CMD.
    
    **Keys in returned dict:**
        'CONST': Magic Constant (int).
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'CONST': 165}
    return settings

def CCDFlushBadColumns_settings():
    '''Returns settings related to the CCDFlushBadColumns CMD.
    
    **Keys in returned dict:**
        'CCDSEL': CCD select, 1 bit for each CCD (1..127). (int)
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'CCDSEL': 1}
    return settings

def CCDBadColumn_settings():
    '''Returns settings related to CCDBadColumn CMD.
    
    **Keys in returned dict:**
        'CCDSEL': CCD select, 1 bit for each CCD (1..127). (int) \n
        'NBC': Number of uint16 in BC as a uint16. Big Endian. Maximum number is 63. (int) \n
        'BC': Bad Columns as a list of uint16 (4..2047).
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'CCDSEL': 1, 'NBC': 0, 'BC': []}
    return settings

def PM_settings():
    '''Returns settings related to the PM (photometer) CMD.
    
    **Keys in returned dict:**
        'TEXPMS': Exposure time [ms] for the photometer (int) \n
        'TEXPIMS': Exposure interval time [ms] for the photometer (int)
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'TEXPMS': 1500, 'TEXPIMS': 2000}
    return settings

def CCDBIAS_settings():
    '''Returns settings related to the CCDBIAS CMD.
    
    **Keys in returned dict:**
        'CCDSEL': CCD select, 1 bit for each CCD (1..127). (int) \n
        'VGATE': 8-bit value representing a Voltage (int) \n
        'VSUBST': 8-bit value representing a Voltage (int) \n
        'VRD': 8-bit value representing a Voltage (int) \n
        'VOD': 8-bit value representing a Voltage (int) \n
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'CCDSEL': 127, 'VGATE': 0, 'VSUBST': 128, 'VRD': 126, 'VOD': 100}
    return settings



def CCD_macro_settings(CCDMacroSelect):
    '''Returns CCD settings for a specific CCD macro.
    
    Each key in the output represents settings for a corresponding CCDSEL argument.
    TEXPIMS for the CCDs (except nadir) is not changeable as they need to be synchronized with a calculated TEXPIMS to prevent streaks.
    
    **Keys in returned dict:**
        'CCDSEL_16': Represents settings for UV1 (CCD5) \n
        'CCDSEL_32': Represents settings for UV2 (CCD6) \n
        'CCDSEL_1': Represents settings for IR1 (CCD1) \n
        'CCDSEL_8': Represents settings for IR2 (CCD4) \n
        'CCDSEL_2': Represents settings for IR4 (CCD2) \n
        'CCDSEL_4': Represents settings for IR3 (CCD3) \n
        'CCDSEL_64': Represents settings for Nadir (CCD6) \n
        
        
    Arguments:
        CCDMacroSelect (str): Specifies for which CCD macro, settings are returned for. 'CustomBinning', 'HighResUV', 'HighResIR', 'BinnedCalibration', 'FullReadout', 'LowPixel'.
        
    Returns:
        (:obj:`dict`): CCD_settings
    
    '''
    
    CCD_settings = {'CCDSEL_16': {}, 'CCDSEL_32': {}, 'CCDSEL_1': {}, 'CCDSEL_8': {}, 'CCDSEL_2': {}, 'CCDSEL_4': {}, 'CCDSEL_64': {} }
    
    if( CCDMacroSelect == 'CustomBinning'):
        CCD_settings['CCDSEL_16'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_32'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_1'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 3, 'NROW': 170, 'NCSKIP': 0, 'NCBIN': 80, 'NCOL': 24, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_8'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 3, 'NROW': 170, 'NCSKIP': 0, 'NCBIN': 80, 'NCOL': 24, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_2'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_4'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 1500, 'TEXPIMS': 2000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 50, 'NROW': 8, 'NCSKIP': 0, 'NCBIN': 50, 'NCOL': 32, 'NCBINFPGA': 0, 'SIGMODE': 1}
    
    
    elif( CCDMacroSelect == 'HighResUV'):
        CCD_settings['CCDSEL_16'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_32'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_1'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 3, 'NROW': 170, 'NCSKIP': 0, 'NCBIN': 80, 'NCOL': 24, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_8'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 3, 'NROW': 170, 'NCSKIP': 0, 'NCBIN': 80, 'NCOL': 24, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_2'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_4'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 1500, 'TEXPIMS': 2000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 63, 'NROW': 8, 'NCSKIP': 0, 'NCBIN': 63, 'NCOL': 31, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    elif( CCDMacroSelect == 'HighResIR'):
        CCD_settings['CCDSEL_16'] = {'PWR': 0, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 0, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_32'] = {'PWR': 0, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 0, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_1'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_8'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_2'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_4'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 1500, 'TEXPIMS': 2000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 36, 'NROW': 14, 'NCSKIP': 0, 'NCBIN': 36, 'NCOL': 55, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    elif( CCDMacroSelect == 'BinnedCalibration'):
        CCD_settings['CCDSEL_16'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_32'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_1'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_8'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 2, 'NROW': 255, 'NCSKIP': 0, 'NCBIN': 40, 'NCOL': 50, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_2'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_4'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 6, 'NROW': 85, 'NCSKIP': 0, 'NCBIN': 200, 'NCOL': 8, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_64'] = {'PWR': 1, 'WDW': 128, 'JPEGQ': 90, 'SYNC': 0, 'TEXPMS': 0, 'TEXPIMS': 2000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 36, 'NROW': 14, 'NCSKIP': 0, 'NCBIN': 36, 'NCOL': 55, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    elif( CCDMacroSelect == 'FullReadout'):
        CCD_settings['CCDSEL_16'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2047, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_32'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2047, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_1'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2047, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_8'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2047, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_2'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2047, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_4'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2047, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_64'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 0, 'TEXPIMS': 62800, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 1, 'NROW': 511, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 2047, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    elif( CCDMacroSelect == 'LowPixel'):
        CCD_settings['CCDSEL_16'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_32'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 3000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_1'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_8'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_2'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_4'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 5000, 'GAIN': 0, 'NFLUSH': 1023, 
                                'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        CCD_settings['CCDSEL_64'] = {'PWR': 1, 'WDW': 7, 'JPEGQ': 110, 'SYNC': 0, 'TEXPMS': 0, 'TEXPIMS': 2000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 63, 'NROW': 7, 'NCSKIP': 0, 'NCBIN': 255, 'NCOL': 7, 'NCBINFPGA': 0, 'SIGMODE': 1}
        
        
    return CCD_settings
        
        

#################################################################################
#################################################################################
"""
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
    FreezeDuration = int(round(MATS_P*(pitch_angle_difference)/360,0))
    
    return FreezeDuration
"""