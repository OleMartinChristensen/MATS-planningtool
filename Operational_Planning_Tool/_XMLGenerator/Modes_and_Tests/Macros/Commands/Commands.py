# -*- coding: utf-8 -*-
"""Contains command functions as listed in "InnoSat Payload Timeline XML Definition" document.

Add commands to the XML-tree as specified in "InnoSat Payload Timeline XML Definition" document.

Arguments:
    root (lxml.etree.Element):  XML tree structure. Main container object for the ElementTree API. \n
    relativeTime (int): The relative starting relativeTime of the CMD with regard to the start of the timeline [s]. \n
    *CMD specific parameters*: A number of CMD specific parameters as defined in "InnoSat Payload Timeline XML Definition" document for each corresponding command. \n
    comment (str): A comment regarding the CMD.

Returns: 
    incremented_time (int) = The scheduled relativeTime of the command increased by a number equal to OPT_Config_File.Timeline.settings()['command_separation'], 
    This to prevent the command buffer on the satellite from overloading. When TC_acfLimbPointingAltitudeOffset is scheduled with Rate = '0', a different relativeTime period is added to let the attitude stabilize.

"""

import logging, importlib
from lxml import etree

from Operational_Planning_Tool import _Globals
from Operational_Planning_Tool._Library import calculate_time_per_row

OPT_Config_File = importlib.import_module(_Globals.Config_File)
#from OPT_Config_File import Timeline_settings, Logger_name, PM_settings

Logger = logging.getLogger(OPT_Config_File.Logger_name())



def TC_pafMode(root, relativeTime, mode, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 1 <= mode <= 2 and type(mode) == int ):
        Logger.error('Invalid argument: Final')
        raise ValueError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafMODE")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "MODE")
    root[1][len(root[1])-1][2][0].text = str(mode)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
    
def TC_acfLimbPointingAltitudeOffset(root, relativeTime, Initial = 92500, Final = 92500, Rate = 0, comment = ''):
    """Schedules Pointing Command unless the desired attitude is already set and Rate = 0."""
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 0 <= Initial <= 300000 and type(Initial) == int ):
        Logger.error('Invalid argument: Initial')
        raise ValueError
    if not( 0 <= Final <= 300000 and type(Final) == int ):
        Logger.error('Invalid argument: Final')
        raise ValueError
    if not( 0 <= Rate <= 1000 and ( type(Rate) == int or type(Rate) == float) ):
        Logger.error('Invalid argument: Rate')
        raise ValueError
    
    current_pointing = _Globals.current_pointing
    
    Logger.debug('current_pointing: '+str(current_pointing))
    Logger.debug('Initial: '+str(Initial)+', Final: '+str(Final)+', Rate: '+str(Rate))
    
    if(current_pointing != Final or current_pointing != Initial ):
        Logger.debug('Scheduling pointing command')
        
        etree.SubElement(root[1], 'command', mnemonic = "TC_acfLimbPointingAltitudeOffset")
        
        etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
        root[1][len(root[1])-1][0].text = str(relativeTime)
        
        etree.SubElement(root[1][len(root[1])-1], 'comment')
        root[1][len(root[1])-1][1].text = comment
        
        etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
        etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Initial")
        root[1][len(root[1])-1][2][0].text = str(Initial)
        
        etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Final")
        root[1][len(root[1])-1][2][1].text = str(Final)
        
        etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Rate")
        root[1][len(root[1])-1][2][2].text = str(Rate)
        
        if( Rate != 0 ):
            incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
            _Globals.current_pointing= None
        elif( Final == Initial and Rate == 0):
            _Globals.current_pointing= Final
            incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['pointing_stabilization']
        
    else:
        Logger.debug('Skipping pointing command as satellite is already oriented the desired way')
        incremented_time = relativeTime
        
    return incremented_time
    
def TC_affArgFreezeStart(root, relativeTime, StartTime, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    "Within the years 2019-2100"
    if not( 1198800018 < StartTime < 3786480018 ):
        Logger.error('Invalid argument: StartTime is set before the year 2018 (GPSTIME 1198800018) or after the year 2100 (GPSTIME 3786480018)')
        raise ValueError
    etree.SubElement(root[1], 'command', mnemonic = "TC_affArgFreezeStart")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "StartTime")
    root[1][len(root[1])-1][2][0].text = str(StartTime)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
    
