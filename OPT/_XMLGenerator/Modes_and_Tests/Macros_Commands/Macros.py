# -*- coding: utf-8 -*-
"""Contain Macro functions, that calls for Command functions located in the *Commands* module.

Macros consists of frequently used combinations of Commands.

"""

import importlib, logging


from OPT import _Library, _Globals

#from .Commands import Commands

from . import Commands

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, pointing_altitude, comment = ''):
    ''' Macro that corresponds to pointing towards a Limb altitude in Operational Mode.
    
    1. Set Payload to idle mode
    2. Point the satellite to a limb altitide.
    3. Start Photometers
    4. Run CCD Synchronize Command with calculated settings.
    5. Run CCD Commands with given settings.
    6. Set Payload to operational mode
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (:obj:`dict` of :obj:`dict` of int): Settings for the CCDs. Defined in the *Configuration File*.
        pointing_altitude (int): The altitude of the tangential point [m].
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    comment = comment + ', Operational_Limb_Pointing_macro'
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings['CCDSYNC_ExtraOffset'], _Globals.Timeline_settings['CCDSYNC_ExtraIntervalTime'])
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    #relativeTime_OperationalMode = relativeTime+_Globals.Timeline_settings['pointing_stabilization']
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime,  Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSYNCHRONIZE(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings = CCD_settings, 
                             TEXPIMS = TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime

"""
def FullReadout_Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, pointing_altitude, TEXPIMS, comment):
    ''' Macro that corresponds to pointing towards a Limb altitude in Operational Mode. 
    
    Has an dedicated set Exposure Interval to prevent CRB-crashes when transferring very large images.
    
    1. Set Payload to idle mode
    2. Point the satellite to a limb altitide.
    3. Start Photometers.
    4. Run CCD Synchronize Command with calculated settings.
    5. Run CCD Commands with given settings.
    6. Set Payload to operational mode
        
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (:obj:`dict` of :obj:`dict` of int): Settings for the CCDs.. Defined in the *Configuration File*.
        pointing_altitude (int): The altitude of the tangential point [m].
        TEXPIMS (int): Exposure Interval [ms]. Note! Must be set very large when handling large images, at least 60000ms.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
        
    '''
    
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings['CCDSYNC_ExtraOffset'], _Globals.Timeline_settings['CCDSYNC_ExtraIntervalTime'])
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    #relativeTime_OperationalMode = relativeTime+_Globals.Timeline_settings['pointing_stabilization']
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSYNCHRONIZE(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime
"""

def Operational_Sweep_macro(root, relativeTime, CCD_settings, pointing_altitude_from, pointing_altitude_to, sweep_rate, comment = ''):
    '''Macro that corresponds to performing a sweep while in Operational Mode.
    
    1. Set Payload to idle mode
    2. Point the satellite to a limb altitide.
    3. Start Photometers
    4. Run CCD Synchronize Command with calculated settings.
    5. Run CCD Commands with given settings.
    6. Set Payload to operational mode.
    7. Start Sweep of satellite.
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (dict of dict of int): Settings for the CCDs.. Defined in the *Configuration File*.
        pointing_altitude_from (int): The altitude in meters from which to start the sweep 
        pointing_altitude_from (int): The altitude in meters where the sweep will end
        sweep_rate (int): The rate of the sweep in m/s.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    comment = comment + ', Operational_Sweep_macro'
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings['CCDSYNC_ExtraOffset'], _Globals.Timeline_settings['CCDSYNC_ExtraIntervalTime'])
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    #relativeTime_OperationalMode = relativeTime+_Globals.Timeline_settings['pointing_stabilization']
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude_from, Final = pointing_altitude_from, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSYNCHRONIZE(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude_from, Final = pointing_altitude_to, Rate = sweep_rate, comment = comment)
    
    return relativeTime


