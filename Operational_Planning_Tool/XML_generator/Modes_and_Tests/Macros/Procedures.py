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

from . Commands import Commands

def Standard_binning_procedure(root, relativeTime, nadir, ExpIntUV = '3001', ExpTimeUV = '3000', ExpIntIR = '5001', ExpTimeIR = '5000', comment = ''):
    '''Standard CCD binning, see module description for more details.
        
        Arguments: 
            nadir (str): Sets the nadir CCD on or off. Either "1" for on or "0" for off.
            ExpIntUV (str): Exposure interval of UV CCDs in ms
            ExpTimeUV (str): Exposure time of UV CCDs in ms
            ExpIntIR (str): Exposure interval of IR CCDs in ms
            ExpTimeIR (str): Exposure time of IR CCDs in ms
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '3', PWR = '1', ExpInterval = ExpIntUV, ExpTime = ExpTimeUV, comment = comment, 
                  NRSKIP = '100', NRBIN= '2', NROW = '400', NCBIN = '40', NCOL = '2000')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '12', PWR = '1', ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = '100', NRBIN= '3', NROW = '400', NCBIN = '81', NCOL = '2000')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '1', ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = '100', NRBIN= '7', NROW = '400', NCBIN = '409', NCOL = '2000')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = nadir, ExpInterval = '1400', ExpTime = '1000', comment = comment, 
                  NRSKIP = '0', NRBIN= '110', NROW = '500', NCBIN = '196', NCOL = '1980', JPEGQ = '100')
    
    return relativeTime


def Full_CCD_stopNadir_procedure(root, relativeTime, comment = ''):
    '''Full CCD binning with nadir camera off, see module description for more details.
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '3', PWR = '1', ExpInterval = '3000', ExpTime = '3000', comment = comment, 
                  NRSKIP = '0', NRBIN= '1', NROW = '512', NCBIN = '1', NCOL = '2048')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '12', PWR = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '1', NROW = '512', NCBIN = '1', NCOL = '2048')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '1', NROW = '512', NCBIN = '1', NCOL = '2048')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '0', ExpInterval = '1400', ExpTime = '1000', comment = comment, 
                  NRSKIP = '0', NRBIN= '110', NROW = '500', NCBIN = '196', NCOL = '1980', JPEGQ = '100')
    
    return relativeTime


def Single_pixel_stopNadir_procedure(root, relativeTime, ExpInt, ExpTime, comment = ''):
    '''Single Pixel CCD binning with nadir stopped, see module description for more details.
    
        Arguments: 
            ExpInt (str): Exposure interval of UV and IR CCDs in ms
            ExpTime (str): Exposure time of UV and IR CCDs in ms
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '3', PWR = '1', ExpInterval = ExpInt, ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '512', NROW = '512', NCBIN = '2048', NCOL = '2048')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '12', PWR = '1', ExpInterval = ExpInt, ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '512', NROW = '512', NCBIN = '2048', NCOL = '2048')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '1', ExpInterval = ExpInt, ExpTime = ExpTime, comment = comment, 
                  NRSKIP = '0', NRBIN= '512', NROW = '512', NCBIN = '2048', NCOL = '2048')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '0', ExpInterval = '1400', ExpTime = '1000', comment = comment, 
                  NRSKIP = '0', NRBIN= '110', NROW = '500', NCBIN = '196', NCOL = '1980', JPEGQ = '100')
    
    return relativeTime


def High_res_IR_procedure(root, relativeTime, nadir, comment = ''):
    '''High resolution IR binning, see module description for more details.
        
        Arguments: 
            nadir (str): Sets the nadir CCD on or off. Either "1" for on or "0" for off.
    
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '3', PWR = '0', ExpInterval = '3000', ExpTime = '3000', comment = comment, 
                  NRSKIP = '100', NRBIN= '2', NROW = '400', NCBIN = '40', NCOL = '2000')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '12', PWR = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '100', NRBIN= '3', NROW = '400', NCBIN = '81', NCOL = '2000')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '1', ExpInterval = '5000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '100', NRBIN= '7', NROW = '400', NCBIN = '409', NCOL = '2000')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = nadir, ExpInterval = '1400', ExpTime = '1000', comment = comment, 
                  NRSKIP = '0', NRBIN= '110', NROW = '500', NCBIN = '196', NCOL = '1980', JPEGQ = '100')
    
    return relativeTime