def TC_affArgFreezeDuration(root, relativeTime, FreezeDuration, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 0 < FreezeDuration < OPT_Config_File.Timeline_settings()['duration'] ):
        Logger.error('Invalid argument: negative FreezeDuration or exceeding timeline duration')
        raise ValueError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_affArgFreezeDuration")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "FreezeDuration")
    root[1][len(root[1])-1][2][0].text = str(FreezeDuration)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
def TC_pafPWRToggle(root, relativeTime, CONST = 165, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( CONST == 165 and type(CONST) == int ):
        Logger.error('Invalid argument: CONST')
        raise ValueError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafPWRTOGGLE")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CONST")
    root[1][len(root[1])-1][2][0].text = str(CONST)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
    
def TC_pafUpload(root, relativeTime, PINDEX = 0, PTOTAL = 0, WFLASH = 0, NIMG = 0, IMG = [], comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 0 <= PINDEX and type(PINDEX) == int ):
        Logger.error('Invalid argument: PINDEX')
        raise ValueError
    if not( 0 <= PTOTAL and type(PTOTAL) == int ):
        Logger.error('Invalid argument: PTOTAL')
        raise ValueError
    if not( PINDEX <= (PTOTAL-1) ):
        Logger.error('Invalid argument: PINDEX or PTOTAL')
        raise ValueError
    if not( NIMG == len(IMG) and type(NIMG) == int ):
        Logger.error('Invalid argument: NIMG')
        raise ValueError
    if not( 0 <= WFLASH <= 1 and type(WFLASH) == int ):
        Logger.error('Invalid argument: WFLASH')
        raise ValueError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafUPLOAD")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PINDEX")
    root[1][len(root[1])-1][2][0].text = str(PINDEX)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PTOTAL")
    root[1][len(root[1])-1][2][1].text = str(PTOTAL)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "WFLASH")
    root[1][len(root[1])-1][2][2].text = str(WFLASH)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NIMG")
    root[1][len(root[1])-1][2][3].text = str(NIMG)
    
    x = 4
    for Image in IMG:
        if not( 0 <= Image <= 255 and type(Image) == int):
             Logger.error('Invalid argument: Image')
             raise ValueError
        etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "IMG")
        root[1][len(root[1])-1][2][x].text = str(Image)
        x = x + 1
    
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
def TC_pafHTR(root, relativeTime, HTRSEL, SET, P, I, D, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( (1 <= HTRSEL <= 3 or 64 <= HTRSEL <= 67 or 128 <= HTRSEL <= 131 or 192 <= HTRSEL <= 195)  and type(HTRSEL) == int ):
        Logger.error('Invalid argument: HTRSEL')
        raise ValueError
    if not( 300 <= SET <= 3000 and type(SET) == int ):
        Logger.error('Invalid argument: 300 > SET or SET > 3000')
        raise ValueError
    if not( 0 <= P <= 65536 and type(P) == int ):
        Logger.error('Invalid argument: P')
        raise ValueError
    if not( 0 <= I <= 65536 and type(I) == int ):
        Logger.error('Invalid argument: I')
        raise ValueError
    if not( 0 <= D <= 65536 and type(D) == int ):
        Logger.error('Invalid argument: D')
        raise ValueError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafHTR")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "HTRSEL")
    root[1][len(root[1])-1][2][0].text = str(HTRSEL)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SET")
    root[1][len(root[1])-1][2][1].text = str(SET)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "P")
    root[1][len(root[1])-1][2][2].text = str(P)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "I")
    root[1][len(root[1])-1][2][3].text = str(I)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "D")
    root[1][len(root[1])-1][2][4].text = str(D)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
    
