# -*- coding: utf-8 -*-
"""Contains Macro functions, that in calls for Command functions located in the *Commands* module.

Macros consists of frequently used combinations of Commands.

"""

import importlib


from OPT import _Library, _Globals

#from .Commands import Commands

from . import Commands

OPT_Config_File = importlib.import_module(_Globals.Config_File)



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
        CCD_settings (:obj:`dict` of :obj:`dict` of int): Settings for the CCDs.
        pointing_altitude (int): The altitude of the tangential point [m].
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings['CCDSYNC_ExtraOffset'], _Globals.Timeline_settings['CCDSYNC_ExtraIntervalTime'])
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    #relativeTime_OperationalMode = relativeTime+_Globals.Timeline_settings['pointing_stabilization']
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime,  Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings = CCD_settings, 
                             TEXPIMS = TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


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
        CCD_settings (:obj:`dict` of :obj:`dict` of int): Settings for the CCDs.
        pointing_altitude (int): The altitude of the tangential point [m].
        TEXPIMS (int): Exposure Interval [ms]. Note! Must be set very large when handling large images, at least 60000ms.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
        
    '''
    
    
    CCDSEL, NCCD, TEXPIOFS, Disregarded = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings['CCDSYNC_ExtraOffset'], _Globals.Timeline_settings['CCDSYNC_ExtraIntervalTime'])
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    #relativeTime_OperationalMode = relativeTime+_Globals.Timeline_settings['pointing_stabilization']
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


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
        CCD_settings (dict of dict of int): Settings for the CCDs.
        pointing_altitude_from (int): The altitude in meters from which to start the sweep 
        pointing_altitude_from (int): The altitude in meters where the sweep will end
        sweep_rate (int): The rate of the sweep in m/s.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings['CCDSYNC_ExtraOffset'], _Globals.Timeline_settings['CCDSYNC_ExtraIntervalTime'])
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    #relativeTime_OperationalMode = relativeTime+_Globals.Timeline_settings['pointing_stabilization']
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude_from, Final = pointing_altitude_from, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
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
    6. Take a Snapshot with each CCD (except Nadir) starting at *Snapshot_relativeTime* with a spacing of *SnapshotSpacing*.
    7. Point the satellite to *LP_pointing_altitude*.
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (dict of dict of int): Settings for the CCDs.
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
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = FreezeTime, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
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
    4. Take a Snapshot with each CCD (except Nadir) with a spacing of *SnapshotSpacing*.
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (dict of dict of int): Settings for the CCDs.
        pointing_altitude (int): The altitude of the tangential point [m].
        SnapshotSpacing (int): The time in seconds inbetween snapshots of individual CCDs.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    #relativeTime_SnapShot = relativeTime+_Globals.Timeline_settings['pointing_stabilization']
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSEL = CCDSEL, comment = comment)
        relativeTime += SnapshotSpacing
        
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
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 127, PWR = 0, ExpInterval = 6000, ExpTime = 0, comment = comment)
    
    Commands.TC_pafPWRToggle(root, relativeTime, CONST = CONST, comment = comment)
    
    
    return relativeTime



def CCD_macro(root, relativeTime, CCD_settings, TEXPIMS = 60000, comment = ''):
    """ Macro that corresponds to configurating the settings of the CCDs.
    
    The settings are set for each corresponding CCDSEL argument. 
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_settings (:obj:`dict` of int): A dict containing settings for the CCDs.
        TEXPIMS (int): ExposureIntervalTime for the CCDs in ms.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
    
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
        
    """
    
    CCDSEL_16 = CCD_settings['CCDSEL_16']
    CCDSEL_32 = CCD_settings['CCDSEL_32']
    CCDSEL_1 = CCD_settings['CCDSEL_1']
    CCDSEL_8 = CCD_settings['CCDSEL_8']
    CCDSEL_2 = CCD_settings['CCDSEL_2']
    CCDSEL_4 = CCD_settings['CCDSEL_4']
    CCDSEL_64 = CCD_settings['CCDSEL_64']
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 16, PWR = CCDSEL_16['PWR'], WDW = CCDSEL_16['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCDSEL_16['TEXPMS'], GAIN = CCDSEL_16['GAIN'], 
                                          NFLUSH = CCDSEL_16['NFLUSH'], NRSKIP = CCDSEL_16['NRSKIP'], NRBIN = CCDSEL_16['NRBIN'], 
                                          NROW = CCDSEL_16['NROW'], NCSKIP = CCDSEL_16['NCSKIP'], NCBIN = CCDSEL_16['NCBIN'], 
                                          NCOL = CCDSEL_16['NCOL'], NCBINFPGA = CCDSEL_16['NCBINFPGA'], SIGMODE = CCDSEL_16['SIGMODE'], comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 32, PWR = CCDSEL_32['PWR'], WDW = CCDSEL_32['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCDSEL_32['TEXPMS'], GAIN = CCDSEL_32['GAIN'], 
                                          NFLUSH = CCDSEL_32['NFLUSH'], NRSKIP = CCDSEL_32['NRSKIP'], NRBIN = CCDSEL_32['NRBIN'], 
                                          NROW = CCDSEL_32['NROW'], NCSKIP = CCDSEL_32['NCSKIP'], NCBIN = CCDSEL_32['NCBIN'], 
                                          NCOL = CCDSEL_32['NCOL'], NCBINFPGA = CCDSEL_32['NCBINFPGA'], SIGMODE = CCDSEL_32['SIGMODE'], comment = comment)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 1, PWR = CCDSEL_1['PWR'], WDW = CCDSEL_1['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCDSEL_1['TEXPMS'], GAIN = CCDSEL_1['GAIN'], 
                                          NFLUSH = CCDSEL_1['NFLUSH'], NRSKIP = CCDSEL_1['NRSKIP'], NRBIN = CCDSEL_1['NRBIN'], 
                                          NROW = CCDSEL_1['NROW'], NCSKIP = CCDSEL_1['NCSKIP'], NCBIN = CCDSEL_1['NCBIN'], 
                                          NCOL = CCDSEL_1['NCOL'], NCBINFPGA = CCDSEL_1['NCBINFPGA'], SIGMODE = CCDSEL_1['SIGMODE'], comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 8, PWR = CCDSEL_8['PWR'], WDW = CCDSEL_8['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCDSEL_8['TEXPMS'], GAIN = CCDSEL_8['GAIN'], 
                                          NFLUSH = CCDSEL_8['NFLUSH'], NRSKIP = CCDSEL_8['NRSKIP'], NRBIN = CCDSEL_8['NRBIN'], 
                                          NROW = CCDSEL_8['NROW'], NCSKIP = CCDSEL_8['NCSKIP'], NCBIN = CCDSEL_8['NCBIN'], 
                                          NCOL = CCDSEL_8['NCOL'], NCBINFPGA = CCDSEL_8['NCBINFPGA'], SIGMODE = CCDSEL_8['SIGMODE'], comment = comment)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 2, PWR = CCDSEL_2['PWR'], WDW = CCDSEL_2['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCDSEL_2['TEXPMS'], GAIN = CCDSEL_2['GAIN'], 
                                          NFLUSH = CCDSEL_2['NFLUSH'], NRSKIP = CCDSEL_2['NRSKIP'], NRBIN = CCDSEL_2['NRBIN'], 
                                          NROW = CCDSEL_2['NROW'], NCSKIP = CCDSEL_2['NCSKIP'], NCBIN = CCDSEL_2['NCBIN'], 
                                          NCOL = CCDSEL_2['NCOL'], NCBINFPGA = CCDSEL_2['NCBINFPGA'], SIGMODE = CCDSEL_2['SIGMODE'], comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 4, PWR = CCDSEL_4['PWR'], WDW = CCDSEL_4['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCDSEL_4['TEXPMS'], GAIN = CCDSEL_4['GAIN'], 
                                          NFLUSH = CCDSEL_4['NFLUSH'], NRSKIP = CCDSEL_4['NRSKIP'], NRBIN = CCDSEL_4['NRBIN'], 
                                          NROW = CCDSEL_4['NROW'], NCSKIP = CCDSEL_4['NCSKIP'], NCBIN = CCDSEL_4['NCBIN'], 
                                          NCOL = CCDSEL_4['NCOL'], NCBINFPGA = CCDSEL_4['NCBINFPGA'], SIGMODE = CCDSEL_4['SIGMODE'], comment = comment)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = CCDSEL_64['PWR'], WDW = CCDSEL_64['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCDSEL_64['TEXPMS'], GAIN = CCDSEL_64['GAIN'], 
                                          NFLUSH = CCDSEL_64['NFLUSH'], NRSKIP = CCDSEL_64['NRSKIP'], NRBIN = CCDSEL_64['NRBIN'], 
                                          NROW = CCDSEL_64['NROW'], NCSKIP = CCDSEL_64['NCSKIP'], NCBIN = CCDSEL_64['NCBIN'], 
                                          NCOL = CCDSEL_64['NCOL'], NCBINFPGA = CCDSEL_64['NCBINFPGA'], SIGMODE = CCDSEL_64['SIGMODE'], comment = comment)
    
    return relativeTime


def Limb_functional_test_macro(root, relativeTime, pointing_altitude, ExpTime, JPEGQ, comment = ''):
    '''Limb_functional_test_macro
    
    Arguments: 
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        pointing_altitude (int): The altitude of the tangential point [m].
        ExpTime (int): Exposure time in ms
        JPEGQ (int): The JPEG quality in %
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = '48', PWR = '1', ExpInterval = '100', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '100', NRBIN= '2', NROW = '400', NCBIN = '40', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = '9', PWR = '1', ExpInterval = '100', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '100', NRBIN= '3', NROW = '400', NCBIN = '81', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = '6', PWR = '1', ExpInterval = '100', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '100', NRBIN= '7', NROW = '400', NCBIN = '409', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = '64', PWR = '0', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '110', NROW = '500', NCBIN = '196', NCOL = '1980', JPEGQ = '100')
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSEL = '63', comment = '')
    
    ''' #Snapshot with on CCD at a time with 5 seconds intervall
    for CCDSEL in ['1','2','4','8','16','32']:
        
        relativeTime = TC_pafCCDSnapshot(root, relativeTime, CCDSEL = CCDSEL, comment = '')
        relativeTime = str(round(float(relativeTime) + 5-Timeline_settings()['command_separation'],2))
    '''
    
    return relativeTime



