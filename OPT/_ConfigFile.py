# -*- coding: utf-8 -*-
"""Contains functions that return settings for the Operational Planning Tool. A ConfigFile must be chosen
by calling *OPT.Set_ConfigFile()* and it must be visible in *sys.path*.
    
"""


from OPT import _Globals, _Library


def Logger_name():
    """Returns the name of the shared logger.
    
    Returns:
        (str): Logger_name
    
    """

    Logger_name = "OPT_logger"

    return Logger_name


def Version():
    """'Returns the version ID of this Configuration File.
    
    The version ID should only be changed when the default *Configuration File*, _ConfigFile in OPT, is changed.
    
    Returns:
        (str): version_name 
    
    """
    version_ID = "Original"
    return version_ID


def Scheduling_priority():
    """Returns the Modes (except *Operational Science Modes* (Mode 1,2,5)) and StartUpCMDs planned to be schedueled in a *Science Mode Timeline* using *Timeline_gen*.
    
    **Available choices are:** \n
    
        - 'ArgEnableYawComp',
        - 'Payload_Power_Toggle',
        - 'TurnONCCDs',
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
     
    The order of which the Modes/StartUpCMDs appear is also their priority order (top-down). \n
    Repeat Modes/CMDs to schedule them several times, though there is currently not feature that allows multiple Modes/CMDs 
    to be scheduled with different settings. Some settings that does not affect the duration of the Mode can still be changed manually afterwards in the generated Science Mode Timeline.
    Each string must be equal to the name of a function imported in the *_Timeline_generator.Modes.Modes_Header* module. \n
    
    'Payload_Power_Toggle', 'TurnONCCDs', 'ArgEnableYawComp', 'CCDFlushBadColumns', 'CCDBadColumn', 'PM', 'CCDBIAS' are called StartUpCMDs and are recommended to run at the start of each 
    timeline, as they together reset and initialize the intrument. If "HTR" is scheduled, arguments is needed to be entered manually into the created *Science Mode Timeline* because of safety reasons. \n
    
    'Payload_Power_Toggle' is a OHB procedure that safely power toggles the instrument. \n
    
    'TurnONCCDs' is a special CCD macro that turns on the CCDs.
    
    Returns:
        (:obj:`list` of :obj:`str`): Modes_priority
    
    """

    Modes_priority = [
        "Payload_Power_Toggle",
        "ArgEnableYawComp",
        "PM",
        "TurnONCCDs",
        "CCDFlushBadColumns",
        "CCDBadColumn",
        "CCDBIAS",
        "Mode124",
        "Mode120",
        "Mode120",
        "Mode123",
        "Mode121",
        "Mode110",
        "Mode100",
        "Mode130",
        "Mode132",
        "Mode133",
        "Mode122",
        "Mode131",
        "Mode134",
    ]

    return Modes_priority


def getTLE():
    """Returns the TLE as two strings in a list.
    
    Returns a TLE from the *_Globals* module if *Set_ConfigFile* has been ran with a TLE as input.
    Otherwise returns any TLE values stated here.
    
    Returns:
        (:obj:`list` of :obj:`str`): First Element is the first TLE row, and the second Element is the second row.
    
    """

    if not (_Globals.TLE == ("", "")):
        TLE1 = _Globals.TLE[0]
        TLE2 = _Globals.TLE[1]
    else:
        "If no TLE has been chosen with *Set_ConfigFile*, these values are used instead."
        TLE1 = "1 54321U 19100G   20172.75043981 0.00000000  00000-0  75180-4 0  0014"
        TLE2 = "2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010"

    return [TLE1, TLE2]


