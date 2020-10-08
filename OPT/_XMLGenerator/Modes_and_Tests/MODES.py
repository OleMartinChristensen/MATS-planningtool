# -*- coding: utf-8 -*-
"""Contain Mode functions which generates and calculates parameters for each mode, 
then calls for Macros/Commands functions located in the *Macros_Commands* package, which will in turn write commands to the XML tree object *root*.

Functions on the form "X", where X is any Mode:

    **Arguments:**
        **root** (*lxml.etree.Element*):  XML tree structure. Main container object for the ElementTree API. \n
        **date** (*ephem.Date*): Starting date of the Mode. On the form of the ephem.Date class. \n
        **duration** (*int*): The duration of the mode [s]. \n
        **relativeTime** (*int*): The starting time of the mode with regard to the start of the timeline [s]. \n
        **Timeline_settings** (*dict*): Dictionary containing the settings of the Timeline given in the *Science_Mode_Timeline*. If no Timeline settings were present in the Science Mode Timeline, they were instead taken from the *Configuration File*. \n
        **Mode_settings** (*dict*): Dictionary containing the settings of the Mode given in the *Science_Mode_Timeline*.

    **Returns:**
        None

When creating new Mode functions it is crucial that the function name is
*X*, where *X* is the same as the string used in the *Science Mode Timeline*. Because OPT will automatically look for any function with the same name as the string in the *Science Mode Timeline*
        
@author: David Skånberg
"""


import ephem, logging, sys, pylab, importlib, skyfield.api

from OPT import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
from OPT._Library import (
    Satellite_Simulator,
    dict_comparator,
    utc_to_onboardTime,
    SunAngle,
    CCDSELExtracter,
)
from .Macros_Commands import Macros, Commands

Logger = logging.getLogger(OPT_Config_File.Logger_name())
# Timeline_settings = OPT_Config_File.Timeline_settings()


"######### Operational Science Modes #########################"
"##############################################################"


