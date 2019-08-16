# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 14:31:43 2018

Contains macro functions that represent parts of or a whole science-mode/test.

Arguments:
    root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
    relativeTime (float): The relative starting time of the macro with regard to the start of the timeline [s]
    comment (str): A comment for the macro
    *Any other optional inputs depending on the macro which are defined in each macro function*
    
Returns:
    relativeTime (float): Time in seconds as a str class equal to the input "relativeTime" with added delay from the scheduling of commands, where the delay between commands is stated in OPT_Config_File.

"""


from . Commands import Commands
from .Procedures import BinnedCalibration_procedure, Full_CCD_procedure, LowPixel_procedure, High_res_IR_procedure, High_res_UV_procedure, CustomBinning_procedure


def Mode1_2_3_4_custom(root, relativeTime, pointing_altitude, UV_on = True, nadir_on = True, comment = ''):
    ''' Macro that corresponds to Mode1/3 when exposure on the nadir CCD is enabled during NLC season at LP latitudes polewards of X degrees, where X is specified in OPT_Config_File.Mode_1_2_3_4_5_6settings"
        
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    if( UV_on == True and nadir_on == True ):
        relativeTime = CustomBinning_procedure(root = root, relativeTime = relativeTime, comment = comment)
    elif( UV_on == False and nadir_on == True):
        relativeTime = CustomBinning_procedure(root = root, relativeTime = relativeTime, UV_TEXPMS = 0, comment = comment)
    elif( UV_on == True and nadir_on == False):
        relativeTime = CustomBinning_procedure(root = root, relativeTime = relativeTime, nadirTEXPMS = 0, comment = comment)
    elif( UV_on == False and nadir_on == False):
        relativeTime = CustomBinning_procedure(root = root, relativeTime = relativeTime, UV_TEXPMS = 0, nadirTEXPMS = 0, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime



def Mode5_6(root, relativeTime, pointing_altitude, comment = ''):
    ''' Macro that corresponds to Mode5/6
        
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    
    relativeTime = CustomBinning_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime

def NLC_night(root, relativeTime, pointing_altitude, UV_on, comment):
    ''' Macro that corresponds to Mode1/3 when exposure on the nadir CCD is enabled during NLC season at LP latitudes polewards of X degrees, where X is specified in OPT_Config_File.Mode_1_2_3_4_5_6settings"
        
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    if( UV_on == True ):
        relativeTime = High_res_UV_procedure(root = root, relativeTime = relativeTime, comment = comment)
    elif( UV_on == False):
        relativeTime = High_res_UV_procedure(root = root, relativeTime = relativeTime, UV_TEXPMS = 0, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime
    
    
def NLC_day(root, relativeTime, pointing_altitude, UV_on, comment):
    ''' Macro that corresponds to Mode1/3 when exposure on the nadir CCD is disabled during NLC season at LP latitudes polewards of X degrees, where X is specified in OPT_Config_File.Mode_1_2_3_4_5_6settings"
        
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    if( UV_on == True ):
        relativeTime = High_res_UV_procedure(root = root, relativeTime = relativeTime, nadirTEXPMS = 0, comment = comment)
    elif( UV_on == False):
        relativeTime = High_res_UV_procedure(root = root, relativeTime = relativeTime, nadirTEXPMS = 0, UV_TEXPMS = 0, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime,  Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime

"""
def NLC_nadir_on_off(root, relativeTime, nadir_on, comment):
    ''' Macro that corresponds to effectively turning the nadir imager on/off by setting the TEXPMS. Used by Mode1/3 to avoid having to re-send commands for all CCDs.
        
        Arguments:
            nadir_on (bool): Either enables or disables exposure on the nadir CCD by setting the TEXPMS. True for enabled and False for disabled.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    if( nadir_on == True):
        relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 2000, ExpTime = 1500, comment = comment, 
                                              NRSKIP = 0, NRBIN= 73, NROW = 7, NCBIN = 73, NCOL = 28, JPEGQ = 90)
    elif( nadir_on == False):
        relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 2000, ExpTime = 0, comment = comment, 
                                              NRSKIP = 0, NRBIN= 73, NROW = 7, NCBIN = 73, NCOL = 28, JPEGQ = 90)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime
"""
   
    
    
def IR_night(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode1/3 (at LP latitudes equatorwards of +-45 degrees) and Mode2/4. Exposure on Nadir is enabled."
        
        Arguments:
            pointing_altitude (int): The altitude of the tangential LP [m].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = High_res_IR_procedure(root, relativeTime, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime
    

def IR_day(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode1/3 (at LP latitudes equatorwards of +-45 degrees) and Mode2/4. Exposure on Nadir is disabled."
        
        Arguments:
            pointing_altitude (int): The altitude of the tangential LP [m].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = High_res_IR_procedure(root, relativeTime, nadirTEXPMS = 0, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime

"""
def IR_nadir_on_off(root, relativeTime, nadir_on, comment):
    ''' Macro that corresponds to effectively turning the nadir imager on/off by setting the TEXPMS. Used by Mode1-4 to avoid having to re-send commands for all CCDs.
        
        Arguments:
            nadir_on (bool): Either enables or disables exposure on the nadir CCD by setting the TEXPMS. True for enabled and False for disabled.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    if( nadir_on == True ):
        relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 2000, ExpTime = 1500, comment = comment, 
                                              NRSKIP = 0, NRBIN= 36, NROW = 14, NCBIN = 36, NCOL = 56, JPEGQ = 90)
    if( nadir_on == False ):
        relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 2000, ExpTime = 0, comment = comment, 
                                              NRSKIP = 0, NRBIN= 36, NROW = 14, NCBIN = 36, NCOL = 56, JPEGQ = 90)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime
"""

def Mode100_macro(root, relativeTime, pointing_altitude, ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, comment = ''):
    ''' Macro that corresponds to Mode100.
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential LP [m].
            ExpTimeUV (int) = Sets the exposuretime of the UV CCDs in ms.
            ExpIntUV (int) = Sets the exposuretime interval of the UV CCDs in ms.
            ExpTimeIR (int) = Sets the exposuretime of the IR CCDs in ms.
            ExpIntIR (int) = Sets the exposuretime interval of the IR CCDs in ms.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = BinnedCalibration_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpIntUV, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpIntIR, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime
    


def Mode110_macro(root, relativeTime, pointing_altitude_from, pointing_altitude_to, sweep_rate, comment = ''):
    '''Macro that corresponds to Mode110
    
        Arguments:
            pointing_altitude_from (int): The altitude in meters from which to start the sweep 
            pointing_altitude_from (int): The altitude in meters where the sweep will end
            sweep_rate (int): The rate of the sweep in m/s.
            
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = BinnedCalibration_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
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
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Full_CCD_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
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
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = Full_CCD_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
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
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = BinnedCalibration_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpTimeUV+2000, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpTimeIR+2000, comment = comment)
    
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
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    
    relativeTime = LowPixel_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpTimeUV+2000, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpTimeIR+2000, comment = comment)
    
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
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Full_CCD_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSEL = CCDSEL, comment = comment)
        Snapshot_relativeTime = Snapshot_relativeTime + SnapshotSpacing
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = LP_pointing_altitude, Final = LP_pointing_altitude, Rate = 0, comment = comment)
    
    return relativeTime


def Mode130_macro(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode130
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Full_CCD_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    for CCDSEL in [1,2,4,8,16,32]:
        relativeTime = Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSEL = CCDSEL, comment = comment)
        relativeTime = relativeTime + 1
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Mode131_macro(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode132
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Full_CCD_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Mode132_macro(root, relativeTime, pointing_altitude, ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, comment):
    ''' Macro that corresponds to Mode132
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
            ExpInt (int): Exposure interval [ms].
            ExpTime (int): Exposure time [ms].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = BinnedCalibration_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpIntUV, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpIntIR, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime


def Mode133_macro(root, relativeTime, pointing_altitude, ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, comment):
    ''' Macro that corresponds to Mode133
    
        Arguments:
            pointing_altitude (int): The altitude of the tangential point [m].
            ExpInt (int): Exposure interval [ms].
            ExpTime (int): Exposure time [ms].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = LowPixel_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpIntUV, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpIntIR, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = 0, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
    
    return relativeTime




def PWRTOGGLE_macro(root, relativeTime, CONST, comment = ''):
    ''' Macro that corresponds to the PWRTOGGLE CMD.
    
    Switches off all CCDs before PWRTOGGLING
    
        Arguments:
            CONST (int): Magical constant.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 127, PWR = 0, ExpInterval = 6000, ExpTime = 0, comment = comment)
    
    Commands.TC_pafPWRToggle(root, relativeTime, CONST = CONST, comment = comment)
    
    
    return relativeTime


def Limb_functional_test_macro(root, relativeTime, pointing_altitude, ExpTime, JPEGQ, comment = ''):
    '''Limb_functional_test_macro
    
        Arguments: 
            pointing_altitude (int): The altitude of the tangential point [m].
            ExpTime (int): Exposure time in ms
            JPEGQ (int): The JPEG quality in %
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
            ExpTime (int): Exposure time in ms
            ExpInt (int): Exposure interval in ms
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 2, comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, time = relativeTime, TEXPMS= ExpTime, TEXPIMS = ExpInt)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1, comment = comment)
        
    return relativeTime



def Nadir_functional_test_macro(root, relativeTime, pointing_altitude, ExpTime, JPEGQ, comment = ''):
    '''Nadir_functional_test
    
        Arguments: 
            pointing_altitude (int): The altitude of the tangential point [m].
            ExpTime (int): Exposure time in ms
            JPEGQ (int): The JPEG quality in %
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