def Snapshot_Inertial_macro(root, relativeTime, CCD_settings, FreezeTime, FreezeDuration, pointing_altitude, 
                  LP_pointing_altitude, SnapshotSpacing, Snapshot_relativeTime, comment):
    ''' Macro that corresponds to pointing towards an Inertial direction and take a Snapshot with all the CCDs (except Nadir).
    
    1. Set Payload to idle mode
    2. Point the satellite to *pointing_altitude*.
    3. Run CCD Commands with given settings.
    4. Run ArgFreezeStart Command with *FreezeTime*.
    5. Run ArgFreezeDuration Command with *FreezeDuration*.
    6. Start Photometers
    7. Take a Snapshot with each CCD (except Nadir) starting at *Snapshot_relativeTime* with a spacing of *SnapshotSpacing*.
    8. Point the satellite to *LP_pointing_altitude*.
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (dict of dict of int): Settings for the CCDs.. Defined in the *Configuration File*.
        FreezeTime (float): Start time of attitude freeze command in on-board time [s].
        FreezeDuration (int): Duration of freeze [s].
        pointing_altitude (int): The altitude of the tangential point [m].
        LP_pointing_altitude (int): The altitude of the LP [m].
        SnapshotSpacing (int): The time in seconds inbetween snapshots of individual CCDs.
        Snapshot_relativeTime (float): The relativeTime (time from start of timeline) at which the first Snapshot is taken.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    comment = comment + ', Snapshot_Inertial_macro'
    
    Disregarded, Disregarded, Disregarded, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings['CCDSYNC_ExtraOffset'], _Globals.Timeline_settings['CCDSYNC_ExtraIntervalTime'])
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = FreezeTime, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSEL = CCDSEL, comment = comment)
        Snapshot_relativeTime += SnapshotSpacing
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = LP_pointing_altitude, Final = LP_pointing_altitude, Rate = 0, comment = comment)
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Snapshot_Limb_Pointing_macro(root, relativeTime, CCD_settings, pointing_altitude, SnapshotSpacing, comment):
    ''' Macro that corresponds to pointing towards a Limb altitude and taking a Snapshot with each CCD (except Nadir).
    
    1. Set Payload to idle mode
    2. Point the satellite to *pointing_altitude*.
    3. Run CCD Commands with given settings.
    4. Start Photometers
    5. Take a Snapshot with each CCD (except Nadir) with a spacing of *SnapshotSpacing*.
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (dict of dict of int): Settings for the CCDs.. Defined in the *Configuration File*.
        pointing_altitude (int): The altitude of the tangential point [m].
        SnapshotSpacing (int): The time in seconds inbetween snapshots of individual CCDs.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    comment = comment + ', Snapshot_Limb_Pointing_macro'
    
    Disregarded, Disregarded, Disregarded, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings['CCDSYNC_ExtraOffset'], _Globals.Timeline_settings['CCDSYNC_ExtraIntervalTime'])
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    #relativeTime_SnapShot = relativeTime+_Globals.Timeline_settings['pointing_stabilization']
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, TEXPIMS=TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSEL = CCDSEL, comment = comment)
        relativeTime += SnapshotSpacing
        
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime



def NadirSnapshot_Limb_Pointing_macro(root, relativeTime, CCD_settings, pointing_altitude, comment):
    ''' Macro that corresponds to pointing towards a Limb altitude and taking a Snapshot with Nadir.
    
    1. Set Payload to idle mode
    2. Point the satellite to *pointing_altitude*.
    3. Run CCD Commands with given settings.
    4. Take a Snapshot with Nadir.
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (dict of dict of int): Settings for the CCDs.. Defined in the *Configuration File*.
        pointing_altitude (int): The altitude of the tangential point [m].
        SnapshotSpacing (int): The time in seconds inbetween snapshots of individual CCDs.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    comment = comment + ', NadirSnapshot_Limb_Pointing_macro'
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    #relativeTime_SnapShot = relativeTime+_Globals.Timeline_settings['pointing_stabilization']
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    CCDSEL_64 = CCD_settings['CCDSEL_64']
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = CCDSEL_64['PWR'], WDW = CCDSEL_64['WDW'], JPEGQ = CCDSEL_64['JPEGQ'], SYNC = CCDSEL_64['SYNC'], 
                                          TEXPIMS = CCDSEL_64['TEXPIMS'], TEXPMS = CCDSEL_64['TEXPMS'], GAIN = CCDSEL_64['GAIN'], 
                                          NFLUSH = CCDSEL_64['NFLUSH'], NRSKIP = CCDSEL_64['NRSKIP'], NRBIN = CCDSEL_64['NRBIN'], 
                                          NROW = CCDSEL_64['NROW'], NCSKIP = CCDSEL_64['NCSKIP'], NCBIN = CCDSEL_64['NCBIN'], 
                                          NCOL = CCDSEL_64['NCOL'], NCBINFPGA = CCDSEL_64['NCBINFPGA'], SIGMODE = CCDSEL_64['SIGMODE'], comment = comment)
    
    
    relativeTime = Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSEL = 64, comment = comment)
    
        
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def PWRTOGGLE_macro(root, relativeTime, CONST, comment = ''):
    ''' Macro that corresponds to the PWRTOGGLE CMD.
    
    Switches off all CCDs before PWRTOGGLING
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CONST (int): Magical constant.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.

    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    comment = comment + ', PWRTOGGLE_macro'
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 127, PWR = 0, TEXPIMS = 6000, TEXPMS = 0, NRSKIP = 0, NRBIN = 1, NROW = 1, 
                                          NCBIN = 1, NCOL=1, WDW = 7, JPEGQ = 110, SYNC = 0, NCBINFPGA = 0, SIGMODE = 1, GAIN = 0, 
                                          NFLUSH = 1023, NCSKIP = 0, comment = comment)
    
    Commands.TC_pafPWRToggle(root, relativeTime, CONST = CONST, comment = comment)
    
    
    
    return relativeTime



