# -*- coding: utf-8 -*-
"""
@author: David Skånberg
"""

from scipy.spatial.transform import Rotation as R
from pylab import (
    rcParams,
    savefig,
    scatter,
    pi,
    cross,
    array,
    arccos,
    arctan,
    dot,
    norm,
    transpose,
    zeros,
    sqrt,
    floor,
    figure,
    plot_date,
    datestr2num,
    xlabel,
    ylabel,
    title,
    legend,
    date2num,
)
from skyfield.api import load, EarthSatellite
import ephem, logging, importlib, h5py, json, csv
import datetime, os, pickle, astropy.time, sys, ntpath

from OPT import _Library, _MATS_coordinates, _Globals


OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())

rcParams["figure.max_open_warning"] = 30


def Timeline_Plotter(Science_Mode_Path, OHB_H5_Path, STK_CSV_FILE, Timestep=10):
    """Core function of the Timeline_Plotter.
    
    Goes through the *Science Mode Timeline*, one mode at a time.
    
    Arguments:
        Science_Mode_Path (str): Path to the Science Mode Timeline to be plotted.
        OHB_H5_Path (str): Path to the .h5 file containing position, time, and attitude data.
        STK_CSV_PATH (str): Path to the .csv file containing position (column 1-3), velocity (column 4-6), and time (column 7), generated in STK. Position and velocity data is assumed to be in km and in ICRF.
        Timestep (int): The timestep used for the Science Mode Timeline simulation and if possible when accessing OHB data. Needs to be evenly dividable with the h5-data timestep (or the h5-data timestep needs to be a even multiple of Timestep) to allow synchronized direct comparison. The h5 state data should have a timestep of 10s according to Ground Segment ICD document.
        
    Returns:
        (tuple): Tuple containing:
            (:obj:`dict` of :obj:`list`): **Data_MATS**, updated with the new simulated values from the current Science Mode. \n
            (:obj:`dict` of :obj:`list`): **Data_LP**, updated with the new simulated values from the current Science Mode. \n
            (list): **Time**, updated with new simulated timestamps (utc) from the current Science Mode. \n
            (list): **Time_OHB**, Timestamps of the OHB data (utc).
    
    """

    ############# Set up Logger #################################
    _Library.SetupLogger(OPT_Config_File.Logger_name())
    Logger = logging.getLogger(OPT_Config_File.Logger_name())

    Version = OPT_Config_File.Version()
    Logger.info(
        "Configuration File used: " + _Globals.Config_File + ", Version: " + Version
    )

    "Get Timeline settings and TLE from Configuration File. Only used if not given in the Science Mode Timeline"
    Timeline_settings = OPT_Config_File.Timeline_settings()
    TLE = OPT_Config_File.getTLE()

    "Checks whether data from OHB as a .h5 file was given"
    if OHB_H5_Path == "":
        Timestamp_fraction_of_second = 0
        timestep_OHB_StateData = 1
        OHB_StartTime = 0
        StartIndexState = 0
        StartIndexAttitude = 0
        DataIndexStepState = 0
        DataIndexStepAttitude = 0

    else:
        "Read data and check the timestamps"
        OHB_data = h5py.File(OHB_H5_Path, "r")
        Level1A_data = OHB_data["root"]["Level1A"]

        Time_State_OHB = Level1A_data["ReconstructedData"]["PreciseOrbitEstimation"][
            "Time"
        ][0, :]
        Time_Attitude_OHB = Level1A_data["ReconstructedData"][
            "PreciseAttitudeEstimation"
        ]["Time"][0, :]

        "Go through the data until the time is nonzero. That is where the data begins"
        StartIndexState = 0
        while Time_State_OHB[StartIndexState] == 0:
            StartIndexState += 1

        "Parameters needed to allow synchronization of the science mode timeine simulation to the timestamps of the OHB data"
        Timestamp_fraction_of_second = Time_State_OHB[0] - int(Time_State_OHB[0])
        timestep_OHB_StateData = (
            Time_State_OHB[1 + StartIndexState] - Time_State_OHB[StartIndexState]
        )

        if not (timestep_OHB_StateData == 10):
            Logger.warning(
                "The frequency of the State data in the h5 file is not 0.1 Hz for some reason."
            )

        "Time Synchronization will allow the maximum amount of error values between the simulation and the OHB data to be calculated"
        Time_State_OHB_float = float(Time_State_OHB[StartIndexState])
        OHB_StartTime = astropy.time.Time(
            Time_State_OHB_float, format="gps", scale="utc"
        )
        OHB_StartTime = ephem.Date(OHB_StartTime.to_datetime())
        # OHB_StartTime = ephem.Date(datetime.datetime(1980,1,6)+datetime.timedelta(seconds = Time_State_OHB_float-18))

        "The index stepsize when going through the h5 data"
        if Timestep % timestep_OHB_StateData == 0:
            DataIndexStepState = int(Timestep / timestep_OHB_StateData)
        elif timestep_OHB_StateData % Timestep == 0:
            DataIndexStepState = 1
        else:
            Logger.warning(
                "Timestep of Science Mode Timeline simulation is neither equal to timestep_OHB_StateData*n or timestep_OHB_StateData/n, where n=1,2,3... Synchronized data comparison will not be possible... Setting the h5 DataIndexStepState = 1."
            )
            DataIndexStepState = 1

        "Find out where the attitude data time is equal to the state data time."
        StartIndexAttitude = 0
        while int(Time_Attitude_OHB[StartIndexAttitude]) != int(
            Time_State_OHB[StartIndexState]
        ):
            StartIndexAttitude += 1

        timestep_OHB_AttitudeData = (
            Time_Attitude_OHB[StartIndexAttitude + 1]
            - Time_Attitude_OHB[StartIndexAttitude]
        )

        "Calculate the index step size of attitude date which will allow time synchronization between attitude and state data"
        DataIndexStepAttitude = DataIndexStepState * (
            (timestep_OHB_StateData) / (timestep_OHB_AttitudeData)
        )
        if DataIndexStepAttitude < 1:
            DataIndexStepAttitude = DataIndexStepAttitude * (1 / DataIndexStepAttitude)
            DataIndexStepState = DataIndexStepState * (1 / DataIndexStepAttitude)

        "Abort operation if attitude and state data is not possible to synchronize"
        if not (
            DataIndexStepAttitude == int(DataIndexStepAttitude)
            and DataIndexStepState == int(DataIndexStepState)
        ):
            Logger.error(
                "The timestep of the State is not an even multiple of the time step of the attitude or the other way around."
            )
            sys.exit()

        "Convert a float with no decimals (such as 10.0) to an int. Will cause errors otherwise when indexing"
        DataIndexStepAttitude = int(DataIndexStepAttitude)
        DataIndexStepState = int(DataIndexStepState)

    "Create dictionaries to contain simulated data"
    Data_MATS = {
        "ScienceMode": [],
        "ColorRGB": [],
        "r_MATS [m]": [],
        "r_MATS_ECEF [m]": [],
        "v_MATS [km/s]": [],
        "v_MATS_ECEF [km/s]": [],
        "r_normal_orbit": [],
        "r_normal_orbit_ECEF": [],
        "lat_MATS [degrees]": [],
        "long_MATS [degrees]": [],
        "alt_MATS [m]": [],
        "Yaw_function [degrees]": [],
        "yaw_MATS [degrees]": [],
        "pitch_MATS [degrees]": [],
        "roll_MATS [degrees]": [],
        "r_optical_axis": [],
        "r_optical_axis_ECEF": [],
        "optical_axis_RA [degrees]": [],
        "optical_axis_Dec [degrees]": [],
    }

    Data_LP = {
        "r_LP [m]": [],
        "r_LP_ECEF [m]": [],
        "lat_LP [degrees]": [],
        "long_LP [degrees]": [],
        "alt_LP [m]": [],
    }

    Time = []

    "################# Read Science Mode Timeline json file ############"
    with open(Science_Mode_Path, "r") as read_file:
        ScienceMode = json.load(read_file)

    "######## START GOING THROUGH THE SCIENCE MODE TIMELINE #############"
    "Loop through Science Mode Timeline"
    for x in range(len(ScienceMode)):
        Logger.info("")
        Logger.info("Iteration number: " + str(x + 1))
        Logger.info(str(ScienceMode[x][0]))

        "Skip the first entry and save it, if it only contains Timeline_settings used for the creation of the Science Mode Timeline"
        if ScienceMode[x][0] == "Timeline_settings":
            Timeline_settings = ScienceMode[x][
                3
            ]  # Use Timeline_settings given in the Timeline instead of from the Configuration File
            TLE = ScienceMode[x][4]
            continue

        Data_MATS, Data_LP, Time = Simulator(
            ScienceMode=ScienceMode[x],
            Timestamp_fraction_of_second=Timestamp_fraction_of_second,
            Timestep=Timestep,
            Timeline_settings=Timeline_settings,
            TLE=TLE,
            Data_MATS=Data_MATS,
            Data_LP=Data_LP,
            Time=Time,
            OHB_StartTime=OHB_StartTime,
        )

    Logger.info("End of Simulation")

    "Convert the data from python lists into Numpy arrays"
    "Allows easier data manipulation"
    Data_MATS["lat_MATS [degrees]"] = array(Data_MATS["lat_MATS [degrees]"])
    Data_MATS["long_MATS [degrees]"] = array(Data_MATS["long_MATS [degrees]"])
    Data_MATS["alt_MATS [m]"] = array(Data_MATS["alt_MATS [m]"])
    Data_MATS["Yaw_function [degrees]"] = array(Data_MATS["Yaw_function [degrees]"])

    Data_MATS["r_MATS [m]"] = array(Data_MATS["r_MATS [m]"])
    Data_MATS["r_MATS_ECEF [m]"] = array(Data_MATS["r_MATS_ECEF [m]"])

    Data_MATS["r_normal_orbit"] = array(Data_MATS["r_normal_orbit"])
    Data_MATS["r_normal_orbit_ECEF"] = array(Data_MATS["r_normal_orbit_ECEF"])

    Data_MATS["v_MATS [km/s]"] = array(Data_MATS["v_MATS [km/s]"])
    Data_MATS["v_MATS_ECEF [km/s]"] = array(Data_MATS["v_MATS_ECEF [km/s]"])

    Data_MATS["r_optical_axis"] = array(Data_MATS["r_optical_axis"])
    Data_MATS["r_optical_axis_ECEF"] = array(Data_MATS["r_optical_axis_ECEF"])

    Data_MATS["yaw_MATS [degrees]"] = array(Data_MATS["yaw_MATS [degrees]"])
    Data_MATS["pitch_MATS [degrees]"] = array(Data_MATS["pitch_MATS [degrees]"])
    Data_MATS["roll_MATS [degrees]"] = array(Data_MATS["roll_MATS [degrees]"])

    Data_MATS["optical_axis_RA [degrees]"] = array(
        Data_MATS["optical_axis_RA [degrees]"]
    )
    Data_MATS["optical_axis_Dec [degrees]"] = array(
        Data_MATS["optical_axis_Dec [degrees]"]
    )

    Data_LP["lat_LP [degrees]"] = array(Data_LP["lat_LP [degrees]"])
    Data_LP["long_LP [degrees]"] = array(Data_LP["long_LP [degrees]"])
    Data_LP["alt_LP [m]"] = array(Data_LP["alt_LP [m]"])

    Data_LP["r_LP [m]"] = array(Data_LP["r_LP [m]"])
    Data_LP["r_LP_ECEF [m]"] = array(Data_LP["r_LP_ECEF [m]"])

    Time_OHB = Plotter(
        Data_MATS,
        Data_LP,
        Time,
        DataIndexStepState,
        StartIndexState,
        DataIndexStepAttitude,
        StartIndexAttitude,
        OHB_H5_Path,
        STK_CSV_FILE,
        Science_Mode_Path,
    )

    return Data_MATS, Data_LP, Time, Time_OHB


