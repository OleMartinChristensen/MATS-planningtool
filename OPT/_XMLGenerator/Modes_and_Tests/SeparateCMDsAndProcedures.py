# -*- coding: utf-8 -*-
"""Calls CMDs/Procedures, which will generate commands in the XML-file. These functions are used when CMDs/Procedures are scheduled separately in a Science Mode Timeline.  \n

For the definition of CMDs/Procedures see the "InnoSat Payload Timeline XML Definition" document. \n

For PM, CCDBadColumn, CCDFlushBadColumns: Compares settings given in the Science Mode Timeline to the same 
given in the set *Configuration File* and fills in any values missing in the Science Mode Timeline. \n

For the rest of the CMDS, each setting must be given in the *Science Mode Timeline* as a dictionary with each key representing an argument of the CMD. \n

TurnONCCDs will always call TC_pafCCDMain with fixed arguments to turn ON all CCDs. \n

Functions on the form "X", where X is any CMD:
    
    **Arguments:**
        **root** (*lxml.etree.Element*):  XML tree structure. Main container object for the ElementTree API. lxml.etree.Element class \n
        **date** (*ephem.Date*): Starting date of the CMD. On the form of the ephem.Date class. \n
        **duration** (*int*): The duration of the CMD [s] as an integer class. \n
        **relativeTime** (*int*): The starting time [s] of the CMD with regard to the start of the timeline as an integer class \n
        **Timeline_settings** (*dict*): Dictionary containing the settings of the Timeline given in either the *Science Mode Timeline* or the *Configuration File*. \n 
        **CMD_settings** (*dict*): Dictionary containing the settings/arguments of the CMD given in the Science Mode Timeline.
    
    Returns:
        None

@author: David Skånberg
"""

import logging, importlib, sys

from .Macros_Commands import Commands, Macros
from OPT._Library import dict_comparator
from OPT import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)

Logger = logging.getLogger(OPT_Config_File.Logger_name())


"################# Procedures ############################"


def Payload_Power_Toggle(
    root, date, duration, relativeTime, Timeline_settings, CMD_settings={}
):

    Commands.Payload_Power_Toggle(
        root,
        round(relativeTime, 2),
        Timeline_settings=Timeline_settings,
        comment="Payload_Power_Toggle, " + str(date),
    )


"################# PAYLOAD COMMANDS ############################"

"A CMD with fixed arguments used to just turn on the CCDs"


