# -*- coding: utf-8 -*-
"""
Contain procedures which represent a sequence of commands often used by macros.

Arguments:
    root (lxml.etree._Element) =  XML tree structure. Main container object for the ElementTree API. \n
    relativeTime (int) = The relative time of the procedure with regard to the start of the timeline [s]. \n
    comment (str) = A comment for the procedure. \n
    *Any other optional inputs depending on the procedure which are defined in each procedure function*
    
Output:
    relativeTime (int) = Time [s] as a str class equal to the input "relativeTime" with added delay from the scheduling of each command, where the delay between commands is stated in OPT_Config_File.

"""

from . Commands import Commands


def CustomBinning_procedure(root, relativeTime, nadirTEXPMS = 1500, UV_TEXPMS = 3000, comment = ''):
    '''Custom binning, see module description for more details.
    
    Custom binning procedure used by Mode5-6.
        
    Arguments: 
        nadirTEXPMS (int): Sets the exposure time [ms] of the nadir CCD.
        UV_TEXPMS (int): Sets the exposure time [ms] of the UV CCDs.
    
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 48, PWR = 0, ExpInterval = 4000, ExpTime = UV_TEXPMS, comment = comment, 
                  NRSKIP = 0, NRBIN= 2, NROW = 255, NCBIN = 40, NCOL = 50, SIGMODE = 0)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 9, PWR = 1, ExpInterval = 6000, ExpTime = 5000, comment = comment, 
                  NRSKIP = 0, NRBIN= 2, NROW = 255, NCBIN = 40, NCOL = 50, WDW = 4)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 6, PWR = 1, ExpInterval = 6000, ExpTime = 5000, comment = comment, 
                  NRSKIP = 0, NRBIN= 6, NROW = 85, NCBIN = 200, NCOL = 8)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 4500, ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = 0, NRBIN= 25, NROW = 16, NCBIN = 36, NCOL = 55, JPEGQ = 90)
    
    return relativeTime



def BinnedCalibration_procedure(root, relativeTime, nadirTEXPMS = 0, ExpIntUV = 4000, ExpTimeUV = 3000, ExpIntIR = 6000, ExpTimeIR = 5000, comment = ''):
    '''Standard CCD binning with exposure on nadir camera by default is disabled, see module description for more details.
        
    Arguments: 
        nadirTEXPMS (int): Sets the exposure time [ms] of the nadir CCD.
        ExpIntUV (int): Exposure interval of UV CCDs in ms.
        ExpTimeUV (int): Exposure time of UV CCDs in ms.
        ExpIntIR (int): Exposure interval of IR CCDs in ms.
        ExpTimeIR (int): Exposure time of IR CCDs in ms.
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 48, PWR = 1, ExpInterval = ExpIntUV, ExpTime = ExpTimeUV, comment = comment, 
                  NRSKIP = 0, NRBIN= 2, NROW = 255, NCBIN = 40, NCOL = 50, SIGMODE = 0)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 9, PWR = 1, ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = 0, NRBIN= 2, NROW = 255, NCBIN = 40, NCOL = 50)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 6, PWR = 1, ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = 0, NRBIN= 6, NROW = 85, NCBIN = 200, NCOL = 8)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 4500, ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = 0, NRBIN= 25, NROW = 16, NCBIN = 25, NCOL = 64, JPEGQ = 90)
    
    return relativeTime