def Mode5(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode5
    
    **Macro:** Operational_Limb_Pointing_macro \n
    **CCD_Macro:** Chosen in the settings of the Mode. \n
            
    """

    pointing_altitude = Timeline_settings["StandardPointingAltitude"]

    Mode_settings_ConfigFile = OPT_Config_File.Operational_Science_Mode_settings()

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    CCD_settings = OPT_Config_File.CCD_macro_settings(
        Mode_settings["Choose_Mode5CCDMacro"]
    )
    PM_settings = OPT_Config_File.PM_settings()

    Mode_name = sys._getframe(0).f_code.co_name.replace("", "")
    comment = Mode_name + " starting date: " + str(date) + ", " + str(Mode_settings)

    # pointing_altitude = Mode_settings['pointing_altitude']

    # Macros.Custom_Binning_Macro(root,relativeTime, pointing_altitude=pointing_altitude, Timeline_settings = Timeline_settings, comment = comment)
    Macros.Operational_Limb_Pointing_macro(
        root,
        relativeTime,
        CCD_settings,
        PM_settings=PM_settings,
        pointing_altitude=pointing_altitude,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )


############################################################################################


def Mode1(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode1
    
    **Macro:** Operational_Limb_Pointing_macro \n
    **CCD_Macro:** HighResUV \n
    
    Disable exposure on UV channels for +-lat degrees latitude equatorwards.
    Stop/Start Nadir at dusk/dawn below MATS.
    Simulates MATS and the LP with or without yaw movement to be able to predict and schedule commands in the XML-file.
    
    """

    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos

    CCD_settings = OPT_Config_File.CCD_macro_settings("HighResUV")
    PM_settings = OPT_Config_File.PM_settings()
    Mode_settings_ConfigFile = OPT_Config_File.Operational_Science_Mode_settings()

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    timestep = Mode_settings["timestep"]
    TEXPMS_16 = CCD_settings[16]["TEXPMS"]
    TEXPMS_32 = CCD_settings[32]["TEXPMS"]
    TEXPMS_nadir = CCD_settings[64]["TEXPMS"]

    log_timestep = Mode_settings["log_timestep"]
    Logger.debug("log_timestep [s]: " + str(log_timestep))

    TLE = OPT_Config_File.getTLE()

    "Pre-allocate space"
    lat_MATS = zeros((duration, 1))
    r_MATS = zeros((duration, 3))
    r_MATS_ECEF = zeros((duration, 3))
    r_MATS_unit_vector = zeros((duration, 3))
    optical_axis = zeros((duration, 3))
    lat_LP = zeros((duration, 1))
    MATS_P = zeros((duration, 1))

    sun_angle = zeros((duration, 1))
    lat_LP = zeros((duration, 1))

    R_mean = 6371000  # Radius of Earth in m
    pointing_altitude = Timeline_settings["StandardPointingAltitude"]
    lat = Mode_settings["lat"]

    heightAboveSurface = 35000  # Altitude in km where sun is deemed to reflect in atmosphere, determining night and day below satellite"

    # Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = (
        arccos(R_mean / (R_mean + heightAboveSurface)) / pi * 180 + 90
    )

    Logger.debug("MATS_nadir_eclipse_angle : " + str(MATS_nadir_eclipse_angle))
    Logger.debug("")
    t = -1

    MATS_skyfield = skyfield.api.EarthSatellite(TLE[0], TLE[1])

    new_relativeTime = relativeTime
    current_time = ephem.Date(date)

    # for t in range(int(duration/timestep)):
    "Simulation begins here"
    while current_time < ephem.second * duration + ephem.Date(date):

        t += 1

        if t != 0:
            "Incremented time from scheduling CMDs"
            CMD_scheduling_delay = new_relativeTime - relativeTime
            "Increment with timestep each loop and add any added time from CMD scheduling"
            current_time = ephem.Date(
                current_time + ephem.second * (timestep + CMD_scheduling_delay)
            )
            # current_time = ephem.Date( current_time+ephem.second*(new_relativeTime-relativeTime) )
            relativeTime = new_relativeTime + timestep

        new_relativeTime = relativeTime

        if t * timestep % log_timestep == 0:
            LogFlag = True
        else:
            LogFlag = False

        Satellite_dict = Satellite_Simulator(
            MATS_skyfield,
            current_time,
            Timeline_settings,
            pointing_altitude / 1000,
            LogFlag,
            Logger,
        )

        r_MATS[t] = Satellite_dict["Position [km]"]
        MATS_P[t] = Satellite_dict["OrbitalPeriod [s]"]
        lat_MATS[t] = Satellite_dict["Latitude [degrees]"]
        optical_axis[t] = Satellite_dict["OpticalAxis"]
        lat_LP[t] = Satellite_dict["EstimatedLatitude_LP [degrees]"]

        sun_angle[t] = SunAngle(r_MATS[t], current_time)

        if t * timestep % log_timestep == 0:
            Logger.debug("sun_angle [degrees]: " + str(sun_angle[t]))

        ############# Initial Mode setup ##########################################

        if t == 0:

            "Check if night or day"
            if sun_angle[t] > MATS_nadir_eclipse_angle:

                if abs(lat_LP[t]) < lat:
                    current_state = "Mode1_night_UV_off"
                    comment = (
                        current_state
                        + ": "
                        + str(current_time)
                        + ", parameters: "
                        + str(Mode_settings)
                    )
                    # new_relativeTime = Macros.Mode1_macro(root,relativeTime, pointing_altitude=pointing_altitude, UV_on = False, nadir_on = True, Timeline_settings = Timeline_settings, comment = comment)
                    CCD_settings[16]["TEXPMS"] = 0
                    CCD_settings[32]["TEXPMS"] = 0
                    CCD_settings[64]["TEXPMS"] = TEXPMS_nadir
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                        root,
                        relativeTime,
                        CCD_settings,
                        PM_settings=PM_settings,
                        pointing_altitude=pointing_altitude,
                        Timeline_settings=Timeline_settings,
                        comment=comment,
                    )

                elif abs(lat_LP[t]) > lat:
                    current_state = "Mode1_night_UV_on"
                    comment = (
                        current_state
                        + ": "
                        + str(current_time)
                        + ", parameters: "
                        + str(Mode_settings)
                    )
                    # new_relativeTime = Macros.Mode1_macro(root,relativeTime, pointing_altitude=pointing_altitude, UV_on = True, nadir_on = True, Timeline_settings = Timeline_settings, comment = comment)
                    CCD_settings[16]["TEXPMS"] = TEXPMS_16
                    CCD_settings[32]["TEXPMS"] = TEXPMS_32
                    CCD_settings[64]["TEXPMS"] = TEXPMS_nadir
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                        root,
                        relativeTime,
                        CCD_settings,
                        PM_settings=PM_settings,
                        pointing_altitude=pointing_altitude,
                        Timeline_settings=Timeline_settings,
                        comment=comment,
                    )

            elif sun_angle[t] < MATS_nadir_eclipse_angle:

                if abs(lat_LP[t]) < lat:
                    current_state = "Mode1_day_UV_off"
                    comment = (
                        current_state
                        + ": "
                        + str(current_time)
                        + ", parameters: "
                        + str(Mode_settings)
                    )
                    # new_relativeTime = Macros.Mode1_macro(root,relativeTime,pointing_altitude, UV_on = False, nadir_on = False, Timeline_settings = Timeline_settings, comment = comment)
                    CCD_settings[16]["TEXPMS"] = 0
                    CCD_settings[32]["TEXPMS"] = 0
                    CCD_settings[64]["TEXPMS"] = 0
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                        root,
                        relativeTime,
                        CCD_settings,
                        PM_settings=PM_settings,
                        pointing_altitude=pointing_altitude,
                        Timeline_settings=Timeline_settings,
                        comment=comment,
                    )

                elif abs(lat_LP[t]) > lat:
                    current_state = "Mode1_day_UV_on"
                    comment = (
                        current_state
                        + ": "
                        + str(current_time)
                        + ", parameters: "
                        + str(Mode_settings)
                    )
                    # new_relativeTime = Macros.Mode1_macro(root,relativeTime,pointing_altitude, UV_on = True, nadir_on = False, Timeline_settings = Timeline_settings, comment = comment)
                    CCD_settings[16]["TEXPMS"] = TEXPMS_16
                    CCD_settings[32]["TEXPMS"] = TEXPMS_32
                    CCD_settings[64]["TEXPMS"] = 0
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                        root,
                        relativeTime,
                        CCD_settings,
                        PM_settings=PM_settings,
                        pointing_altitude=pointing_altitude,
                        Timeline_settings=Timeline_settings,
                        comment=comment,
                    )

            Logger.debug(current_state)
            Logger.debug("")

        ############# End of Initial Mode setup ###################################

        if t != 0:
            ####################### SCI-mode Operation planner ################

            # Check if night or day
            if sun_angle[t] > MATS_nadir_eclipse_angle:

                # Check latitude
                if abs(lat_LP[t]) < lat and current_state != "Mode1_night_UV_off":

                    # Check dusk/dawn and latitude boundaries
                    if (
                        sun_angle[t] > MATS_nadir_eclipse_angle
                        and sun_angle[t - 1] < MATS_nadir_eclipse_angle
                    ) or (abs(lat_LP[t]) < lat and abs(lat_LP[t - 1]) > lat):

                        Logger.debug("")
                        current_state = "Mode1_night_UV_off"
                        comment = (
                            current_state
                            + ": "
                            + str(current_time)
                            + ", parameters: "
                            + str(Mode_settings)
                        )
                        # new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude, UV_on = False, nadir_on = True, Timeline_settings = Timeline_settings, comment = comment)
                        CCD_settings[16]["TEXPMS"] = 0
                        CCD_settings[32]["TEXPMS"] = 0
                        CCD_settings[64]["TEXPMS"] = TEXPMS_nadir
                        new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                            root,
                            relativeTime,
                            CCD_settings,
                            PM_settings=PM_settings,
                            pointing_altitude=pointing_altitude,
                            Timeline_settings=Timeline_settings,
                            comment=comment,
                        )

                        Logger.debug(current_state)
                        Logger.debug("current_time: " + str(current_time))
                        Logger.debug("lat_MATS [degrees]: " + str(lat_MATS[t]))
                        Logger.debug("lat_LP [degrees]: " + str(lat_LP[t]))
                        Logger.debug("sun_angle [degrees]: " + str(sun_angle[t]))
                        Logger.debug("")

                # Check latitude
                if abs(lat_LP[t]) > lat and current_state != "Mode1_night_UV_on":

                    # Check dusk/dawn and latitude boundaries
                    if (
                        sun_angle[t] > MATS_nadir_eclipse_angle
                        and sun_angle[t - 1] < MATS_nadir_eclipse_angle
                    ) or (abs(lat_LP[t]) > lat and abs(lat_LP[t - 1]) < lat):

                        Logger.debug("")
                        current_state = "Mode1_night_UV_on"
                        comment = (
                            current_state
                            + ": "
                            + str(current_time)
                            + ", parameters: "
                            + str(Mode_settings)
                        )
                        # new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, UV_on = True, nadir_on = True, Timeline_settings = Timeline_settings, comment = comment)
                        CCD_settings[16]["TEXPMS"] = TEXPMS_16
                        CCD_settings[32]["TEXPMS"] = TEXPMS_32
                        CCD_settings[64]["TEXPMS"] = TEXPMS_nadir
                        new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                            root,
                            relativeTime,
                            CCD_settings,
                            PM_settings=PM_settings,
                            pointing_altitude=pointing_altitude,
                            Timeline_settings=Timeline_settings,
                            comment=comment,
                        )

                        Logger.debug(current_state)
                        Logger.debug("current_time: " + str(current_time))
                        Logger.debug("lat_MATS [degrees]: " + str(lat_MATS[t]))
                        Logger.debug("lat_LP [degrees]: " + str(lat_LP[t]))
                        Logger.debug("sun_angle [degrees]: " + str(sun_angle[t]))
                        Logger.debug("")
                        # Mode1_macro(root,str(t+relativeTime),pointing_altitude, Timeline_settings = Timeline_settings, comment = comment)

            # Check if night or day#
            if sun_angle[t] < MATS_nadir_eclipse_angle:

                # Check latitude
                if abs(lat_LP[t]) < lat and current_state != "Mode1_day_UV_off":

                    # Check dusk/dawn and latitude boundaries
                    if (
                        sun_angle[t] < MATS_nadir_eclipse_angle
                        and sun_angle[t - 1] > MATS_nadir_eclipse_angle
                    ) or (abs(lat_LP[t]) < lat and abs(lat_LP[t - 1]) > lat):

                        Logger.debug("")
                        current_state = "Mode1_day_UV_off"
                        comment = (
                            current_state
                            + ": "
                            + str(current_time)
                            + ", parameters: "
                            + str(Mode_settings)
                        )
                        # new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, UV_on = False, nadir_on = False, Timeline_settings = Timeline_settings, comment = comment)
                        CCD_settings[16]["TEXPMS"] = 0
                        CCD_settings[32]["TEXPMS"] = 0
                        CCD_settings[64]["TEXPMS"] = 0
                        new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                            root,
                            relativeTime,
                            CCD_settings,
                            PM_settings=PM_settings,
                            pointing_altitude=pointing_altitude,
                            Timeline_settings=Timeline_settings,
                            comment=comment,
                        )

                        Logger.debug(current_state)
                        Logger.debug("current_time: " + str(current_time))
                        Logger.debug("lat_MATS [degrees]: " + str(lat_MATS[t]))
                        Logger.debug("lat_LP [degrees]: " + str(lat_LP[t]))
                        Logger.debug("sun_angle [degrees]: " + str(sun_angle[t]))
                        Logger.debug("")

                # Check latitude
                if abs(lat_LP[t]) > lat and current_state != "Mode1_day_UV_on":

                    # Check dusk/dawn and latitude boundaries
                    if (
                        sun_angle[t] > MATS_nadir_eclipse_angle
                        and sun_angle[t - 1] < MATS_nadir_eclipse_angle
                    ) or (abs(lat_LP[t]) > lat and abs(lat_LP[t - 1]) < lat):

                        Logger.debug("")
                        current_state = "Mode1_day_UV_on"
                        comment = (
                            current_state
                            + ": "
                            + str(current_time)
                            + ", parameters: "
                            + str(Mode_settings)
                        )
                        # new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, UV_on = True, nadir_on = False, Timeline_settings = Timeline_settings, comment = comment)
                        CCD_settings[16]["TEXPMS"] = TEXPMS_16
                        CCD_settings[32]["TEXPMS"] = TEXPMS_32
                        CCD_settings[64]["TEXPMS"] = 0
                        new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                            root,
                            relativeTime,
                            CCD_settings,
                            PM_settings=PM_settings,
                            pointing_altitude=pointing_altitude,
                            Timeline_settings=Timeline_settings,
                            comment=comment,
                        )

                        Logger.debug(current_state)
                        Logger.debug("current_time: " + str(current_time))
                        Logger.debug("lat_MATS [degrees]: " + str(lat_MATS[t]))
                        Logger.debug("lat_LP [degrees]: " + str(lat_LP[t]))
                        Logger.debug("sun_angle [degrees]: " + str(sun_angle[t]))
                        Logger.debug("")
                        # Mode1_macro(root,str(t+relativeTime),pointing_altitude, Timeline_settings = Timeline_settings, comment = comment)

            ############### End of SCI-mode operation planner #################