def Timeline_settings():
    """Returns settings related to a *Science Mode Timeline* as a whole.
    
    **Keys:**
        'start_date': Sets the starting date of the timeline (str), (example: '2018/9/3 08:00:40'). Contains _Globals.StartTime if *Set_ConfigFile* has been ran with a start date as an input. Otherwise any value stated here.  \n
        'duration': Sets the duration [s] of the timeline. Will drastically change the runtime of *Timeline_gen*. A runtime of around 15 min is estimated for a duration of 1 week (int) \n
        
        'Mode1_2_5_minDuration': Minimum amount of available time needed, inbetween scheduled Modes/CMDs in a *Science Mode Timeline*, to allow the scheduling of *Operational Science Modes* when running *Timeline_gen* [s]. \n
        'mode_separation': Time in seconds for an added buffer when determining the duration of a Mode/CMD. (int) \n
        'CMD_duration': Sets the amount of time scheduled for separate PayloadCMDs when using *Timeline_gen*. Should be large enough to allow any separate CMD to finish processing.  (int) \n
        
        'yaw_correction': Determines if yaw correction shall be used for the duration of the timeline. Mainly impacts simulations of MATS's pointing. But also determines the argument of the ArgEnableYawComp CMD. (bool) \n
        'yaw_amplitude': Amplitude of the yaw function, A*cos(argument_of_latitude - B - phase), where B is angle between optical axis and negative velocity vector in the orbital plane. (float) \n
        'yaw_phase': Phase of the yaw function, A*cos(argument_of_latitude - B - phase), where B is angle between optical axis and negative velocity vector in the orbital plane. (float) \n
        'Choose_Operational_Science_Mode': Set to 1, 2, or 5 to choose either Mode1, Mode2, or Mode5 as the *Operational Science Mode*. Set to 0 to schedule either Mode1 or Mode2 depending of the time of the year.
        'StandardPointingAltitude': Sets pointing altitude in meters for the timeline. Used to set the pointing altitude of *Operational Science Modes* and to calculate the duration of attitude freezes (because attitude freezes last until the pointing altitude is reorientated to this value).  (int) \n
        
        'CMD_separation': Changes the separation in time [s] between commands that are scheduled in *XML_gen*. If set too large, it is possible that not enough time is scheduled for the duration of Modes, causing Modes to overlap in time. Impacts the estimated duration of certain Science Modes in *Timeline_gen*. (float) \n
        'pointing_stabilization': The maximum time it takes for an attitude change to stabilize [s]. Used before scheduling certain CMDs in *XML_gen* to make sure that the attitude has been stabilized after running *TC_acfLimbPointingAltitudeOffset*. Impacts the estimated duration of Science Modes in *Timeline_gen*. (int) \n
        'CCDSYNC_ExtraOffset': Extra offset time [ms] that is added to an estimated ReadoutTime when calculating TEXPIOFS for the CCD Synchronize CMD. (int) \n
        'CCDSYNC_ExtraIntervalTime': Extra time [ms] that is added to the calculated Exposure Interval Time (for example when calculating arguments for the CCD Synchronize CMD or nadir TEXPIMS). (int) \n
        'CCDSYNC_Waittime': Time to wait after running CCDSYNC to allow for the synchronization to be set correctly (should be longer than longest TEXPIMS) 
        
    Returns:
        (:obj:`dict`): Timeline_settings
    """

    if _Globals.StartTime != None:
        StartTime = _Globals.StartTime
    else:
        "If no start date has been chosen with *Set_ConfigFile*, this value is used instead."
        StartTime = "2020/6/20 18:32:42"

    Timeline_settings = {
        "start_date": StartTime,
        "duration": 1 * 8 * 3600,
        "Mode1_2_5_minDuration": 300,
        "mode_separation": 15,
        "CMD_duration": 30,
        "yaw_correction": True,
        "yaw_amplitude": -3.8,
        "yaw_phase": 20,
        "Choose_Operational_Science_Mode": 1,
        "StandardPointingAltitude": 92500,
        "CMD_separation": 2,
        "pointing_stabilization": 100,
        "CCDSYNC_ExtraOffset": 200,
        "CCDSYNC_ExtraIntervalTime": 500,
        "CCDSYNC_Waittime": 30,
    }

    return Timeline_settings


