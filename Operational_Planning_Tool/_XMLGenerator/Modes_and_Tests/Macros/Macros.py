# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 14:31:43 2018

Contains macro functions that represent parts of or a whole science-mode/test.

Arguments:
    root (lxml.etree._Element):  XML tree structure. Main container object for the ElementTree API.
    relativeTime (str): The relative starting time of the macro with regard to the start of the timeline [s]
    comment (str): A comment for the macro
    *Any other optional inputs depending on the macro which are defined in each macro function*
    
Returns:
    relativeTime (str): Time in seconds as a str class equal to the input "relativeTime" with added delay from the scheduling of commands, where the delay between commands is stated in OPT_Config_File.

"""


from . Commands import Commands
from .Procedures import BinnedCalibration_procedure, Full_CCD_procedure, Single_pixel_procedure, High_res_IR_procedure, High_res_UV_procedure

def NLC_night(root, relativeTime, pointing_altitude, UV_on, comment):
    ''' Macro that corresponds to Mode1/3 when exposure on the nadir CCD is enabled during NLC season at LP latitudes polewards of X degrees, where X is specified in OPT_Config_File.Mode_1_2_3_4_settings"
        
        Arguments:
            pointing_altitude (str): The altitude of the tangential point [m].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    if( UV_on == True ):
        relativeTime = High_res_UV_procedure(root = root, relativeTime = relativeTime, nadirTEXPMS = '1500', UV_TEXPMS = '3000', comment = comment)
    elif( UV_on == False):
        relativeTime = High_res_UV_procedure(root = root, relativeTime = relativeTime, nadirTEXPMS = '1500', UV_TEXPMS = '0', comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    
    
def NLC_day(root, relativeTime, pointing_altitude, UV_on, comment):
    ''' Macro that corresponds to Mode1/3 when exposure on the nadir CCD is disabled during NLC season at LP latitudes polewards of X degrees, where X is specified in OPT_Config_File.Mode_1_2_3_4_settings"
        
        Arguments:
            pointing_altitude (str): The altitude of the tangential point [m].
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    if( UV_on == True ):
        relativeTime = High_res_UV_procedure(root = root, relativeTime = relativeTime, nadirTEXPMS = '0', UV_TEXPMS = '3000', comment = comment)
    elif( UV_on == False):
        relativeTime = High_res_UV_procedure(root = root, relativeTime = relativeTime, nadirTEXPMS = '0', UV_TEXPMS = '0', comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime,  Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def NLC_nadir_on_off(root, relativeTime, nadir_on, comment):
    ''' Macro that corresponds to effectively turning the nadir imager on/off by setting the TEXPMS. Used by Mode1/3 to avoid having to re-send commands for all CCDs.
        
        Arguments:
            nadirTEXPMS (str): Either enables or disables exposure on the nadir CCD by setting the TEXPMS to "X", where X is a number in ms, for enabled or to "0" for disabled.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    if( nadir_on == True):
        relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '2000', ExpTime = '1500', comment = comment, 
                                              NRSKIP = '0', NRBIN= '73', NROW = '7', NCBIN = '73', NCOL = '28', JPEGQ = '90')
    elif( nadir_on == False):
        relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '2000', ExpTime = '0', comment = comment, 
                                              NRSKIP = '0', NRBIN= '73', NROW = '7', NCBIN = '73', NCOL = '28', JPEGQ = '90')
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
   
    
    
def IR_night(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode1/3 (at LP latitudes equatorwards of +-45 degrees) and Mode2/4. Exposure on Nadir is enabled."
        
        Arguments:
            pointing_altitude (str): The altitude of the tangential LP [m] as a str class.
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = High_res_IR_procedure(root, relativeTime, nadirTEXPMS = '1500', comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    

def IR_day(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode1/3 (at LP latitudes equatorwards of +-45 degrees) and Mode2/4. Exposure on Nadir is disabled."
        
        Arguments:
            pointing_altitude (str): The altitude of the tangential LP [m] as a str class.
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, relativeTime, comment = comment)
    
    relativeTime = High_res_IR_procedure(root, relativeTime, nadirTEXPMS = '0', comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def IR_nadir_on_off(root, relativeTime, nadir_on, comment):
    ''' Macro that corresponds to effectively turning the nadir imager on/off by setting the TEXPMS. Used by Mode1-4 to avoid having to re-send commands for all CCDs.
        
        Arguments:
            nadirTEXPMS (str): Either enables or disables exposure on the nadir CCD by setting the TEXPMS to "X", where X is a number in ms, for enabled or to "0" for disabled.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    if( nadir_on == True ):
        relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '2000', ExpTime = '1500', comment = comment, 
                                              NRSKIP = '0', NRBIN= '36', NROW = '14', NCBIN = '36', NCOL = '56', JPEGQ = '90')
    if( nadir_on == False ):
        relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '2000', ExpTime = '0', comment = comment, 
                                              NRSKIP = '0', NRBIN= '36', NROW = '14', NCBIN = '36', NCOL = '56', JPEGQ = '90')
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
 

def Mode100_macro(root, relativeTime, pointing_altitude, ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, comment = ''):
    ''' Macro that corresponds to Mode100.
    
        Arguments:
            pointing_altitude (str): The altitude of the tangential LP [m] as a str class.
            ExpTimeUV (str) = Sets the exposuretime of the UV CCDs.
            ExpIntUV (str) = Sets the exposuretime interval of the UV CCDs.
            ExpTimeIR (str) = Sets the exposuretime of the IR CCDs.
            ExpIntIR (str) = Sets the exposuretime interval of the IR CCDs.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = BinnedCalibration_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpIntUV, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpIntIR, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    


def Mode110_macro(root, relativeTime, pointing_altitude_from, pointing_altitude_to, sweep_rate, relativeTime_sweep_start, comment = ''):
    '''Macro that corresponds to Mode110
    
        Arguments:
            pointing_altitude_from (str): The altitude in meters from which to start the sweep 
            pointing_altitude_from (str): The altitude in meters where the sweep will end
            sweep_rate (str): The rate of the sweep in m/s.
            relativeTime_sweep (str): The relative starting time of the sweep in seconds with regard to the start of the timeline
            
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = BinnedCalibration_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude_from, Final = pointing_altitude_from, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime_sweep_start, Initial = pointing_altitude_from, Final = pointing_altitude_to, Rate = sweep_rate, comment = comment)
    
    return relativeTime
    
    


def Mode120_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, Snapshot_relativeTime, comment):
    ''' Macro that corresponds to Mode120.
    
        Arguments:
            freezeTime (str): Start time of attitude freeze command in on-board time [s] as a str class.
            FreezeDuration (str): Duration of freeze [s] as a str class.
            pointing_altitude (str): The altitude of the tangential point [m] as a str class.
            Snapshot_relativeTime (str): The relativeTime (time from start of timeline) at which the Snapshot is taken.
    '''
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Full_CCD_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSelect = "63", comment = comment)
    
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode121_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, Snapshot_relativeTime, 
                  ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, comment):
    ''' Macro that corresponds to Mode121.
    
        Arguments:
            freezeTime (str): Start time of attitude freeze command in on-board time [s] as a str class.
            FreezeDuration (str): Duration of freeze [s] as a str class.
            pointing_altitude (str): The altitude of the tangential point [m] as a str class.
            Snapshot_relativeTime (str): The relativeTime (time from start of timeline) at which the Snapshot is taken.
    '''
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = BinnedCalibration_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpIntUV, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpIntIR, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSelect = "63", comment = comment)
    
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode122_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, Snapshot_relativeTime, 
                  ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, comment):
    ''' Macro that corresponds to Mode122.
    
        Arguments:
            freezeTime (str): Start time of attitude freeze command in on-board time [s] as a str class.
            FreezeDuration (str): Duration of freeze [s] as a str class.
            pointing_altitude (str): The altitude of the tangential point [m] as a str class.
            ExpInt (str): Exposure interval [ms] as a str.
            ExpTime (str): Exposure time [ms] as a str.
            Snapshot_relativeTime (str): The relativeTime (time from start of timeline) at which the Snapshot is taken.
    '''
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = Single_pixel_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpIntUV, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpIntIR, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSnapshot(root, Snapshot_relativeTime, CCDSelect = "63", comment = comment)
    
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    
    

def Mode130_macro(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode130
    
        Arguments:
            pointing_altitude (str): The altitude of the tangential point [m] as a str class.
    '''
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Full_CCD_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    relativeTime = Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSelect = "63", comment = comment)
    
    #relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode131_macro(root, relativeTime, pointing_altitude, ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, comment):
    ''' Macro that corresponds to Mode131
    
        Arguments:
            pointing_altitude (str): The altitude of the tangential point [m] as a str class.
            ExpInt (str): Exposure interval [ms] as a str.
            ExpTime (str): Exposure time [ms] as a str.
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = BinnedCalibration_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpIntUV, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpIntIR, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode132_macro(root, relativeTime, pointing_altitude, ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, comment):
    ''' Macro that corresponds to Mode132
    
        Arguments:
            pointing_altitude (str): The altitude of the tangential point [m] as a str class.
            ExpInt (str): Exposure interval [ms] as a str.
            ExpTime (str): Exposure time [ms] as a str.
    '''
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Single_pixel_procedure(root = root, relativeTime = relativeTime, ExpTimeUV = ExpTimeUV, 
                                              ExpIntUV = ExpIntUV, ExpTimeIR = ExpTimeIR, ExpIntIR = ExpIntIR, comment = comment)
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode200_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, comment):
    ''' Macro that corresponds to Mode200.
    
        Arguments:
            freezeTime (str): Start time of attitude freeze command in on-board time [s] as a str class.
            FreezeDuration (str): Duration of freeze [s] as a str class.
            pointing_altitude (str): The altitude of the tangential point [m] as a str class.
    '''
    
    
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = Commands.TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = BinnedCalibration_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def PWRTOGGLE_macro(root, relativeTime, CONST, comment = ''):
    ''' Macro that corresponds to the PWRTOGGLE CMD.
    
    Switches off all CCDs before PWRTOGGLING
    
        Arguments:
            CONST (str): Magical constant.
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '127', PWR = '0', ExpInterval = '1500', ExpTime = '1000', comment = comment)
    
    Commands.TC_pafPWRToggle(root, relativeTime, CONST = CONST, comment = comment)
    
    
    return relativeTime


def Limb_functional_test_macro(root, relativeTime, pointing_altitude, ExpTime, JPEGQ, comment = ''):
    '''Limb_functional_test_macro
    
        Arguments: 
            pointing_altitude (str): The altitude of the tangential point [m].
            ExpTime (str): Exposure time in ms
            JPEGQ (str): The JPEG quality in %
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '1', ExpInterval = '100', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '100', NRBIN= '2', NROW = '400', NCBIN = '40', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '9', PWR = '1', ExpInterval = '100', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '100', NRBIN= '3', NROW = '400', NCBIN = '81', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '6', PWR = '1', ExpInterval = '100', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '100', NRBIN= '7', NROW = '400', NCBIN = '409', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '0', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '110', NROW = '500', NCBIN = '196', NCOL = '1980', JPEGQ = '100')
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSelect = '63', comment = '')
    
    ''' #Snapshot with on CCD at a time with 5 seconds intervall
    for CCDSelect in ['1','2','4','8','16','32']:
        
        relativeTime = TC_pafCCDSnapshot(root, relativeTime, CCDSelect = CCDSelect, comment = '')
        relativeTime = str(round(float(relativeTime) + 5-Timeline_settings()['command_separation'],2))
    '''
    
    return relativeTime



def Photometer_test_1_macro(root, relativeTime, ExpTime, ExpInt, comment = ''):
    '''Photometer_test_1_macro

        Arguments:
            ExpTime (str): Exposure time in ms
            ExpInt (str): Exposure interval in ms
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Commands.TC_pafPM(root, time = relativeTime, TEXPMS= ExpTime, TEXPIMS = ExpInt)
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "1", comment = comment)
        
    return relativeTime



def Nadir_functional_test_macro(root, relativeTime, pointing_altitude, ExpTime, JPEGQ, comment = ''):
    '''Nadir_functional_test
    
        Arguments: 
            pointing_altitude (str): The altitude of the tangential point [m].
            ExpTime (str): Exposure time in ms
            JPEGQ (str): The JPEG quality in %
    '''
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '0', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '2', NROW = '400', NCBIN = '40', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '9', PWR = '0', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '3', NROW = '400', NCBIN = '81', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '6', PWR = '0', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '7', NROW = '400', NCBIN = '409', NCOL = '2000', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '110', NROW = '500', NCBIN = '196', NCOL = '1980', JPEGQ = JPEGQ)
    
    
    relativeTime = Commands.TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
        
    relativeTime = Commands.TC_pafCCDSnapshot(root, relativeTime, CCDSelect = '64', comment = '')
    
    return relativeTime



'''
def Mode_User_Specified_macro(root, relativeTime, comment = ''):
    "This is a template for a new macro. Exchange '_User_Specified' for the name of the new macro"
    
    
    return relativeTime
    
'''