def Full_CCD_procedure(root, relativeTime, nadirTEXPMS = 0, comment = ''):
    '''Full CCD binning with exposure on nadir camera by default is disabled, see module description for more details.
    
    Arguments:
        nadirTEXPMS (int): Sets the exposure time [ms] of the nadir CCD.
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 48, PWR = 1, ExpInterval = 60000, ExpTime = 3000, comment = comment, 
                  NRSKIP = 0, NRBIN= 1, NROW = 511, NCBIN = 1, NCOL = 2047, JPEGQ = 110, SIGMODE = 0)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 9, PWR = 1, ExpInterval = 60000, ExpTime = 5000, comment = comment, 
                  NRSKIP = 0, NRBIN= 1, NROW = 511, NCBIN = 1, NCOL = 2047, JPEGQ = 110, WDW = 4)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 6, PWR = 1, ExpInterval = 60000, ExpTime = 5000, comment = comment, 
                  NRSKIP = 0, NRBIN= 1, NROW = 511, NCBIN = 1, NCOL = 2047, JPEGQ = 110)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 60000, ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = 0, NRBIN= 1, NROW = 511, NCBIN = 1, NCOL = 2047)
    
    return relativeTime


def LowPixel_procedure(root, relativeTime, ExpTimeUV, ExpIntUV, ExpTimeIR, ExpIntIR, nadirTEXPMS = 0, comment = ''):
    '''Low Pixel CCD binning with exposure on nadir camera by default is disabled, see module description for more details.
    
    Arguments: 
        nadirTEXPMS (int): Sets the exposure time [ms] of the nadir CCD.
        ExpIntUV (int): Exposure interval of UV CCDs in ms.
        ExpTimeUV (int): Exposure time of UV CCDs in ms.
        ExpIntIR (int): Exposure interval of IR CCDs in ms.
        ExpTimeIR (int): Exposure time of IR CCDs in ms.
    
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 48, PWR = 1, ExpInterval = ExpIntUV, ExpTime = ExpTimeUV, comment = comment, 
                  NRSKIP = 0, NRBIN= 63, NROW = 7, NCBIN = 255, NCOL = 7, JPEGQ = 110)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 9, PWR = 1, ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = 0, NRBIN= 63, NROW = 7, NCBIN = 255, NCOL = 7, JPEGQ = 110)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 6, PWR = 1, ExpInterval = ExpIntIR, ExpTime = ExpTimeIR, comment = comment, 
                  NRSKIP = 0, NRBIN= 63, NROW = 7, NCBIN = 255, NCOL = 7, JPEGQ = 110)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 2000, ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = 0, NRBIN= 63, NROW = 7, NCBIN = 255, NCOL = 7)
    
    return relativeTime


def High_res_UV_procedure(root, relativeTime, nadirTEXPMS = 1500, UV_TEXPMS = 3000, comment = ''):
    '''Standard CCD binning, see module description for more details.
        
    Arguments: 
        nadirTEXPMS (int): Sets the exposure time [ms] of the nadir CCD.
        UV_TEXPMS (int): Sets the exposure time [ms] of the UV CCDs.
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 48, PWR = 1, ExpInterval = 4000, ExpTime = UV_TEXPMS, comment = comment, 
                  NRSKIP = 0, NRBIN= 2, NROW = 255, NCBIN = 40, NCOL = 50, SIGMODE = 0)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 9, PWR = 1, ExpInterval = 6000, ExpTime = 5000, comment = comment, 
                  NRSKIP = 0, NRBIN= 3, NROW = 170, NCBIN = 80, NCOL = 24, WDW = 4)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 6, PWR = 1, ExpInterval = 6000, ExpTime = 5000, comment = comment, 
                  NRSKIP = 0, NRBIN= 6, NROW = 85, NCBIN = 200, NCOL = 8)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 2000, ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = 0, NRBIN= 50, NROW = 8, NCBIN = 50, NCOL = 32, JPEGQ = 90)
    
    return relativeTime


def High_res_IR_procedure(root, relativeTime, nadirTEXPMS = 1500, comment = ''):
    '''High resolution IR binning, see module description for more details.
        
    Arguments: 
        nadirTEXPMS (int): Sets the exposure time [ms] of the nadir CCD.
    
    '''
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 48, PWR = 0, ExpInterval = 6000, ExpTime = 0, comment = comment, 
                  NRSKIP = 0, NRBIN= 2, NROW = 255, NCBIN = 40, NCOL = 50, SIGMODE = 0)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 9, PWR = 1, ExpInterval = 6000, ExpTime = 5000, comment = comment, 
                  NRSKIP = 0, NRBIN= 2, NROW = 255, NCBIN = 40, NCOL = 50, WDW = 4)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 6, PWR = 1, ExpInterval = 6000, ExpTime = 5000, comment = comment, 
                  NRSKIP = 0, NRBIN= 6, NROW = 85, NCBIN = 200, NCOL = 8)
    
    
    relativeTime = Commands.TC_pafCCDMain(root, relativeTime, CCDSEL = 64, PWR = 1, ExpInterval = 4500, ExpTime = nadirTEXPMS, comment = comment, 
                  NRSKIP = 0, NRBIN= 25, NROW = 16, NCBIN = 36, NCOL = 55, JPEGQ = 90)
    
    return relativeTime
