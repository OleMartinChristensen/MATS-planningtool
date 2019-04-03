# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 15:58:38 2019
Contain procedures which represent a sequence of commands often used by macros.

Arguments:
    root =  XML tree structure. Main container object for the ElementTree API. lxml.etree.Element class
    relativeTime = The relative time of the procedure with regard to the start of the timeline [s] as an str class
    comment = A comment for the procedure as a str class
    *Any other optional inputs depending on the procedure which are defined in each procedure function*
    
Output:
    relativeTime = Time [s] as a str class equal to the input "relativeTime" with added delay from the scheduling of each command, where the delay between commands is stated in OPT_Config_File.

@author: David
"""

from Operational_Planning_Tool.OPT_XML_generator_Commands import *

def Standard_binning_procedure(root, relativeTime, nadir, comment = ''):
    '''Standard CCD binning, see module description for more details.
        
        Arguments: 
            nadir [str]: Sets the nadir CCD on or off. Either "1" for on or "0" for off.
    
    '''
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = nadir, ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    return relativeTime


def Full_CCD_stopNadir_procedure(root, relativeTime, comment = ''):
    '''Full CCD binning with nadir camera off, see module description for more details.
    '''
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = '3000', ExpTime = '3000', comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '1', NumRows = '512', NumColumnsBin = '1', NumColumns = '2048')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '1', NumRows = '512', NumColumnsBin = '1', NumColumns = '2048')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '1', NumRows = '512', NumColumnsBin = '1', NumColumns = '2048')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    return relativeTime


def Single_pixel_stopNadir_procedure(root, relativeTime, ExpInt, ExpTime, comment = ''):
    '''Single Pixel CCD binning with nadir stopped, see module description for more details.
    
        Arguments: 
            ExpInt [str]: Exposure interval in ms
            ExpTime [str]: Exposure time in ms
    '''
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '1', ExpInterval = ExpInt, ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '512', NumRows = '512', NumColumnsBin = '2048', NumColumns = '2048')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = ExpInt, ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '512', NumRows = '512', NumColumnsBin = '2048', NumColumns = '2048')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = ExpInt, ExpTime = ExpTime, comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '512', NumRows = '512', NumColumnsBin = '2048', NumColumns = '2048')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = '0', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    return relativeTime


def High_res_IR_procedure(root, relativeTime, nadir, comment = ''):
    '''High resolution IR binning, see module description for more details.
        
        Arguments: 
            nadir [str]: Sets the nadir CCD on or off. Either "1" for on or "0" for off.
    
    '''
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '3', CCDMode = '0', ExpInterval = '3000', ExpTime = '3000', comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '2', NumRows = '400', NumColumnsBin = '40', NumColumns = '2000')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '12', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '3', NumRows = '400', NumColumnsBin = '81', NumColumns = '2000')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '48', CCDMode = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '100', NumRowsBin= '7', NumRows = '400', NumColumnsBin = '409', NumColumns = '2000')
    
    
    relativeTime = TC_pafCCDMain(root, relativeTime, CCDselect = '64', CCDMode = nadir, ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NumRowsSkip = '0', NumRowsBin= '110', NumRows = '500', NumColumnsBin = '196', NumColumns = '1980', JPEGquality = '100')
    
    return relativeTime
