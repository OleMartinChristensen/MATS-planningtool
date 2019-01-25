# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 15:18:38 2018

Creates commands expressed in XML as specified in InnoSat Payload Timeline XML Definition

@author: David
"""
from lxml import etree

def TC_pafMode(root, time, mode, comment = ''):

    etree.SubElement(root[1], 'command', mnemonic = "TC_pafMode")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "mode")
    root[1][len(root[1])-1][2][0].text = mode
    
    
def TC_acfLimbPointingAltitudeOffset(root, time, Initial = "92500", Final = "92500", Rate = "0", comment = ''):

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
    
def TC_affArgFreezeStart(root, time, StartTime, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_affArgFreezeStart")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "StartTime")
    root[1][len(root[1])-1][2][0].text = StartTime
    
    
def TC_affArgFreezeDuration(root, time, FreezeDuration, comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_affArgFreezeDuration")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "FreezeDuration")
    root[1][len(root[1])-1][2][0].text = FreezeDuration
    
    
def TC_pafPWRToggle(root, time, comment = ''):

    etree.SubElement(root[1], 'command', mnemonic = "TC_pafPWRToggle")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    
def TC_pafUpload(root, time, PacketIndex, PacketTotal, Data, comment = ''):

    etree.SubElement(root[1], 'command', mnemonic = "TC_pafUpload")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PacketIndex")
    root[1][len(root[1])-1][2][0].text = PacketIndex
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "PacketTotal")
    root[1][len(root[1])-1][2][0].text = PacketTotal
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Data")
    root[1][len(root[1])-1][2][0].text = Data
    
    
def TC_pafHTR(root, time, HtrSelect, SetPoint, P, I, D, comment = ''):

    etree.SubElement(root[1], 'command', mnemonic = "TC_pafHTR")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "HtrSelect")
    root[1][len(root[1])-1][2][0].text = HtrSelect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "SetPoint")
    root[1][len(root[1])-1][2][0].text = SetPoint
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "P")
    root[1][len(root[1])-1][2][0].text = P
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "I")
    root[1][len(root[1])-1][2][0].text = I
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "D")
    root[1][len(root[1])-1][2][0].text = D
    
    
def TC_pafCCDMain(root, time, CCDselect, CCDMode, ExpInterval, ExpTime, NumRowsSkip, NumRowsBin,
                  NumRows, NumColumnsBin, NumColumns, WindowMode = "1", JPEGquality = "90", Expsync = "1", 
                  RowBinningMode = "2", ColumnBinningMode = "2", DigitalGain = "0", 
                  NumFlush = "10", NumColumnsSkip = "50", comment = ''):
    
    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDMain")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDselect")
    root[1][len(root[1])-1][2][0].text = CCDselect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDMode")
    root[1][len(root[1])-1][2][1].text = CCDMode
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "WindowMode")
    root[1][len(root[1])-1][2][2].text = WindowMode
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "JPEGquality")
    root[1][len(root[1])-1][2][3].text = JPEGquality
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Expsync")
    root[1][len(root[1])-1][2][4].text = Expsync
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "ExpInterval")
    root[1][len(root[1])-1][2][5].text = ExpInterval
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "ExpTime")
    root[1][len(root[1])-1][2][6].text = ExpTime
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "RowBinningMode")
    root[1][len(root[1])-1][2][7].text = RowBinningMode
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "ColumnBinningMode")
    root[1][len(root[1])-1][2][8].text = ColumnBinningMode
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "DigitalGain")
    root[1][len(root[1])-1][2][9].text = DigitalGain
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NumFlush")
    root[1][len(root[1])-1][2][10].text = NumFlush
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NumRowsSkip")
    root[1][len(root[1])-1][2][11].text = NumRowsSkip
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NumRowsBin")
    root[1][len(root[1])-1][2][12].text = NumRowsBin
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NumRows")
    root[1][len(root[1])-1][2][13].text = NumRows
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NumColumnsSkip")
    root[1][len(root[1])-1][2][14].text = NumColumnsSkip
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NumColumnsBin")
    root[1][len(root[1])-1][2][15].text = NumColumnsBin
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CumColumns")
    root[1][len(root[1])-1][2][16].text = NumColumns
    
    
def TC_pafCCDBadColumn(root, time, CCDSelect, NumColumns, BadColumn, comment = ''):

    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDBadColumn")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSelect")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "NumColumns")
    root[1][len(root[1])-1][2][0].text = NumColumns
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "BadColumn")
    root[1][len(root[1])-1][2][0].text = BadColumn
    
    
def TC_pafCCDFlushBadColumns(root, time, CCDSelect, comment = ''):

    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDFlushBadColumns")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSelect")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    
def TC_pafCCDBias(root, time, CCDSelect, Gate, Substrate, ResetTransitionDrain, OutputDrain, comment = ''):

    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDBias")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSelect")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Gate")
    root[1][len(root[1])-1][2][0].text = Gate
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "Substrate")
    root[1][len(root[1])-1][2][0].text = Substrate
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "ResetTransitionDrain")
    root[1][len(root[1])-1][2][0].text = ResetTransitionDrain
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "OutputDrain")
    root[1][len(root[1])-1][2][0].text = OutputDrain
    
    
def TC_pafCCDSnapshot(root, time, CCDSelect, comment = ''):

    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDFlushBadColumns")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "CCDSelect")
    root[1][len(root[1])-1][2][0].text = CCDSelect
    
    
def TC_pafCCDPM(root, time, ExposureTime, ExposureInterval, comment = ''):

    etree.SubElement(root[1], 'command', mnemonic = "TC_pafCCDFlushBadColumns")
    
    etree.SubElement(root[1][len(root[1])-1], 'relativeTime')
    root[1][len(root[1])-1][0].text = time
    
    etree.SubElement(root[1][len(root[1])-1], 'comment')
    root[1][len(root[1])-1][1].text = comment
    
    etree.SubElement(root[1][len(root[1])-1], 'tcArguments')
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "ExposureTime")
    root[1][len(root[1])-1][2][0].text = ExposureTime
    
    etree.SubElement(root[1][len(root[1])-1][2], 'tcArgument', mnemonic = "ExposureInterval")
    root[1][len(root[1])-1][2][0].text = ExposureInterval