#######################################################################################


def Mode2(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode2
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: HighResIR (High-resolution IR binning). \n
    
    Stop/Start Nadir at dusk/dawn below MATS.
    Simulates MATS to determine when a point below MATS is at night or daytime.
    
    """

    CCD_settings = OPT_Config_File.CCD_macro_settings("HighResIR")
    PM_settings = OPT_Config_File.PM_settings()
    Mode_settings_ConfigFile = OPT_Config_File.Operational_Science_Mode_settings()
    # Timeline_settings = OPT_Config_File.Timeline_settings()

    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    timestep = Mode_settings["timestep"]
    TEXPMS_nadir = CCD_settings[64]["TEXPMS"]

    log_timestep = Mode_settings["log_timestep"]
    Logger.debug("log_timestep [s]: " + str(log_timestep))

    TLE = OPT_Config_File.getTLE()

    "Pre-allocate space"
    sun_angle = zeros((duration, 1))
    r_MATS = zeros((duration, 3))

    R_mean = 6371000  # Radius of Earth in m
    pointing_altitude = Timeline_settings["StandardPointingAltitude"]

    heightAboveSurface = 35000  # Altitude in m where sun is deemed to reflect in atmosphere, determining night and day below satellite"

    # Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = (
        arccos(R_mean / (R_mean + heightAboveSurface)) / pi * 180 + 90
    )
    Logger.debug("MATS_nadir_eclipse_angle : " + str(MATS_nadir_eclipse_angle))

    MATS_skyfield = skyfield.api.EarthSatellite(TLE[0], TLE[1])

    t = -1

    new_relativeTime = relativeTime
    current_time = ephem.Date(date)

    # for t in range(int(duration/timestep)):
    while current_time < ephem.second * duration + ephem.Date(date):

        t += 1

        if t != 0:
            CMD_scheduling_delay = new_relativeTime - relativeTime
            "Increment with timestep each loop and add any added time if new_relativeTime was changed"
            current_time = ephem.Date(
                current_time + ephem.second * (timestep + CMD_scheduling_delay)
            )
            # current_time = ephem.Date( current_time+ephem.second*(new_relativeTime-relativeTime) )

            relativeTime = new_relativeTime + timestep

        new_relativeTime = relativeTime

        # relativeTime = relativeTime + t * timestep
        # current_time = ephem.Date(date+ephem.second*timestep*t)

        if t * timestep % log_timestep == 0:
            LogFlag = True
        else:
            LogFlag = False

        Satellite_dict = Satellite_Simulator(
            MATS_skyfield,
            current_time,
            Timeline_settings,
            pointing_altitude / 1000,
            LogFlag,
            Logger,
        )

        r_MATS[t] = Satellite_dict["Position [km]"]
        sun_angle[t] = SunAngle(r_MATS[t], current_time)

        if t % log_timestep == 0:
            Logger.debug("")
            Logger.debug("current_time: " + str(current_time))
            Logger.debug("sun_angle [degrees]: " + str(sun_angle[t]))

        ############# Initial Mode setup ##########################################

        if t == 0:

            "Check if night or day"
            if sun_angle[t] > MATS_nadir_eclipse_angle:
                current_state = "Mode2_night"
                comment = current_state + ": " + str(Mode_settings)
                # new_relativeTime = Macros.Mode1_macro(root,relativeTime, pointing_altitude=pointing_altitude, nadir_on = True, Timeline_settings = Timeline_settings, comment = comment)
                CCD_settings[64]["TEXPMS"] = TEXPMS_nadir
                new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                    root,
                    relativeTime,
                    CCD_settings,
                    PM_settings=PM_settings,
                    pointing_altitude=pointing_altitude,
                    Timeline_settings=Timeline_settings,
                    comment=comment,
                )

            elif sun_angle[t] < MATS_nadir_eclipse_angle:
                current_state = "Mode2_day"
                comment = current_state + ": " + str(Mode_settings)
                # new_relativeTime = Macros.Mode1_macro(root,relativeTime, pointing_altitude=pointing_altitude, nadir_on = False, Timeline_settings = Timeline_settings, comment = comment)
                CCD_settings[64]["TEXPMS"] = 0
                new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                    root,
                    relativeTime,
                    CCD_settings,
                    PM_settings=PM_settings,
                    pointing_altitude=pointing_altitude,
                    Timeline_settings=Timeline_settings,
                    comment=comment,
                )

        ############# End of Initial Mode setup ###################################

        if t != 0:
            ####################### SCI-mode Operation planner ################

            # Check if night or day
            if (
                sun_angle[t] > MATS_nadir_eclipse_angle
                and current_state != "Mode2_night"
            ):

                # Check dusk/dawn boundaries
                if (
                    sun_angle[t] > MATS_nadir_eclipse_angle
                    and sun_angle[t - 1] < MATS_nadir_eclipse_angle
                ):

                    Logger.debug("")
                    current_state = "Mode2_night"
                    comment = current_state + ": " + str(Mode_settings)
                    # new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, nadir_on = True, Timeline_settings = Timeline_settings, comment = comment)
                    CCD_settings[64]["TEXPMS"] = TEXPMS_nadir
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                        root,
                        relativeTime,
                        CCD_settings,
                        PM_settings=PM_settings,
                        pointing_altitude=pointing_altitude,
                        Timeline_settings=Timeline_settings,
                        comment=comment,
                    )

                    Logger.debug("current_time: " + str(current_time))
                    Logger.debug("sun_angle [degrees]: " + str(sun_angle[t]))
                    Logger.debug("")

            # Check if night or day
            if sun_angle[t] < MATS_nadir_eclipse_angle and current_state != "Mode2_day":

                # Check dusk/dawn boundaries
                if (
                    sun_angle[t] < MATS_nadir_eclipse_angle
                    and sun_angle[t - 1] > MATS_nadir_eclipse_angle
                ):

                    Logger.debug("")
                    current_state = "Mode2_day"
                    comment = current_state + ": " + str(Mode_settings)
                    # new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, nadir_on = False, Timeline_settings = Timeline_settings, comment = comment)
                    CCD_settings[64]["TEXPMS"] = 0
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(
                        root,
                        relativeTime,
                        CCD_settings,
                        PM_settings=PM_settings,
                        pointing_altitude=pointing_altitude,
                        Timeline_settings=Timeline_settings,
                        comment=comment,
                    )

                    Logger.debug("current_time: " + str(current_time))
                    Logger.debug("sun_angle [degrees]: " + str(sun_angle[t]))
                    Logger.debug("")

        ############### End of SCI-mode operation planner #################


################################################################################################

"######### Calibration Modes ##################################"
"##############################################################"


def Mode100(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """ Mode100
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: BinnedCalibration with configurable exposure time of UV and IR CCDs. \n
    
    Successively point at altitudes from X-Y in Operational Mode in intervals of Z with increasing Exposure Times.
    Where X is *pointing_altitude_from*, Y is *pointing_altitude_to, and Z is *pointing_altitude_interval*.
    All defined in *Mode100_settings*.
    
    """

    CCD_settings = OPT_Config_File.CCD_macro_settings("BinnedCalibration")
    PM_settings = OPT_Config_File.PM_settings()
    Mode_settings_ConfigFile = OPT_Config_File.Mode100_settings()

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name + " starting date: " + str(date) + ", " + str(Mode_settings)

    pointing_altitude_from = Mode_settings["pointing_altitude_from"]
    pointing_altitude_to = Mode_settings["pointing_altitude_to"]
    pointing_altitude_interval = Mode_settings["pointing_altitude_interval"]
    ExpTimeUV = Mode_settings["Exp_Time_UV"]
    ExpTimeIR = Mode_settings["Exp_Time_IR"]
    ExpTime_step = Mode_settings["ExpTime_step"]

    number_of_altitudes = int(
        abs(
            (pointing_altitude_to - pointing_altitude_from) / pointing_altitude_interval
            + 1
        )
    )
    pointing_altitudes = [
        pointing_altitude_from + x * pointing_altitude_interval
        for x in range(number_of_altitudes)
    ]

    # Mode_macro = getattr(Macros,Mode_name+'_macro')
    relativeTimeEndOfMode = (
        relativeTime + duration - Timeline_settings["mode_separation"]
    )  # go to idle mode separation (s) before endDate
    initial_relativeTime = relativeTime
    duration_flag = 0
    x = 0
    "Schedule macros for steadily increasing pointing altitudes and exposure times"
    for pointing_altitude in pointing_altitudes:
        mode_relativeTime = relativeTime - initial_relativeTime
        CCD_settings[16]["TEXPMS"] = ExpTimeUV + x * ExpTime_step
        CCD_settings[32]["TEXPMS"] = ExpTimeUV + x * ExpTime_step
        CCD_settings[1]["TEXPMS"] = ExpTimeIR + x * ExpTime_step
        CCD_settings[8]["TEXPMS"] = ExpTimeIR + x * ExpTime_step
        CCD_settings[2]["TEXPMS"] = ExpTimeIR + x * ExpTime_step
        CCD_settings[4]["TEXPMS"] = ExpTimeIR + x * ExpTime_step

        if mode_relativeTime > duration and duration_flag == 0:
            Logger.warning(
                "Warning!! The scheduled time for " + Mode_name + " has ran out."
            )
            # input('Enter anything to ackknowledge and continue:\n')
            duration_flag = 1

        # relativeTime = Mode_macro(root, round(relativeTime,2), CCD_settings,
        #                          pointing_altitude = pointing_altitude, Timeline_settings = Timeline_settings, comment = comment)
        relativeTime = Macros.Operational_Limb_Pointing_macro(
            root,
            round(relativeTime, 2),
            CCD_settings,
            PM_settings=PM_settings,
            pointing_altitude=pointing_altitude,
            Timeline_settings=Timeline_settings,
            comment=comment,
        )

        relativeTime = relativeTime + Mode_settings["pointing_duration"]

        x += 1

    Commands.TC_pafMode(
        root,
        relativeTimeEndOfMode,
        MODE=2,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )


##############################################################################################

##############################################################################################


def Mode110(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode110
    
    **Macro**: Operational_Sweep_macro. \n
    **CCD_Macro**: BinnedCalibration with configurable exposure time of UV and IR CCDs. \n
    
    
    Scan atmosphere from X to Y altitudes with a rate of Z.
    Where X, Y, Z is defined in *Mode110_settings*.
    
    """

    CCD_settings = OPT_Config_File.CCD_macro_settings("BinnedCalibration")
    PM_settings = OPT_Config_File.PM_settings()
    Mode_settings_ConfigFile = OPT_Config_File.Mode110_settings()

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    ExpTimeUV = Mode_settings["Exp_Time_UV"]
    ExpTimeIR = Mode_settings["Exp_Time_IR"]
    CCD_settings[16]["TEXPMS"] = ExpTimeUV
    CCD_settings[32]["TEXPMS"] = ExpTimeUV
    CCD_settings[1]["TEXPMS"] = ExpTimeIR
    CCD_settings[8]["TEXPMS"] = ExpTimeIR
    CCD_settings[2]["TEXPMS"] = ExpTimeIR
    CCD_settings[4]["TEXPMS"] = ExpTimeIR

    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name + " starting date: " + str(date) + ", " + str(Mode_settings)

    pointing_altitude_from = Mode_settings["pointing_altitude_from"]
    pointing_altitude_to = Mode_settings["pointing_altitude_to"]
    sweep_rate = Mode_settings["sweep_rate"]

    relativeTimeEndOfMode = (
        relativeTime + duration - Timeline_settings["mode_separation"]
    )  # go to idle mode separation (s) before endDate

    # Mode_macro = getattr(Macros,Mode_name+'_macro')

    Macros.Operational_Sweep_macro(
        root,
        round(relativeTime, 2),
        CCD_settings,
        PM_settings=PM_settings,
        pointing_altitude_from=pointing_altitude_from,
        pointing_altitude_to=pointing_altitude_to,
        sweep_rate=sweep_rate,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )

    Commands.TC_pafMode(
        root,
        relativeTimeEndOfMode,
        MODE=2,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )


####################################################################################################

#######################################################################################################


def Mode12X(
    root, date, duration, relativeTime, Timeline_settings, Mode_settings, CCD_settings
):
    """Subfunction of Mode12X, where X is 0,1,2,3....
    
    **Macro**: Snapshot_Inertial_macro. \n
    
    Arguments:
        CCD_settings (:obj:`dict` of :obj:`dict` of int): Settings for the CCDs. Defined in the *Configuration File*.
    
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir and also do not have TEXPMS set to 0.
    
    """

    Mode_name = sys._getframe(1).f_code.co_name.replace("", "")
    comment = Mode_name + " starting date: " + str(date) + ", " + str(Mode_settings)

    freeze_start_utc = ephem.Date(date + ephem.second * Mode_settings["freeze_start"])

    Snapshot_relativeTime = (
        relativeTime + Mode_settings["freeze_start"] + Mode_settings["SnapshotTime"]
    )

    FreezeTime = utc_to_onboardTime(freeze_start_utc)

    FreezeDuration = Mode_settings["freeze_duration"]

    pointing_altitude = Mode_settings["pointing_altitude"]

    SnapshotSpacing = Mode_settings["SnapshotSpacing"]

    Logger.debug("freeze_start_utc: " + str(freeze_start_utc))
    Logger.debug("FreezeTime [GPS]: " + str(FreezeTime))
    Logger.debug("FreezeDuration: " + str(FreezeDuration))

    Macros.Snapshot_Inertial_macro(
        root,
        round(relativeTime, 2),
        CCD_settings,
        FreezeTime=FreezeTime,
        FreezeDuration=FreezeDuration,
        pointing_altitude=pointing_altitude,
        StandardPointingAltitude=Timeline_settings["StandardPointingAltitude"],
        SnapshotSpacing=SnapshotSpacing,
        Snapshot_relativeTime=Snapshot_relativeTime,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )


################################################################################################


def Mode120(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode120
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: FullReadout \n
    
    Stare at a point in inertial reference frame and take one Snapshot with each CCDSEL argument defined by the 'CCDSELs' settings and also do not have TEXPMS set to 0. 
    Used for star calibration.
    
    """

    Mode_settings_ConfigFile = OPT_Config_File.Mode120_settings()
    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    CCD_settings = OPT_Config_File.CCD_macro_settings("FullReadout")
    "Set TEXPMS to 0 for CCDs that are not going to take snapshots"
    for CCDSEL in [1, 2, 4, 8, 16, 32, 64]:
        if CCDSEL in Mode_settings["CCDSELs"]:
            continue
        else:
            CCD_settings[CCDSEL]["TEXPMS"] = 0

    Mode12X(
        root,
        date,
        duration,
        relativeTime,
        Timeline_settings=Timeline_settings,
        Mode_settings=Mode_settings,
        CCD_settings=CCD_settings,
    )


################################################################################################


##############################################################################################


def Mode121(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode121
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: FullReadout \n
    
    Stare at a point in inertial reference frame and take one Snapshot with each CCDSEL argument defined by the 'CCDSELs' settings and also do not have TEXPMS set to 0.
    
    """

    Mode_settings_ConfigFile = OPT_Config_File.Mode121_settings()
    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    CCD_settings = OPT_Config_File.CCD_macro_settings("FullReadout")
    "Set TEXPMS to 0 for CCDs that are not going to take snapshots"
    for CCDSEL in [1, 2, 4, 8, 16, 32, 64]:
        if CCDSEL in Mode_settings["CCDSELs"]:
            continue
        else:
            CCD_settings[CCDSEL]["TEXPMS"] = 0

    Mode12X(
        root,
        date,
        duration,
        relativeTime,
        Timeline_settings=Timeline_settings,
        Mode_settings=Mode_settings,
        CCD_settings=CCD_settings,
    )


############################################################################################


def Mode122(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode122
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: BinnedCalibration with configurable exposure time of UV and IR CCDs. \n
    
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir and also do not have TEXPMS set to 0.
    
    """

    Mode_settings_ConfigFile = OPT_Config_File.Mode122_settings()
    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    CCD_settings = OPT_Config_File.CCD_macro_settings("BinnedCalibration")
    ExpTimeUV = Mode_settings["Exp_Time_UV"]
    ExpTimeIR = Mode_settings["Exp_Time_IR"]
    CCD_settings[16]["TEXPMS"] = ExpTimeUV
    CCD_settings[32]["TEXPMS"] = ExpTimeUV
    CCD_settings[1]["TEXPMS"] = ExpTimeIR
    CCD_settings[8]["TEXPMS"] = ExpTimeIR
    CCD_settings[2]["TEXPMS"] = ExpTimeIR
    CCD_settings[4]["TEXPMS"] = ExpTimeIR

    Mode12X(
        root,
        date,
        duration,
        relativeTime,
        Timeline_settings=Timeline_settings,
        Mode_settings=Mode_settings,
        CCD_settings=CCD_settings,
    )


################################################################################################

############################################################################################


def Mode123(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode123
    
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: LowPixel with configurable exposure time of UV and IR CCDs. \n
    
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir and also do not have TEXPMS set to 0.
    
    
    """

    Mode_settings_ConfigFile = OPT_Config_File.Mode123_settings()
    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    CCD_settings = OPT_Config_File.CCD_macro_settings("LowPixel")
    ExpTimeUV = Mode_settings["Exp_Time_UV"]
    ExpTimeIR = Mode_settings["Exp_Time_IR"]
    CCD_settings[16]["TEXPMS"] = ExpTimeUV
    CCD_settings[32]["TEXPMS"] = ExpTimeUV
    CCD_settings[1]["TEXPMS"] = ExpTimeIR
    CCD_settings[8]["TEXPMS"] = ExpTimeIR
    CCD_settings[2]["TEXPMS"] = ExpTimeIR
    CCD_settings[4]["TEXPMS"] = ExpTimeIR

    Mode12X(
        root,
        date,
        duration,
        relativeTime,
        Timeline_settings=Timeline_settings,
        Mode_settings=Mode_settings,
        CCD_settings=CCD_settings,
    )


##############################################################################################


def Mode124(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode124
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: FullReadout. \n
    
    Stare at a point in inertial reference frame and take one Snapshot with each CCDSEL argument defined by the 'CCDSELs' settings and also do not have TEXPMS set to 0. 
    Used for moon calibration.
    """

    Mode_settings_ConfigFile = OPT_Config_File.Mode124_settings()
    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    CCD_settings = OPT_Config_File.CCD_macro_settings("FullReadout")

    "Set TEXPMS to 0 for CCDs that are not going to take snapshots"
    for CCDSEL in [1, 2, 4, 8, 16, 32]:
        if CCDSEL in Mode_settings["CCDSELs"]:
            continue
        else:
            CCD_settings[CCDSEL]["TEXPMS"] = 0

    Mode12X(
        root,
        date,
        duration,
        relativeTime,
        Timeline_settings=Timeline_settings,
        Mode_settings=Mode_settings,
        CCD_settings=CCD_settings,
    )


##############################################################################################


################################################################################################


def Mode130(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode130
    
    **Macro**: Snapshot_Limb_Pointing_macro. \n
    **CCD_Macro**: FullReadout. \n
    
    Look at fixed limb altitude and take Snapshots with all CCD except nadir  and also do not have TEXPMS set to 0.
    """

    CCD_settings = OPT_Config_File.CCD_macro_settings("FullReadout")
    Mode_settings_ConfigFile = OPT_Config_File.Mode130_settings()

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name + " starting date: " + str(date) + ", " + str(Mode_settings)

    pointing_altitude = Mode_settings["pointing_altitude"]
    SnapshotSpacing = Mode_settings["SnapshotSpacing"]

    # Mode_macro = getattr(Macros,Mode_name+'_macro')

    Macros.Snapshot_Limb_Pointing_macro(
        root,
        round(relativeTime, 2),
        CCD_settings,
        pointing_altitude=pointing_altitude,
        SnapshotSpacing=SnapshotSpacing,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )


#####################################################################################################

##############################################################################################


def Mode131(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode131
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: FullReadout. \n
    
    Look at fixed limb altitude in operational mode.
    """

    CCD_settings = OPT_Config_File.CCD_macro_settings("FullReadout")
    PM_settings = OPT_Config_File.PM_settings()
    Mode_settings_ConfigFile = OPT_Config_File.Mode131_settings()

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name + " starting date: " + str(date) + ", " + str(Mode_settings)

    pointing_altitude = Mode_settings["pointing_altitude"]
    relativeTimeEndOfMode = (
        relativeTime + duration - Timeline_settings["mode_separation"]
    )  # go to idle mode separation (s) before endDate

    "CMDs and Macros"
    Macros.Operational_Limb_Pointing_macro(
        root,
        round(relativeTime, 2),
        CCD_settings,
        PM_settings=PM_settings,
        pointing_altitude=pointing_altitude,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )

    Commands.TC_pafMode(
        root,
        relativeTimeEndOfMode,
        MODE=2,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )


################################################################################################

##############################################################################################


def Mode132_133(
    root, date, duration, relativeTime, Timeline_settings, Mode_settings, CCD_settings
):
    """Subfunction of Mode132 and Mode133
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    
    Arguments:
        CCD_settings (:obj:`dict` of :obj:`dict` of int): Settings for the CCDs. Defined in the *Configuration File*.
    
    Look at fixed limb altitude in operational mode with a set of exposure times for UV and IR CCDs.
    """

    Mode_name = sys._getframe(1).f_code.co_name.replace("", "")
    comment = Mode_name + " starting date: " + str(date) + ", " + str(Mode_settings)

    PM_settings = OPT_Config_File.PM_settings()
    pointing_altitude = Mode_settings["pointing_altitude"]
    relativeTimeEndOfMode = (
        relativeTime + duration - Timeline_settings["mode_separation"]
    )  # go to idle mode separation (s) before endDate

    for ExpTimeUV, ExpTimeIR in zip(
        Mode_settings["Exp_Times_UV"], Mode_settings["Exp_Times_IR"]
    ):

        CCD_settings[16]["TEXPMS"] = ExpTimeUV
        CCD_settings[32]["TEXPMS"] = ExpTimeUV
        CCD_settings[1]["TEXPMS"] = ExpTimeIR
        CCD_settings[8]["TEXPMS"] = ExpTimeIR
        CCD_settings[2]["TEXPMS"] = ExpTimeIR
        CCD_settings[4]["TEXPMS"] = ExpTimeIR
        relativeTime = Macros.Operational_Limb_Pointing_macro(
            root,
            round(relativeTime, 2),
            CCD_settings,
            PM_settings=PM_settings,
            pointing_altitude=pointing_altitude,
            Timeline_settings=Timeline_settings,
            comment=comment,
        )

        relativeTime = relativeTime + Mode_settings["session_duration"]

    Commands.TC_pafMode(
        root,
        relativeTimeEndOfMode,
        MODE=2,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )


################################################################################################

################################################################################################


def Mode132(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode132
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: BinnedCalibration with changing exposure times for UV and IR CCDs. \n
    
    Look at fixed limb altitude in operational mode for a set duration with each exposure time.
    """

    CCD_settings = OPT_Config_File.CCD_macro_settings("BinnedCalibration")
    Mode_settings_ConfigFile = OPT_Config_File.Mode132_settings()

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    Mode132_133(
        root,
        date,
        duration,
        relativeTime,
        Timeline_settings=Timeline_settings,
        Mode_settings=Mode_settings,
        CCD_settings=CCD_settings,
    )


##############################################################################################

################################################################################################


def Mode133(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode133,
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: LowPixel with changing exposure times for UV and IR CCDs. \n
    
    Look at fixed limb altitude in operational mode for a set duration with each exposure time.
    """

    CCD_settings = OPT_Config_File.CCD_macro_settings("LowPixel")
    Mode_settings_ConfigFile = OPT_Config_File.Mode133_settings()

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    Mode132_133(
        root,
        date,
        duration,
        relativeTime,
        Timeline_settings=Timeline_settings,
        Mode_settings=Mode_settings,
        CCD_settings=CCD_settings,
    )


##############################################################################################

##############################################################################################


def Mode134(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """Mode134, Operational_Limb_Pointing_macro.
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: CustomBinning \n
    
    Look at fixed limb altitude in Operational Mode.
    """

    CCD_settings = OPT_Config_File.CCD_macro_settings("CustomBinning")
    PM_settings = OPT_Config_File.PM_settings()
    Mode_settings_ConfigFile = OPT_Config_File.Mode134_settings()

    Mode_settings = dict_comparator(Mode_settings, Mode_settings_ConfigFile, Logger)

    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name + " starting date: " + str(date) + ", " + str(Mode_settings)

    pointing_altitude = Mode_settings["pointing_altitude"]
    relativeTimeEndOfMode = (
        relativeTime + duration - Timeline_settings["mode_separation"]
    )  # go to idle mode separation (s) before endDate

    "CMDs and Macros"
    Macros.Operational_Limb_Pointing_macro(
        root,
        round(relativeTime, 2),
        CCD_settings,
        PM_settings=PM_settings,
        pointing_altitude=pointing_altitude,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )

    Commands.TC_pafMode(
        root,
        relativeTimeEndOfMode,
        MODE=2,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )


################################################################################################

##############################################################################################


##############################################################################################


def X(root, date, duration, relativeTime, Timeline_settings, Mode_settings={}):
    """This is a template for a new mode or test. Exchange 'X' for the name of the new mode/test"
    
    Currently this template mode only schedules a *TC_acfLimbPointingAltitudeOffset* CMD.
    """

    "Calls for settings stated in the Configuration File"
    # Mode_settings_ConfigFile = OPT_Config_File.X_settings()
    "Calls for CCD settings for a specific CCD macro, here the CCD macro is 'CustomBinning'"
    CCD_settings = OPT_Config_File.CCD_macro_settings("CustomBinning")

    "Compares settings given in the Science Mode Timeline to settings given in the Configuration File"
    # Mode_settings = dict_comparator(Mode_settings,Mode_settings_ConfigFile)

    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name + " starting date: " + str(date) + ", " + str(Mode_settings)
    relativeTimeEndOfMode = (
        relativeTime + duration - Timeline_settings["mode_separation"]
    )

    Commands.TC_acfLimbPointingAltitudeOffset(
        root,
        round(relativeTime, 2),
        Initial=120000,
        Final=120000,
        Rate=0,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )

    "A call for the macro called Operational_Limb_Pointing_macro"
    Macros.Operational_Limb_Pointing_macro(
        root=root,
        relativeTime=round(relativeTime, 2),
        CCD_settings=CCD_settings,
        PM_settings=OPT_Config_File.PM_settings,
        pointing_altitude=120000,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )

    Commands.TC_pafMode(
        root,
        relativeTimeEndOfMode,
        MODE=2,
        Timeline_settings=Timeline_settings,
        comment=comment,
    )


#######################################################################################################