def TurnONCCDs(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    relativeTime = Commands.TC_pafCCDMain(
        root,
        relativeTime,
        CCDSEL=127,
        PWR=1,
        TEXPIMS=6000,
        TEXPMS=0,
        NRSKIP=0,
        NRBIN=1,
        NROW=1,
        NCBIN=1,
        NCOL=1,
        WDW=7,
        JPEGQ=100,
        SYNC=0,
        NCBINFPGA=0,
        SIGMODE=1,
        GAIN=0,
        NFLUSH=1023,
        NCSKIP=0,
        Timeline_settings=Timeline_settings,
        comment="TurnONCCDs, " + str(date),
    )


def MODE(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    # CMD_settings_ConfigFile = {'MODE': 0}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)

    CMD_name = sys._getframe(0).f_code.co_name
    Commands.TC_pafMode(
        root,
        round(relativeTime, 2),
        MODE=CMD_settings["MODE"],
        Timeline_settings=Timeline_settings,
        comment=CMD_name + ", " + str(date),
    )


def PWRTOGGLE(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    # CMD_settings_ConfigFile = OPT_Config_File.PWRTOGGLE_settings()
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafPWRToggle(
        root,
        round(relativeTime, 2),
        CONST=CMD_settings["CONST"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def UPLOAD(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    # CMD_settings_ConfigFile = {'PINDEX': 0, 'PTOTAL': 0, 'WFLASH': 0, 'NIMG': 0, 'IMG': 0}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafUpload(
        root,
        round(relativeTime, 2),
        PINDEX=CMD_settings["PINDEX"],
        PTOTAL=CMD_settings["PTOTAL"],
        WFLASH=CMD_settings["WFLASH"],
        NIMG=CMD_settings["NIMG"],
        IMG=CMD_settings["IMG"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def HTR(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    # CMD_settings_ConfigFile = {'HTRSEL': 1, 'SET': 2000, 'P': 10, 'I': 0, 'D': 0}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafHTR(
        root,
        round(relativeTime, 2),
        HTRSEL=CMD_settings["HTRSEL"],
        SET=CMD_settings["SET"],
        PVALUE=CMD_settings["PVALUE"],
        IVALUE=CMD_settings["IVALUE"],
        DVALUE=CMD_settings["DVALUE"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def CCD(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    # CMD_settings_ConfigFile = {'CCDSEL': 1, 'PWR': 1, 'WDW': 4, 'JPEGQ': 95, 'SYNC': 0, 'TEXPIMS': 3000, 'TEXPMS': 1000, 'GAIN': 0, 'NFLUSH': 1023,
    #                             'NRSKIP': 0, 'NRBIN': 1, 'NROW': 50, 'NCSKIP': 0, 'NCBIN': 1, 'NCOL': 200, 'NCBINFPGA': 0, 'SIGMODE': 1}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafCCDMain(
        root,
        round(relativeTime, 2),
        CCDSEL=CMD_settings["CCDSEL"],
        PWR=CMD_settings["PWR"],
        WDW=CMD_settings["WDW"],
        JPEGQ=CMD_settings["JPEGQ"],
        SYNC=CMD_settings["SYNC"],
        TEXPMS=CMD_settings["TEXPMS"],
        TEXPIMS=CMD_settings["TEXPIMS"],
        GAIN=CMD_settings["GAIN"],
        NFLUSH=CMD_settings["NFLUSH"],
        NRSKIP=CMD_settings["NRSKIP"],
        NRBIN=CMD_settings["NRBIN"],
        NROW=CMD_settings["NROW"],
        NCSKIP=CMD_settings["NCSKIP"],
        NCBIN=CMD_settings["NCBIN"],
        NCOL=CMD_settings["NCOL"],
        NCBINFPGA=CMD_settings["NCBINFPGA"],
        SIGMODE=CMD_settings["SIGMODE"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def CCDBadColumn(
    root, date, duration, relativeTime, Timeline_settings, CMD_settings={}
):

    CMD_settings_ConfigFile = OPT_Config_File.CCDBadColumn_settings()
    CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafCCDBadColumn(
        root,
        relativeTime,
        CCDSEL=CMD_settings["CCDSEL"],
        NBC=CMD_settings["NBC"],
        BC=CMD_settings["BC"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def CCDFlushBadColumns(
    root, date, duration, relativeTime, Timeline_settings, CMD_settings={}
):

    CMD_settings_ConfigFile = OPT_Config_File.CCDFlushBadColumns_settings()
    CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafCCDFlushBadColumns(
        root,
        relativeTime,
        CCDSEL=CMD_settings["CCDSEL"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def CCDBIAS(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    CMD_settings_ConfigFile = OPT_Config_File.CCDBIAS_settings()
    CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)

    Commands.TC_pafCCDBIAS(
        root,
        relativeTime,
        CCDSEL=CMD_settings["CCDSEL"],
        VGATE=CMD_settings["VGATE"],
        VSUBST=CMD_settings["VSUBST"],
        VRD=CMD_settings["VRD"],
        VOD=CMD_settings["VOD"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def CCDSNAPSHOT(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    # CMD_settings_ConfigFile = {'CCDSEL': 1}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafCCDSnapshot(
        root,
        round(relativeTime, 2),
        CCDSEL=CMD_settings["CCDSEL"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def CCDTRANSPARENTCMD(
    root, date, duration, relativeTime, Timeline_settings, CMD_settings={}
):

    # CMD_settings_ConfigFile = {'CCDSEL': 1, 'CHAR': 0}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafCCDTRANSPARENTCMD(
        root,
        round(relativeTime, 2),
        CCDSEL=CMD_settings["CCDSEL"],
        CHAR=str(CMD_settings["CHAR"]),
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def Dbg(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    # CMD_settings_ConfigFile = {'CCDSEL': 1}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafDbg(
        root,
        round(relativeTime, 2),
        CCDSEL=CMD_settings["CCDSEL"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def PM(root, date, duration, relativeTime, Timeline_settings, CMD_settings={}):

    CMD_settings_ConfigFile = OPT_Config_File.PM_settings()
    CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_pafPM(
        root,
        round(relativeTime, 2),
        TEXPMS=CMD_settings["TEXPMS"],
        TEXPIMS=CMD_settings["TEXPIMS"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def CCDSynchronize(
    root, date, duration, relativeTime, Timeline_settings, CMD_settings={}
):

    Commands.TC_pafCCDSYNCHRONIZE(
        root,
        round(relativeTime, 2),
        CCDSEL=CMD_settings["CCDSEL"],
        NCCD=CMD_settings["NCCD"],
        TEXPIOFS=CMD_settings["TEXPIOFS"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


################# PLATFORM COMMANDS ############################


def LimbPointingAltitudeOffset(
    root, date, duration, relativeTime, Timeline_settings, CMD_settings={}
):

    # CMD_settings_ConfigFile = {'Initial': 92500, 'Final': 92500, 'Rate': 0}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_acfLimbPointingAltitudeOffset(
        root,
        round(relativeTime, 2),
        Initial=CMD_settings["Initial"],
        Final=CMD_settings["Final"],
        Rate=CMD_settings["Rate"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def ArgFreezeStart(
    root, date, duration, relativeTime, Timeline_settings, CMD_settings={}
):

    # CMD_settings_ConfigFile = {'StartTime': 0}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_affArgFreezeStart(
        root,
        round(relativeTime, 2),
        StartTime=CMD_settings["StartTime"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def ArgFreezeDuration(
    root, date, duration, relativeTime, Timeline_settings, CMD_settings={}
):

    # CMD_settings_ConfigFile = {'FreezeDuration': 0}
    # CMD_settings = dict_comparator(CMD_settings, CMD_settings_ConfigFile)
    Commands.TC_affArgFreezeDuration(
        root,
        round(relativeTime, 2),
        FreezeDuration=CMD_settings["FreezeDuration"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )


def ArgEnableYawComp(
    root, date, duration, relativeTime, Timeline_settings, CMD_settings={}
):

    Commands.TC_acfArgEnableYawComp(
        root,
        round(relativeTime, 2),
        EnableYawComp=CMD_settings["EnableYawComp"],
        Timeline_settings=Timeline_settings,
        comment=str(date),
    )

