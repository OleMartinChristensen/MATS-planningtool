# -*- coding: utf-8 -*-
"""Contain command functions. Each command function represent a CMD/Procedure listed in the "InnoSat Payload Timeline XML Definition" document.

Add commands to the XML-tree as specified in "InnoSat Payload Timeline XML Definition" document.
Also checks if parameters given are valid for the CMDs.

Each Command function has these inputs/outputs in common.

    **Arguments:**
        **root** (*lxml.etree.Element*):  XML tree structure. Main container object for the ElementTree API. \n
        **relativeTime** (*float*): The *relativeTime* of the CMD with regard to the start of the timeline [s]. \n
        **CMD specific parameters**: A number of CMD specific parameters as defined in "InnoSat Payload Timeline XML Definition" document for each corresponding command. \n
        **Timeline_settings** (*dict*): Dictionary containing the settings of the Timeline given in either the *Science_Mode_Timeline* or the *Configuration File*. \n
        **comment** (*str*): A comment regarding the CMD.

    **Returns:** 
        **incremented_time** (*int*) = The scheduled relativeTime of the command increased by a number equal to *Timeline.settings()['CMD_separation']*. 
        This to prevent the command buffer on the satellite from overloading. Note: Exception to this is when *TC_acfLimbPointingAltitudeOffset* is scheduled.
"""

import logging, importlib
from lxml import etree
from pylab import sign, ceil

from OPT import _Globals
from OPT._Library import calculate_time_per_row

OPT_Config_File = importlib.import_module(_Globals.Config_File)
# from OPT_Config_File import Timeline_settings, Logger_name, PM_settings

Logger = logging.getLogger(OPT_Config_File.Logger_name())