def Operational_Science_Mode_settings():
    """Returns settings related to Operational Science Modes (Mode1, 2, and 5).
    
    **Keys:**
        'lat': Applies only to Mode1! Sets in degrees the latitude (+ and -) that the LP crosses that causes the UV exposure to swith on/off. (int) \n
        'log_timestep': Used only in *XML_gen*. Sets the frequency of data being logged [s] for Mode1-2. Only determines how much of simulated data is logged for debugging purposes. (int) \n
        'timestep': Sets the timestep [s] of the XML generator simulation of Mode1-2. Will impact accuracy of command generation but also drastically changes the runtime of XML-gen. (int) \n
        'Choose_Mode5CCDMacro': Applies only to Mode5! Sets the CCD macro to be used by Mode5. Used as input to *CCD_macro_settings* in the ConfigFile (str).
        
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {
        "lat": 45,
        "log_timestep": 800,
        "timestep": 8,
        "Choose_Mode5CCDMacro": "CustomBinning",
    }
    return settings


"""
def Mode5_settings():
    '''Returns settings related to Mode5.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. If set to 0, Timeline_settings['StandardPointingAltitude'] will be used (int) 
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    
    settings = {'pointing_altitude': 110000}
    
    return settings

"""


def Mode100_settings():
    """Returns settings related to Mode100.
    
    **Keys in returned dict:**
        'pointing_altitude_from': Sets in meters the starting altitude. Part in determining the estimated duration of the mode. (int) \n
        'pointing_altitude_to': Sets in meters the ending altitude. Part in determining the estimated duration of the mode. (int) \n
        'pointing_altitude_interval': Sets in meters the interval size of each succesive pointing. Part in determining the estimated duration of the mode. (int) \n
        'pointing_duration': Sets the time [s] from attitude stabilization until next pointing command. Part in determining the estimated duration of the mode. (int) \n
        'Exp_Time_IR': Sets starting exposure time [ms] as a integer. \n
        'Exp_Time_UV': Sets starting exposure time [ms] as a integer. \n
        'ExpTime_step': Sets in ms the interval size of both ExpTimeUV and ExpTimeIR for each succesive pointing. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline_settings['start_date'] will be used.
        
    Returns:
        (:obj:`dict`): settings
            
    """
    settings = {
        "pointing_altitude_from": 40000,
        "pointing_altitude_to": 150000,
        "pointing_altitude_interval": 5000,
        "pointing_duration": 60,
        "Exp_Time_UV": 1000,
        "Exp_Time_IR": 1000,
        "ExpTime_step": 500,
        "start_date": "0",
    }
    return settings


def Mode110_settings():
    """Returns settings related to Mode110.
    
    **Keys in returned dict:**
        'pointing_altitude_from': Sets in meters the starting altitude of the sweep. Part in determining the estimated duration of the mode. (int) \n
        'pointing_altitude_to': Sets in meters the ending altitude of the sweep. Part in determining the estimated duration of the mode. (int) \n
        'sweep_rate': Sets the rate of the sweep in m/s. Part in determining the estimated duration of the mode. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline_settings['start_date'] will be used.
        'Exp_Time_IR': Sets exposure time [ms] of the IR CCDs. (int) \n
        'Exp_Time_UV': Sets exposure time [ms] of the UV CCDs. (int) \n
        
    Returns:
        (:obj:`dict`): settings
        
    """
    settings = {
        "pointing_altitude_from": 40000,
        "pointing_altitude_to": 150000,
        "sweep_rate": 500,
        "start_date": "0",
        "Exp_Time_IR": 5000,
        "Exp_Time_UV": 3000,
    }
    return settings


def Mode120_settings():
    """Returns settings related to Mode120.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'V_offset': Used only in *Timeline_gen*. Sets the Vertical-offset angle (position in FOV) in degrees for the star to have passed, when the attitude freeze command is scheduled. 
        Multiple values can be set but additional values will only be used when Mode120 is scheduled several times. (list of int) \n
        'H_offset': Used only in *Timeline_gen*. Sets the maximum Horizontal-offset angle in degrees that determines if stars are visible. (int) \n
        'Vmag': Used only in *Timeline_gen*. Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2'). Drastically changes the runtime. \n
        'TimeToConsider': Used only in *Timeline_gen*. Sets the time in seconds for which scheduling is considered. Used to plan star calibration at the start of each timeline (useful as TLE accuracy deteriorates). Drastically affects simulation time. (int) \n
        'timestep': Used only in *Timeline_gen*. Sets timestep used in scheduling simulation [s]. Will impact scheduling accuracy. (int) \n
        'TimeSkip': Used only in *Timeline_gen*. Set the amount of seconds to skip ahead after one complete orbit is simulated. Will drastically change the runtime of the simulation. (int) \n
        'log_timestep': Used only in *Timeline_gen*. Sets the timestep of data being logged [s]. Only determines how much of simulated data is logged for debugging purposes.. (int) \n
        'automatic': Used only in *Timeline_gen*. Sets if 'start_date' will be calculated or user provided. True for calculated and False for user provided. (bool) \n
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freezes. Part in determining the estimated duration of the mode. (int) \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. Part in determining the estimated duration of the mode. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with *Timeline_settings['StandardPointingAltitude']* (Normally around 50 s). (int) \n
        'SnapshotTime': Sets in seconds the time, from the start of the attitude freeze, to when the first Snapshot is taken. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. (int) \n
        'CCDSELs': List of CCDSEL arguments (except nadir) for which to take snapshots with. (list of int)
    
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {
        "pointing_altitude": 230000,
        "V_offset": [-0.6, 0.6],
        "H_offset": 2,
        "TimeToConsider": 8 * 3600,
        "Vmag": "<2",
        "timestep": 2,
        "TimeSkip": 3600 * 2,
        "log_timestep": 3600,
        "automatic": True,
        "start_date": "0",
        "freeze_start": 150,
        "freeze_duration": 0,
        "SnapshotTime": 3,
        "SnapshotSpacing": 6,
        "CCDSELs": [16, 32, 1, 8],
    }

    if settings["freeze_duration"] == 0:
        settings["freeze_duration"] = _Library.FreezeDuration_calculator(
            Timeline_settings()["StandardPointingAltitude"],
            settings["pointing_altitude"],
            getTLE()[1],
        )

    return settings


def Mode121_122_123_settings():
    """Returns settings shared between Mode121-123.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'H_FOV': Used only in *Timeline_gen*. Sets full Horizontal FOV of the Limb instrument in degrees. Used to determine if stars are visible. (float) \n
        'V_FOV': Used only in *Timeline_gen*. Sets full Vertical FOV of the Limb instrument in degrees. Used to determine if stars are visible. (float) \n
        'TimeToConsider': Used only in *Timeline_gen*. Sets the time in seconds for which scheduling is considered. Used to plan calibration at the start of each timeline (useful as TLE accuracy deteriorates). Drastically affects simulation time at the cost of fewer time slots being considered. (int) \n
        'Vmag': Used only in *Timeline_gen*. Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2'). Drastically changes the runtime. \n
        'timestep': Used only in *Timeline_gen*. Set timestep used in scheduling simulation [s]. Will impact scheduling accuracy. (int) \n
        'TimeSkip': Used only in *Timeline_gen*. Set the amount of seconds to skip ahead after one complete orbit is simulated. Will drastically change the runtime of the simulation. (float) \n
        'log_timestep': Used only in *Timeline_gen*. Sets the timestep of data being logged [s]. Only determines how much of simulated data is logged for debugging purposes. (int) \n
        'freeze_start': Sets in seconds, the time from start of the Mode to when the attitude freezes. Part in determining the estimated duration of the mode. (int) \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. Part in determining the estimated duration of the mode. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with *Timeline_settings['StandardPointingAltitude']* (Normally around 50 s). (int) \n
        'SnapshotTime': Sets in seconds the time, from the start of the attitude freeze, to when the first Snapshot is taken. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. Needs to be larger than any CCD ReadoutTimes to avoid streaks. (int)
    
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {
        "pointing_altitude": 230000,
        "H_FOV": 6,
        "V_FOV": 1.5,
        "TimeToConsider": 8 * 3600,
        "Vmag": "<4",
        "timestep": 6,
        "TimeSkip": 3600 * 4,
        "log_timestep": 3600,
        "freeze_start": 150,
        "freeze_duration": 0,
        "SnapshotTime": 2,
        "SnapshotSpacing": 3,
    }

    if settings["freeze_duration"] == 0:
        settings["freeze_duration"] = _Library.FreezeDuration_calculator(
            Timeline_settings()["StandardPointingAltitude"],
            settings["pointing_altitude"],
            getTLE()[1],
        )

    return settings


def Mode121_settings():
    """Returns settings related to Mode121.
    
    **Keys in returned dict:**
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'automatic': Used only in *Timeline_gen*. Sets if 'start_date' will be calculated or user provided. True for calculated and False for user provided. (bool) \n
        'CCDSELs': List of CCDSEL arguments (except nadir) for which to take snapshots with. (list of int)
        
    Returns:
        (:obj:`dict`): settings
    """

    Settings = {"start_date": "0", "automatic": True, "CCDSELs": [16, 32, 1, 8]}
    CommonSettings = Mode121_122_123_settings()

    settings = {**CommonSettings, **Settings}
    settings["SnapshotSpacing"] = 6

    return settings


def Mode122_settings():
    """Returns settings related to Mode122.
    
    **Keys in returned dict:**
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'automatic': Used only in *Timeline_gen*. Sets if 'start_date' will be calculated or user provided. True for calculated and False for user provided. (bool) \n
        'Exp_Time_IR': Sets exposure time [ms] of the IR CCDs. (int) \n
        'Exp_Time_UV': Sets exposure time [ms] of the UV CCDs. (int) \n
    
    Returns:
        (:obj:`dict`): settings
    """

    Settings = {
        "start_date": "0",
        "automatic": True,
        "Exp_Time_IR": 5000,
        "Exp_Time_UV": 3000,
    }
    CommonSettings = Mode121_122_123_settings()

    settings = {**CommonSettings, **Settings}

    return settings


def Mode123_settings():
    """Returns settings related to Mode123.
    
    **Keys in returned dict:**
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'automatic': Used only in *Timeline_gen*. Sets if 'start_date' will be calculated or user provided. True for calculated and False for user provided. (bool) \n
        'Exp_Time_IR': Sets exposure time [ms] of the IR CCDs. (int) \n
        'Exp_Time_UV': Sets exposure time [ms] of the UV CCDs. (int) \n
    
    Returns:
        (:obj:`dict`): settings
    """

    Settings = {
        "start_date": "0",
        "automatic": True,
        "Exp_Time_IR": 5000,
        "Exp_Time_UV": 3000,
    }
    CommonSettings = Mode121_122_123_settings()

    settings = {**CommonSettings, **Settings}

    return settings


def Mode124_settings():
    """Returns settings related to Mode124.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'V_offset': Used only in *Timeline_gen*. Sets the Vertical-offset angle (position in FOV) in degrees for the Moon to pass, for when the attitude freeze command is scheduled. 
        Multiple values can be set but additional values will only be used when Mode124 is scheduled several times. (list of int) \n
        'H_offset': Used only in *Timeline_gen*. Sets the maximum H-offset angle from the optical axis in degrees that determines if the Moon is available. (float) \n
        'TimeToConsider': Used only in *Timeline_gen*. Sets the time in seconds for which scheduling is considered. Used to plan calibration at the start of each timeline (useful as TLE accuracy deteriorates). Drastically affects simulation time at the cost of fewer time slots being considered. (int) \n
        'timestep':  Used only in *Timeline_gen*. Sets in seconds the timestep during scheduling simulation [s]. Will impact scheduling accuracy. (int) \n
        'log_timestep': Used only in *Timeline_gen*. Sets the timestep of data being logged [s]. Only determines how much of simulated data is logged for debugging purposes. (int) \n
        'automatic':  Used only in *Timeline_gen*. Sets if the mode date is to be calculated or user provided. True for calculated or False for user provided. (bool) \n
        'start_date':  Note! only applies if *automatic* is set to False. Used only in *Timeline_gen*. Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If set to '0', Timeline_settings['start_date'] will be used. \n
        'freeze_start': Sets in seconds the time from start of the Mode to when the attitude freeze command is scheduled. Part in determining the estimated duration of the mode. (int) \n
        'freeze_duration': Sets in seconds the duration of the attitude freeze. Part in determining the estimated duration of the mode. If set to 0, it will be estimated to a 
        value corresponding to the attitude being frozen until realigned with *Timeline_settings['StandardPointingAltitude']*. (int) \n
        'SnapshotTime': Sets in seconds the time, from the start of the attitude freeze, to when the first Snapshot is taken. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. Needs to be larger than any CCD ReadoutTimes to avoid streaks. (int) \n
        'CCDSELs': List of CCDSEL arguments (except nadir) for which to take snapshots with. (list of int)
    
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {
        "pointing_altitude": 230000,
        "V_offset": [-0.6, 0.6],
        "H_offset": 2.5,
        "TimeToConsider": 8 * 3600,
        "timestep": 2,
        "log_timestep": 1200,
        "automatic": True,
        "start_date": "0",
        "freeze_start": 150,
        "freeze_duration": 0,
        "SnapshotTime": 2,
        "SnapshotSpacing": 6,
        "CCDSELs": [16, 32, 1, 8],
    }

    if settings["freeze_duration"] == 0:
        settings["freeze_duration"] = _Library.FreezeDuration_calculator(
            Timeline_settings()["StandardPointingAltitude"],
            settings["pointing_altitude"],
            getTLE()[1],
        )

    return settings


def Mode130_settings():
    """Returns settings related to Mode130.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'SnapshotSpacing': Sets in seconds the time inbetween Snapshots with individual CCDs. Part in determining the estimated duration of the mode. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline_settings['start_date'] will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    """
    settings = {"pointing_altitude": 230000, "SnapshotSpacing": 6, "start_date": "0"}
    return settings


def Mode131_settings():
    """Returns settings related to Mode131.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. Must be long enough to allow any pointing stabilization, CCD synchronization (takes 1 TEXPIMS cycle to execute), and execution of CMDs to occur. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline_settings['start_date'] will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    """
    settings = {"pointing_altitude": 230000, "mode_duration": 300, "start_date": "0"}
    return settings


def Mode132_settings():
    """Returns settings related to Mode132.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline_settings['start_date'] will be used. \n
        'Exp_Times_IR': Sets exposure times [ms] as a list of integers. Part in determining the estimated duration of the mode. Shall have equal length to 'Exp_Times_UV'.  \n
        'Exp_Times_UV': Sets exposure times [ms] as a list of integers. Part in determining the estimated duration of the mode. Shall have equal length to 'Exp_Times_IR'. \n
        'session_duration': Sets the duration [s] of each session spent in operational mode using the different exposure times in *Exp_Times*. Part in determining the estimated duration of the mode. (int)
    
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {
        "pointing_altitude": 230000,
        "start_date": "0",
        "Exp_Times_IR": [1000, 5000, 10000, 20000],
        "Exp_Times_UV": [1000, 5000, 10000, 20000],
        "session_duration": 120,
    }
    return settings


def Mode133_settings():
    """Returns settings related to Mode133.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline_settings['start_date'] will be used. \n
        'Exp_Times_IR': Sets exposure times [ms] as a list of integers. Part in determining the estimated duration of the mode. Shall have equal length to 'Exp_Times_UV'.  \n
        'Exp_Times_UV': Sets exposure times [ms] as a list of integers. Part in determining the estimated duration of the mode. Shall have equal length to 'Exp_Times_IR'. \n
        'session_duration': Sets the duration [s] of each session spent in operational mode using the different exposure times in *Exp_Times_UV* and *Exp_Times_IR*. Part in determining the estimated duration of the mode. (int)
    
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {
        "pointing_altitude": 230000,
        "start_date": "0",
        "Exp_Times_IR": [1000, 5000, 10000, 20000],
        "Exp_Times_UV": [1000, 5000, 10000, 20000],
        "session_duration": 120,
    }
    return settings


def Mode134_settings():
    """Returns settings related to Mode134.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. (int) \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. Must be long enough to allow any pointing stabilization, CCD synchronization (takes 1 TEXPIMS cycle to execute), and execution of CMDs to occur. (int) \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline_settings['start_date'] will be used.
    
    Returns:
        (:obj:`dict`): settings
        
    """
    settings = {"pointing_altitude": 110000, "mode_duration": 900, "start_date": "0"}
    return settings


"""
def Mode201_settings():
    '''Returns settings related to Mode201.
    
    **Keys in returned dict:**
        'pointing_altitude': Sets in meters the altitude of the pointing command. \n
        'mode_duration': Sets the scheduled duration of the Mode in seconds. \n
        'start_date': Sets the scheduled date for the mode as a str, (example: '2018/9/3 08:00:40'). If the date is set to '0', Timeline_settings['start_date'] will be used.
    
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
    """Returns settings related to the PWRTOGGLE CMD.
    
    **Keys in returned dict:**
        'CONST': Magic Constant (int).
        
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {"CONST": 165}
    return settings


def CCDFlushBadColumns_settings():
    """Returns settings related to the CCDFlushBadColumns CMD.
    
    **Keys in returned dict:**
        'CCDSEL': CCD select, 1 bit for each CCD (1..127). (int)
        
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {"CCDSEL": 127}
    return settings


