# -*- coding: utf-8 -*-
"""Contains macro functions that represent parts of or a whole science-mode/test.

"""

import importlib


from Operational_Planning_Tool import _Library, _Globals

from . Commands import Commands

OPT_Config_File = importlib.import_module(_Globals.Config_File)



def Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, pointing_altitude, comment = ''):
    ''' Macro that corresponds to pointing towards a Limb altitude in Operational Mode.
    
    1. Set Payload to idle mode
    2. Start Photmeters
    3. Run CCD Synchronize Command with calculated settings.
    4. Run CCD Commands with given settings.
    5. Point the satellite to a limb altitide.
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
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings)
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings = CCD_settings, 
                             TEXPIMS = TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime,  Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def FullReadout_Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, pointing_altitude, TEXPIMS, comment):
    ''' Macro that corresponds to pointing towards a Limb altitude in Operational Mode. 
    
    Has an dedicated set Exposure Interval to prevent CRB-crashes when transferring very large images.
    
    1. Set Payload to idle mode
    2. Start Photometers.
    3. Run CCD Synchronize Command with calculated settings.
    4. Run CCD Commands with given settings.
    5. Point the satellite to a limb altitide.
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
    
    
    CCDSEL, NCCD, TEXPIOFS, Disregarded = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Operational_Sweep_macro(root, relativeTime, CCD_settings, pointing_altitude_from, pointing_altitude_to, sweep_rate, comment = ''):
    '''Macro that corresponds to performing a sweep while in Operational Mode.
    
    1. Set Payload to idle mode
    2. Start Photometers
    3. Run CCD Synchronize Command with calculated settings.
    4. Run CCD Commands with given settings.
    5. Point the satellite to a limb altitide.
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
    
    
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, _Globals.Timeline_settings)
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude_from, Final = pointing_altitude_from, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude_from, Final = pointing_altitude_to, Rate = sweep_rate, comment = comment)
    
    return relativeTime


def Snapshot_Inertial_macro(root, relativeTime, CCD_settings, FreezeTime, FreezeDuration, pointing_altitude, 
                  LP_pointing_altitude, SnapshotSpacing, Snapshot_relativeTime, comment):
    ''' Macro that corresponds to pointing towards an Inertial direction and take a Snapshot with all the CCDs (except Nadir).
    
    1. Set Payload to idle mode
    2. Run CCD Commands with given settings.
    3. Point the satellite to *pointing_altitude*.
    4. Run ArgFreezeStart Command with *FreezeTime*.
    5. Run ArgFreezeDuration Command with *FreezeDuration*.
    6. Take a Snapshot with each CCD (except Nadir) starting at *Snapshot_relativeTime* with a spacing of *SnapshotSpacing*.
    6. Point the satellite to *LP_pointing_altitude*.
    
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
    
    Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = FreezeTime, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSEL = CCDSEL, comment = comment)
        Snapshot_relativeTime = Snapshot_relativeTime + SnapshotSpacing
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = LP_pointing_altitude, Final = LP_pointing_altitude, Rate = 0, comment = comment)
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Snapshot_Limb_Pointing_macro(root, relativeTime, CCD_settings, pointing_altitude, SnapshotSpacing, comment):
    ''' Macro that corresponds to pointing towards a Limb altitude and taking a Snapshot with each CCD (except Nadir).
    
    1. Set Payload to idle mode
    2. Run CCD Commands with given settings.
    3. Point the satellite to *pointing_altitude*.
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
    
    relativeTime = CCD_macro(root, relativeTime, CCD_settings, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSEL = CCDSEL, comment = comment)
        relativeTime = relativeTime + SnapshotSpacing
        
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime

"""
def Custom_Binning_Macro(root, relativeTime, pointing_altitude, comment = ''):
    ''' Macro that corresponds to Mode5 and Mode160
        
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('Custom_Binning')
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_48, CCD_9, CCD_6, CCD_64)
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime

    
    
