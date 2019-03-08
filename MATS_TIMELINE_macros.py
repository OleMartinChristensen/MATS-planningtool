# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 14:31:43 2018

Contains macros that represent parts of or a whole sciencemode

@author: David
"""

from lxml import etree
from MATS_TIMELINE_Commands import *


def NLC_night(root, relativeTime, pointing_altitude):

    TC_pafMode(root, relativeTime, mode = "2", comment = "NLC_NIGHT,"+pointing_altitude)
    
    TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = "NLC_NIGHT,"+pointing_altitude)
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', comment = "NLC_NIGHT,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "NLC_NIGHT,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "NLC_NIGHT,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "NLC_NIGHT,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    
    '''
    TC_pafCCDMain(root, relativeTime, CCDselect = '1', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '2', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '4', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '5', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '6', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '7', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    '''
    
    TC_pafMode(root, relativeTime, mode = "1", comment = "NLC_NIGHT,"+pointing_altitude)
    
    
def NLC_day(root, relativeTime, pointing_altitude):

    TC_pafMode(root, relativeTime, mode = "2", comment = "NLC_DAY,"+pointing_altitude)
    
    TC_acfLimbPointingAltitudeOffset(root, relativeTime,  Initial = pointing_altitude, Final = pointing_altitude, comment = "NLC_DAY,"+pointing_altitude)
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', comment = "NLC_DAY,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "NLC_DAY,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "NLC_DAY,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', comment = "NLC_DAY,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    '''
    TC_pafCCDMain(root, relativeTime, CCDselect = '1', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '2', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '4', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '5', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '6', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '7', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    '''
    
    TC_pafMode(root, relativeTime, mode = "1", comment = "NLC_DAY,"+pointing_altitude)
    
    
def IR_night(root, relativeTime, pointing_altitude):

    TC_pafMode(root, relativeTime, mode = "2", comment = "IR_NIGHT,"+pointing_altitude)
    
    TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = "IR_NIGHT,"+pointing_altitude)
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '0', ExpInterval = '3000', ExpTime = '3000', comment = "IR_NIGHT,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "IR_NIGHT,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "IR_NIGHT,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "IR_NIGHT,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    '''
    TC_pafCCDMain(root, relativeTime, CCDselect = '1', CCDMode = '0', ExpInterval = '3000', ExpTime = '3000', 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '2', CCDMode = '0', ExpInterval = '3000', ExpTime = '3000', 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '4', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '5', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '6', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '7', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    '''
    
    TC_pafMode(root, relativeTime, mode = "1", comment = "IR_NIGHT,"+pointing_altitude)
    

def IR_day(root, relativeTime, pointing_altitude):

    TC_pafMode(root, relativeTime, mode = "2", comment = "IR_DAY,"+pointing_altitude)
    
    TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, comment = "IR_DAY,"+pointing_altitude,)
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '0', ExpInterval = '3000', ExpTime = '3000', comment = "IR_DAY,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "IR_DAY,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "IR_DAY,"+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', comment = "IR_DAY,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    '''
    TC_pafCCDMain(root, relativeTime, CCDselect = '1', CCDMode = '0', ExpInterval = '3000', ExpTime = '3000', 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '2', CCDMode = '0', ExpInterval = '3000', ExpTime = '3000', 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '4', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '5', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '6', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '7', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    '''
    
    TC_pafMode(root, relativeTime, mode = "1", comment = "IR_DAY,"+pointing_altitude)
    
    
def Mode120_macro(root, relativeTime, StartTime, FreezeDuration, pointing_altitude):
    
    TC_pafMode(root, relativeTime, mode = "2", comment = "star_calibration,"+pointing_altitude)
    
    TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = "star_calibration,"+pointing_altitude)
    
    TC_affArgFreezeStart(root, relativeTime, StartTime = StartTime, comment = "star_calibration,"+pointing_altitude)
    
    TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = "star_calibration,"+pointing_altitude)
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', comment = "star_calibration,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '1', NumRows = '512', NumColumnsBin = '1', NumColumns = '2048')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "star_calibration,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '1', NumRows = '512', NumColumnsBin = '1', NumColumns = '2048')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "star_calibration,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '1', NumRows = '512', NumColumnsBin = '1', NumColumns = '2048')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', comment = "star_calibration,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    TC_pafMode(root, relativeTime, mode = "1", comment = "star_calibration, "+pointing_altitude)
    

def Mode130_macro(root, relativeTime, pointing_altitude):
    
    TC_pafMode(root, relativeTime, mode = "2", comment = "Mode130,"+pointing_altitude)
    
    TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = "Mode130,"+pointing_altitude)
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', comment = "Mode130,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '1', NumRows = '512', NumColumnsBin = '1', NumColumns = '2048')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "Mode130,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '1', NumRows = '512', NumColumnsBin = '1', NumColumns = '2048')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "Mode130,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '1', NumRows = '512', NumColumnsBin = '1', NumColumns = '2048')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', comment = "Mode130,"+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    TC_pafMode(root, relativeTime, mode = "1", comment = "Mode130, "+pointing_altitude)


def Mode200_macro(root, relativeTime, StartTime, FreezeDuration, pointing_altitude):
    
    TC_pafMode(root, relativeTime, mode = "2", comment = "Mode200, "+pointing_altitude)
    
    TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = pointing_altitude, Final = pointing_altitude, Rate = "0", comment = "Mode200, "+pointing_altitude)
    
    TC_affArgFreezeStart(root, relativeTime, StartTime = StartTime, comment = "Mode200, "+pointing_altitude)
    
    TC_affArgFreezeDuration(root, relativeTime, FreezeDuration = FreezeDuration, comment = "Mode200, "+pointing_altitude)
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', comment = "Mode200, "+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "Mode200, "+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = "Mode200, "+pointing_altitude, 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', comment = "Mode200, "+pointing_altitude, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    TC_pafMode(root, relativeTime, mode = "1", comment = "Mode200, "+pointing_altitude)
    
    
    