def TC_pafMode(root, relativeTime, MODE, Timeline_settings, comment=""):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        Logger.error(_Globals.latestRelativeTime)
        Logger.error(relativeTime)
        raise ValueError
    if not (1 <= MODE <= 2 and type(MODE) == int):
        Logger.error("Invalid argument: MODE")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_pafMODE")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="MODE")
    root[1][len(root[1]) - 1][2][0].text = str(MODE)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_acfLimbPointingAltitudeOffset(
    root, relativeTime, Initial, Final, Rate, Timeline_settings, comment=""
):
    """Schedules Pointing Command
    
    If the desired pointing altitude is already set, the maximum TEXPMS last set with a CCD_macro is added to *relativeTime*.
    Otherwise if Rate == 0, a delay equal to *Timeline_settings['pointing_stabilization']* is added to *relativeTime*.
    If Rate != 0, only *Timeline_settings['CMD_separation']* is added to *relativeTime* to allow the payload to enter operation mode during the sweep.
    
    """

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (-60000 <= Initial <= 230000 and type(Initial) == int):
        Logger.error("Invalid argument: Initial")
        raise ValueError
    if not (-60000 <= Final <= 230000 and type(Final) == int):
        Logger.error("Invalid argument: Final")
        raise ValueError
    if not (-5000 <= Rate <= 5000 and (type(Rate) == int or type(Rate) == float)):
        Logger.error("Invalid argument: Rate")
        raise ValueError
    if Rate != 0 and sign(Final - Initial) != sign(Rate):
        Logger.error("Invalid argument: sign(Final - Initial) != sign(Rate)")
        raise ValueError

    current_pointing = _Globals.current_pointing

    Logger.debug("current_pointing: " + str(current_pointing))
    Logger.debug(
        "Initial: " + str(Initial) + ", Final: " + str(Final) + ", Rate: " + str(Rate)
    )

    # if(current_pointing != Final or current_pointing != Initial ):
    #    Logger.debug('Scheduling pointing command')

    etree.SubElement(root[1], "command", mnemonic="TC_acfLimbPointingAltitudeOffset")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="Initial")
    root[1][len(root[1]) - 1][2][0].text = str(Initial)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="Final")
    root[1][len(root[1]) - 1][2][1].text = str(Final)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="Rate")
    root[1][len(root[1]) - 1][2][2].text = str(Rate)

    if Rate != 0:
        incremented_time = relativeTime + Timeline_settings["CMD_separation"]
        _Globals.current_pointing = None
        Logger.debug(
            'Rate != 0, meaning a sweep is scheduled. Next CMD is only staggered by Timeline_settings["CMD_separation"]'
        )
    elif current_pointing == Final and current_pointing == Initial:
        _Globals.current_pointing = Final
        incremented_time = (
            relativeTime
            + int(ceil(_Globals.LargestSetTEXPMS / 1000))
            + Timeline_settings["CMD_separation"]
        )
        Logger.debug(
            'Satellite is already orientated the right way. Next CMD is staggered by Timeline_settings["CMD_separation"]+_Globals.LargestSetTEXPMS/1000, rounded up.'
        )
        Logger.debug("_Globals.LargestSetTEXPMS: " + str(_Globals.LargestSetTEXPMS))
    elif Rate == 0:
        _Globals.current_pointing = Final
        incremented_time = relativeTime + Timeline_settings["pointing_stabilization"]
        Logger.debug(
            'Satellite is not orientated the right way. Next CMD is staggered by Timeline_settings["pointing_stabilization"]'
        )

    # else:
    #    Logger.debug('Skipping pointing command as satellite is already oriented the desired way')
    #    incremented_time = relativeTime

    # incremented_time = relativeTime+Timeline_settings['CMD_separation']
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_affArgFreezeStart(root, relativeTime, StartTime, Timeline_settings, comment=""):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    "Within the years 2019-2100"
    if not (1198843200 < StartTime <= 1893067200):
        Logger.error("Invalid argument: StartTime")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_affArgFreezeStart")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="StartTime")
    root[1][len(root[1]) - 1][2][0].text = str(StartTime)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_affArgFreezeDuration(
    root, relativeTime, FreezeDuration, Timeline_settings, comment=""
):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (0 < FreezeDuration <= 3600):
        Logger.error("Invalid argument: negative FreezeDuration or too long.")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_affArgFreezeDuration")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(
        root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="FreezeDuration"
    )
    root[1][len(root[1]) - 1][2][0].text = str(FreezeDuration)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_acfArgEnableYawComp(
    root, relativeTime, EnableYawComp, Timeline_settings, comment=""
):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (EnableYawComp == 1 or EnableYawComp == 0):
        Logger.error("Invalid argument: EnableYawComp")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_acfArgEnableYawComp")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(
        root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="EnableYawComp"
    )
    root[1][len(root[1]) - 1][2][0].text = str(EnableYawComp)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafPWRToggle(root, relativeTime, CONST, Timeline_settings, comment=""):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (CONST == 165 and type(CONST) == int):
        Logger.error("Invalid argument: CONST")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_pafPWRTOGGLE")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CONST")
    root[1][len(root[1]) - 1][2][0].text = str(CONST)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafUpload(
    root, relativeTime, PINDEX, PTOTAL, WFLASH, NIMG, IMG, Timeline_settings, comment=""
):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (0 <= PINDEX and type(PINDEX) == int):
        Logger.error("Invalid argument: PINDEX")
        raise ValueError
    if not (0 <= PTOTAL and type(PTOTAL) == int):
        Logger.error("Invalid argument: PTOTAL")
        raise ValueError
    if not (PINDEX <= (PTOTAL - 1)):
        Logger.error("Invalid argument: PINDEX or PTOTAL")
        raise ValueError
    if not (NIMG == len(IMG) and type(NIMG) == int):
        Logger.error("Invalid argument: NIMG")
        raise ValueError
    if not (0 <= WFLASH <= 1 and type(WFLASH) == int):
        Logger.error("Invalid argument: WFLASH")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_pafUPLOAD")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="PINDEX")
    root[1][len(root[1]) - 1][2][0].text = str(PINDEX)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="PTOTAL")
    root[1][len(root[1]) - 1][2][1].text = str(PTOTAL)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="WFLASH")
    root[1][len(root[1]) - 1][2][2].text = str(WFLASH)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NIMG")
    root[1][len(root[1]) - 1][2][3].text = str(NIMG)

    x = 4
    for Image in IMG:
        if not (0 <= Image <= 255 and type(Image) == int):
            Logger.error("Invalid argument: Image")
            raise ValueError
        etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="IMG")
        root[1][len(root[1]) - 1][2][x].text = str(Image)
        x = x + 1

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafHTR(
    root,
    relativeTime,
    HTRSEL,
    SET,
    PVALUE,
    IVALUE,
    DVALUE,
    Timeline_settings,
    comment="",
):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (
        (
            1 <= HTRSEL <= 3
            or 64 <= HTRSEL <= 67
            or 128 <= HTRSEL <= 131
            or 192 <= HTRSEL <= 195
        )
        and type(HTRSEL) == int
    ):
        Logger.error("Invalid argument: HTRSEL")
        raise ValueError
    if not (86 <= SET <= 2285 and type(SET) == int):
        Logger.error("Invalid argument: 86 > SET or SET > 2285")
        raise ValueError
    if not (0 <= PVALUE <= 65536 and type(PVALUE) == int):
        Logger.error("Invalid argument: PVALUE")
        raise ValueError
    if not (0 <= IVALUE <= 65536 and type(IVALUE) == int):
        Logger.error("Invalid argument: IVALUE")
        raise ValueError
    if not (0 <= DVALUE <= 65536 and type(DVALUE) == int):
        Logger.error("Invalid argument: DVALUE")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_pafHTR")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="HTRSEL")
    root[1][len(root[1]) - 1][2][0].text = str(HTRSEL)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="SET")
    root[1][len(root[1]) - 1][2][1].text = str(SET)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="PVALUE")
    root[1][len(root[1]) - 1][2][2].text = str(PVALUE)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="IVALUE")
    root[1][len(root[1]) - 1][2][3].text = str(IVALUE)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="DVALUE")
    root[1][len(root[1]) - 1][2][4].text = str(DVALUE)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafCCDMain(
    root,
    relativeTime,
    CCDSEL,
    PWR,
    TEXPMS,
    TEXPIMS,
    NRSKIP,
    NRBIN,
    NROW,
    NCBIN,
    NCOL,
    WDW,
    JPEGQ,
    SYNC,
    NCBINFPGA,
    SIGMODE,
    GAIN,
    NFLUSH,
    NCSKIP,
    Timeline_settings,
    comment="",
):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (1 <= CCDSEL <= 127 and type(CCDSEL) == int):
        Logger.error("Invalid argument: CCDSEL")
        raise ValueError
    if not (0 <= PWR <= 255 and type(PWR) == int):
        Logger.error("Invalid argument: PWR")
        raise ValueError
    if not (0 <= NRSKIP <= 510 and type(NRSKIP) == int):
        Logger.error("Invalid argument: NRSKIP")
        raise ValueError
    if not (1 <= NRBIN <= 63 and type(NRBIN) == int):
        Logger.error("Invalid argument: NRBIN")
        raise ValueError
    if not (1 <= NROW <= 511 and type(NROW) == int):
        Logger.error("Invalid argument: NROW")
        raise ValueError
    if not (0 <= NCSKIP <= 2046 and type(NCSKIP) == int):
        Logger.error("Invalid argument: NCSKIP")
        raise ValueError
    if not (1 <= NCBIN <= 255 and type(NCBIN) == int):
        Logger.error("Invalid argument: NCBIN")
        raise ValueError
    if not (1 <= NCOL <= 2047 and type(NCOL) == int):
        Logger.error("Invalid argument: NCOL")
        raise ValueError
    if not (0 <= NCBINFPGA <= 7 and type(NCBINFPGA) == int):
        Logger.error(
            "Invalid argument: NCBINFPGA, if NCBINFPGA=8 then the CRB may stop working"
        )
        raise ValueError
    if not (1 <= SIGMODE <= 255 and type(SIGMODE) == int):
        Logger.error(
            "Invalid argument: SIGMODE, if SIGMODE=0 then the CCDs may be unstable and stop working."
        )
        raise ValueError
    if not ((0 <= WDW <= 7 or WDW == 128) and type(WDW) == int):
        Logger.error("Invalid argument: WDW")
        raise ValueError
    # if( WDW == 7 and JPEGQ <= 100):
    #    Logger.error('Invalid argument: WDW == 7, but JPEGQ <= 100')
    #    raise ValueError
    # if( 0 <= WDW <= 4 and JPEGQ >= 101):
    #    Logger.error('Invalid argument: 0 <= WDW <= 4, but JPEGQ >= 101')
    #    raise ValueError
    if not (0 <= JPEGQ <= 100 and type(JPEGQ) == int):
        Logger.error("Invalid argument: JPEGQ")
        raise ValueError
    if not (0 <= GAIN <= 7 and type(GAIN) == int):
        Logger.error("Invalid argument: GAIN")
        raise ValueError
    if not (0 <= NFLUSH <= 1023 and type(NFLUSH) == int):
        Logger.error("Invalid argument: NFLUSH")
        raise ValueError
    if not (NROW * NRBIN + NRSKIP <= 511):
        Logger.error("Invalid argument: NROW * NRBIN + NRSKIP exceeds 511")
        raise ValueError
    if not ((NCOL + 1) * NCBIN * 2 ** NCBINFPGA + NCSKIP <= 2048):
        Logger.error(
            "Invalid argument: (NCOL+1) * NCBIN * 2^NCBINFPGA + NCSKIP exceeds 2048"
        )
        raise ValueError

    T_readout, T_delay, T_Extra = calculate_time_per_row(
        NCOL=NCOL,
        NCBIN=NCBIN,
        NCBINFPGA=NCBINFPGA,
        NRSKIP=NRSKIP,
        NROW=NROW,
        NRBIN=NRBIN,
        NFLUSH=NFLUSH,
    )
    ReadOutTime = T_readout + T_delay + T_Extra
    # Logger.debug('ReadOutTime = '+str(ReadOutTime))
    if not (0 <= TEXPMS <= 32000 and TEXPMS + ReadOutTime < TEXPIMS):
        Logger.error(
            "Invalid argument: 32000 < TEXPMS < 0 or TEXPMS + ReadOutTime > TEXPIMS"
        )
        raise ValueError
    if not (type(TEXPMS) == int and type(TEXPIMS) == int):
        Logger.error("Invalid argument: TEXPMS or TEXPIMS is not an integer")
        raise TypeError

    etree.SubElement(root[1], "command", mnemonic="TC_pafCCD")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CCDSEL")
    root[1][len(root[1]) - 1][2][0].text = str(CCDSEL)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="PWR")
    root[1][len(root[1]) - 1][2][1].text = str(PWR)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="WDW")
    root[1][len(root[1]) - 1][2][2].text = str(WDW)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="JPEGQ")
    root[1][len(root[1]) - 1][2][3].text = str(JPEGQ)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="SYNC")
    root[1][len(root[1]) - 1][2][4].text = str(SYNC)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="TEXPIMS")
    root[1][len(root[1]) - 1][2][5].text = str(TEXPIMS)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="TEXPMS")
    root[1][len(root[1]) - 1][2][6].text = str(TEXPMS)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="GAIN")
    root[1][len(root[1]) - 1][2][7].text = str(GAIN)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NFLUSH")
    root[1][len(root[1]) - 1][2][8].text = str(NFLUSH)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NRSKIP")
    root[1][len(root[1]) - 1][2][9].text = str(NRSKIP)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NRBIN")
    root[1][len(root[1]) - 1][2][10].text = str(NRBIN)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NROW")
    root[1][len(root[1]) - 1][2][11].text = str(NROW)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NCSKIP")
    root[1][len(root[1]) - 1][2][12].text = str(NCSKIP)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NCBIN")
    root[1][len(root[1]) - 1][2][13].text = str(NCBIN)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NCOL")
    root[1][len(root[1]) - 1][2][14].text = str(NCOL)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NCBINFPGA")
    root[1][len(root[1]) - 1][2][15].text = str(NCBINFPGA)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="SIGMODE")
    root[1][len(root[1]) - 1][2][16].text = str(SIGMODE)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafCCDSYNCHRONIZE(
    root, relativeTime, CCDSEL, NCCD, TEXPIOFS, Timeline_settings, comment=""
):
    "Note: CCDSYNCHRONIZE takes one TEXPIMS cycle to execute."

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (
        3 <= CCDSEL <= 127 and CCDSEL not in [4, 8, 16, 32, 64] and type(CCDSEL) == int
    ):
        Logger.error("Invalid argument: CCDSEL")
        raise ValueError
    if not (2 <= NCCD <= 7 and NCCD == bin(CCDSEL).count("1") and type(NCCD) == int):
        Logger.error(
            "Invalid argument: More than 7 CCDs chosen (or less than 2) or NCCD does not coincide with CCDSEL"
        )
        raise ValueError
    if not (len(TEXPIOFS) == NCCD):
        Logger.error(
            "Invalid argument: Number of CCDs (NCCD) does not coincide with the number of time-offsets (TEXPIOFS)."
        )
        raise ValueError
    for TEXPIOFS_value in TEXPIOFS:
        if not (0 <= TEXPIOFS_value <= 12000):
            Logger.error("Invalid argument: 0 > TEXPIOFS_value, TEXPIOFS_value > 12000")
            raise ValueError

    Logger.debug("CCDSEL: " + str(CCDSEL))
    Logger.debug("NCCD: " + str(NCCD))
    Logger.debug("TEXPIOFS: " + str(TEXPIOFS))

    etree.SubElement(root[1], "command", mnemonic="TC_pafCCDSYNCHRONIZE")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CCDSEL")
    root[1][len(root[1]) - 1][2][0].text = str(CCDSEL)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NCCD")
    root[1][len(root[1]) - 1][2][1].text = str(NCCD)

    Leading_CCD_selected = False
    x = 2
    for TimeOffset in TEXPIOFS:

        if not (
            0 <= TimeOffset <= 12000
            and TimeOffset / 10 == round(TimeOffset / 10, 0)
            and type(TimeOffset) == int
        ):
            Logger.error("Invalid argument: TEXPIOFS")
            raise ValueError
        if TimeOffset == 0:
            Leading_CCD_selected = True

        etree.SubElement(
            root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="TEXPIOFS"
        )
        root[1][len(root[1]) - 1][2][x].text = str(TimeOffset)
        x = x + 1

    if not (Leading_CCD_selected == True):
        Logger.error(
            "Invalid argument: Any TEXPIOFS not set to 0 -> No leading CCD selected"
        )
        raise ValueError

    incremented_time = (
        relativeTime
        + Timeline_settings["CMD_separation"]
        + Timeline_settings["CCDSYNC_Waittime"]
    )
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafCCDBadColumn(
    root, relativeTime, CCDSEL, NBC, BC, Timeline_settings, comment=""
):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (1 <= CCDSEL <= 127 and type(CCDSEL) == int):
        Logger.error("Invalid argument: CCDSEL")
        raise ValueError
    if not (0 <= NBC <= 63 and type(NBC) == int):
        Logger.error(
            "Invalid argument: More than 63 BadColumns chosen (or less than 0)"
        )
        raise ValueError
    if not (len(BC) == NBC):
        Logger.error(
            "Invalid argument: Number of BadColumns (NBC) does not coincide with Bad Column (BC)."
        )
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_pafCCDBadColumn")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CCDSEL")
    root[1][len(root[1]) - 1][2][0].text = str(CCDSEL)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="NBC")
    root[1][len(root[1]) - 1][2][1].text = str(NBC)

    x = 2
    for BadColumn in BC:
        if not (4 <= BadColumn <= 2047 and type(BadColumn) == int):
            Logger.error("Invalid argument: BC")
            raise ValueError
        etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="BC")
        root[1][len(root[1]) - 1][2][x].text = str(BadColumn)
        x = x + 1

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafCCDFlushBadColumns(root, relativeTime, CCDSEL, Timeline_settings, comment=""):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (1 <= CCDSEL <= 127 and type(CCDSEL) == int):
        Logger.error("Invalid argument: CCDSEL")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_pafCCDFlushBadColumns")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CCDSEL")
    root[1][len(root[1]) - 1][2][0].text = str(CCDSEL)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]

    return incremented_time