def TC_pafCCDMain(root, relativeTime, CCDSEL, PWR, ExpInterval, ExpTime, NRSKIP = 0, NRBIN = 1,
                  NROW = 1, NCBIN = 1, NCOL = 1, WDW = 128, JPEGQ = 90, SYNC = 0, 
                  NCBINFPGA = 0, SIGMODE = 1, GAIN = 0, 
                  NFLUSH = 1023, NCSKIP = 0, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 1 <= CCDSEL <= 127 and type(CCDSEL) == int ):
        Logger.error('Invalid argument: CCDSEL')
        raise ValueError
    if not( 0 <= PWR <= 255 and type(PWR) == int ):
        Logger.error('Invalid argument: PWR')
        raise ValueError
    if not( 0 <= NRSKIP <= 511 and type(NRSKIP) == int ):
        Logger.error('Invalid argument: NRSKIP')
        raise ValueError
    if not( 1 <= NRBIN <= 63 and type(NRBIN) == int ):
        Logger.error('Invalid argument: NRBIN')
        raise ValueError
    if not( 1 <= NROW <= 511 and type(NROW) == int ):
        Logger.error('Invalid argument: NROW')
        raise ValueError
    if not( 0 <= NCSKIP <= 2047 and type(NCSKIP) == int ):
        Logger.error('Invalid argument: NCSKIP')
        raise ValueError
    if not( 1 <= NCBIN <= 255 and type(NCBIN) == int ):
        Logger.error('Invalid argument: NCBIN')
        raise ValueError
    if not( 1 <= NCOL <= 2048 and type(NCOL) == int ):
        Logger.error('Invalid argument: NCOL')
        raise ValueError
    if not( 0 <= NCBINFPGA <= 8 and type(NCBINFPGA) == int ):
        Logger.error('Invalid argument: NCBINFPGA')
        raise ValueError
    if not( 0 <= SIGMODE <= 255 and type(SIGMODE) == int ):
        Logger.error('Invalid argument: SIGMODE')
        raise ValueError
    if not( (0 <= WDW <= 7 or WDW == 128) and type(WDW) == int ):
        Logger.error('Invalid argument: WDW')
        raise ValueError
    if not( 0 <= JPEGQ <= 255 and type(JPEGQ) == int ):
        Logger.error('Invalid argument: JPEGQ')
        raise ValueError
    if not( 0 <= GAIN <= 7 and type(GAIN) == int ):
        Logger.error('Invalid argument: GAIN')
        raise ValueError
    if not( 0 <= NFLUSH <= 1023 and type(NFLUSH) == int ):
        Logger.error('Invalid argument: NFLUSH')
        raise ValueError
    if not( NROW * NRBIN + NRSKIP <=  511 ):
        Logger.error('Invalid argument: NROW * NRBIN + NRSKIP exceeds 511')
        raise ValueError
    if not( (NCOL+1) * NCBIN * 2**NCBINFPGA + NCSKIP <= 2048 ):
        Logger.error('Invalid argument: (NCOL+1) * NCBIN * 2^NCBINFPGA + NCSKIP exceeds 2048')
        raise ValueError
        
        
    
    ReadOutTime = calculate_time_per_row(NCOL, NCBIN, NCBINFPGA, NRSKIP, NROW, NRBIN, NFLUSH)*10**-9
    Logger.debug(ReadOutTime)
    if not( 0 <= ExpTime and ExpTime + ReadOutTime < ExpInterval ):
        Logger.error('Invalid argument: TEXPMS is negative or ExpTime + ReadOutTime > ExpInterval')
        raise ValueError
    if not( type(ExpTime) == int and type(ExpInterval) == int ):
        Logger.error('Invalid argument: TEXPMS or TEXPIMS is not an integer')
        raise TypeError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCD")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = str(CCDSEL)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PWR")
    root[1][len(root[1])-1][2][1].text = str(PWR)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "WDW")
    root[1][len(root[1])-1][2][2].text = str(WDW)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "JPEGQ")
    root[1][len(root[1])-1][2][3].text = str(JPEGQ)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SYNC")
    root[1][len(root[1])-1][2][4].text = str(SYNC)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPIMS")
    root[1][len(root[1])-1][2][5].text = str(ExpInterval)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPMS")
    root[1][len(root[1])-1][2][6].text = str(ExpTime)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "GAIN")
    root[1][len(root[1])-1][2][7].text = str(GAIN)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NFLUSH")
    root[1][len(root[1])-1][2][8].text = str(NFLUSH)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NRSKIP")
    root[1][len(root[1])-1][2][9].text = str(NRSKIP)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NRBIN")
    root[1][len(root[1])-1][2][10].text = str(NRBIN)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NROW")
    root[1][len(root[1])-1][2][11].text = str(NROW)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCSKIP")
    root[1][len(root[1])-1][2][12].text = str(NCSKIP)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCBIN")
    root[1][len(root[1])-1][2][13].text = str(NCBIN)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCOL")
    root[1][len(root[1])-1][2][14].text = str(NCOL)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCBINFPGA")
    root[1][len(root[1])-1][2][15].text = str(NCBINFPGA)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SIGMODE")
    root[1][len(root[1])-1][2][16].text = str(SIGMODE)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
    
