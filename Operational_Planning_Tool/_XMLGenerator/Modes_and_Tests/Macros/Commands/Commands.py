# -*- coding: utf-8 -*-
"""Contains command functions as listed in "InnoSat Payload Timeline XML Definition" document.

Add commands to the XML-tree as specified in "InnoSat Payload Timeline XML Definition" document.

Arguments:
    root (lxml.etree.Element):  XML tree structure. Main container object for the ElementTree API. \n
    time (str): The relative starting time of the CMD with regard to the start of the timeline [s]. \n
    *CMD specific parameters* (str): A number of CMD specific parameters as defined in "InnoSat Payload Timeline XML Definition" document for each corresponding command. \n
    comment (str): A comment regarding the CMD.

Returns: 
    incremented_time (str) = The scheduled time of the command increased by a number equal to OPT_Config_File.Timeline.settings()['command_separation'], 
    This to prevent the command buffer on the satellite from overloading. When TC_acfLimbPointingAltitudeOffset is scheduled with Rate = '0', a different time period is added to let the attitude stabilize.

"""

import logging, importlib
from lxml import etree

from Operational_Planning_Tool import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
#from OPT_Config_File import Timeline_settings, Logger_name, PM_settings

Logger = logging.getLogger(OPT_Config_File.Logger_name())



def TC_pafMode(root, time, mode, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafMODE")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "MODE")
    root[1][len(root[1])-1][2][0].text = mode
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_acfLimbPointingAltitudeOffset(root, time, Initial = "92500", Final = "92500", Rate = "0", comment = ''):
    """Schedules Pointing Command unless the desired attitude is already set and Rate = 0."""
    
    
    #global current_pointing
    
    current_pointing = _Globals.current_pointing
    
    Logger.debug('current_pointing: '+str(current_pointing))
    Logger.debug('Initial: '+Initial+', Final: '+Final+', Rate: '+Rate)
    
    if(current_pointing != Final or current_pointing != Initial ):
        Logger.debug('Scheduling pointing command')
        
        etree.SubElement(root[1], 'command', mnemonic = "TC_acfLimbPointingAltitudeOffset")
        
        etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
        root[1][len(root[1])-1][0].text = time
        
        etree.SubElement(root[1][len(root[1])-1], 'comment')
        root[1][len(root[1])-1][1].text = comment
        
        etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
        etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Initial")
        root[1][len(root[1])-1][2][0].text = Initial
        
        etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Final")
        root[1][len(root[1])-1][2][1].text = Final
        
        etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Rate")
        root[1][len(root[1])-1][2][2].text = Rate
        
        if( Rate != '0' ):
            incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
            _Globals.current_pointing= None
        elif( Final == Initial and Rate == '0'):
            _Globals.current_pointing= Final
            incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['pointing_stabilization'],2))
        
    else:
        Logger.debug('Skipping pointing command as satellite is already oriented the desired way')
        incremented_time = time
        
    return incremented_time
    