def TC_pafCCDBIAS(
    root, relativeTime, CCDSEL, VGATE, VSUBST, VRD, VOD, Timeline_settings, comment=""
):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (1 <= CCDSEL <= 127 and type(CCDSEL) == int):
        Logger.error("Invalid argument: CCDSEL")
        raise ValueError
    if not (
        0 <= VGATE <= 255
        and 0 <= VSUBST <= 255
        and 0 <= VRD <= 255
        and 0 <= VOD <= 255
        and type(VGATE) == int
        and type(VSUBST) == int
        and type(VRD) == int
        and type(VOD) == int
    ):
        Logger.error(
            "Invalid argument: CCDBIAS values are not set as integers, or too high or low"
        )
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_pafCCDBIAS")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CCDSEL")
    root[1][len(root[1]) - 1][2][0].text = str(CCDSEL)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="VGATE")
    root[1][len(root[1]) - 1][2][1].text = str(VGATE)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="VSUBST")
    root[1][len(root[1]) - 1][2][2].text = str(VSUBST)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="VRD")
    root[1][len(root[1]) - 1][2][3].text = str(VRD)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="VOD")
    root[1][len(root[1]) - 1][2][4].text = str(VOD)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafCCDSnapshot(root, relativeTime, CCDSEL, Timeline_settings, comment=""):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (1 <= CCDSEL <= 127 and type(CCDSEL) == int):
        Logger.error("Invalid argument: CCDSEL")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_pafCCDSNAPSHOT")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CCDSEL")
    root[1][len(root[1]) - 1][2][0].text = str(CCDSEL)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]

    return incremented_time


