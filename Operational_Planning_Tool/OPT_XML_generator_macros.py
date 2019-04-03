# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 14:31:43 2018

Contains macro functions that represent parts of or a whole science-mode/test.

Arguments:
    root [lxml.etree._Element]:  XML tree structure. Main container object for the ElementTree API.
    relativeTime [str]: The relative starting time of the macro with regard to the start of the timeline [s]
    comment [str]: A comment for the macro
    *Any other optional inputs depending on the macro which are defined in each macro function*
    
Returns:
    relativeTime [str]: Time in seconds as a str class equal to the input "relativeTime" with added delay from the scheduling of commands, where the delay between commands is stated in OPT_Config_File.

@author: David
"""


from Operational_Planning_Tool.OPT_XML_generator_Commands import *
from Operational_Planning_Tool.OPT_XML_generator_procedures import Standard_binning_procedure, Full_CCD_stopNadir_procedure, Single_pixel_stopNadir_procedure, High_res_IR_procedure
from OPT_Config_File import Timeline_settings


def NLC_night(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode1 when nadir is on during NLC season at latitudes polewards of +-45 degrees"
        
        Arguments:
            pointing_altitude [str]: The altitude of the tangential point [m].
    '''
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    
    relativeTime = Standard_binning_procedure(root = root, relativeTime = relativeTime, nadir = '1', comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    
    
def NLC_day(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode1 when nadir is off during NLC season at latitudes polewards of +-45 degrees"
        
        Arguments:
            pointing_altitude [str]: The altitude of the tangential point [m].
    '''
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime,  Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    
    relativeTime = Standard_binning_procedure(root = root, relativeTime = relativeTime, nadir = '0', comment = comment)
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    
    
def IR_night(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode1 (at latitudes equatorwards of +-45 degrees) and Mode2. Nadir is on."
        
        Arguments:
            pointing_altitude [str]: The altitude of the tangential LP [m] as a str class.
    '''
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = High_res_IR_procedure(root, relativeTime, nadir = '1', comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    

def IR_day(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode1 (at latitudes equatorwards of +-45 degrees) and Mode2. Nadir is off."
        
        Arguments:
            pointing_altitude [str]: The altitude of the tangential LP [m] as a str class.
    '''
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = High_res_IR_procedure(root, relativeTime, nadir = '0', comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    

def Mode100_macro(root, relativeTime, pointing_altitude, comment = ''):
    ''' Macro that corresponds to Mode100.
    
        Arguments:
            pointing_altitude [str]: The altitude of the tangential LP [m] as a str class.
    '''
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = Standard_binning_procedure(root = root, relativeTime = relativeTime, nadir = '0', comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    


def Mode110_macro(root, relativeTime, pointing_altitude_from, pointing_altitude_to, sweep_rate, relativeTime_sweep_start, comment = ''):
    '''Macro that corresponds to Mode110
    
        Arguments:
            pointing_altitude_from [str]: The altitude in meters from which to start the sweep 
            pointing_altitude_from [str]: The altitude in meters where the sweep will end
            sweep_rate [str]: The rate of the sweep in m/s.
            relativeTime_sweep [str]: The relative starting time of the sweep in seconds with regard to the start of the timeline
            
    '''
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = Standard_binning_procedure(root = root, relativeTime = relativeTime, nadir = '0', comment = comment)
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude_from, Final = pointing_altitude_from, comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime_sweep_start, Initial = pointing_altitude_from, Final = pointing_altitude_to, Rate = sweep_rate, comment = comment)
    
    return relativeTime
    
    


def Mode120_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, comment):
    ''' Macro that corresponds to Mode120.
    
        Arguments:
            freezeTime [str]: Start time of attitude freeze command in on-board time [s] as a str class.
            FreezeDuration [str]: Duration of freeze [s] as a str class.
            pointing_altitude [str]: The altitude of the tangential point [m] as a str class.
    '''
    
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    
    relativeTime = TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    Full_CCD_stopNadir_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode121_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, comment):
    ''' Macro that corresponds to Mode121.
    
        Arguments:
            freezeTime [str]: Start time of attitude freeze command in on-board time [s] as a str class.
            FreezeDuration [str]: Duration of freeze [s] as a str class.
            pointing_altitude [str]: The altitude of the tangential point [m] as a str class.
    '''
    
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    
    relativeTime = TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = Standard_binning_procedure(root = root, relativeTime = relativeTime, nadir = '0', comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode122_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, ExpInt, ExpTime, comment):
    ''' Macro that corresponds to Mode122.
    
        Arguments:
            freezeTime [str]: Start time of attitude freeze command in on-board time [s] as a str class.
            FreezeDuration [str]: Duration of freeze [s] as a str class.
            pointing_altitude [str]: The altitude of the tangential point [m] as a str class.
            ExpInt [str]: Exposure interval [ms] as a str.
            ExpTime [str]: Exposure time [ms] as a str.
    '''
    
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    
    relativeTime = TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = Single_pixel_stopNadir_procedure(root = root, relativeTime = relativeTime, ExpInt = ExpInt, ExpTime = ExpTime, comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime
    
    

def Mode130_macro(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode130
    
        Arguments:
            pointing_altitude [str]: The altitude of the tangential point [m] as a str class.
    '''
    
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    Full_CCD_stopNadir_procedure(root = root, relativeTime = relativeTime, comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode131_macro(root, relativeTime, pointing_altitude, comment):
    ''' Macro that corresponds to Mode131
    
        Arguments:
            pointing_altitude [str]: The altitude of the tangential point [m] as a str class.
            ExpInt [str]: Exposure interval [ms] as a str.
            ExpTime [str]: Exposure time [ms] as a str.
    '''
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    relativeTime = Standard_binning_procedure(root = root, relativeTime = relativeTime, nadir = '0', comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode132_macro(root, relativeTime, pointing_altitude, ExpInt, ExpTime, comment):
    ''' Macro that corresponds to Mode132
    
        Arguments:
            pointing_altitude [str]: The altitude of the tangential point [m] as a str class.
            ExpInt [str]: Exposure interval [ms] as a str.
            ExpTime [str]: Exposure time [ms] as a str.
    '''
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    Single_pixel_stopNadir_procedure(root = root, relativeTime = relativeTime, ExpInt = ExpInt, ExpTime = ExpTime, comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime


def Mode200_macro(root, relativeTime, freezeTime, FreezeDuration, pointing_altitude, comment):
    ''' Macro that corresponds to Mode200.
    
        Arguments:
            freezeTime [str]: Start time of attitude freeze command in on-board time [s] as a str class.
            FreezeDuration [str]: Duration of freeze [s] as a str class.
            pointing_altitude [str]: The altitude of the tangential point [m] as a str class.
    '''
    
    
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = comment)
    
    
    relativeTime = TC_affArgFreezeStart(root, relativeTime, StartTime = freezeTime, comment = comment)
    
    
    relativeTime = TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = comment)
    
    relativeTime = Standard_binning_procedure(root = root, relativeTime = relativeTime, nadir = '0', comment = comment)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
    
    return relativeTime



def Limb_functional_test_macro(root, relativeTime, pointing_altitude, ExpTime, JPEGQ, comment = ''):
    '''Limb_functional_test_macro
    
        Arguments: 
            pointing_altitude [str]: The altitude of the tangential point [m].
            ExpTime [str]: Exposure time in ms
            JPEGQ [str]: The JPEG quality in %
    '''
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000', JPEGquality = JPEGQ)
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000', JPEGquality = JPEGQ)
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000', JPEGquality = JPEGQ)
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
    
    relativeTime = TC_pafCCDSnapshot(root, relativeTime, CCDSelect = '63', comment = '')
    
    ''' #Snapshot with on CCD at a time with 5 seconds intervall
    for CCDSelect in ['1','2','4','8','16','32']:
        
        relativeTime = TC_pafCCDSnapshot(root, relativeTime, CCDSelect = CCDSelect, comment = '')
        relativeTime = str(round(float(relativeTime) + 5-Timeline_settings()['command_separation'],2))
    '''
    
    return relativeTime



def Photometer_test_1_macro(root, relativeTime, ExpTime, ExpInt, comment = ''):
    '''Photometer_test_1_macro

        Arguments:
            ExpTime [str]: Exposure time in ms
            ExpInt [str]: Exposure interval in ms
    '''
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = TC_pafCCDPM(root, time = relativeTime, ExposureTime = ExpTime, ExposureInterval = ExpInt)
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "1", comment = comment)
        
    return relativeTime



def Nadir_functional_test_macro(root, relativeTime, pointing_altitude, ExpTime, JPEGQ, comment = ''):
    '''Nadir_functional_test
    
        Arguments: 
            pointing_altitude [str]: The altitude of the tangential point [m].
            ExpTime [str]: Exposure time in ms
            JPEGQ [str]: The JPEG quality in %
    '''
    
    relativeTime = TC_pafMode(root, relativeTime, mode = "2", comment = comment)
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '0', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000', JPEGquality = JPEGQ)
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '0', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000', JPEGquality = JPEGQ)
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '0', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000', JPEGquality = JPEGQ)
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '1', ExpInterval = '0', ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = JPEGQ)
    
    
    relativeTime = TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = comment)
        
    relativeTime = TC_pafCCDSnapshot(root, relativeTime, CCDSelect = '64', comment = '')
    
    return relativeTime



'''
def Mode_User_Specified_macro(root, relativeTime, comment = ''):
    "This is a template for a new macro. Exchange '_User_Specified' for the name of the new macro"
    
    
    return relativeTime
    
'''
