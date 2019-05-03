# -*- coding: utf-8 -*-
"""Contains command functions as listed in "InnoSat Payload Timeline XML Definition" document.

Add commands to the XML-tree as specified in "InnoSat Payload Timeline XML Definition" document.

Arguments:
    root =  XML tree structure. Main container object for the ElementTree API. lxml.etree.Element class
    The rest are str class and defined as in "InnoSat Payload Timeline XML Definition" document for each corresponding command.

Returns: 
    incremented_time = The scheduled time of the command increased by a number equal to OPT_Config_File.Timeline.settings()['command_separation'].
        This to prevent the command buffer on the satellite from overloading. When scheduling TC_acfLimbPointingAltitudeOffset with Rate = '0', another time period is added to let the attitude stabilize.

@author: David

"""

import logging
from lxml import etree

from OPT_Config_File import Timeline_settings, Logger_name
from Operational_Planning_Tool import Globals

Logger = logging.getLogger(Logger_name())



def TC_pafMode(root, time, mode, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafMODE")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "MODE")
    root[1][len(root[1])-1][2][0].text = mode
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_acfLimbPointingAltitudeOffset(root, time, Initial = "92500", Final = "92500", Rate = "0", comment = ''):
    "Schedules Pointing Command unless the desired attitude is already set and Rate = 0."
    
    
    #global current_pointing
    
    current_pointing = Globals.current_pointing
    
    Logger.info('current_pointing: '+str(current_pointing))
    Logger.info('Initial: '+Initial+', Final: '+Final+', Rate: '+Rate)
    
    if(current_pointing != Final or current_pointing != Initial ):
        Logger.info('Scheduling pointing command')
        
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
            incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
            Globals.current_pointing= None
        elif( Final == Initial and Rate == '0'):
            Globals.current_pointing= Final
            incremented_time = str(round(float(time)+Timeline_settings()['pointing_stabilization'],2))
        
    else:
        Logger.info('Skipping pointing command as satellite is already oriented the desired way')
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
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
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
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
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
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafUpload(root, time, PacketIndex, PacketTotal, WFLASH, NIMG, IMG, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafUPLOAD")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PINDEX")
    root[1][len(root[1])-1][2][0].text = PacketIndex
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PTOTAL")
    root[1][len(root[1])-1][2][1].text = PacketTotal
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "WFLASH")
    root[1][len(root[1])-1][2][2].text = WFLASH
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NIMG")
    root[1][len(root[1])-1][2][3].text = NIMG
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "IMG")
    root[1][len(root[1])-1][2][4].text = IMG
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
def TC_pafHTR(root, time, HtrSelect, SetPoint, P, I, D, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafHTR")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "HTRSEL")
    root[1][len(root[1])-1][2][0].text = HtrSelect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SET")
    root[1][len(root[1])-1][2][1].text = SetPoint
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "P")
    root[1][len(root[1])-1][2][2].text = P
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "I")
    root[1][len(root[1])-1][2][3].text = I
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "D")
    root[1][len(root[1])-1][2][4].text = D
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafCCDMain(root, time, CCDselect, CCDMode, ExpInterval, ExpTime, NumRowsSkip, NumRowsBin,
                  NumRows, NumColumnsBin, NumColumns, WindowMode = '128', JPEGquality = "90", Expsync = "0", 
                  NCBINFPGA = "0", SIGMODE = "1", DigitalGain = "0", 
                  NumFlush = "10", NumColumnsSkip = "50", comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCD")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDselect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PWR")
    root[1][len(root[1])-1][2][1].text = CCDMode
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "WDW")
    root[1][len(root[1])-1][2][2].text = WindowMode
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "JPEGQ")
    root[1][len(root[1])-1][2][3].text = JPEGquality
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SYNC")
    root[1][len(root[1])-1][2][4].text = Expsync
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPIMS")
    root[1][len(root[1])-1][2][5].text = ExpInterval
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "TEXPMS")
    root[1][len(root[1])-1][2][6].text = ExpTime
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "GAIN")
    root[1][len(root[1])-1][2][7].text = DigitalGain
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NFLUSH")
    root[1][len(root[1])-1][2][8].text = NumFlush
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NRSKIP")
    root[1][len(root[1])-1][2][9].text = NumRowsSkip
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NRBIN")
    root[1][len(root[1])-1][2][10].text = NumRowsBin
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NROW")
    root[1][len(root[1])-1][2][11].text = NumRows
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCSKIP")
    root[1][len(root[1])-1][2][12].text = NumColumnsSkip
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCBIN")
    root[1][len(root[1])-1][2][13].text = NumColumnsBin
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCOL")
    root[1][len(root[1])-1][2][14].text = NumColumns
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NCBINFPGA")
    root[1][len(root[1])-1][2][15].text = NCBINFPGA
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SIGMODE")
    root[1][len(root[1])-1][2][16].text = SIGMODE
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafCCDBadColumn(root, time, CCDSelect, NumColumns, BadColumn, comment = ''):
    
    import logging
    from OPT_Config_File import Logger_name
    Logger = logging.getLogger(Logger_name())
    
    if( int(BadColumn) >= 2**256):
        Logger.warning('More than 256 BadColumns chosen, risk of command being too large')
        input('Enter anything to confirm the chosen size of BadColumns\n')
        
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDBadColumn")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NBC")
    root[1][len(root[1])-1][2][1].text = NumColumns
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "BC")
    root[1][len(root[1])-1][2][2].text = BadColumn
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafCCDFlushBadColumns(root, time, CCDSelect, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDFlushBadColumns")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time
    
    
def TC_pafCCDBias(root, time, CCDSelect, Gate, Substrate, ResetTransitionDrain, OutputDrain, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDBIAS")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VGATE")
    root[1][len(root[1])-1][2][1].text = Gate
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VSUBST")
    root[1][len(root[1])-1][2][2].text = Substrate
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VRD")
    root[1][len(root[1])-1][2][3].text = ResetTransitionDrain
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "VOD")
    root[1][len(root[1])-1][2][4].text = OutputDrain
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
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
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time


def TC_pafCCDTRANSPARENTCMD(root, time, CCDSelect, CHAR, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDTRANSPARENTCMD")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CHAR")
    root[1][len(root[1])-1][2][1].text = CHAR
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time
    

def TC_pafDbg(root, time, CCDSelect, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafDbg")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSEL")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time


def TC_pafCCDPM(root, time, TEXPMS, TEXPIMS, comment = ''):
    
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
    
    incremented_time = str(round(float(time)+Timeline_settings()['command_separation'],2))
    
    return incremented_time