def CCD_macro(root, relativeTime, CCD_settings, TEXPIMS, comment = ''):
    """Macro that corresponds to configurating the settings of the CCDs
    
    Used when the Synchronization CMD is used to synchronize all the CCDs (except nadir), or when Snapshots are utilized where TEXPIMS is irrelevant.
    TEXPIMS for all the CCDs except nadir is set to the same value to allow Synchronization.
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (:obj:`dict` of int): A dict containing Settings for the CCDs.. Defined in the *Configuration File*.
        TEXPIMS (int): ExposureIntervalTime for the CCDs (except nadir) in ms.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
    
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
        
    """
    
    Logger.debug('TEXPIMS: '+str(TEXPIMS))
    
    CCDSEL_16 = CCD_settings['CCDSEL_16']
    CCDSEL_32 = CCD_settings['CCDSEL_32']
    CCDSEL_1 = CCD_settings['CCDSEL_1']
    CCDSEL_8 = CCD_settings['CCDSEL_8']
    CCDSEL_2 = CCD_settings['CCDSEL_2']
    CCDSEL_4 = CCD_settings['CCDSEL_4']
    CCDSEL_64 = CCD_settings['CCDSEL_64']
    
    #T_readout, T_delay, T_Extra = _Library.calculate_time_per_row(NCOL = CCDSEL_64['NCOL'], NCBIN = CCDSEL_64['NCBIN'], NCBINFPGA = CCDSEL_64['NCBINFPGA'], 
    #                                                     NRSKIP = CCDSEL_64['NRSKIP'], NROW = CCDSEL_64['NROW'], NRBIN = CCDSEL_64['NRBIN'], NFLUSH = CCDSEL_64['NFLUSH'])
    
    #ReadOutTime_64 = T_readout + T_delay + T_Extra
    
    #TEXPIMS_64 = int(ReadOutTime_64) + +CCDSEL_64['TEXPMS'] + _Globals.Timeline_settings['CCDSYNC_ExtraIntervalTime']
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 16, PWR = CCDSEL_16['PWR'], WDW = CCDSEL_16['WDW'], JPEGQ = CCDSEL_16['JPEGQ'], SYNC = CCDSEL_16['SYNC'],   
                                          TEXPIMS = TEXPIMS, TEXPMS = CCDSEL_16['TEXPMS'], GAIN = CCDSEL_16['GAIN'], 
                                          NFLUSH = CCDSEL_16['NFLUSH'], NRSKIP = CCDSEL_16['NRSKIP'], NRBIN = CCDSEL_16['NRBIN'], 
                                          NROW = CCDSEL_16['NROW'], NCSKIP = CCDSEL_16['NCSKIP'], NCBIN = CCDSEL_16['NCBIN'], 
                                          NCOL = CCDSEL_16['NCOL'], NCBINFPGA = CCDSEL_16['NCBINFPGA'], SIGMODE = CCDSEL_16['SIGMODE'], comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 32, PWR = CCDSEL_32['PWR'], WDW = CCDSEL_32['WDW'], JPEGQ = CCDSEL_32['JPEGQ'], SYNC = CCDSEL_32['SYNC'], 
                                          TEXPIMS = TEXPIMS, TEXPMS = CCDSEL_32['TEXPMS'], GAIN = CCDSEL_32['GAIN'], 
                                          NFLUSH = CCDSEL_32['NFLUSH'], NRSKIP = CCDSEL_32['NRSKIP'], NRBIN = CCDSEL_32['NRBIN'], 
                                          NROW = CCDSEL_32['NROW'], NCSKIP = CCDSEL_32['NCSKIP'], NCBIN = CCDSEL_32['NCBIN'], 
                                          NCOL = CCDSEL_32['NCOL'], NCBINFPGA = CCDSEL_32['NCBINFPGA'], SIGMODE = CCDSEL_32['SIGMODE'], comment = comment)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 1, PWR = CCDSEL_1['PWR'], WDW = CCDSEL_1['WDW'], JPEGQ = CCDSEL_1['JPEGQ'], SYNC = CCDSEL_1['SYNC'], 
                                          TEXPIMS = TEXPIMS, TEXPMS = CCDSEL_1['TEXPMS'], GAIN = CCDSEL_1['GAIN'], 
                                          NFLUSH = CCDSEL_1['NFLUSH'], NRSKIP = CCDSEL_1['NRSKIP'], NRBIN = CCDSEL_1['NRBIN'], 
                                          NROW = CCDSEL_1['NROW'], NCSKIP = CCDSEL_1['NCSKIP'], NCBIN = CCDSEL_1['NCBIN'], 
                                          NCOL = CCDSEL_1['NCOL'], NCBINFPGA = CCDSEL_1['NCBINFPGA'], SIGMODE = CCDSEL_1['SIGMODE'], comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 8, PWR = CCDSEL_8['PWR'], WDW = CCDSEL_8['WDW'], JPEGQ = CCDSEL_8['JPEGQ'], SYNC = CCDSEL_8['SYNC'], 
                                          TEXPIMS = TEXPIMS, TEXPMS = CCDSEL_8['TEXPMS'], GAIN = CCDSEL_8['GAIN'], 
                                          NFLUSH = CCDSEL_8['NFLUSH'], NRSKIP = CCDSEL_8['NRSKIP'], NRBIN = CCDSEL_8['NRBIN'], 
                                          NROW = CCDSEL_8['NROW'], NCSKIP = CCDSEL_8['NCSKIP'], NCBIN = CCDSEL_8['NCBIN'], 
                                          NCOL = CCDSEL_8['NCOL'], NCBINFPGA = CCDSEL_8['NCBINFPGA'], SIGMODE = CCDSEL_8['SIGMODE'], comment = comment)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 2, PWR = CCDSEL_2['PWR'], WDW = CCDSEL_2['WDW'], JPEGQ = CCDSEL_2['JPEGQ'], SYNC = CCDSEL_2['SYNC'], 
                                          TEXPIMS = TEXPIMS, TEXPMS = CCDSEL_2['TEXPMS'], GAIN = CCDSEL_2['GAIN'], 
                                          NFLUSH = CCDSEL_2['NFLUSH'], NRSKIP = CCDSEL_2['NRSKIP'], NRBIN = CCDSEL_2['NRBIN'], 
                                          NROW = CCDSEL_2['NROW'], NCSKIP = CCDSEL_2['NCSKIP'], NCBIN = CCDSEL_2['NCBIN'], 
                                          NCOL = CCDSEL_2['NCOL'], NCBINFPGA = CCDSEL_2['NCBINFPGA'], SIGMODE = CCDSEL_2['SIGMODE'], comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 4, PWR = CCDSEL_4['PWR'], WDW = CCDSEL_4['WDW'], JPEGQ = CCDSEL_4['JPEGQ'], SYNC = CCDSEL_4['SYNC'], 
                                          TEXPIMS = TEXPIMS, TEXPMS = CCDSEL_4['TEXPMS'], GAIN = CCDSEL_4['GAIN'], 
                                          NFLUSH = CCDSEL_4['NFLUSH'], NRSKIP = CCDSEL_4['NRSKIP'], NRBIN = CCDSEL_4['NRBIN'], 
                                          NROW = CCDSEL_4['NROW'], NCSKIP = CCDSEL_4['NCSKIP'], NCBIN = CCDSEL_4['NCBIN'], 
                                          NCOL = CCDSEL_4['NCOL'], NCBINFPGA = CCDSEL_4['NCBINFPGA'], SIGMODE = CCDSEL_4['SIGMODE'], comment = comment)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = CCDSEL_64['PWR'], WDW = CCDSEL_64['WDW'], JPEGQ = CCDSEL_64['JPEGQ'], SYNC = CCDSEL_64['SYNC'], 
                                          TEXPIMS = CCDSEL_64['TEXPIMS'], TEXPMS = CCDSEL_64['TEXPMS'], GAIN = CCDSEL_64['GAIN'], 
                                          NFLUSH = CCDSEL_64['NFLUSH'], NRSKIP = CCDSEL_64['NRSKIP'], NRBIN = CCDSEL_64['NRBIN'], 
                                          NROW = CCDSEL_64['NROW'], NCSKIP = CCDSEL_64['NCSKIP'], NCBIN = CCDSEL_64['NCBIN'], 
                                          NCOL = CCDSEL_64['NCOL'], NCBINFPGA = CCDSEL_64['NCBINFPGA'], SIGMODE = CCDSEL_64['SIGMODE'], comment = comment)
    
    return relativeTime




'''
def Mode_User_Specified_macro(root, relativeTime, comment = ''):
    "This is a template for a new macro. Exchange '_User_Specified' for the name of the new macro"
    
    
    return relativeTime
    
'''