def CCDBadColumn_settings():
    """Returns settings related to CCDBadColumn CMD.
    
    **Keys in returned dict:**
        'CCDSEL': CCD select, 1 bit for each CCD (1..127). (int) \n
        'NBC': Number of uint16 in BC as a uint16. Big Endian. Maximum number is 63. (int) \n
        'BC': Bad Columns as a list of uint16 (4..2047).
        
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {"CCDSEL": 1, "NBC": 0, "BC": []}
    return settings


def PM_settings():
    """Returns settings related to the PM (photometer) CMD.
    
    **Keys in returned dict:**
        'TEXPMS': Exposure time [ms] for the photometer (int) \n
        'TEXPIMS': Exposure interval time [ms] for the photometer (int)
        
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {"TEXPMS": 1500, "TEXPIMS": 2000}
    return settings


def CCDBIAS_settings():
    """Returns settings related to the CCDBIAS CMD.
    
    **Keys in returned dict:**
        'CCDSEL': CCD select, 1 bit for each CCD (1..127). (int) \n
        'VGATE': 8-bit value representing a Voltage (int) \n
        'VSUBST': 8-bit value representing a Voltage (int) \n
        'VRD': 8-bit value representing a Voltage (int) \n
        'VOD': 8-bit value representing a Voltage (int) \n
        
    Returns:
        (:obj:`dict`): settings
    
    """
    settings = {"CCDSEL": 127, "VGATE": 0, "VSUBST": 128, "VRD": 126, "VOD": 100}
    return settings