def Simulator(
    ScienceMode,
    Timestamp_fraction_of_second,
    Timestep,
    Timeline_settings,
    TLE,
    Data_MATS,
    Data_LP,
    Time,
    OHB_StartTime,
):
    """Subfunction, Simulates the position and attitude of MATS depending on the Mode given in *ScienceMode*.
    
    Appends the data during each timestep to *Data_MATS*, *Data_LP*, and *Time*.
    
    Arguments:
        ScienceMode (list): List containing the name of the Science Mode, the start_date, the end_date, and settings related to the Science Mode. 
        Timestamp_fraction_of_second (float): The fraction of a second timestamp for the h5 data. Used here to synchronize timestamps between Timeline Simulation datapoints and OHB h5 file datapoints.
        Timestep (int): The Timestep [s] for the simulation.
        Timeline_settings (dict): A dictionary containing settings for the Timeline given in the *Science Mode Timeline* or in the *Configuration File*.
        TLE (list): A list containing the TLE given in the Science Mode Timeline or in the *Configuration File*.
        Data_MATS (dict of lists): Dictionary containing lists of simulated data of MATS.
        Data_LP (dict of lists): Dictionary containing lists of simulated data of LP.
        Time (list): List containing timestamps (utc) of the simulated data in Data_MATS and Data_LP.
        OHB_StartTime (:obj:`ephem.Date`): Date and time of the first OHB data to be plotted. Used here to synchronize timestamps between Timeline Simulation datapoints and OHB datapoints.
        
    Returns:
        (tuple): Tuple containing:
            (:obj:`dict` of :obj:`list`): **Data_MATS**, updated with the new simulated values from the current Science Mode. \n
            (:obj:`dict` of :obj:`list`): **Data_LP**, updated with the new simulated values from the current Science Mode. \n
            (list): **Time**, updated with new simulated timestamps (utc) from the current Science Mode.
        
    """

    ModeName = ScienceMode[0]
    Settings = ScienceMode[3]

    ###################################################
    "Synchronize simulation Timesteps with OHB Data"
    Mode_start_date = ephem.Date(
        ephem.Date(ScienceMode[1]) + ephem.second * Timestamp_fraction_of_second
    )
    TimeDifferenceRest = round(
        (abs(Mode_start_date - OHB_StartTime) / ephem.second) % Timestep, 0
    )

    if TimeDifferenceRest == 0:
        StartingTimeRelative2StartOfMode = 0
    elif Mode_start_date < OHB_StartTime:
        Mode_start_date = ephem.Date(
            Mode_start_date + ephem.second * TimeDifferenceRest
        )
        StartingTimeRelative2StartOfMode = TimeDifferenceRest
    else:
        Mode_start_date = ephem.Date(
            Mode_start_date + ephem.second * (Timestep - TimeDifferenceRest)
        )
        StartingTimeRelative2StartOfMode = Timestep - TimeDifferenceRest

    "Simulation length"
    Mode_end_date = ephem.Date(ScienceMode[2])
    duration = (Mode_end_date - Mode_start_date) * 24 * 3600

    "If duration of current Mode is very long -> increase timestep to decrease runtime"
    if duration > 12 * 3600:
        Timestep = 180
        Logger.info(
            ScienceMode[0]
            + " has a duration longer than 12 h . Timestep is set to: "
            + str(Timestep)
        )
        timesteps = int(floor(duration / Timestep)) + 1
    else:
        timesteps = int(floor(duration / Timestep)) + 1

    "Timestep of logging"
    log_timestep = 1800
    #######################################################

    #############################################################
    "Determine the science mode, which in turn determines the behaviour of the simulation"
    if (
        ModeName == "Mode120"
        or ModeName == "Mode121"
        or ModeName == "Mode122"
        or ModeName == "Mode123"
        or ModeName == "Mode124"
    ):
        Simulator_Select = "Mode12X"
        freeze_start = Settings["freeze_start"]
        freeze_duration = Settings["freeze_duration"]
        pointing_altitude = Settings["pointing_altitude"]
        freeze_flag = 0

        if ModeName == "Mode120":
            Color = (0, 1, 0)
        elif ModeName == "Mode121":
            Color = (0, 1, 0.5)
        elif ModeName == "Mode122":
            Color = (0, 1, 1)
        elif ModeName == "Mode123":
            Color = (0.5, 0, 0)
        elif ModeName == "Mode124":
            Color = (0.5, 0, 0.5)

    elif ModeName == "Mode1" or ModeName == "Mode2" or ModeName == "Mode5":
        Simulator_Select = "ModeX"
        pointing_altitude = Timeline_settings["StandardPointingAltitude"]

        if ModeName == "Mode1":
            Color = (0, 0, 0.5)
        elif ModeName == "Mode2":
            Color = (0, 0, 1)
        elif ModeName == "Mode5":
            Color = (0, 0.5, 0)

        # elif( ModeName == 'Mode5'):
        #    Simulator_Select = 'ModeX'
        #    pointing_altitude = Settings['pointing_altitude']
        #    Color = (0,0.5,0)

    elif (
        ModeName == "Mode130"
        or ModeName == "Mode131"
        or ModeName == "Mode132"
        or ModeName == "Mode133"
        or ModeName == "Mode134"
    ):
        Simulator_Select = "Mode13X"
        pointing_altitude = Settings["pointing_altitude"]

        if ModeName == "Mode130":
            Color = (0.5, 0, 1)
        elif ModeName == "Mode131":
            Color = (0.5, 0.5, 0)
        elif ModeName == "Mode132":
            Color = (0.5, 0.5, 0.5)
        elif ModeName == "Mode133":
            Color = (0.5, 0.5, 1)
        elif ModeName == "Mode134":
            Color = (0.5, 1, 0)

    elif ModeName == "Mode100":
        Simulator_Select = "Mode100"
        pointing_altitude = Settings["pointing_altitude_from"]
        pointing_altitude_to = Settings["pointing_altitude_to"]
        pointing_altitude_interval = Settings["pointing_altitude_interval"]
        NumberOfCMDStepsForEachAltitude = 11
        pointing_duration = (
            Settings["pointing_duration"]
            + Timeline_settings["pointing_stabilization"]
            + NumberOfCMDStepsForEachAltitude * Timeline_settings["CMD_separation"]
            + Timeline_settings["CCDSYNC_Waittime"]
        )
        timestamp_change_of_pointing_altitude = pointing_duration
        Color = (0, 0.5, 0.5)

    elif ModeName == "Mode110":
        Simulator_Select = "Mode110"
        pointing_altitude = Settings["pointing_altitude_from"]
        pointing_altitude_to = Settings["pointing_altitude_to"]
        sweep_rate = Settings["sweep_rate"]
        pointing_stabilization = Timeline_settings["pointing_stabilization"]
        CMD_separation = Timeline_settings["CMD_separation"]
        Color = (0, 0.5, 0.1)

    else:
        return Data_MATS, Data_LP, Time
    ############################################################################

    "Pre-allocate space"
    lat_MATS = zeros((timesteps, 1))
    long_MATS = zeros((timesteps, 1))
    alt_MATS = zeros((timesteps, 1))
    r_MATS = zeros((timesteps, 3))
    r_MATS_unit_vector = zeros((timesteps, 3))
    r_MATS_ECEF = zeros((timesteps, 3))
    v_MATS = zeros((timesteps, 3))
    v_MATS_ECEF = zeros((timesteps, 3))
    v_MATS_unit_vector = zeros((timesteps, 3))
    normal_orbit = zeros((timesteps, 3))
    lat_LP_estimated = zeros((timesteps, 1))
    Yaw_function = zeros((timesteps, 1))

    optical_axis = zeros((timesteps, 3))
    optical_axis_ECEF = zeros((timesteps, 3))

    r_LP = zeros((timesteps, 3))
    r_LP_ECEF = zeros((timesteps, 3))

    r_V_offset_normal = zeros((timesteps, 3))
    r_H_offset_normal = zeros((timesteps, 3))

    MATS_P = zeros((timesteps, 1))
    yaw_offset_angle = zeros((timesteps, 1))
    pitch_MATS = zeros((timesteps, 1))
    roll_MATS = zeros((timesteps, 1))
    Euler_angles = zeros((timesteps, 3))
    z_SLOF = zeros((timesteps, 3))

    RA_optical_axis = zeros((timesteps, 1))
    Dec_optical_axis = zeros((timesteps, 1))

    lat_LP = zeros((timesteps, 1))
    long_LP = zeros((timesteps, 1))
    alt_LP = zeros((timesteps, 1))
    normal_orbit = zeros((timesteps, 3))
    normal_orbit_ECEF = zeros((timesteps, 3))
    current_time = zeros((timesteps, 1))

    MATS_skyfield = EarthSatellite(TLE[0], TLE[1])

    ###################################################################################
    "Start of Simulation"
    for t in range(timesteps):

        t = t

        if Simulator_Select == "Mode100":
            "Increment the pointing altitude as defined by Mode100"
            if (
                t * Timestep + StartingTimeRelative2StartOfMode
                >= timestamp_change_of_pointing_altitude
                and pointing_altitude_to > pointing_altitude
            ):
                pointing_altitude += pointing_altitude_interval
                timestamp_change_of_pointing_altitude += pointing_duration
        elif Simulator_Select == "Mode110":
            "Perform sweep as defined by Mode110"
            "Check if the sweep is positive or negative"
            if sweep_rate > 0:
                if (
                    t * Timestep + StartingTimeRelative2StartOfMode
                    > pointing_stabilization + 11 * CMD_separation
                    and pointing_altitude_to > pointing_altitude
                ):
                    pointing_altitude += sweep_rate * Timestep
                elif pointing_altitude_to <= pointing_altitude:
                    pointing_altitude = pointing_altitude_to
            elif sweep_rate < 0:
                if (
                    t * Timestep + StartingTimeRelative2StartOfMode
                    > pointing_stabilization + 11 * CMD_separation
                    and pointing_altitude_to < pointing_altitude
                ):
                    pointing_altitude += sweep_rate * Timestep
                elif pointing_altitude_to >= pointing_altitude:
                    pointing_altitude = pointing_altitude_to

        elif (
            Simulator_Select == "Mode12X"
            and t * Timestep + StartingTimeRelative2StartOfMode
            >= freeze_duration + freeze_start
        ):
            "Looking at StandardPointingAltitude after attitude freeze for Mode12X"
            pointing_altitude = Timeline_settings["StandardPointingAltitude"]

        else:
            "Looking at pointing_altitude"
            pass

        "Increment Time"
        current_time = ephem.Date(Mode_start_date + ephem.second * (Timestep * t))
        current_time_datetime = ephem.Date(current_time).datetime()

        "Only log data at certain intervals depending on log_timestep"
        if t * Timestep % log_timestep == 0:
            LogFlag = True
        else:
            LogFlag = False

        "Run the satellite simulation for the current time"
        Satellite_dict = _Library.Satellite_Simulator(
            MATS_skyfield,
            current_time,
            Timeline_settings,
            pointing_altitude / 1000,
            LogFlag,
            Logger,
        )

        "Save results"
        r_MATS[t] = Satellite_dict["Position [km]"]
        v_MATS[t] = Satellite_dict["Velocity [km/s]"]
        normal_orbit[t] = Satellite_dict["OrbitNormal"]
        r_V_offset_normal[t] = Satellite_dict["Normal2V_offset"]
        r_H_offset_normal[t] = Satellite_dict["Normal2H_offset"]
        MATS_P[t] = Satellite_dict["OrbitalPeriod [s]"]
        alt_MATS[t] = Satellite_dict["Altitude [km]"]
        lat_MATS[t] = Satellite_dict["Latitude [degrees]"]
        long_MATS[t] = Satellite_dict["Longitude [degrees]"]
        optical_axis[t] = Satellite_dict["OpticalAxis"]
        Dec_optical_axis[t] = Satellite_dict["Dec_OpticalAxis [degrees]"]
        RA_optical_axis[t] = Satellite_dict["RA_OpticalAxis [degrees]"]
        pitch_MATS[t] = Satellite_dict["Pitch [degrees]"]
        lat_LP_estimated[t] = Satellite_dict["EstimatedLatitude_LP [degrees]"]
        Yaw_function[t] = Satellite_dict["Yaw [degrees]"]

        v_MATS_unit_vector[t, 0:3] = v_MATS[t, 0:3] / norm(v_MATS[t, 0:3])
        r_MATS_unit_vector[t, 0:3] = r_MATS[t, 0:3] / norm(r_MATS[t, 0:3])

        "Coordinate transformations and calculations"
        (
            r_MATS_ECEF[t, 0],
            r_MATS_ECEF[t, 1],
            r_MATS_ECEF[t, 2],
        ) = _MATS_coordinates.eci2ecef(
            r_MATS[t, 0] * 1000,
            r_MATS[t, 1] * 1000,
            r_MATS[t, 2] * 1000,
            current_time_datetime,
        )

        (
            optical_axis_ECEF[t, 0],
            optical_axis_ECEF[t, 1],
            optical_axis_ECEF[t, 2],
        ) = _MATS_coordinates.eci2ecef(
            optical_axis[t, 0],
            optical_axis[t, 1],
            optical_axis[t, 2],
            current_time_datetime,
        )

        (
            r_LP_ECEF[t, 0],
            r_LP_ECEF[t, 1],
            r_LP_ECEF[t, 2],
        ) = _MATS_coordinates.ecef2tanpoint(
            r_MATS_ECEF[t][0],
            r_MATS_ECEF[t][1],
            r_MATS_ECEF[t][2],
            optical_axis_ECEF[t, 0],
            optical_axis_ECEF[t, 1],
            optical_axis_ECEF[t, 2],
        )

        lat_LP[t], long_LP[t], alt_LP[t] = _MATS_coordinates.ECEF2lla(
            r_LP_ECEF[t, 0], r_LP_ECEF[t, 1], r_LP_ECEF[t, 2]
        )

        r_LP[t, 0], r_LP[t, 1], r_LP[t, 2] = _MATS_coordinates.ecef2eci(
            r_LP_ECEF[t, 0], r_LP_ECEF[t, 1], r_LP_ECEF[t, 2], current_time_datetime
        )

        (
            v_MATS_ECEF[t, 0],
            v_MATS_ECEF[t, 1],
            v_MATS_ECEF[t, 2],
        ) = _MATS_coordinates.eci2ecef(
            v_MATS[t, 0], v_MATS[t, 1], v_MATS[t, 2], current_time_datetime
        )

        (
            normal_orbit_ECEF[t, 0],
            normal_orbit_ECEF[t, 1],
            normal_orbit_ECEF[t, 2],
        ) = _MATS_coordinates.eci2ecef(
            normal_orbit[t, 0],
            normal_orbit[t, 1],
            normal_orbit[t, 2],
            current_time_datetime,
        )

        # orbangle_between_LP_MATS_array_dotproduct[t] = arccos( dot(r_MATS_unit_vector[t], r_LP[t]) / norm(r_LP[t]) ) / pi*180

        "Freezing the attitude"
        # if( Simulator_Select == 'Mode12X' and t*Timestep+Timestep > freeze_start and t*Timestep <= freeze_duration+freeze_start):
        if (
            Simulator_Select == "Mode12X"
            and t * Timestep + StartingTimeRelative2StartOfMode > freeze_start
            and t * Timestep + StartingTimeRelative2StartOfMode
            <= freeze_duration + freeze_start
        ):
            "Save the pointing for the exact time when attitude freeze is initiated"
            if freeze_flag == 0:

                "Exact timing of Attitude freeze"
                current_time_freeze = ephem.Date(
                    ephem.Date(ScienceMode[1]) + ephem.second * (freeze_start)
                )

                "Run the satellite simulation for the freeze time"
                Satellite_dict = _Library.Satellite_Simulator(
                    MATS_skyfield,
                    current_time_freeze,
                    Timeline_settings,
                    pointing_altitude / 1000,
                    LogFlag,
                    Logger,
                )

                "Save results"
                r_V_offset_normal_Freeze = Satellite_dict["Normal2V_offset"]
                r_H_offset_normal_Freeze = Satellite_dict["Normal2H_offset"]
                optical_axis_Freeze = Satellite_dict["OpticalAxis"]

            freeze_flag = 1

            "Maintain the same optical axis as the simulation progresses during the freeze"
            optical_axis[t, :] = optical_axis_Freeze
            (
                optical_axis_ECEF[t, 0],
                optical_axis_ECEF[t, 1],
                optical_axis_ECEF[t, 2],
            ) = _MATS_coordinates.eci2ecef(
                optical_axis[t, 0],
                optical_axis[t, 1],
                optical_axis[t, 2],
                current_time_datetime,
            )

            r_V_offset_normal[t, :] = r_V_offset_normal_Freeze
            r_H_offset_normal[t, :] = r_H_offset_normal_Freeze

            (
                r_LP_ECEF[t, 0],
                r_LP_ECEF[t, 1],
                r_LP_ECEF[t, 2],
            ) = _MATS_coordinates.ecef2tanpoint(
                r_MATS_ECEF[t][0],
                r_MATS_ECEF[t][1],
                r_MATS_ECEF[t][2],
                optical_axis_ECEF[t, 0],
                optical_axis_ECEF[t, 1],
                optical_axis_ECEF[t, 2],
            )

            lat_LP[t], long_LP[t], alt_LP[t] = _MATS_coordinates.ECEF2lla(
                r_LP_ECEF[t, 0], r_LP_ECEF[t, 1], r_LP_ECEF[t, 2]
            )

            r_LP[t, 0], r_LP[t, 1], r_LP[t, 2] = _MATS_coordinates.ecef2eci(
                r_LP_ECEF[t, 0], r_LP_ECEF[t, 1], r_LP_ECEF[t, 2], current_time_datetime
            )

            Dec_optical_axis[t] = (
                arctan(
                    optical_axis[t, 2]
                    / sqrt(optical_axis[t, 0] ** 2 + optical_axis[t, 1] ** 2)
                )
                / pi
                * 180
            )
            RA_optical_axis[t] = (
                arccos(
                    dot([1, 0, 0], [optical_axis[t, 0], optical_axis[t, 1], 0])
                    / norm([optical_axis[t, 0], optical_axis[t, 1], 0])
                )
                / pi
                * 180
            )

            if optical_axis[t, 1] < 0:
                RA_optical_axis[t] = 360 - RA_optical_axis[t]

        "Define SLOF basis and convert ECI coordinates to SLOF"
        z_SLOF = -r_MATS[t, :]
        z_SLOF = z_SLOF / norm(z_SLOF)
        y_SLOF = -normal_orbit[t, :]
        y_SLOF = y_SLOF / norm(y_SLOF)
        x_SLOF = v_MATS[t, :]
        x_SLOF = x_SLOF / norm(x_SLOF)

        "A change of basis matrix is calculated from the transpose of a matrix where the columns are the basis vectors"
        dcm_SLOF_coordinate_system = array(
            (
                [x_SLOF[0], y_SLOF[0], z_SLOF[0]],
                [x_SLOF[1], y_SLOF[1], z_SLOF[1]],
                [x_SLOF[2], y_SLOF[2], z_SLOF[2]],
            )
        )
        dcm_change_of_basis_ECI_to_SLOF = transpose(dcm_SLOF_coordinate_system)
        r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_ECI_to_SLOF)

        optical_axis_SLOF = r_change_of_basis_ECI_to_SLOF.apply(optical_axis[t, :])
        r_V_offset_normal_SLOF = r_change_of_basis_ECI_to_SLOF.apply(
            r_V_offset_normal[t, :]
        )
        r_H_offset_normal_SLOF = r_change_of_basis_ECI_to_SLOF.apply(
            r_H_offset_normal[t, :]
        )

        "Find rotation and Euler angles by matching basis vectors of optical axis in SLOF (Spacecraft Local orbit Frame) to basis vectors of SBF (Spacecraft Body Frame) in SLOF"
        basis_SBF = array(
            ((optical_axis_SLOF), (r_V_offset_normal_SLOF), (r_H_offset_normal_SLOF))
        )
        basis_SLOF = array(((0, 0, -1), (0, 1, 0), (1, 0, 0)))
        rotation, sensitivity_matrix = R.match_vectors(basis_SBF, basis_SLOF)

        "The intrinsic (ZYZ) Euler angles which corresponds to rotating the Z-axis of the SLOF basis to the Spacecraft body frame -Z-axis (which correspond to the optical axis)"
        Euler_angles[t, :] = rotation.as_euler("ZYZ", degrees=True)
        yaw_offset_angle[t] = Euler_angles[t, 0]
        pitch_MATS[t] = Euler_angles[t, 1]
        roll_MATS[t] = Euler_angles[t, 2]

        "Save data"
        Data_MATS["ScienceMode"].append(ModeName)
        Data_MATS["ColorRGB"].append(Color)

        Data_MATS["lat_MATS [degrees]"].append(lat_MATS[t])
        Data_MATS["long_MATS [degrees]"].append(long_MATS[t])
        Data_MATS["alt_MATS [m]"].append(alt_MATS[t] * 1000)
        Data_MATS["Yaw_function [degrees]"].append(Yaw_function[t])

        Data_MATS["r_MATS [m]"].append(r_MATS[t] * 1000)
        Data_MATS["r_MATS_ECEF [m]"].append(r_MATS_ECEF[t])

        Data_MATS["r_normal_orbit"].append(normal_orbit[t])
        Data_MATS["r_normal_orbit_ECEF"].append(normal_orbit_ECEF[t])

        Data_MATS["v_MATS [km/s]"].append(v_MATS[t])
        Data_MATS["v_MATS_ECEF [km/s]"].append(v_MATS_ECEF[t])

        Data_MATS["r_optical_axis"].append(optical_axis[t])
        Data_MATS["r_optical_axis_ECEF"].append(optical_axis_ECEF[t])

        Data_MATS["yaw_MATS [degrees]"].append(yaw_offset_angle[t])
        Data_MATS["pitch_MATS [degrees]"].append(pitch_MATS[t])
        Data_MATS["roll_MATS [degrees]"].append(roll_MATS[t])

        Data_MATS["optical_axis_RA [degrees]"].append(RA_optical_axis[t])
        Data_MATS["optical_axis_Dec [degrees]"].append(Dec_optical_axis[t])

        Data_LP["lat_LP [degrees]"].append(lat_LP[t])
        Data_LP["long_LP [degrees]"].append(long_LP[t])
        Data_LP["alt_LP [m]"].append(alt_LP[t])

        Data_LP["r_LP [m]"].append(r_LP[t])
        Data_LP["r_LP_ECEF [m]"].append(r_LP_ECEF[t])

        Time.append(current_time_datetime)

    return Data_MATS, Data_LP, Time