def TC_pafCCDBadColumn(root, relativeTime, CCDSEL, NBC, BC, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 1 <= CCDSEL <= 127 and type(CCDSEL) == int ):
        Logger.error('Invalid argument: CCDSEL')
        raise ValueError
    if not( 0 <= NBC <= 63 and type(NBC) == int ):
        Logger.error('Invalid argument: More than 63 BadColumns chosen (or less than 0)')
        raise ValueError
    if not( len(BC) == NBC ):
        Logger.error('Invalid argument: Number of BadColumns (NBC) does not coincide with Bad Column (BC).')
        raise ValueError
    
        
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDBadColumn")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = str(CCDSEL)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NBC")
    root[1][len(root[1])-1][2][1].text = str(NBC)
    
    x = 2
    for BadColumn in BC:
        if not( 4 <= BadColumn <= 2047 and type(BadColumn) == int):
             Logger.error('Invalid argument: BC')
             raise ValueError
        etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "BC")
        root[1][len(root[1])-1][2][x].text = str(BadColumn)
        x = x + 1
        
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
    
def TC_pafCCDFlushBadColumns(root, relativeTime, CCDSEL, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 1 <= CCDSEL <= 127 and type(CCDSEL) == int ):
        Logger.error('Invalid argument: CCDSEL')
        raise ValueError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDFlushBadColumns")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = str(CCDSEL)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
    
def TC_pafCCDBIAS(root, relativeTime, CCDSEL, VGATE, VSUBST, VRD, VOD, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 1 <= CCDSEL <= 127 and type(CCDSEL) == int ):
        Logger.error('Invalid argument: CCDSEL')
        raise ValueError
    if not( 0 <= VGATE <= 255 and 0 <= VSUBST <= 255 and 0 <= VRD <= 255 and 0 <= VOD <= 255 and 
            type(VGATE) == int  and type(VSUBST) == int  and type(VRD) == int  and type(VOD) == int ):
        Logger.error('Invalid argument: CCDBIAS values are not set as integers, or too high or low')
        raise ValueError
        
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDBIAS")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = str(CCDSEL)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VGATE")
    root[1][len(root[1])-1][2][1].text = str(VGATE)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VSUBST")
    root[1][len(root[1])-1][2][2].text = str(VSUBST)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VRD")
    root[1][len(root[1])-1][2][3].text = str(VRD)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VOD")
    root[1][len(root[1])-1][2][4].text = str(VOD)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    
    
def TC_pafCCDSnapshot(root, relativeTime, CCDSEL, comment = ''):
    
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 1 <= CCDSEL <= 127 and type(CCDSEL) == int ):
        Logger.error('Invalid argument: CCDSEL')
        raise ValueError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDSNAPSHOT")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = str(CCDSEL)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time


def TC_pafCCDTRANSPARENTCMD(root, relativeTime, CCDSEL, CHAR, comment = ''):
    
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 1 <= CCDSEL <= 127 and type(CCDSEL) == int ):
        Logger.error('Invalid argument: CCDSEL')
        raise ValueError
    if not( type(CHAR) == str ):
        Logger.error('Invalid argument: CHAR')
        raise TypeError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDTRANSPARENTCMD")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = str(CCDSEL)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CHAR")
    root[1][len(root[1])-1][2][1].text = CHAR
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time
    

def TC_pafDbg(root, relativeTime, CCDSEL, comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 1 <= CCDSEL <= 127 and type(CCDSEL) == int ):
        Logger.error('Invalid argument: CCDSEL')
        raise ValueError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafDbg")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = str(CCDSEL)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time


def TC_pafPM(root, relativeTime, TEXPMS = OPT_Config_File.PM_settings()['TEXPMS'], TEXPIMS = OPT_Config_File.PM_settings()['TEXPIMS'], comment = ''):
    
    if not( 0 <= relativeTime <= OPT_Config_File.Timeline_settings()['duration']) and type(relativeTime) == int:
        Logger.error('Invalid argument: negative relativeTime, exceeding timeline duration, or not integer')
        raise ValueError
    if not( 0 <= TEXPMS and TEXPIMS >= TEXPMS + 500 ):
        Logger.error('Invalid argument: TEXPMS is negative or TEXPMS is less than 500ms larger then TEXPIMS')
        raise ValueError
    if not( type(TEXPMS) == int and type(TEXPIMS) == int ):
        Logger.error('Invalid argument: TEXPMS or TEXPIMS is not an integer')
        raise TypeError
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafPM")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = str(relativeTime)
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPMS")
    root[1][len(root[1])-1][2][0].text = str(TEXPMS)
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPIMS")
    root[1][len(root[1])-1][2][1].text = str(TEXPIMS)
    
    incremented_time = relativeTime+OPT_Config_File.Timeline_settings()['command_separation']
    
    return incremented_time