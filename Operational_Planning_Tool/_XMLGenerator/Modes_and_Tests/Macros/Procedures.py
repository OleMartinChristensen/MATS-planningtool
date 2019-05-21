# -*- coding: utf-8 -*-
"""
Contain procedures which represent a sequence of commands often used by macros.

Arguments:
    root (lxml.etree._Element) =  XML tree structure. Main container object for the ElementTree API. \n
    relativeTime (str) = The relative time of the procedure with regard to the start of the timeline [s]. \n
    comment (str) = A comment for the procedure. \n
    *Any other optional inputs depending on the procedure which are defined in each procedure function*
    
Output:
    relativeTime (str) = Time [s] as a str class equal to the input "relativeTime" with added delay from the scheduling of each command, where the delay between commands is stated in OPT_Config_File.

"""

from . Commands import Commands




def BinnedCalibration_procedure(root, relativeTime, nadirTEXPMS = '0', ExpIntUV = '4000', ExpTimeUV = '3000', ExpIntIR = '6000', ExpTimeIR = '5000', comment = ''):
    '''Standard CCD binning with exposure on nadir camera by default is disabled, see module description for more details.
        
    Arguments: 
        nadir (str): Sets the nadir CCD on or off. Either "1" for on or "0" for off.
        ExpIntUV (str): Exposure interval of UV CCDs in ms
        ExpTimeUV (str): Exposure time of UV CCDs in ms
        ExpIntIR (str): Exposure interval of IR CCDs in ms
        ExpTimeIR (str): Exposure time of IR CCDs in ms
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '1', ExpInterval = ExpIntUV, ExpTime = ExpTimeUV, comment = comment, 
                  NRSKIP = '0', NRBIN= '2', NROW = '255', NCBIN = '40', NCOL = '51', SIGMODE = '0')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '9', PWR = '1', ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = '0', NRBIN= '2', NROW = '255', NCBIN = '40', NCOL = '51')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '6', PWR = '1', ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = '0', NRBIN= '6', NROW = '85', NCBIN = '400', NCOL = '5')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '4500', ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = '0', NRBIN= '36', NROW = '14', NCBIN = '36', NCOL = '56', JPEGQ = '90')
    
    return relativeTime


def Full_CCD_procedure(root, relativeTime, nadirTEXPMS = '0', comment = ''):
    '''Full CCD binning with exposure on nadir camera by default is disabled, see module description for more details.
    
    Arguments:
        nadir (str): Sets the nadir CCD on or off. Either "1" for on or "0" for off.
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '1', ExpInterval = '5000', ExpTime = '3000', comment = comment, 
                  NRSKIP = '0', NRBIN= '1', NROW = '511', NCBIN = '1', NCOL = '2047', JPEGQ = '110')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '9', PWR = '1', ExpInterval = '7000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '1', NROW = '511', NCBIN = '1', NCOL = '2047', JPEGQ = '110')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '6', PWR = '1', ExpInterval = '7000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '1', NROW = '511', NCBIN = '1', NCOL = '2047', JPEGQ = '110')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '3500', ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = '0', NRBIN= '1', NROW = '511', NCBIN = '1', NCOL = '2047')
    
    return relativeTime


def Single_pixel_procedure(root, relativeTime, ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, nadirTEXPMS = '0', comment = ''):
    '''Single Pixel CCD binning with exposure on nadir camera by default is disabled, see module description for more details.
    
    Arguments: 
        ExpInt (str): Exposure interval of UV and IR CCDs in ms
        ExpTime (str): Exposure time of UV and IR CCDs in ms
        nadir (str): Sets the nadir CCD on or off. Either "1" for on or "0" for off.
    
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '1', ExpInterval = ExpIntUV, ExpTime = ExpTimeUV, comment = comment, 
                  NRSKIP = '0', NRBIN= '511', NROW = '1', NCBIN = '2048', NCOL = '1', JPEGQ = '110')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '9', PWR = '1', ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = '0', NRBIN= '511', NROW = '1', NCBIN = '2048', NCOL = '1', JPEGQ = '110')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '6', PWR = '1', ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = '0', NRBIN= '511', NROW = '1', NCBIN = '2048', NCOL = '1', JPEGQ = '110')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '2000', ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = '0', NRBIN= '36', NROW = '14', NCBIN = '36', NCOL = '56')
    
    return relativeTime


def High_res_UV_procedure(root, relativeTime, nadirTEXPMS, UV_TEXPMS, comment = ''):
    '''Standard CCD binning, see module description for more details.
        
    Arguments: 
        nadir (str): Sets the nadir CCD on or off. Either "1" for on or "0" for off.
        ExpIntUV (str): Exposure interval of UV CCDs in ms
        ExpTimeUV (str): Exposure time of UV CCDs in ms
        ExpIntIR (str): Exposure interval of IR CCDs in ms
        ExpTimeIR (str): Exposure time of IR CCDs in ms
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '1', ExpInterval = '4000', ExpTime = UV_TEXPMS, comment = comment, 
                  NRSKIP = '0', NRBIN= '2', NROW = '255', NCBIN = '40', NCOL = '51', SIGMODE = '0')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '9', PWR = '1', ExpInterval = '6000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '3', NROW = '170', NCBIN = '80', NCOL = '25')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '6', PWR = '1', ExpInterval = '6000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '6', NROW = '85', NCBIN = '400', NCOL = '5')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '2000', ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = '0', NRBIN= '73', NROW = '7', NCBIN = '73', NCOL = '28', JPEGQ = '90')
    
    return relativeTime


def High_res_IR_procedure(root, relativeTime, nadirTEXPMS, comment = ''):
    '''High resolution IR binning, see module description for more details.
        
    Arguments: 
        nadir (str): Sets the nadir CCD on or off. Either "1" for on or "0" for off.
    
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '48', PWR = '0', ExpInterval = '6000', ExpTime = '0', comment = comment, 
                  NRSKIP = '0', NRBIN= '2', NROW = '255', NCBIN = '40', NCOL = '51', SIGMODE = '0')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '9', PWR = '1', ExpInterval = '6000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '2', NROW = '255', NCBIN = '40', NCOL = '51')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '6', PWR = '1', ExpInterval = '6000', ExpTime = '5000', comment = comment, 
                  NRSKIP = '0', NRBIN= '6', NROW = '85', NCBIN = '400', NCOL = '5')
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDselect = '64', PWR = '1', ExpInterval = '4500', ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = '0', NRBIN= '36', NROW = '14', NCBIN = '36', NCOL = '56', JPEGQ = '90')
    
    return relativeTime