def Plotter(
    Data_MATS,
    Data_LP,
    Time,
    DataIndexStepState,
    StartIndexState,
    DataIndexStepAttitude,
    StartIndexAttitude,
    OHB_H5_Path="",
    STK_CSV_FILE="",
    Science_Mode_Path="",
):
    """Subfunction, Extracts data and performs calculations and plots the position and attitude data of MATS and LP.
    
    Performs calculations on the data given in the file located at *OHB_H5_Path* and plots the results. 
    Also plots the simulated data given in *Data_MATS* and *Data_LP* as a function of the 
    timestamps in *Time*. May also plot positional error compared to STK data at any point where the timestamp matches, if *STK_CSV_FILE* is given.
    
    Arguments:
        Data_MATS (dict of lists): Dictionary containing lists of simulated data of MATS.
        Data_LP (dict of lists): Dictionary containing lists of simulated data of LP.
        Time (list): List containing timestamps (datetime utc) of the simulated data in Data_MATS and Data_LP.
        DataIndexStepState (int): The data index step size when going through the state data given in *OHB_H5_Path*.
        StartIndexState (int): The starting data index when going through the state data given in *OHB_H5_Path*.
        DataIndexStepAttitude (int):  The data index step size when going through the attitude data given in *OHB_H5_Path*.
        StartIndexAttitude (int): The starting data index when going through the attitude data given in *OHB_H5_Path*.
        OHB_H5_Path (str): Path to the .h5 file containing position, time, and attitude data. If the string is empty, only Science Mode Timeline data will be plotted.
        STK_CSV_PATH (str): Path to the .csv file containing position (column 1-3), velocity (column 4-6), and time (column 7), generated in STK. Position and velocity data is assumed to be in km and in ICRF.
        
    Returns:
        (list): **Time_OHB**, Timestamps (datetime utc) of the OHB data.
        
    """

    Time_MPL = date2num(Time[:])

    "######## Try to Create a directory for storage of Timeline_Plotter plots and data files #######"
    figureDirectory = ntpath.basename(Science_Mode_Path)
    figureDirectory = os.path.join(
        "Output", figureDirectory.strip(".json"), "Timeline_Plotter_PlotsAndData"
    )
    try:
        os.makedirs(figureDirectory)
    except:
        pass

    "############ OHB DATA Extraction #########################"
    "##############################################################################"
    if OHB_H5_Path == "":
        timesteps = 0
        StartIndexState = 0

    elif OHB_H5_Path != "":
        OHB_data = h5py.File(OHB_H5_Path, "r")

        Level1A_data = OHB_data["root"]["Level1A"]

        # root = OHB_data['root']

        x_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseOrbitEstimation"][
            "acsGnssStateJ2000"
        ][0, :]
        y_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseOrbitEstimation"][
            "acsGnssStateJ2000"
        ][1, :]
        z_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseOrbitEstimation"][
            "acsGnssStateJ2000"
        ][2, :]

        vel_x_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseOrbitEstimation"][
            "acsGnssStateJ2000"
        ][3, :]
        vel_y_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseOrbitEstimation"][
            "acsGnssStateJ2000"
        ][4, :]
        vel_z_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseOrbitEstimation"][
            "acsGnssStateJ2000"
        ][5, :]

        quat1_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseAttitudeEstimation"][
            "afsAttitudeState"
        ][0, :]
        quat2_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseAttitudeEstimation"][
            "afsAttitudeState"
        ][1, :]
        quat3_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseAttitudeEstimation"][
            "afsAttitudeState"
        ][2, :]
        quat4_MATS_OHB = Level1A_data["ReconstructedData"]["PreciseAttitudeEstimation"][
            "afsAttitudeState"
        ][3, :]

        x_MATS_OHB_ECEFdata = Level1A_data["TM_acGnssOps"]["acoOnGnssStateEcef_x"][:]
        y_MATS_OHB_ECEFdata = Level1A_data["TM_acGnssOps"]["acoOnGnssStateEcef_y"][:]
        z_MATS_OHB_ECEFdata = Level1A_data["TM_acGnssOps"]["acoOnGnssStateEcef_z"][:]

        """
        x_MATS_OHB = root['TM_acOnGnss']['acoOnGnssStateJ2000_x']['raw']
        y_MATS_OHB = root['TM_acOnGnss']['acoOnGnssStateJ2000_y']['raw']
        z_MATS_OHB = root['TM_acOnGnss']['acoOnGnssStateJ2000_z']['raw']
        
        vel_x_MATS_OHB = root['TM_acOnGnss']['acoOnGnssStateJ2000_vx']['raw']
        vel_y_MATS_OHB = root['TM_acOnGnss']['acoOnGnssStateJ2000_vy']['raw']
        vel_z_MATS_OHB = root['TM_acOnGnss']['acoOnGnssStateJ2000_vz']['raw']
        
        quat1_MATS_OHB = root['TM_afAre']['afoTmAreAttitudeState_0']['raw']
        quat2_MATS_OHB = root['TM_afAre']['afoTmAreAttitudeState_1']['raw']
        quat3_MATS_OHB = root['TM_afAre']['afoTmAreAttitudeState_2']['raw']
        quat4_MATS_OHB = root['TM_afAre']['afoTmAreAttitudeState_3']['raw']
        """

        # Time_State_OHB = root['TM_acOnGnss']['acoOnGnssStateTime']['raw']
        Time_State_OHB = Level1A_data["ReconstructedData"]["PreciseOrbitEstimation"][
            "Time"
        ][0, :]

        Time_Attitude_OHB = Level1A_data["ReconstructedData"][
            "PreciseAttitudeEstimation"
        ]["Time"][0, :]

        "#########################################################################"
        "Make sure that the amount of timesteps is less than the available data"
        PossibleTimesteps = []

        timesteps = int((len(x_MATS_OHB) - StartIndexState) / DataIndexStepState)
        PossibleTimesteps.append(timesteps)

        timesteps = int((len(quat1_MATS_OHB) - StartIndexState) / DataIndexStepState)
        PossibleTimesteps.append(timesteps)

        timesteps = int((len(Time_State_OHB) - StartIndexState) / DataIndexStepState)
        PossibleTimesteps.append(timesteps)

        "The shortest data series determines the amount of timesteps"
        PossibleTimesteps.sort()
        timesteps = PossibleTimesteps[0]
        "##########################################################################"

        ###### !!!!!!!!!!!!!!!! ############
        # FractionOfDataUsed = 1/3

        Continue = True
        while Continue:
            Input = input(
                "Input the fractional amount of the available OHB h5-data to use (0<=X<=1).\n"
            )
            try:
                Input = float(Input)
                if 0 <= Input <= 1:
                    FractionOfDataUsed = Input
                    timesteps = int(timesteps * FractionOfDataUsed - 1)
                    Logger.info(
                        "Fractional amount of h5-data used: " + str(FractionOfDataUsed)
                    )
                    if timesteps < 1:
                        timesteps = 1
                    Continue = False
                else:
                    print("Try again!")
            except:
                print("Try again!")
        ###### !!!!!!!!!!!!!!!! ############

        "To make sure there is enough data to support the amount of timesteps together with the DataIndexStepState"
        if len(Time_State_OHB) <= DataIndexStepState * timesteps + StartIndexState:
            timesteps = int(len(Time_State_OHB) / DataIndexStepState)

    "#########################################################################"

    "Allocate Space"
    Time_MPL_OHB = zeros((timesteps, 1))
    Time_OHB = []
    Time_OHB_attitude = []
    current_time_attitude = []

    lat_MATS_OHB = zeros((timesteps, 1))
    long_MATS_OHB = zeros((timesteps, 1))
    alt_MATS_OHB = zeros((timesteps, 1))

    q1_MATS_OHB = zeros((timesteps, 1))
    q2_MATS_OHB = zeros((timesteps, 1))
    q3_MATS_OHB = zeros((timesteps, 1))
    q4_MATS_OHB = zeros((timesteps, 1))

    Vel_MATS_OHB = zeros((timesteps, 3))
    r_MATS_OHB = zeros((timesteps, 3))
    r_MATS_OHB_ECEF = zeros((timesteps, 3))
    r_MATS_OHB_ECEFdata = zeros((timesteps, 3))
    r_MATS_OHB_ECEF2 = zeros((timesteps, 3))
    optical_axis_OHB = zeros((timesteps, 3))
    r_LP_OHB_ECEF = zeros((timesteps, 3))
    lat_LP_OHB = zeros((timesteps, 1))
    long_LP_OHB = zeros((timesteps, 1))
    alt_LP_OHB = zeros((timesteps, 1))

    Dec_OHB = zeros((timesteps, 1))
    RA_OHB = zeros((timesteps, 1))

    Time_State_OHB_float = zeros((timesteps, 1))
    Time_Attitude_OHB_float = zeros((timesteps, 1))

    Euler_angles_SLOF_OHB = zeros((timesteps, 3))
    Euler_angles_ECI_OHB = zeros((timesteps, 3))

    optical_axis_OHB = zeros((timesteps, 3))
    optical_axis_OHB_ECEF = zeros((timesteps, 3))

    "############################################################"
    "############## OHB Data Calculations #######################"
    if OHB_H5_Path != "":

        Logger.info("Calculations of OHB Data")
        for t in range(timesteps):

            # t_OHB = round(t* DataIndexStepState + StartIndexState)
            t_OHB_state = round(t * DataIndexStepState + StartIndexState)
            Time_State_OHB_float[t] = float(Time_State_OHB[t_OHB_state])

            t_OHB_attitude = round(t * DataIndexStepAttitude + StartIndexAttitude)
            Time_Attitude_OHB_float[t] = float(Time_Attitude_OHB[t_OHB_attitude])

            Time_OHB.append(
                astropy.time.Time(
                    Time_State_OHB_float[t, 0], format="gps", scale="utc"
                ).to_datetime()
            )
            Time_OHB_attitude.append(
                astropy.time.Time(
                    Time_Attitude_OHB_float[t, 0], format="gps", scale="utc"
                ).to_datetime()
            )

            if not (
                int(Time_State_OHB_float[t]) == int(Time_Attitude_OHB_float[t])
                and abs(Time_Attitude_OHB_float[t] - Time_State_OHB_float[t]) < 1
            ):
                Logger.warning("State time not synchronized to attitude time!!")

            # Time_OHB.append(datetime.datetime(1980,1,6)+datetime.timedelta(seconds = Time_State_OHB_float[t,0]-18) )

            # current_time_attitude.append(datetime.datetime(1980,1,6)+datetime.timedelta(seconds = Time_Attitude_OHB_float[t,0]-18) )

            r_MATS_OHB[t, 0] = x_MATS_OHB[t_OHB_state]
            r_MATS_OHB[t, 1] = y_MATS_OHB[t_OHB_state]
            r_MATS_OHB[t, 2] = z_MATS_OHB[t_OHB_state]

            Vel_MATS_OHB[t, 0] = vel_x_MATS_OHB[t_OHB_state]
            Vel_MATS_OHB[t, 1] = vel_y_MATS_OHB[t_OHB_state]
            Vel_MATS_OHB[t, 2] = vel_z_MATS_OHB[t_OHB_state]

            q1_MATS_OHB[t, 0] = quat1_MATS_OHB[t_OHB_attitude]
            q2_MATS_OHB[t, 0] = quat2_MATS_OHB[t_OHB_attitude]
            q3_MATS_OHB[t, 0] = quat3_MATS_OHB[t_OHB_attitude]
            q4_MATS_OHB[t, 0] = quat4_MATS_OHB[t_OHB_attitude]

            r_MATS_OHB_ECEFdata[t, 0] = x_MATS_OHB_ECEFdata[t_OHB_state]
            r_MATS_OHB_ECEFdata[t, 1] = y_MATS_OHB_ECEFdata[t_OHB_state]
            r_MATS_OHB_ECEFdata[t, 2] = z_MATS_OHB_ECEFdata[t_OHB_state]

            "SLOF = Spacecraft Local Orbit Frame"
            z_SLOF = -r_MATS_OHB[t, 0:3]
            # z_SLOF = -r_MATS[t,0:3]
            z_SLOF = z_SLOF / norm(z_SLOF)
            x_SLOF = Vel_MATS_OHB[t, 0:3]
            x_SLOF = x_SLOF / norm(x_SLOF)
            y_SLOF = cross(z_SLOF, x_SLOF)
            y_SLOF = y_SLOF / norm(y_SLOF)

            "Create change of coordinate matrix from ECI to SLOF"
            dcm_SLOF_coordinate_system = array(
                (
                    [x_SLOF[0], y_SLOF[0], z_SLOF[0]],
                    [x_SLOF[1], y_SLOF[1], z_SLOF[1]],
                    [x_SLOF[2], y_SLOF[2], z_SLOF[2]],
                )
            )
            dcm_change_of_basis_ECI_to_SLOF = transpose(dcm_SLOF_coordinate_system)
            r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_ECI_to_SLOF)

            "Create Rotation from quaternions (ECI to SpaceCraft BodyFrame)"
            MATS_ECI_OHB = R.from_quat(
                [
                    q2_MATS_OHB[t, 0],
                    q3_MATS_OHB[t, 0],
                    q4_MATS_OHB[t, 0],
                    q1_MATS_OHB[t, 0],
                ]
            )

            "Apply rotation to -z to get optical axis"
            optical_axis_OHB[t, :] = MATS_ECI_OHB.apply([0, 0, -1])
            optical_axis_OHB[t, :] = optical_axis_OHB[t, :] / norm(
                optical_axis_OHB[t, :]
            )

            "Caluclate RA and DEC of optical axis"
            Dec_OHB[t] = (
                arctan(
                    optical_axis_OHB[t, 2]
                    / sqrt(optical_axis_OHB[t, 0] ** 2 + optical_axis_OHB[t, 1] ** 2)
                )
                / pi
                * 180
            )
            RA_OHB[t] = (
                arccos(
                    dot([1, 0, 0], [optical_axis_OHB[t, 0], optical_axis_OHB[t, 1], 0])
                    / norm([optical_axis_OHB[t, 0], optical_axis_OHB[t, 1], 0])
                )
                / pi
                * 180
            )
            if optical_axis_OHB[t, 1] < 0:
                RA_OHB[t] = 360 - RA_OHB[t]

            Euler_angles_ECI_OHB[t, :] = MATS_ECI_OHB.as_euler("ZYZ", degrees=True)

            "Rotation multiplication to change the basis to SLOF, giving a rotation from SLOF to SPF"
            MATS_SLOF_OHB = r_change_of_basis_ECI_to_SLOF * MATS_ECI_OHB

            "Yaw, Pitch, Roll as Euler Angles"
            Euler_angles_SLOF_OHB[t, :] = MATS_SLOF_OHB.as_euler("ZYZ", degrees=True)

            (
                optical_axis_OHB_ECEF[t, 0],
                optical_axis_OHB_ECEF[t, 1],
                optical_axis_OHB_ECEF[t, 2],
            ) = _MATS_coordinates.eci2ecef(
                optical_axis_OHB[t, 0],
                optical_axis_OHB[t, 1],
                optical_axis_OHB[t, 2],
                Time_OHB[t],
            )

            optical_axis_OHB_ECEF[t, :] = optical_axis_OHB_ECEF[t, :] / norm(
                optical_axis_OHB_ECEF[t, :]
            )

            (
                r_MATS_OHB_ECEF[t, 0],
                r_MATS_OHB_ECEF[t, 1],
                r_MATS_OHB_ECEF[t, 2],
            ) = _MATS_coordinates.eci2ecef(
                r_MATS_OHB[t, 0], r_MATS_OHB[t, 1], r_MATS_OHB[t, 2], Time_OHB[t]
            )

            (
                lat_MATS_OHB[t],
                long_MATS_OHB[t],
                alt_MATS_OHB[t],
            ) = _MATS_coordinates.ECEF2lla(
                r_MATS_OHB_ECEF[t, 0], r_MATS_OHB_ECEF[t, 1], r_MATS_OHB_ECEF[t, 2]
            )

            (
                r_LP_OHB_ECEF[t, 0],
                r_LP_OHB_ECEF[t, 1],
                r_LP_OHB_ECEF[t, 2],
            ) = _MATS_coordinates.ecef2tanpoint(
                r_MATS_OHB_ECEF[t, 0],
                r_MATS_OHB_ECEF[t, 1],
                r_MATS_OHB_ECEF[t, 2],
                optical_axis_OHB_ECEF[t, 0],
                optical_axis_OHB_ECEF[t, 1],
                optical_axis_OHB_ECEF[t, 2],
            )

            lat_LP_OHB[t], long_LP_OHB[t], alt_LP_OHB[t] = _MATS_coordinates.ECEF2lla(
                r_LP_OHB_ECEF[t, 0], r_LP_OHB_ECEF[t, 1], r_LP_OHB_ECEF[t, 2]
            )

            # R_earth_MATS[t][t] = norm(r_MATS_OHB[t,:]*1000)-alt_MATS_OHB[t]

            Time_MPL_OHB[t] = date2num(Time_OHB[-1])

    "######### END OF OHB DATA CALCULATIONS #########################"
    "#####################################################################################"

    "########################## STK DATA ################################################"
    "####################################################################################"

    Time_STK = []
    if not (STK_CSV_FILE == ""):
        Logger.info("Calculations of STK Data")
        with open(STK_CSV_FILE) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            # interestingrows=[row for idx, row in enumerate(csv_reader) if idx in range(start_from,100000)]

            row_count = sum(1 for row in csv_reader) - 1

            r_MATS_STK_km = zeros((row_count, 3))
            Vel_MATS_STK = zeros((row_count, 3))

            r_MATS_STK_ECEF = zeros((row_count, 3))

        with open(STK_CSV_FILE) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            line_count = 0
            for row in csv_reader:

                if line_count == 0:

                    line_count += 1

                # elif( row_count % timestep != 0):
                #    row_count += 1
                else:
                    try:
                        r_MATS_STK_km[line_count - 1, 0] = row[0]
                        r_MATS_STK_km[line_count - 1, 1] = row[1]
                        r_MATS_STK_km[line_count - 1, 2] = row[2]

                        Vel_MATS_STK[line_count - 1, 0] = row[3]
                        Vel_MATS_STK[line_count - 1, 1] = row[4]
                        Vel_MATS_STK[line_count - 1, 2] = row[5]

                        Time_STK.append(
                            datetime.datetime.strptime(row[6], "%d %b %Y %H:%M:%S.%f")
                        )

                        line_count += 1
                    except IndexError:
                        break

        Time_MPL_STK = date2num(Time_STK[:])

        x_MATS_error_STK = []
        y_MATS_error_STK = []
        z_MATS_error_STK = []
        total_r_MATS_error_STK = []
        Time_error_STK_MPL = []

        "Calculate error between STK DATA and Predicted from Science Mode Timeline data when timestamps are the same"
        for t2 in range(len(Time_STK)):

            (
                r_MATS_STK_ECEF[t2, 0],
                r_MATS_STK_ECEF[t2, 1],
                r_MATS_STK_ECEF[t2, 2],
            ) = _MATS_coordinates.eci2ecef(
                r_MATS_STK_km[t2, 0] * 1000,
                r_MATS_STK_km[t2, 1] * 1000,
                r_MATS_STK_km[t2, 2] * 1000,
                Time_STK[t2],
            )

            for t in range(len(Time)):

                if Time_MPL_STK[t2] == Time_MPL[t]:

                    x_MATS_error_STK.append(
                        abs(Data_MATS["r_MATS_ECEF [m]"][t, 0] - r_MATS_STK_ECEF[t2, 0])
                    )
                    y_MATS_error_STK.append(
                        abs(Data_MATS["r_MATS_ECEF [m]"][t, 1] - r_MATS_STK_ECEF[t2, 1])
                    )
                    z_MATS_error_STK.append(
                        abs(Data_MATS["r_MATS_ECEF [m]"][t, 2] - r_MATS_STK_ECEF[t2, 2])
                    )
                    total_r_MATS_error_STK.append(
                        norm(
                            (
                                x_MATS_error_STK[len(x_MATS_error_STK) - 1],
                                y_MATS_error_STK[len(y_MATS_error_STK) - 1],
                                z_MATS_error_STK[len(z_MATS_error_STK) - 1],
                            )
                        )
                    )

                    Time_error_STK_MPL.append(Time_MPL_STK[t2])
                    break

        fig = figure()
        plot_date(Time_error_STK_MPL[:], x_MATS_error_STK[:], markersize=1, label="x")
        plot_date(Time_error_STK_MPL[:], y_MATS_error_STK[:], markersize=1, label="y")
        plot_date(Time_error_STK_MPL[:], z_MATS_error_STK[:], markersize=1, label="z")
        xlabel("Date")
        ylabel("Meters")
        title("Absolute error in ECEF position of MATS in m (prediction vs STK data")
        legend()
        figurePath = os.path.join(figureDirectory, "PosErrorMATS_STK")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    "########################## End of STK DATA ################################################"
    "####################################################################################"

    "########################## Plotter ###########################################"
    "##############################################################################"

    from mpl_toolkits.mplot3d import axes3d

    fig = figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim3d(-7000000, 7000000)
    ax.set_ylim3d(-7000000, 7000000)
    ax.set_zlim3d(-7000000, 7000000)
    GravParameter = 3.986 * 10 ** 14
    OrbitalPeriod = (
        2 * pi * sqrt((Data_MATS["alt_MATS [m]"][0] + 6371000) ** 3 / GravParameter)
    )
    DataTo = int(OrbitalPeriod * (3 / 4) / (Time[1] - Time[0]).total_seconds())
    ax.scatter(
        Data_MATS["r_MATS_ECEF [m]"][1:DataTo, 0],
        Data_MATS["r_MATS_ECEF [m]"][1:DataTo, 1],
        Data_MATS["r_MATS_ECEF [m]"][1:DataTo, 2],
        label="MATS",
    )
    ax.scatter(
        Data_LP["r_LP_ECEF [m]"][1:DataTo, 0],
        Data_LP["r_LP_ECEF [m]"][1:DataTo, 1],
        Data_LP["r_LP_ECEF [m]"][1:DataTo, 2],
        label="LP",
    )
    title(
        "Positional data in m (ECEF) from Science Mode Timeline of LP and MATS for 3/4 of an orbit"
    )
    legend()

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_MATS["ScienceMode"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    xlabel("Date")
    ylabel("Active ScienceMode")
    legend()
    figurePath = os.path.join(figureDirectory, "ActiveScienceMode")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    """
    figure()
    scatter(Time[:], Data_MATS['yaw_MATS [degrees]'][:], s=10, c=Data_MATS['ColorRGB'], label = 'Predicted from Science Mode Timeline')
    #scatter(Time_OHB[:],Euler_angles_SLOF_OHB[:,0], s=10, c='r', marker="x", label = 'OHB-Data')
    xlabel('Date')
    ylabel('Yaw in degrees [z-axis SLOF]')
    legend()
    
    """

    """
    from pylab import plt
    fig, axs = plt.subplots(1, 1)
    scatter(Time[:], Data_MATS['yaw_MATS [degrees]'][:], s=10, c=Data_MATS['ColorRGB'], label = 'Predicted from Science Mode Timeline')
    #scatter(Time_OHB[:],Euler_angles_SLOF_OHB[:,0], s=10, c='r', marker="x", label = 'OHB-Data')
    xlabel('Date')
    ylabel('Yaw in degrees [z-axis SLOF]')
    legend()
    """

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_MATS["yaw_MATS [degrees]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    plot_date(
        Time_MPL_OHB[:], Euler_angles_SLOF_OHB[:, 0], markersize=1, label="OHB-H5-Data"
    )
    plot_date(
        Time_MPL[:],
        Data_MATS["Yaw_function [degrees]"][:],
        markersize=1,
        label="Yaw-function (without attitude freezes)",
    )
    xlabel("Date")
    ylabel("Degrees")
    title("Yaw of optical-axis [z-axis SLOF (towards earth)]")
    legend()
    figurePath = os.path.join(figureDirectory, "Yaw")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_MATS["pitch_MATS [degrees]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    plot_date(
        Time_MPL_OHB[:], Euler_angles_SLOF_OHB[:, 1], markersize=1, label="OHB-H5-Data"
    )
    xlabel("Date")
    ylabel("Degrees")
    title("Pitch of optical-axis [intrinsic y-axis SLOF]")
    legend()
    figurePath = os.path.join(figureDirectory, "Pitch")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_MATS["roll_MATS [degrees]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    plot_date(
        Time_MPL_OHB[:], Euler_angles_SLOF_OHB[:, 2], markersize=1, label="OHB-H5-Data"
    )
    xlabel("Date")
    ylabel("Degrees")
    ylabel("Roll of optical-axis [intrinsic z-axis SLOF]")
    legend()
    figurePath = os.path.join(figureDirectory, "Roll")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    ###################################

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_MATS["lat_MATS [degrees]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    plot_date(Time_MPL_OHB[:], lat_MATS_OHB[:], markersize=1, label="OHB-H5-Data")
    xlabel("Date")
    ylabel("Degrees")
    title("Geodetic Latitude of MATS")
    legend()
    figurePath = os.path.join(figureDirectory, "Lat")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    """
    for t in range(len(lat_MATS_STK_FIXED)):
        abs_lat_MATS_error_STK[t] = abs( lat_MATS_STK_FIXED[t] - Data_MATS['lat_MATS [degrees]'][t] )
        abs_lat_MATS_error_OHB[t] = abs( lat_MATS_OHB[t] - Data_MATS['lat_MATS [degrees]'][t] )
        
        abs_long_MATS_error_STK[t] = abs( long_MATS_STK_FIXED[t] - Data_MATS['long_MATS [degrees]'][t] )
        abs_long_MATS_error_OHB[t] = abs( long_MATS_OHB[t] - Data_MATS['long_MATS [degrees]'][t] )
    
    
    fig = figure()
    plot_date(current_time_MPL_STK[1:], abs_lat_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs STK')
    plot_date(Time_MPL_OHB[1:], abs_lat_MATS_error_OHB[1:], markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Latitude of MATS (Fixed) in degrees')
    legend()
    """

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_MATS["long_MATS [degrees]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    # plot_date(current_time_MPL_STK[1:], long_MATS_STK_FIXED[1:], markersize = 1, label = 'STK-Data_Fixed')
    plot_date(Time_MPL_OHB[:], long_MATS_OHB[:], markersize=1, label="OHB-H5-Data")
    xlabel("Date")
    ylabel("Degrees")
    title("Longitude of MATS in degrees")
    legend()
    figurePath = os.path.join(figureDirectory, "Long")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    """
    fig = figure()
    plot_date(current_time_MPL[1:], abs_long_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs STK')
    plot_date(Time_MPL_OHB[1:], abs_long_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Longitude of MATS (Fixed) in degrees')
    legend()
    """

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_MATS["alt_MATS [m]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    plot_date(Time_MPL_OHB[:], alt_MATS_OHB[:], markersize=1, label="OHB-H5-Data")
    xlabel("Date")
    ylabel("Meters")
    title("Altitude of MATS")
    legend()
    figurePath = os.path.join(figureDirectory, "Alt")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    fig = figure()
    plot_date(
        Time_MPL_OHB[:],
        abs(r_MATS_OHB_ECEF[:, 0] - r_MATS_OHB_ECEFdata[:, 0]),
        markersize=1,
        label="X",
    )
    plot_date(
        Time_MPL_OHB[:],
        abs(r_MATS_OHB_ECEF[:, 1] - r_MATS_OHB_ECEFdata[:, 1]),
        markersize=1,
        label="Y",
    )
    plot_date(
        Time_MPL_OHB[:],
        abs(r_MATS_OHB_ECEF[:, 2] - r_MATS_OHB_ECEFdata[:, 2]),
        markersize=1,
        label="Z",
    )
    xlabel("Date")
    ylabel("Meters")
    title(
        "Absolute error in ECEF positional data from h5 and converted J2000 data from h5 into ECEF"
    )
    legend()
    figurePath = os.path.join(figureDirectory, "ECEFerror")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    ####################################

    "Allocate variables for error calculations between OHB data and predictions"
    total_r_MATS_error_OHB = []
    x_MATS_error_OHB = []
    y_MATS_error_OHB = []
    z_MATS_error_OHB = []

    total_r_LP_error_OHB = []
    x_LP_error_OHB = []
    y_LP_error_OHB = []
    z_LP_error_OHB = []

    r_MATS_error_OHB_Radial = []
    r_MATS_error_OHB_CrossTrack = []
    r_MATS_error_OHB_InTrack = []
    total_r_MATS_error_OHB_RCI = []

    r_LP_error_OHB_Radial = []
    r_LP_error_OHB_CrossTrack = []
    r_LP_error_OHB_InTrack = []
    total_r_LP_error_OHB_RCI = []

    alt_LP_error = []

    optical_axis_Dec_ERROR = []
    optical_axis_RA_ERROR = []

    Time_error_MPL = []

    if OHB_H5_Path != "":
        "Calculate error between OHB DATA and Predicted from Science Mode Timeline data when timestamps are the same"
        for t2 in range(timesteps):

            for t in range(len(Time)):

                if Time_MPL_OHB[t2] == Time_MPL[t]:

                    x_MATS_error_OHB.append(
                        abs(Data_MATS["r_MATS_ECEF [m]"][t, 0] - r_MATS_OHB_ECEF[t2, 0])
                    )
                    y_MATS_error_OHB.append(
                        abs(Data_MATS["r_MATS_ECEF [m]"][t, 1] - r_MATS_OHB_ECEF[t2, 1])
                    )
                    z_MATS_error_OHB.append(
                        abs(Data_MATS["r_MATS_ECEF [m]"][t, 2] - r_MATS_OHB_ECEF[t2, 2])
                    )
                    total_r_MATS_error_OHB.append(
                        norm(
                            (
                                x_MATS_error_OHB[len(x_MATS_error_OHB) - 1],
                                y_MATS_error_OHB[len(y_MATS_error_OHB) - 1],
                                z_MATS_error_OHB[len(z_MATS_error_OHB) - 1],
                            )
                        )
                    )

                    x_LP_error_OHB.append(
                        abs(Data_LP["r_LP_ECEF [m]"][t, 0] - r_LP_OHB_ECEF[t2, 0])
                    )
                    y_LP_error_OHB.append(
                        abs(Data_LP["r_LP_ECEF [m]"][t, 1] - r_LP_OHB_ECEF[t2, 1])
                    )
                    z_LP_error_OHB.append(
                        abs(Data_LP["r_LP_ECEF [m]"][t, 2] - r_LP_OHB_ECEF[t2, 2])
                    )
                    total_r_LP_error_OHB.append(
                        norm(
                            (
                                x_LP_error_OHB[len(x_LP_error_OHB) - 1],
                                y_LP_error_OHB[len(y_LP_error_OHB) - 1],
                                z_LP_error_OHB[len(z_LP_error_OHB) - 1],
                            )
                        )
                    )

                    alt_LP_error.append(Data_LP["alt_LP [m]"][t] - alt_LP_OHB[t2])

                    optical_axis_Dec_ERROR.append(
                        abs(Data_MATS["optical_axis_Dec [degrees]"][t] - Dec_OHB[t2])
                    )
                    optical_axis_RA_ERROR.append(
                        abs(Data_MATS["optical_axis_RA [degrees]"][t] - RA_OHB[t2])
                    )

                    # in_track = cross( normal_orbit[t], r_MATS_unit_vector[t])
                    # r_MATS_unit_vector_ECEF = array( (Data_MATS['x_MATS_ECEF'][t], Data_MATS['y_MATS_ECEF'][t], Data_MATS['z_MATS_ECEF'][t]) )
                    # v_MATS_unit_vector_ECEF = array( (Data_MATS['vx_MATS_ECEF'][t], Data_MATS['vy_MATS_ECEF'][t], Data_MATS['vz_MATS_ECEF'][t]) ) / norm( array( (Data_MATS['vx_MATS_ECEF'][t], Data_MATS['vy_MATS_ECEF'][t], Data_MATS['vz_MATS_ECEF'][t]) ) )

                    r_MATS_unit_vector_ECEF = Data_MATS["r_MATS_ECEF [m]"][t] / norm(
                        Data_MATS["r_MATS_ECEF [m]"][t]
                    )
                    v_MATS_unit_vector_ECEF = Data_MATS["v_MATS_ECEF [km/s]"][t] / norm(
                        Data_MATS["v_MATS_ECEF [km/s]"][t]
                    )

                    UnitVectorBasis_RCI = transpose(
                        array(
                            (
                                (
                                    r_MATS_unit_vector_ECEF[0],
                                    Data_MATS["r_normal_orbit_ECEF"][t, 0],
                                    v_MATS_unit_vector_ECEF[0],
                                ),
                                (
                                    r_MATS_unit_vector_ECEF[1],
                                    Data_MATS["r_normal_orbit_ECEF"][t, 1],
                                    v_MATS_unit_vector_ECEF[1],
                                ),
                                (
                                    r_MATS_unit_vector_ECEF[2],
                                    Data_MATS["r_normal_orbit_ECEF"][t, 2],
                                    v_MATS_unit_vector_ECEF[2],
                                ),
                            )
                        )
                    )

                    "The transpose of a matrix where the columns are basis vectors is a change of basis matrix"
                    dcm_change_of_basis_RCI = transpose(UnitVectorBasis_RCI)
                    r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_RCI)

                    r_MATS_error_OHB_RCI = r_change_of_basis_ECI_to_SLOF.apply(
                        (
                            (
                                x_MATS_error_OHB[len(x_MATS_error_OHB) - 1],
                                y_MATS_error_OHB[len(y_MATS_error_OHB) - 1],
                                z_MATS_error_OHB[len(z_MATS_error_OHB) - 1],
                            )
                        )
                    )

                    r_MATS_error_OHB_Radial.append(r_MATS_error_OHB_RCI[0])
                    r_MATS_error_OHB_CrossTrack.append(r_MATS_error_OHB_RCI[1])
                    r_MATS_error_OHB_InTrack.append(r_MATS_error_OHB_RCI[2])
                    total_r_MATS_error_OHB_RCI.append(norm(r_MATS_error_OHB_RCI))

                    r_LP_error_OHB_RCI = r_change_of_basis_ECI_to_SLOF.apply(
                        (
                            (
                                x_LP_error_OHB[len(x_LP_error_OHB) - 1],
                                y_LP_error_OHB[len(y_LP_error_OHB) - 1],
                                z_LP_error_OHB[len(z_LP_error_OHB) - 1],
                            )
                        )
                    )

                    r_LP_error_OHB_Radial.append(r_LP_error_OHB_RCI[0])
                    r_LP_error_OHB_CrossTrack.append(r_LP_error_OHB_RCI[1])
                    r_LP_error_OHB_InTrack.append(r_LP_error_OHB_RCI[2])
                    total_r_LP_error_OHB_RCI.append(norm(r_LP_error_OHB_RCI))

                    Time_error_MPL.append(Time_MPL[t])
                    break

        fig = figure()
        plot_date(Time_error_MPL[:], x_MATS_error_OHB[:], markersize=1, label="x")
        plot_date(Time_error_MPL[:], y_MATS_error_OHB[:], markersize=1, label="y")
        plot_date(Time_error_MPL[:], z_MATS_error_OHB[:], markersize=1, label="z")
        xlabel("Date")
        ylabel("Meters")
        title("Absolute error in ECEF position of MATS (prediction vs OHB h5 data")
        legend()
        figurePath = os.path.join(figureDirectory, "PosError")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

        fig = figure()
        plot_date(
            Time_error_MPL[:], r_MATS_error_OHB_Radial[:], markersize=1, label="Radial"
        )
        plot_date(
            Time_error_MPL[:],
            r_MATS_error_OHB_CrossTrack[:],
            markersize=1,
            label="Cross-track",
        )
        plot_date(
            Time_error_MPL[:],
            r_MATS_error_OHB_InTrack[:],
            markersize=1,
            label="Intrack",
        )
        xlabel("Date")
        ylabel("Meters")
        title(
            "Absolute error in ECEF position of MATS as RCI (prediction vs OHB h5 data"
        )
        legend()
        figurePath = os.path.join(figureDirectory, "PosErrorRCI")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

        fig = figure()
        plot_date(
            Time_error_MPL[:], total_r_MATS_error_OHB[:], markersize=1, label="XYZ"
        )
        plot_date(
            Time_error_MPL[:], total_r_MATS_error_OHB_RCI[:], markersize=1, label="RCI"
        )
        xlabel("Date")
        ylabel("Meters")
        title(
            "Magnitude of Absolute error in ECEF position of MATS (prediction vs OHB h5 data)"
        )
        legend()
        figurePath = os.path.join(figureDirectory, "MagPosError")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_LP["lat_LP [degrees]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    plot_date(Time_MPL_OHB[:], lat_LP_OHB[:], markersize=1, label="OHB-H5-Data")
    xlabel("Date")
    ylabel("Degrees")
    title("Latitude of LP")
    legend()
    figurePath = os.path.join(figureDirectory, "Lat_LP")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    """
    fig = figure()
    plot_date(Time_MPL_OHB[1:],abs(lat_LP_OHB[1:]-Data_LP['lat_LP [degrees]'][1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Latitude of LP in degrees [J2000]')
    legend()
    """

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_LP["long_LP [degrees]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    plot_date(Time_MPL_OHB[:], long_LP_OHB[:], markersize=1, label="OHB-H5-Data")
    xlabel("Date")
    ylabel("Degrees")
    title("Longitude of LP")
    legend()
    figurePath = os.path.join(figureDirectory, "Long_LP")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    """
    fig = figure()
    plot_date(current_time_MPL_STK[1:],abs(long_LP_STK[1:]-Data_LP['long_LP [degrees]'][1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(Time_MPL_OHB[1:],abs(long_LP_OHB[1:]-Data_LP['long_LP [degrees]'][1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Longitude of LP in degrees [J2000]')
    legend()
    """

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_LP["alt_LP [m]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    plot_date(Time_MPL_OHB[:], alt_LP_OHB[:], markersize=1, label="OHB-H5-Data")
    xlabel("Date")
    ylabel("Meters")
    title("Altitude of LP")
    legend()
    figurePath = os.path.join(figureDirectory, "Alt_LP")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    if OHB_H5_Path != "":
        fig = figure()
        plot_date(Time_error_MPL[:], alt_LP_error[:], markersize=1)
        xlabel("Date")
        ylabel("Meters")
        title("Error in Altitude of LP (prediction vs OHB-h5-data)")

        figurePath = os.path.join(figureDirectory, "AltError_LP")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

        fig = figure()
        plot_date(Time_error_MPL[:], x_LP_error_OHB[:], markersize=1, label="x")
        plot_date(Time_error_MPL[:], y_LP_error_OHB[:], markersize=1, label="y")
        plot_date(Time_error_MPL[:], z_LP_error_OHB[:], markersize=1, label="z")
        xlabel("Date")
        ylabel("Meters")
        title("Absolute error in ECEF position of LP (prediction vs OHB-h5-data)")
        legend()
        figurePath = os.path.join(figureDirectory, "PosError_LP")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

        fig = figure()
        plot_date(
            Time_error_MPL[:], r_LP_error_OHB_Radial[:], markersize=1, label="Radial"
        )
        plot_date(
            Time_error_MPL[:],
            r_LP_error_OHB_CrossTrack[:],
            markersize=1,
            label="Cross-track",
        )
        plot_date(
            Time_error_MPL[:], r_LP_error_OHB_InTrack[:], markersize=1, label="Intrack"
        )
        xlabel("Date")
        ylabel("Meters")
        title(
            "Absolute error in ECEF position of LP as RCI (prediction vs OHB-h5-data)"
        )
        legend()
        figurePath = os.path.join(figureDirectory, "PosErrorRCI_LP")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

        fig = figure()
        plot_date(Time_error_MPL[:], total_r_LP_error_OHB[:], markersize=1, label="XYZ")
        plot_date(
            Time_error_MPL[:], total_r_LP_error_OHB_RCI[:], markersize=1, label="RCI"
        )
        xlabel("Date")
        ylabel("Meters")
        title("Magnitude of Absolute error of LP ECEF position")
        legend()
        figurePath = os.path.join(figureDirectory, "MagPosError_LP")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_MATS["optical_axis_RA [degrees]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    plot_date(Time_MPL_OHB[:], RA_OHB[:], markersize=1, label="OHB-h5-Data")
    xlabel("Date")
    ylabel("Degrees")
    title("Right Ascension of optical axis [J2000] (Parallax assumed negligable)")
    legend()
    figurePath = os.path.join(figureDirectory, "RA_OpticalAxis")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    if OHB_H5_Path != "":
        fig = figure()
        plot_date(
            Time_error_MPL[:],
            optical_axis_RA_ERROR[:],
            markersize=1,
            label="Prediction vs OHB-h5-data",
        )
        xlabel("Date")
        ylabel("Degrees")
        title("Absolute error in Right Ascension [J2000] (Predicted vs OHB-h5-data)")
        legend()
        figurePath = os.path.join(figureDirectory, "RA_OpticalAxisError")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    fig = figure()
    plot_date(
        Time_MPL[:],
        Data_MATS["optical_axis_Dec [degrees]"][:],
        markersize=1,
        label="Predicted from Science Mode Timeline",
    )
    # plot_date(current_time_MPL_STK[1:],Dec_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(Time_MPL_OHB[:], Dec_OHB[:], markersize=1, label="OHB-h5-Data")
    xlabel("Date")
    ylabel("Degrees")
    title("Declination of optical axis [J2000] (Parallax assumed negligable)")
    legend()
    figurePath = os.path.join(figureDirectory, "Dec_OpticalAxis")
    pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    if OHB_H5_Path != "":
        fig = figure()
        plot_date(
            Time_error_MPL[:],
            optical_axis_Dec_ERROR[:],
            markersize=1,
            label="Prediction vs OHB-h5-data",
        )
        xlabel("Date")
        ylabel("Degrees")
        title("Absolute error in Declination [J2000] (Predicted vs OHB-h5-data)")
        legend()
        figurePath = os.path.join(figureDirectory, "Dec_OpticalAxisError")
        pickle.dump(fig, open(figurePath + ".fig.pickle", "wb"))

    "######## Save data to pickle files ##########"
    "################################################"
    DataPath = os.path.join(figureDirectory, "Data_MATS.data.pickle")
    f = open(DataPath, "wb")
    pickle.dump(Data_MATS, f)
    f.close()

    DataPath = os.path.join(figureDirectory, "Data_LP.data.pickle")
    f = open(DataPath, "wb")
    pickle.dump(Data_LP, f)
    f.close()

    DataPath = os.path.join(figureDirectory, "Time.data.pickle")
    f = open(DataPath, "wb")
    pickle.dump(Time, f)
    f.close()

    "#################################################"

    logging.shutdown()
    return Time_OHB