"""
def HTR_settings():
    '''Returns settings related to the HTR CMD.
    
    **Keys in returned dict:**
        'HTRSEL': HTR select, 1 bit for each HTR (bits 0,1,6,7). (int) \n
        'SET': Heater set point (int) \n
        'PVALUE': Regulator Proportional constant (int) \n
        'IVALUE': Regulator Integral constant (int) \n
        'DVALUE': Regulator Derivative constant (int) \n
        
    Returns:
        (:obj:`dict`): settings
    
    '''
    settings = {'CCDSEL': 3, 'SET': 1402, 'PVALUE': 256, 'IVALUE': 10, 'DVALUE': 0}
    return settings
"""


def CCD_macro_settings(CCDMacroSelect):
    """Returns CCD settings for a specific CCD macro.
    
    Each key in the output represents settings for a corresponding CCDSEL argument.
    TEXPIMS for the CCDs (except nadir) is not changeable as they need to be synchronized with a calculated TEXPIMS to prevent streaks. This is usually performed when macros are scheduled.
    
    **Keys in returned dict:**
        16: Represents settings for UV1 (CCD5) \n
        32: Represents settings for UV2 (CCD6) \n
        1: Represents settings for IR1 (CCD1) \n
        8: Represents settings for IR2 (CCD4) \n
        2: Represents settings for IR4 (CCD2) \n
        4: Represents settings for IR3 (CCD3) \n
        64: Represents settings for Nadir (CCD6) \n
        
        
    Arguments:
        CCDMacroSelect (str): Specifies for which CCD macro, settings are returned for. 'CustomBinning', 'HighResUV', 'HighResIR', 'BinnedCalibration', 'FullReadout', 'LowPixel'.
        
    Returns:
        (:obj:`dict`): CCD_settings
    
    """

    CCD_settings = {16: {}, 32: {}, 1: {}, 8: {}, 2: {}, 4: {}, 64: {}}

    if CCDMacroSelect == "CustomBinning":
        CCD_settings[16] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 90,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 2,
            "NROW": 255,
            "NCSKIP": 0,
            "NCBIN": 40,
            "NCOL": 50,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[32] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 90,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 2,
            "NROW": 255,
            "NCSKIP": 0,
            "NCBIN": 40,
            "NCOL": 50,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[1] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 90,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 3,
            "NROW": 170,
            "NCSKIP": 0,
            "NCBIN": 80,
            "NCOL": 24,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[8] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 90,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 3,
            "NROW": 170,
            "NCSKIP": 0,
            "NCBIN": 80,
            "NCOL": 24,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[2] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 90,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 6,
            "NROW": 85,
            "NCSKIP": 0,
            "NCBIN": 200,
            "NCOL": 8,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[4] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 90,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 6,
            "NROW": 85,
            "NCSKIP": 0,
            "NCBIN": 200,
            "NCOL": 8,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[64] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 90,
            "SYNC": 0,
            "TEXPMS": 1500,
            "TEXPIMS": 2000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 50,
            "NROW": 8,
            "NCSKIP": 0,
            "NCBIN": 50,
            "NCOL": 32,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

    elif CCDMacroSelect == "HighResUV":
        CCD_settings[16] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 2,
            "NROW": 160,
            "NCSKIP": 23,
            "NCBIN": 40,
            "NCOL": 49,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[32] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 2,
            "NROW": 160,
            "NCSKIP": 23,
            "NCBIN": 40,
            "NCOL": 49,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[1] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 3,
            "NROW": 107,
            "NCSKIP": 23,
            "NCBIN": 80,
            "NCOL": 24,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[8] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 3,
            "NROW": 107,
            "NCSKIP": 23,
            "NCBIN": 80,
            "NCOL": 24,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[2] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 6,
            "NROW": 53,
            "NCSKIP": 23,
            "NCBIN": 200,
            "NCOL": 9,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[4] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 6,
            "NROW": 53,
            "NCSKIP": 23,
            "NCBIN": 200,
            "NCOL": 9,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[64] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 1500,
            "TEXPIMS": 2000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 63,
            "NROW": 8,
            "NCSKIP": 0,
            "NCBIN": 63,
            "NCOL": 31,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

    elif CCDMacroSelect == "HighResIR":
        CCD_settings[16] = {
            "PWR": 0,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 0,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 3,
            "NROW": 107,
            "NCSKIP": 23,
            "NCBIN": 40,
            "NCOL": 49,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[32] = {
            "PWR": 0,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 0,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 3,
            "NROW": 107,
            "NCSKIP": 23,
            "NCBIN": 40,
            "NCOL": 49,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[1] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 2,
            "NROW": 160,
            "NCSKIP": 23,
            "NCBIN": 40,
            "NCOL": 49,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[8] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 2,
            "NROW": 160,
            "NCSKIP": 23,
            "NCBIN": 40,
            "NCOL": 49,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[2] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 6,
            "NROW": 53,
            "NCSKIP": 23,
            "NCBIN": 200,
            "NCOL": 9,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[4] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 95,
            "NRBIN": 6,
            "NROW": 53,
            "NCSKIP": 23,
            "NCBIN": 200,
            "NCOL": 9,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[64] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 1500,
            "TEXPIMS": 2000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 36,
            "NROW": 14,
            "NCSKIP": 0,
            "NCBIN": 36,
            "NCOL": 55,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

    elif CCDMacroSelect == "BinnedCalibration":
        CCD_settings[16] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 2,
            "NROW": 255,
            "NCSKIP": 0,
            "NCBIN": 40,
            "NCOL": 50,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[32] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 2,
            "NROW": 255,
            "NCSKIP": 0,
            "NCBIN": 40,
            "NCOL": 50,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[1] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 2,
            "NROW": 255,
            "NCSKIP": 0,
            "NCBIN": 40,
            "NCOL": 50,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[8] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 2,
            "NROW": 255,
            "NCSKIP": 0,
            "NCBIN": 40,
            "NCOL": 50,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[2] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 6,
            "NROW": 85,
            "NCSKIP": 0,
            "NCBIN": 200,
            "NCOL": 9,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[4] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 6,
            "NROW": 85,
            "NCSKIP": 0,
            "NCBIN": 200,
            "NCOL": 9,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[64] = {
            "PWR": 1,
            "WDW": 4,
            "JPEGQ": 85,
            "SYNC": 0,
            "TEXPMS": 0,
            "TEXPIMS": 2000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 36,
            "NROW": 14,
            "NCSKIP": 0,
            "NCBIN": 36,
            "NCOL": 55,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

    elif CCDMacroSelect == "FullReadout":
        CCD_settings[16] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 1,
            "NROW": 511,
            "NCSKIP": 0,
            "NCBIN": 1,
            "NCOL": 2047,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[32] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 1,
            "NROW": 511,
            "NCSKIP": 0,
            "NCBIN": 1,
            "NCOL": 2047,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[1] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 1,
            "NROW": 511,
            "NCSKIP": 0,
            "NCBIN": 1,
            "NCOL": 2047,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[8] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 1,
            "NROW": 511,
            "NCSKIP": 0,
            "NCBIN": 1,
            "NCOL": 2047,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[2] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 1,
            "NROW": 511,
            "NCSKIP": 0,
            "NCBIN": 1,
            "NCOL": 2047,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[4] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 1,
            "NROW": 511,
            "NCSKIP": 0,
            "NCBIN": 1,
            "NCOL": 2047,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[64] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 0,
            "TEXPIMS": 62800,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 1,
            "NROW": 511,
            "NCSKIP": 0,
            "NCBIN": 1,
            "NCOL": 2047,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

    elif CCDMacroSelect == "LowPixel":
        CCD_settings[16] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 63,
            "NROW": 7,
            "NCSKIP": 0,
            "NCBIN": 255,
            "NCOL": 7,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[32] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 3000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 63,
            "NROW": 7,
            "NCSKIP": 0,
            "NCBIN": 255,
            "NCOL": 7,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[1] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 63,
            "NROW": 7,
            "NCSKIP": 0,
            "NCBIN": 255,
            "NCOL": 7,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[8] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 63,
            "NROW": 7,
            "NCSKIP": 0,
            "NCBIN": 255,
            "NCOL": 7,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[2] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 63,
            "NROW": 7,
            "NCSKIP": 0,
            "NCBIN": 255,
            "NCOL": 7,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[4] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 5000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 63,
            "NROW": 7,
            "NCSKIP": 0,
            "NCBIN": 255,
            "NCOL": 7,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

        CCD_settings[64] = {
            "PWR": 1,
            "WDW": 7,
            "JPEGQ": 100,
            "SYNC": 0,
            "TEXPMS": 0,
            "TEXPIMS": 2000,
            "GAIN": 0,
            "NFLUSH": 1023,
            "NRSKIP": 0,
            "NRBIN": 63,
            "NROW": 7,
            "NCSKIP": 0,
            "NCBIN": 255,
            "NCOL": 7,
            "NCBINFPGA": 0,
            "SIGMODE": 1,
        }

    return CCD_settings


#################################################################################