def TC_pafCCDTRANSPARENTCMD(
    root, relativeTime, CCDSEL, CHAR, Timeline_settings, comment=""
):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (1 <= CCDSEL <= 127 and type(CCDSEL) == int):
        Logger.error("Invalid argument: CCDSEL")
        raise ValueError
    if not (type(CHAR) == str):
        Logger.error("Invalid argument: CHAR")
        raise TypeError

    etree.SubElement(root[1], "command", mnemonic="TC_pafCCDTRANSPARENTCMD")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CCDSEL")
    root[1][len(root[1]) - 1][2][0].text = str(CCDSEL)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CHAR")
    root[1][len(root[1]) - 1][2][1].text = CHAR

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafDbg(root, relativeTime, CCDSEL, Timeline_settings, comment=""):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (1 <= CCDSEL <= 127 and type(CCDSEL) == int):
        Logger.error("Invalid argument: CCDSEL")
        raise ValueError

    etree.SubElement(root[1], "command", mnemonic="TC_pafDbg")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="CCDSEL")
    root[1][len(root[1]) - 1][2][0].text = str(CCDSEL)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


def TC_pafPM(root, relativeTime, TEXPMS, TEXPIMS, Timeline_settings, comment=""):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, exceeding timeline duration"
        )
        raise ValueError
    if not (0 <= TEXPMS <= 100000 and TEXPIMS >= TEXPMS + 500):
        Logger.error(
            "Invalid argument: TEXPMS is negative or TEXPMS is less than 500ms larger then TEXPIMS"
        )
        raise ValueError
    if not (type(TEXPMS) == int and type(TEXPIMS) == int):
        Logger.error("Invalid argument: TEXPMS or TEXPIMS is not an integer")
        raise TypeError

    etree.SubElement(root[1], "command", mnemonic="TC_pafPM")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "tcArguments")
    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="TEXPMS")
    root[1][len(root[1]) - 1][2][0].text = str(TEXPMS)

    etree.SubElement(root[1][len(root[1]) - 1][2], "tcArgument", mnemonic="TEXPIMS")
    root[1][len(root[1]) - 1][2][1].text = str(TEXPIMS)

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time


"#################### PROCEDURES ###############################"
"###############################################################"


def Payload_Power_Toggle(root, relativeTime, Timeline_settings, comment=""):

    if not (
        _Globals.latestRelativeTime <= relativeTime <= Timeline_settings["duration"]
    ):
        Logger.error(
            "Invalid argument: negative relativeTime, decreasing relativeTime, or exceeding timeline duration"
        )
        raise ValueError

    etree.SubElement(root[1], "procedure", mnemonic="FCP-MTS-0035_Payload_Power_Toggle")

    etree.SubElement(root[1][len(root[1]) - 1], "relativeTime")
    root[1][len(root[1]) - 1][0].text = str(int(relativeTime))

    etree.SubElement(root[1][len(root[1]) - 1], "comment")
    root[1][len(root[1]) - 1][1].text = comment

    etree.SubElement(root[1][len(root[1]) - 1], "parameters")

    incremented_time = relativeTime + Timeline_settings["CMD_separation"]
    _Globals.latestRelativeTime = relativeTime

    return incremented_time