def Photometer_test_1_macro(root, relativeTime, ExpTime, ExpInt, comment = ''):
    '''Photometer_test_1_macro

    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        ExpTime (int): Exposure time in ms
        ExpInt (int): Exposure interval in ms
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, time = relativeTime, TEXPMS= ExpTime, TEXPIMS = ExpInt)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
        
    return relativeTime



def Nadir_functional_test_macro(root, relativeTime, pointing_altitude, ExpTime, JPEGQ, comment = ''):
    '''Nadir_functional_test
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        pointing_altitude (int): The altitude of the tangential point [m].
        ExpTime (int): Exposure time in ms
        JPEGQ (int): The JPEG quality in %
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
        
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
        '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = '48', PWR = '0', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '2', NROW = '400', NCBIN = '40', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = '9', PWR = '0', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '3', NROW = '400', NCBIN = '81', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = '6', PWR = '0', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '7', NROW = '400', NCBIN = '409', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = '64', PWR = '1', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '110', NROW = '500', NCBIN = '196', NCOL = '1980', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
        
    relativeTime = Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSEL = '64', comment = '')
    
    return relativeTime



'''
def Mode_User_Specified_macro(root, relativeTime, comment = ''):
    "This is a template for a new macro. Exchange '_User_Specified' for the name of the new macro"
    
    
    return relativeTime
    
'''