def TC_affArgFreezeStart(root, time, StartTime, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_affArgFreezeStart")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "StartTime")
    root[1][len(root[1])-1][2][0].text = StartTime
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_affArgFreezeDuration(root, time, FreezeDuration, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_affArgFreezeDuration")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "FreezeDuration")
    root[1][len(root[1])-1][2][0].text = FreezeDuration
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
def TC_pafPWRToggle(root, time, CONST = '165', comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafPWRTOGGLE")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CONST")
    root[1][len(root[1])-1][2][0].text = CONST
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafUpload(root, time, PINDEX = '0', PTOTAL = '0', WFLASH = '0', NIMG = '0', IMG = '0', comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafUPLOAD")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PINDEX")
    root[1][len(root[1])-1][2][0].text = PINDEX
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PTOTAL")
    root[1][len(root[1])-1][2][1].text = PTOTAL
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "WFLASH")
    root[1][len(root[1])-1][2][2].text = WFLASH
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NIMG")
    root[1][len(root[1])-1][2][3].text = NIMG
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "IMG")
    root[1][len(root[1])-1][2][4].text = IMG
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
def TC_pafHTR(root, time, HTRSEL, SET, P, I, D, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafHTR")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "HTRSEL")
    root[1][len(root[1])-1][2][0].text = HTRSEL
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SET")
    root[1][len(root[1])-1][2][1].text = SET
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "P")
    root[1][len(root[1])-1][2][2].text = P
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "I")
    root[1][len(root[1])-1][2][3].text = I
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "D")
    root[1][len(root[1])-1][2][4].text = D
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafCCDMain(root, time, CCDselect, PWR, ExpInterval, ExpTime, NRSKIP = '0', NRBIN = '1',
                  NROW = '1', NCBIN = '1', NCOL = '1', WDW = '128', JPEGQ = "90", SYNC = "0", 
                  NCBINFPGA = "0", SIGMODE = "1", GAIN = "0", 
                  NFLUSH = "1023", NCSKIP = "0", comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCD")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDselect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PWR")
    root[1][len(root[1])-1][2][1].text = PWR
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "WDW")
    root[1][len(root[1])-1][2][2].text = WDW
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "JPEGQ")
    root[1][len(root[1])-1][2][3].text = JPEGQ
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SYNC")
    root[1][len(root[1])-1][2][4].text = SYNC
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPIMS")
    root[1][len(root[1])-1][2][5].text = ExpInterval
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPMS")
    root[1][len(root[1])-1][2][6].text = ExpTime
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "GAIN")
    root[1][len(root[1])-1][2][7].text = GAIN
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NFLUSH")
    root[1][len(root[1])-1][2][8].text = NFLUSH
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NRSKIP")
    root[1][len(root[1])-1][2][9].text = NRSKIP
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NRBIN")
    root[1][len(root[1])-1][2][10].text = NRBIN
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NROW")
    root[1][len(root[1])-1][2][11].text = NROW
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCSKIP")
    root[1][len(root[1])-1][2][12].text = NCSKIP
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCBIN")
    root[1][len(root[1])-1][2][13].text = NCBIN
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCOL")
    root[1][len(root[1])-1][2][14].text = NCOL
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCBINFPGA")
    root[1][len(root[1])-1][2][15].text = NCBINFPGA
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SIGMODE")
    root[1][len(root[1])-1][2][16].text = SIGMODE
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafCCDBadColumn(root, time, CCDSEL, NBC, BC, comment = ''):
    
    
    
    if not( 0 <= int(NBC) <= 63 or int(BC) >= 2**255):
        Logger.error('Invalid argument: More than 63 BadColumns chosen (or less than 0)')
        raise ValueError
        
        
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDBadColumn")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSEL
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NBC")
    root[1][len(root[1])-1][2][1].text = NBC
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "BC")
    root[1][len(root[1])-1][2][2].text = BC
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafCCDFlushBadColumns(root, time, CCDSEL, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDFlushBadColumns")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSEL
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafCCDBIAS(root, time, CCDSEL, VGATE, VSUBST, VRD, VOD, comment = ''):
    
    
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDBIAS")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSEL
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VGATE")
    root[1][len(root[1])-1][2][1].text = VGATE
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VSUBST")
    root[1][len(root[1])-1][2][2].text = VSUBST
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VRD")
    root[1][len(root[1])-1][2][3].text = VRD
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VOD")
    root[1][len(root[1])-1][2][4].text = VOD
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafCCDSnapshot(root, time, CCDSelect, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDSNAPSHOT")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time


def TC_pafCCDTRANSPARENTCMD(root, time, CCDSEL, CHAR, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDTRANSPARENTCMD")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSEL
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CHAR")
    root[1][len(root[1])-1][2][1].text = CHAR
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time
    

def TC_pafDbg(root, time, CCDSEL, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafDbg")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSEL
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time


def TC_pafPM(root, time, TEXPMS = str(OPT_Config_File.PM_settings()['TEXPMS']), TEXPIMS = str(OPT_Config_File.PM_settings()['TEXPIMS']), comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafPM")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPMS")
    root[1][len(root[1])-1][2][0].text = TEXPMS
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPIMS")
    root[1][len(root[1])-1][2][1].text = TEXPIMS
    
    incremented_time = str(round(float(time)+OPT_Config_File.Timeline_settings()['command_separation'],2))
    
    return incremented_time