def Mode1_macro(root, relativeTime, pointing_altitude, UV_on, nadir_on, comment = ''):
    ''' Macro that corresponds to Mode1.
        
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('High_res_UV')
    
    if( UV_on == False):
        CCD_48['TEXPMS'] = 0
    if( nadir_on == False):
        CCD_64['TEXPMS'] = 0
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_48, CCD_9, CCD_6, CCD_64)
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime,  Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


    
def Mode2_macro(root, relativeTime, pointing_altitude, nadir_on, comment):
    ''' Macro that corresponds to Mode2. Exposure on Nadir is enabled."
        
        Arguments:
            pointing_altitude (int): The altitude of the tangential LP [m].
    '''
    
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('High_res_IR')
    
    if( nadir_on == False):
        CCD_64['TEXPMS'] = 0
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_48, CCD_9, CCD_6, CCD_64)
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime
    


def Mode100_macro(root, relativeTime, CCD_settings, pointing_altitude, ExpTimeUV, ExpTimeIR, comment = ''):
    ''' Macro that corresponds to Mode100.
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential LP [m].
            ExpTimeUV (int) = Sets the exposuretime of the UV CCDs in ms.
            ExpTimeIR (int) = Sets the exposuretime of the IR CCDs in ms.
    '''
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    
    CCD_48['TEXPMS'] = ExpTimeUV
    CCD_9['TEXPMS'] = ExpTimeIR
    CCD_6['TEXPMS'] = ExpTimeIR
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_48, CCD_9, CCD_6, CCD_64)
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime
    


def Mode110_macro(root, relativeTime, CCD_settings, pointing_altitude_from, pointing_altitude_to, sweep_rate, comment = ''):
    '''Macro that corresponds to Mode110
    
        Arguments:
            pointing_altitude_from (int): The altitude in meters from which to start the sweep 
            pointing_altitude_from (int): The altitude in meters where the sweep will end
            sweep_rate (int): The rate of the sweep in m/s.
            
    '''
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_48, CCD_9, CCD_6, CCD_64)
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude_from, Final = pointing_altitude_from, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude_from, Final = pointing_altitude_to, Rate = sweep_rate, comment = comment)
    
    return relativeTime
    
    


def Mode120_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, 
                  LP_pointing_altitude, SnapshotSpacing, Snapshot_relativeTime, comment):
    ''' Macro that corresponds to Mode120.
    
        Arguments:
            freezeTime (float): Start time of attitude freeze command in on-board time [s].
            FreezeDuration (int): Duration of freeze [s].
            pointing_altitude (int): The altitude of the tangential point [m].
            Snapshot_relativeTime (float): The relativeTime (time from start of timeline) at which the first Snapshot is taken.
            SnapshotSpacing (int): The time in seconds inbetween sent CMDs for snapshots of individual CCDs.
    '''
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSEL = CCDSEL, comment = comment)
        Snapshot_relativeTime = Snapshot_relativeTime + SnapshotSpacing
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = LP_pointing_altitude, Final = LP_pointing_altitude, Rate = 0, comment = comment)
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Mode121_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, 
                  LP_pointing_altitude, SnapshotSpacing, Snapshot_relativeTime, comment):
    ''' Macro that corresponds to Mode121.
    
        Arguments:
            freezeTime (float): Start time of attitude freeze command in on-board time [s].
            FreezeDuration (int): Duration of freeze [s].
            pointing_altitude (int): The altitude of the tangential point [m].
            Snapshot_relativeTime (float): The relativeTime (time from start of timeline) at which the Snapshot is taken.
            SnapshotSpacing (int): The time in seconds inbetween sent CMDs for snapshots of individual CCDs.
    '''
    
    
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    
    for CCDSEL in [1,2,4,8,16,32]:
        relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSEL = CCDSEL, comment = comment)
        Snapshot_relativeTime = Snapshot_relativeTime + SnapshotSpacing
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = LP_pointing_altitude, Final = LP_pointing_altitude, Rate = 0, comment = comment)
    
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Mode122_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, Snapshot_relativeTime, 
                  LP_pointing_altitude, SnapshotSpacing, ExpTimeUV, ExpTimeIR, comment):
    ''' Macro that corresponds to Mode121.
    
        Arguments:
            freezeTime (float): Start time of attitude freeze command in on-board time [s].
            FreezeDuration (int): Duration of freeze [s].
            pointing_altitude (int): The altitude of the tangential point [m].
            Snapshot_relativeTime (float): The relativeTime (time from start of timeline) at which the Snapshot is taken.
            SnapshotSpacing (int): The time in seconds inbetween sent CMDs for snapshots of individual CCDs.
            ExpTimeUV (int): Exposure time [ms].
            ExpTimeIR (int): Exposure time [ms].
    '''
    
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    
    CCD_48['TEXPMS'] = ExpTimeUV
    CCD_9['TEXPMS'] = ExpTimeIR
    CCD_6['TEXPMS'] = ExpTimeIR
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    
    for CCDSEL in [1,2,4,8,16,32]:
        relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSEL = CCDSEL, comment = comment)
        Snapshot_relativeTime = Snapshot_relativeTime + SnapshotSpacing
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = LP_pointing_altitude, Final = LP_pointing_altitude, Rate = 0, comment = comment)
    
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Mode123_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, Snapshot_relativeTime, 
                  LP_pointing_altitude, SnapshotSpacing, ExpTimeUV, ExpTimeIR, comment):
    ''' Macro that corresponds to Mode122.
    
        Arguments:
            freezeTime (float): Start time of attitude freeze command in on-board time [s].
            FreezeDuration (int): Duration of freeze [s].
            pointing_altitude (int): The altitude of the tangential point [m].
            ExpTimeUV (int): Exposure time [ms].
            ExpTimeIR (int): Exposure time [ms].
            Snapshot_relativeTime (float): The relativeTime (time from start of timeline) at which the Snapshot is taken.
            SnapshotSpacing (int): The time in seconds inbetween sent CMDs for snapshots of individual CCDs.
    '''
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('LowPixel')
    
    CCD_48['TEXPMS'] = ExpTimeUV
    CCD_9['TEXPMS'] = ExpTimeIR
    CCD_6['TEXPMS'] = ExpTimeIR
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, comment = comment)
    
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    
    for CCDSEL in [1,2,4,8,16,32]:
        relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSEL = CCDSEL, comment = comment)
        Snapshot_relativeTime = Snapshot_relativeTime + SnapshotSpacing
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = LP_pointing_altitude, Final = LP_pointing_altitude, Rate = 0, comment = comment)
    
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime



def Mode124_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, 
                  LP_pointing_altitude, SnapshotSpacing, Snapshot_relativeTime, comment):
    ''' Macro that corresponds to Mode124.
    
        Arguments:
            freezeTime (float): Start time of attitude freeze command in on-board time [s].
            FreezeDuration (int): Duration of freeze [s].
            pointing_altitude (int): The altitude of the tangential point [m].
            Snapshot_relativeTime (float): The relativeTime (time from start of timeline) at which the Snapshot is taken.
            SnapshotSpacing (int): The time in seconds inbetween sent CMDs for snapshots of individual CCDs.
    '''
    
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSEL = CCDSEL, comment = comment)
        Snapshot_relativeTime = Snapshot_relativeTime + SnapshotSpacing
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = LP_pointing_altitude, Final = LP_pointing_altitude, Rate = 0, comment = comment)
    
    return relativeTime


def Mode130_macro(root, relativeTime, pointing_altitude, SnapshotSpacing, comment):
    ''' Macro that corresponds to Mode130
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSEL = CCDSEL, comment = comment)
        relativeTime = relativeTime + SnapshotSpacing
        
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Mode131_macro(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode132
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    CCDSEL, NCCD, TEXPIOFS, Disregarded = _Library.SyncArgCalculator(CCD_48, CCD_9, CCD_6, CCD_64)
    TEXPIMS = 60000
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Mode132_macro(root, relativeTime, pointing_altitude, ExpTimeUV, ExpTimeIR, comment):
    ''' Macro that corresponds to Mode132
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
            ExpTimeUV (int): Exposure time of UV CCDs [ms].
            ExpTimeIR (int): Exposure time of IR CCDs [ms].
    '''
    
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    
    CCD_48['TEXPMS'] = ExpTimeUV
    CCD_9['TEXPMS'] = ExpTimeIR
    CCD_6['TEXPMS'] = ExpTimeIR
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_48, CCD_9, CCD_6, CCD_64)
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Mode133_macro(root, relativeTime, pointing_altitude, ExpTimeUV, ExpTimeIR, comment):
    ''' Macro that corresponds to Mode133
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
            ExpTimeUV (int): Exposure time of UV CCDs [ms].
            ExpTimeIR (int): Exposure time of IR CCDs [ms].
    '''
    
    CCD_48, CCD_9, CCD_6, CCD_64 = OPT_Config_File.CCD_macro_settings('LowPixel')
    
    CCD_48['TEXPMS'] = ExpTimeUV
    CCD_9['TEXPMS'] = ExpTimeIR
    CCD_6['TEXPMS'] = ExpTimeIR
    
    CCDSEL, NCCD, TEXPIOFS, TEXPIMS = _Library.SyncArgCalculator(CCD_48, CCD_9, CCD_6, CCD_64)
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSynchronize(root, relativeTime, CCDSEL = CCDSEL, NCCD = NCCD, 
                                                 TEXPIOFS = TEXPIOFS, comment = comment )
    
    relativeTime = CCD_macro(root, relativeTime, CCD_48, CCD_9, CCD_6, CCD_64, TEXPIMS, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime

"""


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
    
    The settings are different for 3 pairs of CCDs and the nadir camera.
    The pairs are CCD5/6 (CCDSEL=48), CCD1/4 (CCDSEL=9), CCD2/3 (CCDSEL=6), and the 
    nadir camera CCD7 (CCDSEL=7).
    
    Arguments:
        root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
        relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
        CCD_48 (:obj:`dict` of int): A dict containing settings for the CCDs corresponding to CCDSEL=48.
        CCD_9 (:obj:`dict` of int): A dict containing settings for the CCDs corresponding to CCDSEL=9.
        CCD_6 (:obj:`dict` of int): A dict containing settings for the CCDs corresponding to CCDSEL=6.
        CCD_64 (:obj:`dict` of int): A dict containing settings for the CCDs corresponding to CCDSEL=64.
        TEXPIMS (int): ExposureIntervalTime for the CCDs in ms.
        comment (str): A comment for the macro. Will be printed in the genereated XML-file.
    
    Returns:
        relativeTime (float): Time in seconds equal to the input "relativeTime" with added delay from the scheduling of commands.
        
    """
    
    CCD_48 = CCD_settings['CCD_48']
    CCD_9 = CCD_settings['CCD_9']
    CCD_6 = CCD_settings['CCD_6']
    CCD_64 = CCD_settings['CCD_64']
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 48, PWR = CCD_48['PWR'], WDW = CCD_48['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCD_48['TEXPMS'], GAIN = CCD_48['GAIN'], 
                                          NFLUSH = CCD_48['NFLUSH'], NRSKIP = CCD_48['NRSKIP'], NRBIN = CCD_48['NRBIN'], 
                                          NROW = CCD_48['NROW'], NCSKIP = CCD_48['NCSKIP'], NCBIN = CCD_48['NCBIN'], 
                                          NCOL = CCD_48['NCOL'], NCBINFPGA = CCD_48['NCBINFPGA'], SIGMODE = CCD_48['SIGMODE'], comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 9, PWR = CCD_9['PWR'], WDW = CCD_9['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCD_9['TEXPMS'], GAIN = CCD_9['GAIN'], 
                                          NFLUSH = CCD_9['NFLUSH'], NRSKIP = CCD_9['NRSKIP'], NRBIN = CCD_9['NRBIN'], 
                                          NROW = CCD_9['NROW'], NCSKIP = CCD_9['NCSKIP'], NCBIN = CCD_9['NCBIN'], 
                                          NCOL = CCD_9['NCOL'], NCBINFPGA = CCD_9['NCBINFPGA'], SIGMODE = CCD_9['SIGMODE'], comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 6, PWR = CCD_6['PWR'], WDW = CCD_6['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCD_6['TEXPMS'], GAIN = CCD_6['GAIN'], 
                                          NFLUSH = CCD_6['NFLUSH'], NRSKIP = CCD_6['NRSKIP'], NRBIN = CCD_6['NRBIN'], 
                                          NROW = CCD_6['NROW'], NCSKIP = CCD_6['NCSKIP'], NCBIN = CCD_6['NCBIN'], 
                                          NCOL = CCD_6['NCOL'], NCBINFPGA = CCD_6['NCBINFPGA'], SIGMODE = CCD_6['SIGMODE'], comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = CCD_64['PWR'], WDW = CCD_64['WDW'], 
                                          ExpInterval = TEXPIMS, ExpTime = CCD_64['TEXPMS'], GAIN = CCD_64['GAIN'], 
                                          NFLUSH = CCD_64['NFLUSH'], NRSKIP = CCD_64['NRSKIP'], NRBIN = CCD_64['NRBIN'], 
                                          NROW = CCD_64['NROW'], NCSKIP = CCD_64['NCSKIP'], NCBIN = CCD_64['NCBIN'], 
                                          NCOL = CCD_64['NCOL'], NCBINFPGA = CCD_64['NCBINFPGA'], SIGMODE = CCD_64['SIGMODE'], comment = comment)
    
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
