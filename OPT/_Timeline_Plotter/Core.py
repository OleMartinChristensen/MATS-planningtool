# -*- coding: utf-8 -*-
"""
@author: David
"""

from scipy.spatial.transform import Rotation as R
from pylab import rcParams, savefig, scatter, pi, cross, array, arccos, arctan, dot, norm, transpose, zeros, sqrt, floor, figure, plot_date, datestr2num, xlabel, ylabel, title, legend, date2num
from skyfield.api import load, EarthSatellite
import ephem, logging, importlib, h5py, json, csv
import datetime, os, pickle

from OPT import _Library, _MATS_coordinates, _Globals


OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())

rcParams['figure.max_open_warning'] = 30


def Timeline_Plotter(Science_Mode_Path, OHB_H5_Path, STK_CSV_FILE, Timestep):
    """Core function of the Timeline_Plotter.
    
    Goes through the *Science Mode Timeline*, one mode at a time.
    
    Arguments:
        Science_Mode_Path (str): Path to the Science Mode Timeline to be plotted.
        OHB_H5_Path (str): Path to the .h5 file containing position, time, and attitude data.
        STK_CSV_PATH (str): Path to the .csv file containing position (column 1-3), velocity (column 4-6), and time (column 7), generated in STK. Position and velocity data is assumed to be in km and in ICRF.
        Timestep (int): The timestep used for the simulation and when accessing OHB data.
        
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
    Logger.info('Configuration File used: '+_Globals.Config_File+', Version: '+Version)
    
    "Get Timeline settings and TLE"
    Timeline_settings = OPT_Config_File.Timeline_settings()
    TLE = OPT_Config_File.getTLE()
    
    "Checks whether data from OHB as a .h5 file was given"
    if ( OHB_H5_Path == ''):
        Timestamp_fraction_of_second = 0
        timestep_OHB_data = 1
        OHB_StartTime = 0
        OHB_StartIndex = 0
        
        """
        #State_OHB = h5py.File('TM_acOnGnss_sep4.h5','r')['root']['TM_acOnGnss']
        #Time_State_OHB = State_OHB['acoOnGnssStateTime']['raw']
        #
        #OHB_StartIndex = 0
        #while( Time_State_OHB[OHB_StartIndex] == 0):
        #    OHB_StartIndex += 1
        #    
        #OHB_StartTime = ephem.Date(datetime.datetime(1980,1,6)+datetime.timedelta(seconds = float(Time_State_OHB[OHB_StartIndex])-18))
        """
        
    else:
        "Read data and check the timestamps"
        OHB_data = h5py.File(OHB_H5_Path,'r')
        root = OHB_data['root']
        Time_State_OHB = root['TM_acOnGnss']['acoOnGnssStateTime']['raw']
        Time_Attitude_OHB = root['afoTmMhObt']['raw']
        
        "Go through the data until the time is nonzero. That is where the data begins"
        OHB_StartIndex = 0
        while( Time_State_OHB[OHB_StartIndex] == 0):
            OHB_StartIndex += 1
            
        #OHB_StartIndex += 5000 
        
        if( abs(Time_Attitude_OHB[OHB_StartIndex] - Time_State_OHB[OHB_StartIndex]) > 1.1):
            Logger.error( 'Mismatch between timestamps of attitude and state')
            raise ValueError 
        
        
        
        "Parameters needed to allow synchronization of the science mode timeine simulation to the timestamps of the OHB data"
        Timestamp_fraction_of_second = Time_State_OHB[0]- int(Time_State_OHB[0])
        timestep_OHB_data = Time_State_OHB[1+OHB_StartIndex] - Time_State_OHB[OHB_StartIndex]
        "Synchronization will allow error values between the simulation and the OHB data to be calculated"
        Time_State_OHB_float = float(Time_State_OHB[OHB_StartIndex])
        OHB_StartTime = ephem.Date(datetime.datetime(1980,1,6)+datetime.timedelta(seconds = Time_State_OHB_float-18))
    
    
    "Create dictionaries to contain simulated data"
    Data_MATS = { 'ScienceMode': [], 'ColorRGB': [], 
                 'r_MATS': [], 'r_MATS_ECEF': [], 'v_MATS': [], 'v_MATS_ECEF': [], 
                 'r_normal_orbit': [], 'r_normal_orbit_ECEF': [], 
                 'lat_MATS': [], 'long_MATS': [], 'alt_MATS': [], 'yaw_MATS': [], 'pitch_MATS': [], 'roll_MATS': [], 
                 'r_optical_axis':[], 'r_optical_axis_ECEF': [], 'optical_axis_RA': [], 'optical_axis_Dec': []}

    Data_LP = { 'r_LP': [], 'r_LP_ECEF': [], 'lat_LP': [], 'long_LP': [], 'alt_LP': [] } 
    
    
    Time = []
    
    "################# Read Science Mode Timeline json file ############"
    with open(Science_Mode_Path, "r") as read_file:
        ScienceMode= json.load(read_file)
    "################# End of Read Science Mode Timeline json file ############"
    
    
    "######## START GOING THROUGH THE SCIENCE MODE TIMELINE #############"
    "Loop through Science Mode Timeline"
    for x in range(len(ScienceMode)):
        Logger.info('')
        Logger.info('Iteration number: '+str(x+1))
        Logger.info(str(ScienceMode[x][0]))
        
        "Skip the first entry and save it, if it only contains Timeline_settings used for the creation of the Science Mode Timeline"
        if(  ScienceMode[x][0] == 'Timeline_settings' ):
            Timeline_settings = ScienceMode[x][3]
            TLE = ScienceMode[x][4]
            continue
        
        Data_MATS, Data_LP, Time = Simulator( ScienceMode = ScienceMode[x], Timestamp_fraction_of_second = Timestamp_fraction_of_second, 
                                             Timestep = Timestep, Timeline_settings = Timeline_settings, TLE = TLE, Data_MATS = Data_MATS, 
                                             Data_LP = Data_LP, Time = Time, OHB_StartTime = OHB_StartTime )
        
    Logger.info('End of Simulation')
    
    
    
    "Convert the data from python lists into Numpy arrays"
    "Allows easier data manipulation"
    Data_MATS['lat_MATS'] = array( Data_MATS['lat_MATS'] )
    Data_MATS['long_MATS'] = array( Data_MATS['long_MATS'] )
    Data_MATS['alt_MATS'] = array( Data_MATS['alt_MATS'] )
    
    Data_MATS['r_MATS'] = array( Data_MATS['r_MATS'] )
    Data_MATS['r_MATS_ECEF'] = array( Data_MATS['r_MATS_ECEF'] )
    
    Data_MATS['r_normal_orbit'] = array( Data_MATS['r_normal_orbit'] )
    Data_MATS['r_normal_orbit_ECEF'] = array( Data_MATS['r_normal_orbit_ECEF'] )
    
    Data_MATS['v_MATS'] = array( Data_MATS['v_MATS'] )
    Data_MATS['v_MATS_ECEF'] = array( Data_MATS['v_MATS_ECEF'] )
    
    Data_MATS['r_optical_axis'] = array( Data_MATS['r_optical_axis'] )
    Data_MATS['r_optical_axis_ECEF'] = array( Data_MATS['r_optical_axis_ECEF'] )
    
    Data_MATS['yaw_MATS'] = array( Data_MATS['yaw_MATS'] )
    Data_MATS['pitch_MATS'] = array( Data_MATS['pitch_MATS'] )
    Data_MATS['roll_MATS'] = array( Data_MATS['roll_MATS'] )
    
    Data_MATS['optical_axis_RA'] = array( Data_MATS['optical_axis_RA'] )
    Data_MATS['optical_axis_Dec'] = array( Data_MATS['optical_axis_Dec'] )
    
    Data_LP['lat_LP'] = array( Data_LP['lat_LP'] )
    Data_LP['long_LP'] = array( Data_LP['long_LP'] )
    Data_LP['alt_LP'] = array( Data_LP['alt_LP'] )
    
    Data_LP['r_LP'] = array( Data_LP['r_LP'] )
    Data_LP['r_LP_ECEF'] = array( Data_LP['r_LP_ECEF'] )
    
    
    Time_OHB = Plotter( Data_MATS, Data_LP, Time, int(Timestep/timestep_OHB_data), OHB_StartIndex, OHB_H5_Path, STK_CSV_FILE, Science_Mode_Path)
    
    return Data_MATS, Data_LP, Time, Time_OHB





def Simulator( ScienceMode, Timestamp_fraction_of_second, Timestep, Timeline_settings, TLE, Data_MATS, Data_LP, Time, OHB_StartTime):
    """Subfunction, Simulates the position and attitude of MATS depending on the Mode given in *ScienceMode*.
    
    Appends the data during each timestep to *Data_MATS*, *Data_LP*, and *Time*.
    
    Arguments:
        ScienceMode (list): List containing the name of the Science Mode, the start_date, the end_date, and settings related to the Science Mode. 
        Timestamp_fraction_of_second (float): The fraction of a second timestamp for the data. Used here to synchronize timestamps between Timeline Simulation datapoints and OHB datapoints.
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
    Mode_start_date = ephem.Date( ephem.Date(ScienceMode[1]) + ephem.second * Timestamp_fraction_of_second )
    TimeDifferenceRest = round( (abs(Mode_start_date - OHB_StartTime) / ephem.second) % Timestep, 0 )
    
    if( TimeDifferenceRest == 0):
        StartingTimeRelative2StartOfMode = 0
    elif( Mode_start_date < OHB_StartTime):
        Mode_start_date = ephem.Date(Mode_start_date + ephem.second * TimeDifferenceRest )
        StartingTimeRelative2StartOfMode = TimeDifferenceRest
    else:
        Mode_start_date = ephem.Date(Mode_start_date + ephem.second * (Timestep-TimeDifferenceRest) )
        StartingTimeRelative2StartOfMode = (Timestep-TimeDifferenceRest)
    
    Mode_end_date = ephem.Date(ScienceMode[2])
    duration = (Mode_end_date - Mode_start_date) *24*3600
    #######################################################
    
    #############################################################
    "Determine the science mode, which in turn determines the behaviour of the simulation"
    if( ModeName == 'Mode120' or ModeName == 'Mode121' or ModeName == 'Mode122' or 
       ModeName == 'Mode123' or ModeName == 'Mode124'):
        Simulator_Select = 'Mode12X'
        freeze_start = Settings['freeze_start']
        freeze_duration = Settings['freeze_duration']
        pointing_altitude = Settings['pointing_altitude']
        freeze_flag = 0
        
        if( ModeName == 'Mode120'):
            Color = (0,1,0)
        elif( ModeName == 'Mode121'):
            Color = (0,1,0.5)
        elif( ModeName == 'Mode122'):
            Color = (0,1,1)
        elif( ModeName == 'Mode123'):
            Color = (0.5,0,0)
        elif( ModeName == 'Mode124'):
            Color = (0.5,0,0.5)
            
        
        
    elif( ModeName == 'Mode1' or ModeName == 'Mode2' or ModeName ==  'Mode5' ):
        Simulator_Select = 'ModeX'
        pointing_altitude = Timeline_settings['StandardPointingAltitude']
        
        if( ModeName == 'Mode1'):
            Color = (0,0,0.5)
        elif( ModeName == 'Mode2'):
            Color = (0,0,1)
        elif( ModeName == 'Mode5'):
            Color = (0,0.5,0)
        
        
        #elif( ModeName == 'Mode5'):
        #    Simulator_Select = 'ModeX'
        #    pointing_altitude = Settings['pointing_altitude']
        #    Color = (0,0.5,0)
        
    elif( ModeName == 'Mode130' or ModeName == 'Mode131' or ModeName == 'Mode132' or 
           ModeName == 'Mode133' or ModeName == 'Mode134' ):
        Simulator_Select = 'Mode13X'
        pointing_altitude = Settings['pointing_altitude']
        
        
        if( ModeName == 'Mode130'):
            Color = (0.5,0,1)
        elif( ModeName == 'Mode131'):
            Color = (0.5,0.5,0)
        elif( ModeName == 'Mode132'):
            Color = (0.5,0.5,0.5)
        elif( ModeName == 'Mode133'):
            Color = (0.5,0.5,1)
        elif( ModeName == 'Mode134'):
            Color = (0.5,1,0)
        
        
    elif( ModeName == 'Mode100' ):
        Simulator_Select = 'Mode100'
        pointing_altitude = Settings['pointing_altitude_from']
        pointing_altitude_to = Settings["pointing_altitude_to"]
        pointing_altitude_interval = Settings["pointing_altitude_interval"]
        NumberOfCMDStepsForEachAltitude = 9
        pointing_duration = Settings["pointing_duration"] + Timeline_settings['pointing_stabilization'] + NumberOfCMDStepsForEachAltitude * Timeline_settings['CMD_separation']
        timestamp_change_of_pointing_altitude = pointing_duration
        Color = (0,0.5,0.5)
        
    elif( ModeName == 'Mode110'):
        Simulator_Select = 'Mode110'
        pointing_altitude = Settings['pointing_altitude_from']
        pointing_altitude_to = Settings['pointing_altitude_to']
        sweep_rate = Settings['sweep_rate']
        pointing_stabilization = Timeline_settings['pointing_stabilization']
        CMD_separation = Timeline_settings['CMD_separation']
        Color = (0,0.5,0.1)
        
    else:
        return Data_MATS, Data_LP, Time
    ############################################################################
    
    
        
    "Simulation length"
    timesteps = int(floor(duration / Timestep))+1
    log_timestep = 1800
    #timesteps = 10000
    
    "Pre-allocate space"
    lat_MATS = zeros((timesteps,1))
    long_MATS = zeros((timesteps,1))
    alt_MATS = zeros((timesteps,1))
    r_MATS = zeros((timesteps,3))
    r_MATS_unit_vector = zeros((timesteps,3))
    r_MATS_ECEF = zeros((timesteps,3))
    v_MATS = zeros((timesteps,3))
    v_MATS_ECEF = zeros((timesteps,3))
    v_MATS_unit_vector = zeros((timesteps,3))
    normal_orbit = zeros((timesteps,3))
    lat_LP_estimated = zeros((timesteps,1))
    
    optical_axis = zeros((timesteps,3))
    optical_axis_ECEF = zeros((timesteps,3))
    
    r_LP = zeros((timesteps,3))
    r_LP_ECEF = zeros((timesteps,3))
    
    r_V_offset_normal = zeros((timesteps,3))
    r_H_offset_normal = zeros((timesteps,3))
    
    MATS_P = zeros((timesteps,1))
    yaw_offset_angle = zeros((timesteps,1))
    pitch_MATS = zeros((timesteps,1))
    roll_MATS = zeros((timesteps,1))
    Euler_angles = zeros((timesteps,3))
    z_SLOF = zeros((timesteps,3))
    
    RA_optical_axis = zeros((timesteps,1))
    Dec_optical_axis = zeros((timesteps,1))
    
    lat_LP = zeros((timesteps,1))
    long_LP = zeros((timesteps,1))
    alt_LP = zeros((timesteps,1))
    normal_orbit = zeros((timesteps,3))
    normal_orbit_ECEF = zeros((timesteps,3))
    current_time = zeros((timesteps,1))
    
    
    MATS_skyfield = EarthSatellite(TLE[0], TLE[1])
    
    ###################################################################################
    "Start of Simulation"
    for t in range(timesteps):
        
        t = t
        
        if( Simulator_Select == 'Mode100' ):
            "Increment the pointing altitude as defined by Mode100"
            if( t*Timestep+StartingTimeRelative2StartOfMode >= timestamp_change_of_pointing_altitude and pointing_altitude_to > pointing_altitude ):
                pointing_altitude += pointing_altitude_interval
                timestamp_change_of_pointing_altitude += pointing_duration 
        elif( Simulator_Select == 'Mode110' ):
            "Perform sweep as defined by Mode110"
            "Check if the sweep is positive or negative"
            if( sweep_rate > 0 ):
                if( t*Timestep+StartingTimeRelative2StartOfMode > pointing_stabilization + 11 * CMD_separation and pointing_altitude_to > pointing_altitude):
                    pointing_altitude += sweep_rate * Timestep
                elif( pointing_altitude_to <= pointing_altitude):
                    pointing_altitude = pointing_altitude_to
            elif( sweep_rate < 0 ):
                if( t*Timestep+StartingTimeRelative2StartOfMode > pointing_stabilization + 11 * CMD_separation and pointing_altitude_to < pointing_altitude):
                    pointing_altitude += sweep_rate * Timestep
                elif( pointing_altitude_to >= pointing_altitude):
                    pointing_altitude = pointing_altitude_to
        
        elif( Simulator_Select == 'Mode12X' and t*Timestep+StartingTimeRelative2StartOfMode >= freeze_duration+freeze_start):
            "Looking at StandardPointingAltitude after attitude freeze for Mode12X"
            pointing_altitude = Timeline_settings['StandardPointingAltitude']
        ############Looking at pointing_altitude##############"
        else:
            "Looking at pointing_altitude"
            pass
            
        
        "Increment Time"
        current_time = ephem.Date(Mode_start_date+ephem.second*(Timestep*t))
        current_time_datetime = ephem.Date(current_time).datetime()
        
        "Only log data at certain intervals depending on log_timestep"
        if( t*Timestep % log_timestep == 0):
            LogFlag = True
        else:
            LogFlag = False
        
        "Run the satellite simulation for the current time"
        Satellite_dict = _Library.Satellite_Simulator( 
                    MATS_skyfield, current_time, Timeline_settings, pointing_altitude/1000, LogFlag, Logger )
        
        "Save results"
        r_MATS[t] = Satellite_dict['Position [km]']
        v_MATS[t] = Satellite_dict['Velocity [km/s]']
        normal_orbit[t] = Satellite_dict['OrbitNormal']
        r_V_offset_normal[t] = Satellite_dict['Normal2V_offset']
        r_H_offset_normal[t] = Satellite_dict['Normal2H_offset']
        MATS_P[t] = Satellite_dict['OrbitalPeriod [s]']
        alt_MATS[t] = Satellite_dict['Altitude [km]']
        lat_MATS[t] =  Satellite_dict['Latitude [degrees]']
        long_MATS[t] =  Satellite_dict['Longitude [degrees]']
        optical_axis[t] = Satellite_dict['OpticalAxis']
        Dec_optical_axis[t] = Satellite_dict['Dec_OpticalAxis [degrees]']
        RA_optical_axis[t] = Satellite_dict['RA_OpticalAxis [degrees]']
        pitch_MATS[t] = Satellite_dict['Pitch [degrees]']
        lat_LP_estimated[t] = Satellite_dict['EstimatedLatitude_LP [degrees]']
        
        v_MATS_unit_vector[t,0:3] = v_MATS[t,0:3] / norm(v_MATS[t,0:3])
        r_MATS_unit_vector[t,0:3] = r_MATS[t,0:3] / norm(r_MATS[t,0:3])
        
        "Coordinate transformations and calculations"
        r_MATS_ECEF[t,0], r_MATS_ECEF[t,1], r_MATS_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                r_MATS[t,0]*1000, r_MATS[t,1]*1000, r_MATS[t,2]*1000, current_time_datetime)
        
        optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                optical_axis[t,0], optical_axis[t,1], optical_axis[t,2], current_time_datetime)
        
        
        r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0], r_MATS_ECEF[t][1], r_MATS_ECEF[t][2], 
                                   optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
        
        lat_LP[t], long_LP[t], alt_LP[t]  = _MATS_coordinates.ECEF2lla(r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2])
        
        
        r_LP[t,0], r_LP[t,1], r_LP[t,2] = _MATS_coordinates.ecef2eci( r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2], 
                                       current_time_datetime)
        
        v_MATS_ECEF[t,0], v_MATS_ECEF[t,1], v_MATS_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                v_MATS[t,0], v_MATS[t,1], v_MATS[t,2], current_time_datetime)
        
        normal_orbit_ECEF[t,0], normal_orbit_ECEF[t,1], normal_orbit_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                normal_orbit[t,0], normal_orbit[t,1], normal_orbit[t,2], current_time_datetime)
        
        
        #orbangle_between_LP_MATS_array_dotproduct[t] = arccos( dot(r_MATS_unit_vector[t], r_LP[t]) / norm(r_LP[t]) ) / pi*180
        
        
        "Freezing the attitude"
        #if( Simulator_Select == 'Mode12X' and t*Timestep+Timestep > freeze_start and t*Timestep <= freeze_duration+freeze_start):
        if( Simulator_Select == 'Mode12X' and t*Timestep+StartingTimeRelative2StartOfMode > freeze_start and t*Timestep+StartingTimeRelative2StartOfMode <= freeze_duration+freeze_start):
            "Save the pointing for the exact time when attitude freeze is initiated"
            if( freeze_flag == 0):
                
                "Exact timing of Attitude freeze"
                current_time_freeze = ephem.Date(ephem.Date(ScienceMode[1])+ephem.second*(freeze_start))
                
                
                "Run the satellite simulation for the freeze time"
                Satellite_dict = _Library.Satellite_Simulator( 
                            MATS_skyfield, current_time_freeze, Timeline_settings, pointing_altitude/1000, LogFlag, Logger )
                
                "Save results"
                r_V_offset_normal_Freeze = Satellite_dict['Normal2V_offset']
                r_H_offset_normal_Freeze = Satellite_dict['Normal2H_offset']
                optical_axis_Freeze = Satellite_dict['OpticalAxis']
                
            freeze_flag = 1
            
           
            
            "Maintain the same optical axis as the simulation progresses"
            optical_axis[t,:] = optical_axis_Freeze
            optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                    optical_axis[t,0], optical_axis[t,1], optical_axis[t,2], current_time_datetime)
            
            r_V_offset_normal[t,:] = r_V_offset_normal_Freeze
            r_H_offset_normal[t,:] = r_H_offset_normal_Freeze
            
            r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0], r_MATS_ECEF[t][1], r_MATS_ECEF[t][2], 
                                   optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
            
            lat_LP[t], long_LP[t], alt_LP[t]  = _MATS_coordinates.ECEF2lla(r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2])
            
            r_LP[t,0], r_LP[t,1], r_LP[t,2] = _MATS_coordinates.ecef2eci( r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2], 
                                               current_time_datetime)
            
            Dec_optical_axis[t] = arctan( optical_axis[t,2] / sqrt(optical_axis[t,0]**2 + optical_axis[t,1]**2) ) /pi * 180
            RA_optical_axis[t] = arccos( dot( [1,0,0], [optical_axis[t,0],optical_axis[t,1],0] ) / norm([optical_axis[t,0],optical_axis[t,1],0]) ) / pi * 180
            
            if( optical_axis[t,1] < 0 ):
                RA_optical_axis[t] = 360-RA_optical_axis[t]
            
        
        "Define SLOF basis and convert ECI coordinates to SLOF"
        z_SLOF = -r_MATS[t,:]
        #z_SLOF = -r_MATS[t,0:3]
        z_SLOF = z_SLOF / norm(z_SLOF)
        y_SLOF = -normal_orbit[t,:]
        y_SLOF = y_SLOF / norm(y_SLOF)
        x_SLOF = v_MATS[t,:]
        x_SLOF = x_SLOF / norm(x_SLOF)
        
        "A change of basis matrix is calculated from the transpose of a matrix where the columns are the basis vectors"
        dcm_SLOF_coordinate_system = array( ([x_SLOF[0], y_SLOF[0], z_SLOF[0]], [x_SLOF[1], y_SLOF[1], z_SLOF[1]], [x_SLOF[2], y_SLOF[2], z_SLOF[2]]) )
        dcm_change_of_basis_ECI_to_SLOF = transpose(dcm_SLOF_coordinate_system)
        r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_ECI_to_SLOF)
    
        optical_axis_SLOF = r_change_of_basis_ECI_to_SLOF.apply( optical_axis[t,:])
        r_V_offset_normal_SLOF = r_change_of_basis_ECI_to_SLOF.apply( r_V_offset_normal[t,:] )
        r_H_offset_normal_SLOF = r_change_of_basis_ECI_to_SLOF.apply( r_H_offset_normal[t,:] )
        
        
        "Find rotation and Euler angles from definition of optical axis in SLOF"
        basis_SBF = array( ( (optical_axis_SLOF), (r_V_offset_normal_SLOF), (r_H_offset_normal_SLOF) ) )
        basis_SLOF = array( ( (0,0,-1), (0,1,0), (1,0,0) ) )
        rotation, sensitivity_matrix = R.match_vectors(basis_SBF, basis_SLOF)
        
        Euler_angles[t,:] = rotation.as_euler('ZYZ', degrees=True)
        yaw_offset_angle[t] = Euler_angles[t,0]
        pitch_MATS[t] = Euler_angles[t,1]
        roll_MATS[t] = Euler_angles[t,2]
        
        "Save data"
        Data_MATS['ScienceMode'].append(ModeName)
        Data_MATS['ColorRGB'].append(Color)
        
        Data_MATS['lat_MATS'].append(lat_MATS[t])
        Data_MATS['long_MATS'].append(long_MATS[t])
        Data_MATS['alt_MATS'].append(alt_MATS[t]*1000)
        
        Data_MATS['r_MATS'].append(r_MATS[t]*1000)
        Data_MATS['r_MATS_ECEF'].append(r_MATS_ECEF[t])
        
        Data_MATS['r_normal_orbit'].append(normal_orbit[t])
        Data_MATS['r_normal_orbit_ECEF'].append(normal_orbit_ECEF[t])
        
        Data_MATS['v_MATS'].append(v_MATS[t])
        Data_MATS['v_MATS_ECEF'].append(v_MATS_ECEF[t])
        
        Data_MATS['r_optical_axis'].append(optical_axis[t])
        Data_MATS['r_optical_axis_ECEF'].append(optical_axis_ECEF[t])
        
        Data_MATS['yaw_MATS'].append(yaw_offset_angle[t])
        Data_MATS['pitch_MATS'].append(pitch_MATS[t])
        Data_MATS['roll_MATS'].append(roll_MATS[t])
        
        Data_MATS['optical_axis_RA'].append(RA_optical_axis[t])
        Data_MATS['optical_axis_Dec'].append(Dec_optical_axis[t])
        
        Data_LP['lat_LP'].append(lat_LP[t])
        Data_LP['long_LP'].append(long_LP[t])
        Data_LP['alt_LP'].append(alt_LP[t])
        
        Data_LP['r_LP'].append(r_LP[t])
        Data_LP['r_LP_ECEF'].append(r_LP_ECEF[t])
        
        
        Time.append(current_time_datetime)
    
    
    return Data_MATS, Data_LP, Time
    
  
    
    

    
