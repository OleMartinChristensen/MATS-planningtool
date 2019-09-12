# -*- coding: utf-8 -*-
"""Calls for macros, which will generate commands in the XML-file. \n

For PWRTOGGLE, PM, CCDBadColumn, CCDFlushBadColumns: Compares parameters given in the Science Mode Timeline to default parameters 
given in the set *Configuration File* and fills in any parameters missing in the Science Mode Timeline. \n

For the rest CMDS, each parameter must be given in the Science Mode Timeline. \n

Functions on the form "XML_generator_X", where the last X is any CMD:
    Arguments:
        root (lxml.etree.Element):  XML tree structure. Main container object for the ElementTree API. lxml.etree.Element class \n
        date (ephem.Date): Starting date of the CMD. On the form of the ephem.Date class. \n
        duration (int): The duration of the CMD [s] as an integer class. \n
        relativeTime (int): The starting time [s] of the CMD with regard to the start of the timeline as an integer class \n
        params (dict): Dictionary containing the parameters of the CMD given in the Science_Mode_Timeline.
    
    Returns:
        None

@author: David
"""

import logging, importlib

from .Macros_Commands import Commands, Macros
from OPT._Library import params_checker
from OPT import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)

Logger = logging.getLogger(OPT_Config_File.Logger_name())

def XML_generator_MODE(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'MODE': 0}
    #params = params_checker(params, params_default)
    
    Commands.TC_pafMode(root, round(relativeTime,2), mode = params['MODE'], comment = str(date))
 

def XML_generator_PWRTOGGLE(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = OPT_Config_File.PWRTOGGLE_settings()
    params = params_checker(params, params_default)
    Macros.PWRTOGGLE_macro(root, round(relativeTime,2), CONST = params['CONST'], comment = str(date))
    
    
def XML_generator_UPLOAD(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'PINDEX': 0, 'PTOTAL': 0, 'WFLASH': 0, 'NIMG': 0, 'IMG': 0}
    #params = params_checker(params, params_default)
    Commands.TC_pafUpload(root, round(relativeTime,2), PINDEX = params['PINDEX'], PTOTAL = params['PTOTAL'], 
                          WFLASH = params['WFLASH'] , NIMG = params['NIMG'], IMG = params['IMG'], comment = str(date))


def XML_generator_HTR(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'HTRSEL': 1, 'SET': 2000, 'P': 10, 'I': 0, 'D': 0}
    #params = params_checker(params, params_default)
    Commands.TC_pafHTR(root, round(relativeTime,2), HTRSEL = params['HTRSEL'], SET = params['SET'], 
                          P = params['P'] , I = params['I'], D = params['D'], comment = str(date))
    

def XML_generator_CCD(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'CCDSEL': 1, 'PWR': 1, 'WDW': 4, 'JPEGQ': 95, 'SYNC': 0, 'TEXPIMS': 3000, 'TEXPMS': 1000, 'GAIN': 0, 'NFLUSH': 1023, 
    #                             'NRSKIP': 0, 'NRBIN': 1, 'NROW': 50, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 200, 'NCBINFPGA': 0, 'SIGMODE': 1}
    #params = params_checker(params, params_default)
    Commands.TC_pafCCDMain(root, round(relativeTime,2), CCDselect = params['CCDSEL'], PWR = params['PWR'], WDW = params['WDW'], 
                       JPEGQ = params['JPEGQ'], SYNC = params['SYNC'], ExpInterval = params['TEXPIMS'], 
                       ExpTime = params['TEXPMS'], GAIN = params['GAIN'], NFLUSH = params['NFLUSH'], 
                        NRSKIP = params['NRSKIP'], NRBIN = params['NRBIN'], NROW = params['NROW'], 
                        NCSKIP = params['NCSKIP'], NCBIN = params['NCBIN'], NCOL = params['NCOL'], 
                        NCBINFPGA = params['NCBINFPGA'], SIGMODE = params['SIGMODE'], comment = str(date))
    

def XML_generator_CCDBadColumn(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = OPT_Config_File.CCDBadColumn_settings()
    params = params_checker(params, params_default)
    Commands.TC_pafCCDBadColumn(root, relativeTime, CCDSEL = params['CCDSEL'], NBC = params['NBC'], 
                             BC = params['BC'], comment = str(date))


def XML_generator_CCDFlushBadColumns(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = OPT_Config_File.CCDFlushBadColumns_settings()
    params = params_checker(params, params_default)
    Commands.TC_pafCCDFlushBadColumns(root, relativeTime, CCDSEL = params['CCDSEL'], comment = str(date))


def XML_generator_CCDBIAS(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = OPT_Config_File.CCDFlushBadColumns_settings()
    params = params_checker(params, params_default)
    
    
    Commands.TC_pafCCDBIAS(root, relativeTime, CCDSEL = params['CCDSEL'], VGATE = params['VGATE'], 
                             VSUBST = params['VSUBST'], VRD = params['VRD'], VOD = params['VOD'], comment = str(date))


def XML_generator_CCDSNAPSHOT(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'CCDSEL': 1}
    #params = params_checker(params, params_default)
    Commands.TC_pafCCDSnapshot(root, round(relativeTime,2), CCDSelect = params['CCDSEL'], comment = str(date))
    

def XML_generator_CCDTRANSPARENTCMD(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'CCDSEL': 1, 'CHAR': 0}
    #params = params_checker(params, params_default)
    Commands.TC_pafCCDTRANSPARENTCMD(root, round(relativeTime,2), CCDSEL = params['CCDSEL'], CHAR = str(params['CHAR']), comment = str(date))
    

def XML_generator_Dbg(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'CCDSEL': 1}
    #params = params_checker(params, params_default)
    Commands.TC_pafDbg(root, round(relativeTime,2), CCDSEL = params['CCDSEL'], comment = str(date))
    

def XML_generator_PM(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = OPT_Config_File.PM_settings()
    params = params_checker(params, params_default)
    Commands.TC_pafPM(root, round(relativeTime,2), TEXPMS = params['TEXPMS'], TEXPIMS = params['TEXPIMS'], comment = str(date))
    

def XML_generator_LimbPointingAltitudeOffset(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'Initial': 92500, 'Final': 92500, 'Rate': 0}
    #params = params_checker(params, params_default)
    Commands.TC_acfLimbPointingAltitudeOffset(root, round(relativeTime,2), Initial = params['Initial'], Final = params['Final'], 
                                              Rate = params['Rate'], comment = str(date))
    

def XML_generator_ArgFreezeStart(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'StartTime': 0}
    #params = params_checker(params, params_default)
    Commands.TC_affArgFreezeStart(root, round(relativeTime,2), StartTime = params['StartTime'], comment = str(date))
    

def XML_generator_ArgFreezeDuration(root, date, duration, relativeTime, 
                       params = {}):
    
    #params_default = {'FreezeDuration': 0}
    #params = params_checker(params, params_default)
    Commands.TC_affArgFreezeDuration(root, round(relativeTime,2), FreezeDuration = params['FreezeDuration'], comment = str(date))
    

