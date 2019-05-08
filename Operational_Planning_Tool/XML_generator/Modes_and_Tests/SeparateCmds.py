# -*- coding: utf-8 -*-
"""
Created on Tue May  7 16:19:57 2019

@author: David
"""

from .Macros.Commands import Commands
from Operational_Planning_Tool.Library import params_checker
import OPT_Config_File

def XML_generator_MODE(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'MODE': 0}
    params = params_checker(params, params_default)
    
    Commands.TC_pafMode(root, str(relativeTime), mode = str(params['MODE']), comment = str(date))
 

def XML_generator_PWRTOGGLE(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = OPT_Config_File.PWRTOGGLE_settings()
    params = params_checker(params, params_default)
    Commands.TC_pafPWRToggle(root, str(relativeTime), CONST = str(params['CONST']), comment = str(date))
    
    
def XML_generator_UPLOAD(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'PINDEX': 0, 'PTOTAL': 0, 'WFLASH': 0, 'NIMG': 0, 'IMG': 0}
    params = params_checker(params, params_default)
    Commands.TC_pafUpload(root, str(relativeTime), PINDEX = str(params['PINDEX']), PTOTAL = str(params['PTOTAL']), 
                          WFLASH = str(params['WFLASH']) , NIMG = str(params['NIMG']), IMG = str(params['IMG']), comment = str(date))


def XML_generator_HTR(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'HTRSEL': 1, 'SET': 2000, 'P': 10, 'I': 0, 'D': 0}
    params = params_checker(params, params_default)
    Commands.TC_pafHTR(root, str(relativeTime), HTRSEL = str(params['HTRSEL']), SET = str(params['SET']), 
                          P = str(params['P']) , I = str(params['I']), D = str(params['D']), comment = str(date))
    

def XML_generator_CCD(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'CCDSEL': 1, 'PWR': 1, 'WDW': 4, 'JPEGQ': 95, 'SYNC': 0, 'TEXPIMS': 3000, 'TEXPMS': 1000, 'GAIN': 0, 'NFLUSH': 1023, 
                                 'NRSKIP': 0, 'NRBIN': 0, 'NROW': 50, 'NCSKIP': 0, 'NCBIN': 0, 'NCOL': 200, 'NCBINFPGA': 0, 'SIGMODE': 1}
    params = params_checker(params, params_default)
    Commands.TC_pafCCDMain(root, str(relativeTime), CCDselect = str(params['CCDSEL']), PWR = str(params['PWR']), WDW = str(params['WDW']), 
                       JPEGQ = str(params['JPEGQ']), SYNC = str(params['SYNC']), ExpInterval = str(params['TEXPIMS']), 
                       ExpTime = str(params['TEXPMS']), GAIN = str(params['GAIN']), NFLUSH = str(params['NFLUSH']), 
                        NRSKIP = str(params['NRSKIP']), NRBIN = str(params['NRBIN']), NROW = str(params['NROW']), 
                        NCSKIP = str(params['NCSKIP']), NCBIN = str(params['NCBIN']), NCOL = str(params['NCOL']), 
                        NCBINFPGA = str(params['NCBINFPGA']), SIGMODE = str(params['SIGMODE']), comment = str(date))
    

def XML_generator_CCDBadColumn(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = OPT_Config_File.CCDBadColumn_settings()
    params = params_checker(params, params_default)
    Commands.TC_pafCCDBadColumn(root, str(relativeTime), CCDSEL = str(params['CCDSEL']), NBC = str(params['NBC']), 
                             BC = str(params['BC']), comment = str(date))


def XML_generator_CCDFlushBadColumns(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = OPT_Config_File.CCDFlushBadColumns_settings()
    params = params_checker(params, params_default)
    Commands.TC_pafCCDFlushBadColumns(root, str(relativeTime), CCDSEL = str(params['CCDSEL']), comment = str(date))


def XML_generator_CCDBIAS(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'CCDSEL': 1, 'VGATE': 0, 'VSUBST': 0, 'VRD': 0, 'VOD': 0}
    params = params_checker(params, params_default)
    Commands.TC_pafCCDBIAS(root, str(relativeTime), CCDSEL = str(params['CCDSEL']), VGATE = str(params['VGATE']), 
                             VSUBST = str(params['VSUBST']), VRD = str(params['VRD']), VOD = str(params['VOD']), comment = str(date))


def XML_generator_CCDSNAPSHOT(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'CCDSEL': 1}
    params = params_checker(params, params_default)
    Commands.TC_pafCCDSnapshot(root, str(relativeTime), CCDSelect = str(params['CCDSEL']), comment = str(date))
    

def XML_generator_CCDTRANSPARENTCMD(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'CCDSEL': 1, 'CHAR': 0}
    params = params_checker(params, params_default)
    Commands.TC_pafCCDTRANSPARENTCMD(root, str(relativeTime), CCDSEL = str(params['CCDSEL']), CHAR = str(params['CHAR']), comment = str(date))
    

def XML_generator_Dbg(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'CCDSEL': 1}
    params = params_checker(params, params_default)
    Commands.TC_pafDbg(root, str(relativeTime), CCDSEL = str(params['CCDSEL']), comment = str(date))
    

def XML_generator_PM(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = OPT_Config_File.PM_settings()
    params = params_checker(params, params_default)
    Commands.TC_pafPM(root, str(relativeTime), TEXPMS = str(params['TEXPMS']), TEXPIMS = str(params['TEXPIMS']), comment = str(date))
    

def XML_generator_LimbPointingAltitudeOffset(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'Initial': 92500, 'Final': 92500, 'Rate': 0}
    params = params_checker(params, params_default)
    Commands.TC_acfLimbPointingAltitudeOffset(root, str(relativeTime), Initial = str(params['Initial']), Final = str(params['Final']), 
                                              Rate = str(params['Rate']), comment = str(date))
    

def XML_generator_ArgFreezeStart(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'StartTime': 0}
    params = params_checker(params, params_default)
    Commands.TC_affArgFreezeStart(root, str(relativeTime), StartTime = str(params['StartTime']), comment = str(date))
    

def XML_generator_ArgFreezeDuration(root, date, duration, relativeTime, 
                       params = {}):
    
    params_default = {'FreezeDuration': 0}
    params = params_checker(params, params_default)
    Commands.TC_affArgFreezeDuration(root, str(relativeTime), FreezeDuration = str(params['FreezeDuration']), comment = str(date))
    