def Plotter(Data_MATS, Data_LP, Time, DataIndexStep, OHB_StartIndex, OHB_H5_Path = '', STK_CSV_FILE = '', Science_Mode_Path = ''):
    """Subfunction, Performs calculations and plots the position and attitude data of MATS and LP.
    
    Performs calculations on the data given in the file located at *OHB_H5_Path* and plots the results. 
    Also plots the simulated data given in *Data_MATS* and *Data_LP* as a function of the 
    timestamps in *Time*. May also plot positional error compared to STK data, if *STK_CSV_FILE* is given.
    
    Arguments:
        Data_MATS (dict of lists): Dictionary containing lists of simulated data of MATS.
        Data_LP (dict of lists): Dictionary containing lists of simulated data of LP.
        Time (list): List containing timestamps (utc) of the simulated data in Data_MATS and Data_LP.
        DataIndexStep (int): The data index step size when going through the data given in *OHB_H5_Path*.
        OHB_StartIndex (int): The starting data index when going through the data given in *OHB_H5_Path*.
        OHB_H5_Path (str): Path to the .h5 file containing position, time, and attitude data. If the string is empty, only Science Mode Timeline data will be plotted.
        STK_CSV_PATH (str): Path to the .csv file containing position (column 1-3), velocity (column 4-6), and time (column 7), generated in STK. Position and velocity data is assumed to be in km and in ICRF.
        
    Returns:
        (list): **Time_OHB**, Timestamps (utc) of the OHB data.
        
    """
    
    
    
    
    Time_MPL = date2num(Time[:])
    
    ######## Try to Create a directory for storage of Timeline_Plotter plots and data files #######
    figureDirectory = os.path.join(Science_Mode_Path.strip('.json'), 'Timeline_Plotter_PlotsAndData')
    try:
        os.makedirs(figureDirectory)
    except:
        pass
    
    "############ OHB DATA Extraction #########################"
    "##############################################################################"
    if( OHB_H5_Path == ''):
        timesteps = 0
        OHB_StartIndex = 0
        
    elif( OHB_H5_Path != ''):
        OHB_data = h5py.File(OHB_H5_Path,'r')
        
        root = OHB_data['root']
        
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
        
        Time_State_OHB = root['TM_acOnGnss']['acoOnGnssStateTime']['raw']
        Time_Attitude_OHB = root['afoTmMhObt']['raw']
        
        
        
        
        "Make sure that the amount of timesteps is less than the available data"
        PossibleTimesteps = []
        
        timesteps = int( (len( x_MATS_OHB ) - OHB_StartIndex) / DataIndexStep )
        PossibleTimesteps.append(timesteps)
        
        timesteps = int( (len( quat1_MATS_OHB ) - OHB_StartIndex) / DataIndexStep )
        PossibleTimesteps.append(timesteps)
        
        timesteps = int( (len( Time_State_OHB ) - OHB_StartIndex) / DataIndexStep )
        PossibleTimesteps.append(timesteps)
        
        "The shortest data series determines the amount of timesteps"
        PossibleTimesteps.sort()
        timesteps = PossibleTimesteps[0]
        
        
        ###### !!!!!!!!!!!!!!!! ############
        FractionOfDataUsed = 1/3
        timesteps = int(timesteps*FractionOfDataUsed -1)
        input("Warning! Fraction of data used ("+str(round(FractionOfDataUsed,2))+")! Press enter to acknowledge.")
        ###### !!!!!!!!!!!!!!!! ############
        
        "To make sure there is enough data to support the amount of timesteps together with the DataIndexStep"
        if( len(Time_State_OHB) <= DataIndexStep*timesteps):
            timesteps = int(len(Time_State_OHB) / DataIndexStep)
        
    "#########################################################################"
    
    "Allocate Space"
    Time_MPL_OHB = zeros((timesteps,1))
    Time_OHB = []
    current_time_attitude = []
    
    lat_MATS_OHB = zeros((timesteps,1))
    long_MATS_OHB = zeros((timesteps,1))
    alt_MATS_OHB = zeros((timesteps,1))
    
    q1_MATS_OHB = zeros((timesteps,1))
    q2_MATS_OHB = zeros((timesteps,1))
    q3_MATS_OHB = zeros((timesteps,1))
    q4_MATS_OHB = zeros((timesteps,1))
    
    Vel_MATS_OHB = zeros((timesteps,3))
    r_MATS_OHB = zeros((timesteps,3))
    r_MATS_OHB_ECEF = zeros((timesteps,3))
    r_MATS_OHB_ECEF2 = zeros((timesteps,3))
    optical_axis_OHB = zeros((timesteps,3))
    r_LP_OHB_ECEF = zeros((timesteps,3))
    lat_LP_OHB = zeros((timesteps,1))
    long_LP_OHB = zeros((timesteps,1))
    alt_LP_OHB = zeros((timesteps,1))
    
    Dec_OHB = zeros((timesteps,1))
    RA_OHB = zeros((timesteps,1))
    
    Time_State_OHB_float = zeros((timesteps,1))
    Time_Attitude_OHB_float = zeros((timesteps,1))
    
    Euler_angles_SLOF_OHB = zeros((timesteps,3))
    Euler_angles_ECI_OHB = zeros((timesteps,3))
    
    optical_axis_OHB = zeros((timesteps,3))
    optical_axis_OHB_ECEF = zeros((timesteps,3))
    
    #ephemDate2MatplotDate = datestr2num('1899/12/31 12:00:00')
    
    "############################################################ "
    "############## OHB Data Calculations ###########"
    if( OHB_H5_Path != ''):
        
        Logger.info('Calculations of OHB Data')
        for t in range(timesteps):
            
            #t_OHB = round(t* DataIndexStep + OHB_StartIndex)
            t_OHB_state = round(t* DataIndexStep + OHB_StartIndex)
            
            "Timestamps of the attitude is assumed to be synchronized to the state"
            t_OHB_attitude = t_OHB_state
            
            Time_State_OHB_float[t] = float(Time_State_OHB[t_OHB_state])
            #Time_State_OHB_float[t] = float(Time_State_OHB[t_OHB])
            #Time_Attitude_OHB_float[t] = float(Time_Attitude_OHB[t_OHB])
            
            Time_OHB.append(datetime.datetime(1980,1,6)+datetime.timedelta(seconds = Time_State_OHB_float[t,0]-18) )
            
            #current_time_attitude.append(datetime.datetime(1980,1,6)+datetime.timedelta(seconds = Time_Attitude_OHB_float[t,0]-18) )
            
            
            
            r_MATS_OHB[t,0] = x_MATS_OHB[t_OHB_state] 
            r_MATS_OHB[t,1] = y_MATS_OHB[t_OHB_state] 
            r_MATS_OHB[t,2] = z_MATS_OHB[t_OHB_state] 
            
            Vel_MATS_OHB[t,0] = vel_x_MATS_OHB[t_OHB_state] 
            Vel_MATS_OHB[t,1] = vel_y_MATS_OHB[t_OHB_state] 
            Vel_MATS_OHB[t,2] = vel_z_MATS_OHB[t_OHB_state] 
            
            q1_MATS_OHB[t,0] = quat1_MATS_OHB[t_OHB_attitude]
            q2_MATS_OHB[t,0] = quat2_MATS_OHB[t_OHB_attitude]
            q3_MATS_OHB[t,0] = quat3_MATS_OHB[t_OHB_attitude]
            q4_MATS_OHB[t,0] = quat4_MATS_OHB[t_OHB_attitude]
            
            
            "SLOF = Spacecraft Local Orbit Frame"
            z_SLOF = -r_MATS_OHB[t,0:3]
            #z_SLOF = -r_MATS[t,0:3]
            z_SLOF = z_SLOF / norm(z_SLOF)
            x_SLOF = Vel_MATS_OHB[t,0:3]
            x_SLOF = x_SLOF / norm(x_SLOF)
            y_SLOF = cross(z_SLOF,x_SLOF)
            y_SLOF = y_SLOF / norm(y_SLOF)
            
            
            "Create change of coordinate matrix from ECI to SLOF"
            dcm_SLOF_coordinate_system = array( ([x_SLOF[0], y_SLOF[0], z_SLOF[0]], [x_SLOF[1], y_SLOF[1], z_SLOF[1]], [x_SLOF[2], y_SLOF[2], z_SLOF[2]]) )
            dcm_change_of_basis_ECI_to_SLOF = transpose(dcm_SLOF_coordinate_system)
            r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_ECI_to_SLOF)
            
            "Create Rotation from quaternions (ECI to SpaceCraft BodyFrame)"
            MATS_ECI_OHB = R.from_quat([q2_MATS_OHB[t,0], q3_MATS_OHB[t,0], q4_MATS_OHB[t,0], q1_MATS_OHB[t,0]])
           
            "Apply rotation to -z to get optical axis"
            optical_axis_OHB[t,:] = MATS_ECI_OHB.apply([0,0,-1])
            optical_axis_OHB[t,:] = optical_axis_OHB[t,:] / norm(optical_axis_OHB[t,:])
            
            "Caluclate RA and DEC of optical axis"
            Dec_OHB[t] = arctan( optical_axis_OHB[t,2] / sqrt(optical_axis_OHB[t,0]**2 + optical_axis_OHB[t,1]**2) ) /pi * 180
            RA_OHB[t] = arccos( dot( [1,0,0], [optical_axis_OHB[t,0],optical_axis_OHB[t,1],0] ) / norm([optical_axis_OHB[t,0],optical_axis_OHB[t,1],0]) ) / pi * 180
            if( optical_axis_OHB[t,1] < 0 ):
                RA_OHB[t] = 360-RA_OHB[t]
            
            
            Euler_angles_ECI_OHB[t,:] = MATS_ECI_OHB.as_euler('ZYZ', degrees=True)
            
            "Rotation multiplication to change the basis to SLOF, giving a rotation from SLOF to SPF"
            MATS_SLOF_OHB = r_change_of_basis_ECI_to_SLOF*MATS_ECI_OHB
            
            
            "Yaw, Pitch, Roll as Euler Angles"
            Euler_angles_SLOF_OHB[t,:] = MATS_SLOF_OHB.as_euler('ZYZ', degrees=True)
            
            optical_axis_OHB_ECEF[t,0], optical_axis_OHB_ECEF[t,1], optical_axis_OHB_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                        optical_axis_OHB[t,0], optical_axis_OHB[t,1], optical_axis_OHB[t,2], Time_OHB[t])
                
            optical_axis_OHB_ECEF[t,:] = optical_axis_OHB_ECEF[t,:] / norm(optical_axis_OHB_ECEF[t,:])
            
            
            
            r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                        r_MATS_OHB[t,0], r_MATS_OHB[t,1], r_MATS_OHB[t,2], Time_OHB[t])
            
            
            
            
            lat_MATS_OHB[t], long_MATS_OHB[t], alt_MATS_OHB[t] = _MATS_coordinates.ECEF2lla(r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2])
            
            r_LP_OHB_ECEF[t,0], r_LP_OHB_ECEF[t,1], r_LP_OHB_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2], 
                                           optical_axis_OHB_ECEF[t,0], optical_axis_OHB_ECEF[t,1], optical_axis_OHB_ECEF[t,2])
            
            lat_LP_OHB[t], long_LP_OHB[t], alt_LP_OHB[t]  = _MATS_coordinates.ECEF2lla(r_LP_OHB_ECEF[t,0], r_LP_OHB_ECEF[t,1], r_LP_OHB_ECEF[t,2])
            
            
            #R_earth_MATS[t][t] = norm(r_MATS_OHB[t,:]*1000)-alt_MATS_OHB[t]
            
            Time_MPL_OHB[t] = date2num(Time_OHB[t])
        
    "######### END OF OHB DATA CALCULATIONS #########################"
    "#####################################################################################"
    
    
    "########################## STK DATA ################################################"
    "####################################################################################"
    
    
    Time_STK = []
    if not( STK_CSV_FILE == "" ):
        Logger.info('Calculations of STK Data')
        with open(STK_CSV_FILE) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            #interestingrows=[row for idx, row in enumerate(csv_reader) if idx in range(start_from,100000)]
            
            row_count = sum(1 for row in csv_reader) - 1
            
            r_MATS_STK_km = zeros((row_count, 3))
            Vel_MATS_STK = zeros((row_count, 3))
            
            r_MATS_STK_ECEF = zeros((row_count, 3))
            
            
            
        with open(STK_CSV_FILE) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                
                if(line_count == 0):
                    
                    line_count += 1
                    
                #elif( row_count % timestep != 0):
                #    row_count += 1
                else:
                    try:
                        r_MATS_STK_km[line_count-1,0] = row[0]
                        r_MATS_STK_km[line_count-1,1] = row[1]
                        r_MATS_STK_km[line_count-1,2] = row[2]
                        
                        Vel_MATS_STK[line_count-1,0] = row[3]
                        Vel_MATS_STK[line_count-1,1] = row[4]
                        Vel_MATS_STK[line_count-1,2] = row[5]
                        
                        Time_STK.append( datetime.datetime.strptime(row[6], "%d %b %Y %H:%M:%S.%f") )
                        
                        line_count += 1
                    except IndexError:
                        break
                    
        
        
            
        
        Time_MPL_STK = date2num(Time_STK[:])
        
        x_MATS_error_STK = []
        y_MATS_error_STK = []
        z_MATS_error_STK = []
        total_r_MATS_error_STK = []
        Time_error_STK_MPL = []
        
        
        "Calculate error between STK DATA and predicted data when timestamps are the same"
        for t2 in range( len(Time_STK) ):
            
            r_MATS_STK_ECEF[t2,0], r_MATS_STK_ECEF[t2,1], r_MATS_STK_ECEF[t2,2] = _MATS_coordinates.eci2ecef(
                        r_MATS_STK_km[t2,0]*1000, r_MATS_STK_km[t2,1]*1000, r_MATS_STK_km[t2,2]*1000, Time_STK[t2])
            
            for t in range(len(Time)):
                
                if( Time_MPL_STK[t2] == Time_MPL[t] ):
                    
                    x_MATS_error_STK.append( abs(Data_MATS['r_MATS_ECEF'][t,0]-r_MATS_STK_ECEF[t2,0]) )
                    y_MATS_error_STK.append( abs(Data_MATS['r_MATS_ECEF'][t,1]-r_MATS_STK_ECEF[t2,1]) )
                    z_MATS_error_STK.append( abs(Data_MATS['r_MATS_ECEF'][t,2]-r_MATS_STK_ECEF[t2,2]) )
                    total_r_MATS_error_STK.append( norm( (x_MATS_error_STK[len(x_MATS_error_STK)-1], y_MATS_error_STK[len(y_MATS_error_STK)-1], z_MATS_error_STK[len(z_MATS_error_STK)-1]) ) )
                    
                    Time_error_STK_MPL.append( Time_MPL_STK[t2] )
                    break
                    
        fig = figure()
        plot_date(Time_error_STK_MPL[:],x_MATS_error_STK[:], markersize = 1, label = 'x')
        plot_date(Time_error_STK_MPL[:],y_MATS_error_STK[:], markersize = 1, label = 'y')
        plot_date(Time_error_STK_MPL[:],z_MATS_error_STK[:], markersize = 1, label = 'z')
        xlabel('Date')
        ylabel('Absolute error in ECEF position of MATS in m (prediction vs STK')
        legend()
        figurePath = os.path.join(figureDirectory, 'PosErrorMATS_STK')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
        
    "########################## End of STK DATA ################################################"
    "####################################################################################"
    
    
    
    
    
    "########################## Plotter ###########################################"
    "##############################################################################"
    
    from mpl_toolkits.mplot3d import axes3d
    
    
    fig=figure()
    ax = fig.add_subplot(111,projection='3d')
    ax.set_xlim3d(-7000000, 7000000)
    ax.set_ylim3d(-7000000, 7000000)
    ax.set_zlim3d(-7000000, 7000000)
    ax.scatter(Data_MATS['r_MATS_ECEF'][1:100,0], Data_MATS['r_MATS_ECEF'][1:100,1], Data_MATS['r_MATS_ECEF'][1:100,2])
    ax.scatter(Data_LP['r_LP_ECEF'][1:100,0], Data_LP['r_LP_ECEF'][1:100,1], Data_LP['r_LP_ECEF'][1:100,2])
    
    
    fig = figure()
    plot_date(Time_MPL[:], Data_MATS['ScienceMode'][:], markersize = 1, label = 'Predicted')
    xlabel('Date')
    ylabel('Active ScienceMode')
    legend()
    figurePath = os.path.join(figureDirectory, 'ActiveScienceMode')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
    """
    figure()
    scatter(Time[:], Data_MATS['yaw_MATS'][:], s=10, c=Data_MATS['ColorRGB'], label = 'Predicted')
    #scatter(Time_OHB[:],Euler_angles_SLOF_OHB[:,0], s=10, c='r', marker="x", label = 'OHB-Data')
    xlabel('Date')
    ylabel('Yaw in degrees [z-axis SLOF]')
    legend()
    
    """
    
    """
    from pylab import plt
    fig, axs = plt.subplots(1, 1)
    scatter(Time[:], Data_MATS['yaw_MATS'][:], s=10, c=Data_MATS['ColorRGB'], label = 'Predicted')
    #scatter(Time_OHB[:],Euler_angles_SLOF_OHB[:,0], s=10, c='r', marker="x", label = 'OHB-Data')
    xlabel('Date')
    ylabel('Yaw in degrees [z-axis SLOF]')
    legend()
    """
    
    fig = figure()
    plot_date(Time_MPL[:], Data_MATS['yaw_MATS'][:], markersize = 1, label = 'Predicted')
    plot_date(Time_MPL_OHB[:],Euler_angles_SLOF_OHB[:,0], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Yaw in degrees [z-axis SLOF]')
    legend()
    figurePath = os.path.join(figureDirectory, 'Yaw')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
    fig = figure()
    plot_date(Time_MPL[:], Data_MATS['pitch_MATS'][:] , markersize = 1, label = 'Predicted')
    plot_date(Time_MPL_OHB[:],Euler_angles_SLOF_OHB[:,1], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Pitch in degrees [intrinsic y-axis SLOF]')
    legend()
    figurePath = os.path.join(figureDirectory, 'Pitch')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
    fig = figure()
    plot_date(Time_MPL[:],Data_MATS['roll_MATS'][:], markersize = 1, label = 'Predicted')
    plot_date(Time_MPL_OHB[:],Euler_angles_SLOF_OHB[:,2], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Roll in degrees [intrinsic z-axis SLOF]')
    legend()
    figurePath = os.path.join(figureDirectory, 'Roll')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
    ###################################
    
    fig = figure()
    plot_date(Time_MPL[:], Data_MATS['lat_MATS'][:], markersize = 1, label = 'Predicted')
    plot_date(Time_MPL_OHB[:], lat_MATS_OHB[:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Geodetic Latitude of MATS (Fixed) in degrees')
    legend()
    figurePath = os.path.join(figureDirectory, 'Lat')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
    
    """
    for t in range(len(lat_MATS_STK_FIXED)):
        abs_lat_MATS_error_STK[t] = abs( lat_MATS_STK_FIXED[t] - Data_MATS['lat_MATS'][t] )
        abs_lat_MATS_error_OHB[t] = abs( lat_MATS_OHB[t] - Data_MATS['lat_MATS'][t] )
        
        abs_long_MATS_error_STK[t] = abs( long_MATS_STK_FIXED[t] - Data_MATS['long_MATS'][t] )
        abs_long_MATS_error_OHB[t] = abs( long_MATS_OHB[t] - Data_MATS['long_MATS'][t] )
    
    
    fig = figure()
    plot_date(current_time_MPL_STK[1:], abs_lat_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs STK')
    plot_date(Time_MPL_OHB[1:], abs_lat_MATS_error_OHB[1:], markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Latitude of MATS (Fixed) in degrees')
    legend()
    """
    
    fig = figure()
    plot_date(Time_MPL[:], Data_MATS['long_MATS'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:], long_MATS_STK_FIXED[1:], markersize = 1, label = 'STK-Data_Fixed')
    plot_date(Time_MPL_OHB[:], long_MATS_OHB[:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Longitude of MATS (Fixed) in degrees')
    legend()
    figurePath = os.path.join(figureDirectory, 'Long')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
    """
    fig = figure()
    plot_date(current_time_MPL[1:], abs_long_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs STK')
    plot_date(Time_MPL_OHB[1:], abs_long_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Longitude of MATS (Fixed) in degrees')
    legend()
    """
    
    fig = figure()
    plot_date(Time_MPL[:],Data_MATS['alt_MATS'][:], markersize = 1, label = 'Predicted')
    plot_date(Time_MPL_OHB[:],alt_MATS_OHB[:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Altitude of MATS in m')
    legend()
    figurePath = os.path.join(figureDirectory, 'Alt')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
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
    
    if( OHB_H5_Path != ''):
        "Calculate error between OHB DATA and predicted data when timestamps are the same"
        for t2 in range(timesteps):
            
            for t in range(len(Time)):
                
                if( Time_MPL_OHB[t2] == Time_MPL[t] ):
                    
                    
                    x_MATS_error_OHB.append( abs(Data_MATS['r_MATS_ECEF'][t,0]-r_MATS_OHB_ECEF[t2,0]) )
                    y_MATS_error_OHB.append( abs(Data_MATS['r_MATS_ECEF'][t,1]-r_MATS_OHB_ECEF[t2,1]) )
                    z_MATS_error_OHB.append( abs(Data_MATS['r_MATS_ECEF'][t,2]-r_MATS_OHB_ECEF[t2,2]) )
                    total_r_MATS_error_OHB.append( norm( (x_MATS_error_OHB[len(x_MATS_error_OHB)-1], y_MATS_error_OHB[len(y_MATS_error_OHB)-1], z_MATS_error_OHB[len(z_MATS_error_OHB)-1]) ) )
                    
                    x_LP_error_OHB.append( abs(Data_LP['r_LP_ECEF'][t,0]-r_LP_OHB_ECEF[t2,0]) )
                    y_LP_error_OHB.append( abs(Data_LP['r_LP_ECEF'][t,1]-r_LP_OHB_ECEF[t2,1]) )
                    z_LP_error_OHB.append( abs(Data_LP['r_LP_ECEF'][t,2]-r_LP_OHB_ECEF[t2,2]) )
                    total_r_LP_error_OHB.append( norm( (x_LP_error_OHB[len(x_LP_error_OHB)-1], y_LP_error_OHB[len(y_LP_error_OHB)-1], z_LP_error_OHB[len(z_LP_error_OHB)-1]) ) )
                    
                    alt_LP_error.append( Data_LP['alt_LP'][t] - alt_LP_OHB[t2] )
                    
                    optical_axis_Dec_ERROR.append( abs(Data_MATS['optical_axis_Dec'][t] - Dec_OHB[t2]) )
                    optical_axis_RA_ERROR.append( abs(Data_MATS['optical_axis_RA'][t] - RA_OHB[t2]) )
                    
                    #in_track = cross( normal_orbit[t], r_MATS_unit_vector[t])
                    #r_MATS_unit_vector_ECEF = array( (Data_MATS['x_MATS_ECEF'][t], Data_MATS['y_MATS_ECEF'][t], Data_MATS['z_MATS_ECEF'][t]) )
                    #v_MATS_unit_vector_ECEF = array( (Data_MATS['vx_MATS_ECEF'][t], Data_MATS['vy_MATS_ECEF'][t], Data_MATS['vz_MATS_ECEF'][t]) ) / norm( array( (Data_MATS['vx_MATS_ECEF'][t], Data_MATS['vy_MATS_ECEF'][t], Data_MATS['vz_MATS_ECEF'][t]) ) )
                    
                    r_MATS_unit_vector_ECEF = Data_MATS['r_MATS_ECEF'][t] / norm(Data_MATS['r_MATS_ECEF'][t] )
                    v_MATS_unit_vector_ECEF = Data_MATS['v_MATS_ECEF'][t] / norm(Data_MATS['v_MATS_ECEF'][t] )
                    
                    
                    UnitVectorBasis_RCI = transpose( array( ( (r_MATS_unit_vector_ECEF[0], Data_MATS['r_normal_orbit_ECEF'][t,0], v_MATS_unit_vector_ECEF[0]),
                                                             (r_MATS_unit_vector_ECEF[1], Data_MATS['r_normal_orbit_ECEF'][t,1], v_MATS_unit_vector_ECEF[1]), 
                                                             (r_MATS_unit_vector_ECEF[2], Data_MATS['r_normal_orbit_ECEF'][t,2], v_MATS_unit_vector_ECEF[2]) ) ) )
                    
                    dcm_change_of_basis_RCI = transpose(UnitVectorBasis_RCI)
                    r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_RCI)
                    
                    r_MATS_error_OHB_RCI = r_change_of_basis_ECI_to_SLOF.apply( ( (x_MATS_error_OHB[len(x_MATS_error_OHB)-1], y_MATS_error_OHB[len(y_MATS_error_OHB)-1], z_MATS_error_OHB[len(z_MATS_error_OHB)-1]) ) )
                    
                    r_MATS_error_OHB_Radial.append( r_MATS_error_OHB_RCI[0] )
                    r_MATS_error_OHB_CrossTrack.append( r_MATS_error_OHB_RCI[1] )
                    r_MATS_error_OHB_InTrack.append( r_MATS_error_OHB_RCI[2] )
                    total_r_MATS_error_OHB_RCI.append( norm(r_MATS_error_OHB_RCI) )
                    
                    r_LP_error_OHB_RCI = r_change_of_basis_ECI_to_SLOF.apply( ( (x_LP_error_OHB[len(x_LP_error_OHB)-1], y_LP_error_OHB[len(y_LP_error_OHB)-1], z_LP_error_OHB[len(z_LP_error_OHB)-1]) ) )
                    
                    r_LP_error_OHB_Radial.append( r_LP_error_OHB_RCI[0] )
                    r_LP_error_OHB_CrossTrack.append( r_LP_error_OHB_RCI[1] )
                    r_LP_error_OHB_InTrack.append( r_LP_error_OHB_RCI[2] )
                    total_r_LP_error_OHB_RCI.append( norm(r_LP_error_OHB_RCI) )
                    
                    Time_error_MPL.append( Time_MPL[t] )
                    break
                
                
        fig = figure()
        plot_date(Time_error_MPL[:],x_MATS_error_OHB[:], markersize = 1, label = 'x')
        plot_date(Time_error_MPL[:],y_MATS_error_OHB[:], markersize = 1, label = 'y')
        plot_date(Time_error_MPL[:],z_MATS_error_OHB[:], markersize = 1, label = 'z')
        xlabel('Date')
        ylabel('Absolute error in ECEF position of MATS in m (prediction vs OHB')
        legend()
        figurePath = os.path.join(figureDirectory, 'PosError')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
        
        
        fig = figure()
        plot_date(Time_error_MPL[:],r_MATS_error_OHB_Radial[:], markersize = 1, label = 'Radial')
        plot_date(Time_error_MPL[:],r_MATS_error_OHB_CrossTrack[:], markersize = 1, label = 'Cross-track')
        plot_date(Time_error_MPL[:],r_MATS_error_OHB_InTrack[:], markersize = 1, label = 'Intrack')
        xlabel('Date')
        ylabel('Absolute error in ECEF position of MATS as RCI in m (prediction vs OHB')
        legend()
        figurePath = os.path.join(figureDirectory, 'PosErrorRCI')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
        
        
        fig = figure()
        plot_date(Time_error_MPL[:],total_r_MATS_error_OHB[:], markersize = 1, label = 'XYZ')
        plot_date(Time_error_MPL[:],total_r_MATS_error_OHB_RCI[:], markersize = 1, label = 'RCI')
        xlabel('Date')
        ylabel('Magnitude of Absolute error in ECEF position of MATS in m (prediction vs OHB')
        legend()
        figurePath = os.path.join(figureDirectory, 'MagPosError')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
        
        
    
    
    
    
    
    
    fig = figure()
    plot_date(Time_MPL[:], Data_LP['lat_LP'][:], markersize = 1, label = 'Predicted')
    plot_date(Time_MPL_OHB[:], lat_LP_OHB[:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Latitude of LP in degrees')
    legend()
    figurePath = os.path.join(figureDirectory, 'Lat_LP')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
    """
    fig = figure()
    plot_date(Time_MPL_OHB[1:],abs(lat_LP_OHB[1:]-Data_LP['lat_LP'][1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Latitude of LP in degrees [J2000]')
    legend()
    """
    
    fig = figure()
    plot_date(Time_MPL[:],Data_LP['long_LP'][:], markersize = 1, label = 'Predicted')
    plot_date(Time_MPL_OHB[:],long_LP_OHB[:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Longitude of LP in degrees')
    legend()
    figurePath = os.path.join(figureDirectory, 'Long_LP')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
    """
    fig = figure()
    plot_date(current_time_MPL_STK[1:],abs(long_LP_STK[1:]-Data_LP['long_LP'][1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(Time_MPL_OHB[1:],abs(long_LP_OHB[1:]-Data_LP['long_LP'][1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Longitude of LP in degrees [J2000]')
    legend()
    """
    
    fig = figure()
    plot_date(Time_MPL[:],Data_LP['alt_LP'][:], markersize = 1, label = 'Predicted')
    plot_date(Time_MPL_OHB[:],alt_LP_OHB[:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Altitude of LP in m')
    legend()
    figurePath = os.path.join(figureDirectory, 'Alt_LP')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    if( OHB_H5_Path != ''):
        fig = figure()
        plot_date(Time_error_MPL[:],alt_LP_error[:], markersize = 1, label = 'Predicted - OHB')
        xlabel('Date')
        ylabel('Error in Altitude of LP in m')
        legend()
        figurePath = os.path.join(figureDirectory, 'AltError_LP')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
        
        
        fig = figure()
        plot_date(Time_error_MPL[:],x_LP_error_OHB[:], markersize = 1, label = 'x')
        plot_date(Time_error_MPL[:],y_LP_error_OHB[:], markersize = 1, label = 'y')
        plot_date(Time_error_MPL[:],z_LP_error_OHB[:], markersize = 1, label = 'z')
        xlabel('Date')
        ylabel('Absolute error in ECEF position of LP in m')
        legend()
        figurePath = os.path.join(figureDirectory, 'PosError_LP')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
        
        
        fig = figure()
        plot_date(Time_error_MPL[:],r_LP_error_OHB_Radial[:], markersize = 1, label = 'Radial')
        plot_date(Time_error_MPL[:],r_LP_error_OHB_CrossTrack[:], markersize = 1, label = 'Cross-track')
        plot_date(Time_error_MPL[:],r_LP_error_OHB_InTrack[:], markersize = 1, label = 'Intrack')
        xlabel('Date')
        ylabel('Absolute error in ECEF position of LP as RCI in m (prediction vs OHB')
        legend()
        figurePath = os.path.join(figureDirectory, 'PosErrorRCI_LP')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
        
        
        fig = figure()
        plot_date(Time_error_MPL[:],total_r_LP_error_OHB[:], markersize = 1, label = 'XYZ')
        plot_date(Time_error_MPL[:],total_r_LP_error_OHB_RCI[:], markersize = 1, label = 'RCI')
        xlabel('Date')
        ylabel('Magnitude of Absolute error of LP ECEF position in m')
        legend()
        figurePath = os.path.join(figureDirectory, 'MagPosError_LP')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
        
        
    
    
    fig = figure()
    plot_date(Time_MPL[:],Data_MATS['optical_axis_RA'][:], markersize = 1, label = 'Predicted')
    plot_date(Time_MPL_OHB[:],RA_OHB[:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Right Ascension of optical axis in degrees [J2000] (Parallax assumed negligable)')
    legend()
    figurePath = os.path.join(figureDirectory, 'RA_OpticalAxis')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    
    if( OHB_H5_Path != ''):
        fig = figure()
        plot_date(Time_error_MPL[:],optical_axis_RA_ERROR[:], markersize = 1, label = 'Prediction vs OHB')
        xlabel('Date')
        ylabel('Absolute error in Right Ascension in degrees [J2000] (Parallax assumed negligable)')
        legend()
        figurePath = os.path.join(figureDirectory, 'RA_OpticalAxisError')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
        
        
    
    fig = figure()
    plot_date(Time_MPL[:],Data_MATS['optical_axis_Dec'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:],Dec_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(Time_MPL_OHB[:],Dec_OHB[:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Declination of optical axis in degrees [J2000] (Parallax assumed negligable)')
    legend()
    figurePath = os.path.join(figureDirectory, 'Dec_OpticalAxis')
    pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
    
    if( OHB_H5_Path != ''):
        fig = figure()
        plot_date(Time_error_MPL[:],optical_axis_Dec_ERROR[:], markersize = 1, label = 'Prediction vs OHB')
        xlabel('Date')
        ylabel('Absolute error in Declination in degrees [J2000] (Parallax assumed negligable)')
        legend()
        figurePath = os.path.join(figureDirectory, 'Dec_OpticalAxisError')
        pickle.dump(fig,open(figurePath+'.fig.pickle', 'wb'))
        
    
    "######## Save data to pickle files ##########"
    "################################################"
    DataPath = os.path.join(figureDirectory, 'Data_MATS.data.pickle')
    f = open(DataPath,"wb")
    pickle.dump(Data_MATS,f)
    f.close()
    
    DataPath = os.path.join(figureDirectory, 'Data_LP.data.pickle')
    f = open(DataPath,"wb")
    pickle.dump(Data_LP,f)
    f.close()
    
    DataPath = os.path.join(figureDirectory, 'Time.data.pickle')
    f = open(DataPath,"wb")
    pickle.dump(Time,f)
    f.close()
    
    "#################################################"
    
    logging.shutdown()
    return Time_OHB
    
