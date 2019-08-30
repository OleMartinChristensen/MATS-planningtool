# -*- coding: utf-8 -*-
"""
Simulates, one by one, Science Modes from a Science Mode Timeline and saves relevant data such as attitude and position.
Also reads data from an .h5 file. Plots data from both the simulation and the .h5 file. As part of the Operational Planning Tool.

@author: David
"""

from scipy.spatial.transform import Rotation as R
from pylab import sin, pi, cos, cross, array, arccos, arcsin, arctan, dot, tan, norm, transpose, zeros, sqrt, floor, figure, plot, plot_date, datestr2num, xlabel, ylabel, title, legend, date2num
import ephem, logging, csv, os, sys, importlib, h5py, json, skyfield.api
import datetime as DT

from Operational_Planning_Tool import _Library, _MATS_coordinates, _Globals


OPT_Config_File = importlib.import_module(_Globals.Config_File)




def Timeline_Plotter(SCIMOD_Path, timestep, OHB_H5_Path = False):
    """Core function of the Timeline_Plotter.
    
    Arguments:
        Science_Mode_Path (str): Path to the Science Mode Timeline to be plotted.
        OHB_H5_Path (str): Path to the .h5 file containing position, time, and attitude data.
        
    Returns:
        None
    
    """
    
    """
    if(os.path.isfile('OPT_Config_File.py') == False):
        print('No OPT_Config_File.py found. Try running Create_ConfigFile()')
        sys.exit()
    """
    
    ############# Set up Logger #################################
    _Library.SetupLogger()
    Logger = logging.getLogger(OPT_Config_File.Logger_name())
    
    Version = OPT_Config_File.Version()
    Logger.info('Configuration File used: '+_Globals.Config_File+', Version: '+Version)
    
    
    Timeline_settings = OPT_Config_File.Timeline_settings()
    TLE = OPT_Config_File.getTLE()
    
    if ( OHB_H5_Path == False):
        Timestamp_fraction_of_second = 0
    else:
        OHB_data = h5py.File(OHB_H5_Path,'r')
        root = OHB_data['root']
        Time_State_OHB = root['TM_acOnGnss']['acoOnGnssStateTime']['raw']
        Time_Attitude_OHB = root['afoTmMhObt']['raw']
        
        if( abs(Time_Attitude_OHB[1000] - Time_State_OHB[1000]) > 0.5):
            Logger.error( 'Mismatch between timestamps of attitude and state')
            sys.exit()
        
        "To allow synchronization of the simulation to the timestamps of the OHB data"
        Timestamp_fraction_of_second = Time_State_OHB[0]- int(Time_State_OHB[0])
        timestep_OHB_data = Time_State_OHB[1] - Time_State_OHB[0]
    
    
    Data_MATS = { 'x_MATS': [], 'y_MATS': [], 'z_MATS': [], 'x_MATS_ECEF': [], 'y_MATS_ECEF': [], 'z_MATS_ECEF': [], 
                 'vx_MATS': [], 'vy_MATS': [], 'vz_MATS': [], 'vx_MATS_ECEF': [], 'vy_MATS_ECEF': [], 'vz_MATS_ECEF': [], 
                 'x_normal_orbit': [], 'y_normal_orbit': [], 'z_normal_orbit': [], 'x_normal_orbit_ECEF': [], 'y_normal_orbit_ECEF': [], 'z_normal_orbit_ECEF': [], 
                 'lat_MATS': [], 'long_MATS': [], 'alt_MATS': [], 'yaw_MATS': [], 
                 'pitch_MATS': [], 'r_optical_axis': [], 'r_optical_axis_ECEF': [], 'optical_axis_RA': [], 'optical_axis_Dec': []}
    
    Data_LP = { 'x_LP_ECEF': [], 'y_LP_ECEF': [], 'z_LP_ECEF': [], 'lat_LP': [], 'long_LP': [], 'alt_LP': [] } 
    
    Time = []
    
    ################# Read Science Mode Timeline json file ############
    with open(SCIMOD_Path, "r") as read_file:
        SCIMOD= json.load(read_file)
    ################# Read Science Mode Timeline json file ############
    
    for x in range(len(SCIMOD)):
        Logger.info('')
        Logger.info('Iteration number: '+str(x+1))
        Logger.info(str(SCIMOD[x][0]))
        
        "Skip the first entry if it only contains Timeline_settings used for the creation of the Science Mode Timeline"
        if(  SCIMOD[x][0] == 'Timeline_settings' ):
            Timeline_settings = SCIMOD[x][3]
            TLE = SCIMOD[x][4]
            continue
        
        Data_MATS, Data_LP, Time = Simulator( SCIMOD = SCIMOD[x], Timestamp_fraction_of_second = Timestamp_fraction_of_second, 
                                             timestep = timestep, Timeline_settings = Timeline_settings, TLE = TLE, Data_MATS = Data_MATS, 
                                             Data_LP = Data_LP, Time = Time )
        
        
    Plotter( Data_MATS, Data_LP, Time, timestep/timestep_OHB_data, OHB_H5_Path)
    
    





def Simulator( SCIMOD, Timestamp_fraction_of_second, timestep, Timeline_settings, TLE, Data_MATS, Data_LP, Time):
    """Subfunction, Simulates the position and attitude of MATS depending on the Mode given in *SCIMOD*.
    
    Appends the data during each timestep to Data_MATS, Data_LP, and Time.
    
    Arguments:
        SCIMOD (list): List containing the name of the Science Mode, the start_date, the end_date, and settings related to the Science Mode. 
        Timestamp_fraction_of_second (float): The fraction of a second timestamp for the data.
        timestep (int): The timestep [s] for the simulation.
        Timeline_settings (dict): A dictionary containing settings for the Timeline given in the Science Mode Timeline or in the *Configuration File*.
        TLE (list): A list containing the TLE given in the Science Mode Timeline or in the *Configuration File*.
        Data_MATS (dict of lists): Dictionary containing lists of simulated data of MATS.
        Data_LP (dict of lists): Dictionary containing lists of simulated data of LP.
        Time (list): List containing timestamps of the simulated data in Data_MATS and Data_LP.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Data_MATS updated with the new simulated values from the current Science Mode. \n
            (:obj:`dict` of :obj:`list`): Data_LP updated with the new simulated values from the current Science Mode. \n
            (list): Time updated with new simulated timestamps from the current Science Mode.
        
    """
    Mode = SCIMOD[0]
    Settings = SCIMOD[3]
    
    if( Mode == 'Mode120' or Mode == 'Mode121' or Mode == 'Mode122' or 
       Mode == 'Mode123' or Mode == 'Mode124'):
        Simulator_Select = 'Mode12X'
        freeze_start = Settings['freeze_start']
        freeze_duration = Settings['freeze_duration']
        pointing_altitude = Settings['pointing_altitude']
        freeze_flag = 0
        
    elif( Mode == 'Mode1' or Mode == 'Mode2' or Mode == 'Mode3' or 
           Mode == 'Mode4' ):
        Simulator_Select = 'ModeX'
        pointing_altitude = Timeline_settings['LP_pointing_altitude']
        
    elif( Mode == 'Mode5' or Mode == 'Mode6'):
        Simulator_Select = 'ModeX'
        pointing_altitude = Settings['pointing_altitude']
        
    elif( Mode == 'Mode130' or Mode == 'Mode131' or Mode == 'Mode132' or 
           Mode == 'Mode133' or Mode == 'Mode160' ):
        Simulator_Select = 'Mode13X'
        pointing_altitude = Settings['pointing_altitude']
        
    elif( Mode == 'Mode100' ):
        Simulator_Select = 'Mode100'
        pointing_altitude = Settings['pointing_altitude_from']
        pointing_altitude_to = Settings["pointing_altitude_to"]
        pointing_altitude_interval = Settings["pointing_altitude_interval"]
        pointing_duration = Settings["pointing_duration"] + Timeline_settings['pointing_stabilization']
        timestamp_change_of_pointing_altitude = pointing_duration
        
        
    elif( Mode == 'Mode110'):
        Simulator_Select = 'Mode110'
        pointing_altitude = Settings['pointing_altitude_from']
        pointing_altitude_to = Settings['pointing_altitude_to']
        sweep_rate = Settings['sweep_rate']
        pointing_stabilization = Timeline_settings['pointing_stabilization']
        
        
    else:
        return Data_MATS, Data_LP, Time
    
    Mode_start_date = ephem.Date( ephem.Date(SCIMOD[1]) + ephem.second * Timestamp_fraction_of_second )
    Mode_end_date = ephem.Date(SCIMOD[2])
    duration = (Mode_end_date - Mode_start_date) *24*3600
    date = Mode_start_date
    
    
        
    "Simulation length"
    timesteps = int(floor(duration / timestep))+1
    #timesteps = 10000
    
    start_from = 6000
    start_from = 0
    
    
    yaw_correction = Timeline_settings['yaw_correction']
    
    
    
    "Pre-allocate space"
    lat_MATS = zeros((timesteps,1))
    long_MATS = zeros((timesteps,1))
    alt_MATS = zeros((timesteps,1))
    a_ra_MATS = zeros((timesteps,1))
    a_dec_MATS = zeros((timesteps,1))
    x_MATS = zeros((timesteps,1))
    y_MATS = zeros((timesteps,1))
    z_MATS = zeros((timesteps,1))
    r_MATS = zeros((timesteps,3))
    r_MATS_unit_vector = zeros((timesteps,3))
    r_MATS_ECEF = zeros((timesteps,3))
    v_MATS = zeros((timesteps,3))
    v_MATS_ECEF = zeros((timesteps,3))
    normal_orbit = zeros((timesteps,3))
    lat_LP_estimated = zeros((timesteps,1))
    
    optical_axis = zeros((timesteps,3))
    optical_axis_ECEF = zeros((timesteps,3))
    
    r_LP = zeros((timesteps,3))
    LP_ECEF = zeros((timesteps,3))
    
    MATS_p = zeros((timesteps,1))
    MATS_P = zeros((timesteps,1))
    yaw_offset_angle = zeros((timesteps,1))
    pitch_MATS = zeros((timesteps,1))
    Euler_angles = zeros((timesteps,3))
    z_SLOF = zeros((timesteps,3))
    
    Ra = zeros((timesteps,1))
    Dec = zeros((timesteps,1))
    
    sun_angle = zeros((timesteps,1))
    lat_LP = zeros((timesteps,1))
    long_LP = zeros((timesteps,1))
    alt_LP = zeros((timesteps,1))
    normal_orbital = zeros((timesteps,3))
    normal_orbit_ECEF = zeros((timesteps,3))
    orbangle_between_LP_MATS_array = zeros((timesteps,1))
    lat_flag = 0
    R_earth_MATS = zeros((timesteps,1))
    current_time = zeros((timesteps,1))
    current_time_MPL = zeros((timesteps,1))
    
    
    
    
    "Constants"
    R_mean = 6371000 #Earth radius [m]
    #wgs84_Re = 6378.137 #Equatorial radius of wgs84 spheroid [km]
    # wgs84_Rp = 6356752.3142 #Polar radius of wgs84 spheroid [km]
    U = 398600441800000 #Earth gravitational parameter
    celestial_eq_normal = array([[0,0,1]])
    LP_pointing_altitude = Timeline_settings['LP_pointing_altitude']
    
    
    MATS_skyfield = skyfield.api.EarthSatellite(TLE[0], TLE[1])
    ts = skyfield.api.load.timescale()
    MATS = ephem.readtle('MATS',TLE[0],TLE[1])
    #current_time[0] = date
    
    for t in range(timesteps):
        
        t = t
        
        if( Simulator_Select == 'Mode100' ):
            if( t*timestep >= timestamp_change_of_pointing_altitude and pointing_altitude_to > pointing_altitude ):
                pointing_altitude += pointing_altitude_interval
                timestamp_change_of_pointing_altitude += pointing_duration 
        elif( Simulator_Select == 'Mode110' ):
            if( t*timestep > pointing_stabilization and pointing_altitude_to > pointing_altitude):
                pointing_altitude += sweep_rate * timestep
            elif( pointing_altitude_to < pointing_altitude):
                pointing_altitude = pointing_altitude_to
            
        
        current_time[t] = ephem.Date(date+ephem.second*(timestep*t+start_from+Timestamp_fraction_of_second))
        
        
        
        current_time_datetime = ephem.Date(current_time[t]).datetime()
        year = current_time_datetime.year
        month = current_time_datetime.month
        day = current_time_datetime.day
        hour = current_time_datetime.hour
        minute = current_time_datetime.minute
        second = current_time_datetime.second + current_time_datetime.microsecond/1000000
        
        current_time_skyfield = ts.utc(year, month, day, hour, minute, second)
        
        MATS_geo = MATS_skyfield.at(current_time_skyfield)
        v_MATS[t] = MATS_geo.velocity.km_per_s
        r_MATS[t] = MATS_geo.position.m
        MATS_distance = MATS_geo.distance().m
        MATS_subpoint = MATS_geo.subpoint()
        lat_MATS[t] = MATS_subpoint.latitude.radians
        long_MATS[t] = MATS_subpoint.longitude.radians
        alt_MATS[t] = MATS_subpoint.elevation.m
        
        
        """
        
        MATS.compute(current_time[t], epoch = '2000/01/01 11:58:55.816')
        
        (lat_MATS[t],long_MATS[t],alt_MATS[t],a_ra_MATS[t],a_dec_MATS[t])= (
                MATS.sublat, MATS.sublong, MATS.elevation, MATS.a_ra, MATS.a_dec)
        
        
        
        ###########################################################
        #First iteration of determining MATS distance from center of Earth
        R_earth_MATS[t] = _Library.lat_2_R(lat_MATS[t])*1000 #WGS84 radius from latitude of MATS
        MATS_distance = R_earth_MATS[t] + alt_MATS[t]
        
        z_MATS[t] = sin(a_dec_MATS[t])*(MATS_distance)
        x_MATS[t] = cos(a_dec_MATS[t])*(MATS_distance)* cos(a_ra_MATS[t])
        y_MATS[t] = cos(a_dec_MATS[t])*(MATS_distance)* sin(a_ra_MATS[t])
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        
        """
        r_MATS_unit_vector[t,0:3] = r_MATS[t,0:3] / norm(r_MATS[t,0:3])
        
        
        r_MATS_ECEF[t,0], r_MATS_ECEF[t,1], r_MATS_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                r_MATS[t,0], r_MATS[t,1], r_MATS[t,2], current_time_datetime)
        
        v_MATS_ECEF[t,0], v_MATS_ECEF[t,1], v_MATS_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                v_MATS[t,0], v_MATS[t,1], v_MATS[t,2], current_time_datetime)
        
        
        ##############################################################
        
        
        #Semi-Major axis of MATS, assuming circular orbit
        MATS_p[t] = norm(r_MATS[t,0:3])
        
        #Orbital Period of MATS
        MATS_P[t] = 2*pi*sqrt(MATS_p[t]**3/U)
        
        ################################################################
        
        
        #Initial Estimated pitch or elevation angle for MATS pointing using R_mean
        if(t == 0):
            orbangle_between_LP_MATS_array[t]= arccos((R_mean+pointing_altitude)/(MATS_distance))/pi*180
            orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
            time_between_LP_and_MATS = MATS_P[t][0]*orbangle_between_LP_MATS/360
            timesteps_between_LP_and_MATS = int(time_between_LP_and_MATS / timestep)
        
    
                
        if(t != 0):
            
            if( t >= timesteps_between_LP_and_MATS):
                    lat_LP_estimated[t] = lat_MATS[t-timesteps_between_LP_and_MATS]
                    R_earth_LP = _Library.lat_2_R(lat_LP_estimated[t][0])*1000
            else:
                date_of_MATSlat_is_equal_2_current_LPlat = ephem.Date(current_time[t] - ephem.second * timesteps_between_LP_and_MATS * timestep).datetime()
                lat_LP_estimated[t] = _Library.lat_calculator( MATS_skyfield, date_of_MATSlat_is_equal_2_current_LPlat )
                R_earth_LP = _Library.lat_2_R(lat_LP_estimated[t][0])*1000
                
            "Vector normal to the orbital plane of MATS"
            normal_orbit[t,0:3] = cross(v_MATS[t], r_MATS[t])
            normal_orbit[t,0:3] = normal_orbit[t,0:3] / norm(normal_orbit[t,0:3])
            
            normal_orbit_ECEF[t,0], normal_orbit_ECEF[t,1], normal_orbit_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                                       normal_orbit[t,0], normal_orbit[t,1], normal_orbit[t,2], current_time_datetime)
                
            
            #Freezing the attitude"
            if( Simulator_Select == 'Mode12X' and t*timestep > freeze_start and t*timestep <= freeze_duration+freeze_start):
                if( freeze_flag == 0):
                    t_freeze = t-1
                    
                
                freeze_flag = 1
                #optical_axis_ECEF[t,:] = LP_ECEF[t_freeze,:] - r_MATS_ECEF[t,:]*1000
                optical_axis[t,:] = optical_axis[t_freeze,:]
                optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                optical_axis[t,0], optical_axis[t,1], optical_axis[t,2], current_time_datetime)
            
                
                LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0], r_MATS_ECEF[t][1], r_MATS_ECEF[t][2], 
                                       optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
                
                lat_LP[t], long_LP[t], alt_LP[t]  = _MATS_coordinates.ECEF2lla(LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2])
                
                Dec[t] = arctan( optical_axis[t,2] / sqrt(optical_axis[t,0]**2 + optical_axis[t,1]**2) ) /pi * 180
                Ra[t] = arccos( dot( [1,0,0], [optical_axis[t,0],optical_axis[t,1],0] ) / norm([optical_axis[t,0],optical_axis[t,1],0]) ) / pi * 180
                
                if( optical_axis[t,1] < 0 ):
                    Ra[t] = 360-Ra[t]
                    
            #Looking at a fixed pointing altitude
            else:
                
                
                
                #Looking at LP_pointing_altitude after attitude freeze
                if( Simulator_Select == 'Mode12X' and t*timestep >= freeze_duration+freeze_start):
                    # More accurate estimation of pitch angle of MATS using R_earth_LP instead of R_mean
                    orbangle_between_LP_MATS_array[t] = array(arccos((R_earth_LP+LP_pointing_altitude)/(MATS_distance))/pi*180)
                    #orbangle_between_LP_MATS_array[t] = array(arccos((R_mean+LP_altitude)/(R_mean+alt_MATS[t]))/pi*180)
                    orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
                #Looking at pointing_altitude
                else:
                    # More accurate estimation of pitch angle of MATS using R_earth_LP instead of R_mean
                    orbangle_between_LP_MATS_array[t] = array(arccos((R_earth_LP+pointing_altitude)/(MATS_distance))/pi*180)
                    #orbangle_between_LP_MATS_array[t] = array(arccos((R_mean+LP_altitude)/(R_mean+alt_MATS[t]))/pi*180)
                    orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
                    
                
                
                pitch_MATS[t] = orbangle_between_LP_MATS + 90
                
                
                ############# Calculations of orbital and pointing vectors ############
                
                if( yaw_correction == True):
                    "Calculate intersection between the orbital plane and the equator"
                    ascending_node = cross(normal_orbit[t,0:3], celestial_eq_normal)
                    
                    arg_of_lat = arccos( dot(ascending_node, r_MATS[t,0:3]) / norm(r_MATS[t,0:3]) / norm(ascending_node) ) /pi*180
                    
                    "To determine if MATS is moving towards the ascending node"
                    if( dot(cross( ascending_node, r_MATS[t,0:3]), normal_orbit[t,0:3]) >= 0 ):
                        arg_of_lat = 360 - arg_of_lat
                        
                    yaw_offset_angle[t] = Timeline_settings['yaw_amplitude'] * cos( arg_of_lat/180*pi - orbangle_between_LP_MATS/180*pi + Timeline_settings['yaw_phase']/180*pi )
                    #yaw_offset_angle = yaw_offset_angle[0]
                    
                    
                elif( yaw_correction == False):
                    yaw_offset_angle[t] = 0
                
                "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
                rot_mat = _Library.rot_arbit(pitch_MATS[t][0]/180*pi, normal_orbit[t,0:3])
                optical_axis[t,0:3] = (rot_mat @ r_MATS[t])
                optical_axis[t,0:3] = optical_axis[t,0:3] / norm(optical_axis[t,0:3])
                
                "Rotate yaw of pointing direction, meaning to rotate around the vector to MATS"
                rot_mat = _Library.rot_arbit( (-yaw_offset_angle[t][0])/180*pi, r_MATS_unit_vector[t,0:3])
                optical_axis[t,0:3] = rot_mat @ optical_axis[t,0:3]
                optical_axis[t,0:3] = optical_axis[t,0:3]/norm(optical_axis[t,0:3])
                
                optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                    optical_axis[t,0], optical_axis[t,1], optical_axis[t,2], ephem.Date(current_time[t][0]).datetime())
                
                LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0], r_MATS_ECEF[t][1], r_MATS_ECEF[t][2], 
                                           optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
                
                lat_LP[t], long_LP[t], alt_LP[t]  = _MATS_coordinates.ECEF2lla(LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2])
                
                Dec[t] = arctan( optical_axis[t,2] / sqrt(optical_axis[t,0]**2 + optical_axis[t,1]**2) ) /pi * 180
                Ra[t] = arccos( dot( [1,0,0], [optical_axis[t,0],optical_axis[t,1],0] ) / norm([optical_axis[t,0],optical_axis[t,1],0]) ) / pi * 180
                
                if( optical_axis[t,1] < 0 ):
                    Ra[t] = 360-Ra[t]
                
            
            z_SLOF = -r_MATS[t,:]
            #z_SLOF = -r_MATS[t,0:3]
            z_SLOF = z_SLOF / norm(z_SLOF)
            y_SLOF = normal_orbit[t,:]
            y_SLOF = y_SLOF / norm(y_SLOF)
            x_SLOF = cross(y_SLOF,z_SLOF)
            x_SLOF = x_SLOF / norm(x_SLOF)
            
            dcm_SLOF_coordinate_system = array( ([x_SLOF[0], y_SLOF[0], z_SLOF[0]], [x_SLOF[1], y_SLOF[1], z_SLOF[1]], [x_SLOF[2], y_SLOF[2], z_SLOF[2]]) )
            dcm_change_of_basis_ECI_to_SLOF = transpose(dcm_SLOF_coordinate_system)
            r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_ECI_to_SLOF)
        
            optical_axis_SLOF = r_change_of_basis_ECI_to_SLOF.apply( -optical_axis[t,:])
            
            Z = [0,0,1]
            
            angle = arccos( dot( Z, optical_axis_SLOF) )
            normal = cross( Z, optical_axis_SLOF)
            normal = normal / norm(normal)
            rot_mat = _Library.rot_arbit(angle, normal)
            rotation = R.from_dcm(rot_mat)
            Euler_angles[t,:] = rotation.as_euler('ZYZ', degrees=True)
            
            yaw_offset_angle[t] = Euler_angles[t,0]
            pitch_MATS[t] = Euler_angles[t,1]
            
            
            
            
            Data_MATS['lat_MATS'].append(lat_MATS[t]/pi*180)
            Data_MATS['long_MATS'].append(long_MATS[t]/pi*180)
            Data_MATS['alt_MATS'].append(alt_MATS[t])
            
            Data_MATS['x_MATS'].append(r_MATS[t][0])
            Data_MATS['x_MATS_ECEF'].append(r_MATS_ECEF[t][0])
            Data_MATS['y_MATS'].append(r_MATS[t][1])
            Data_MATS['y_MATS_ECEF'].append(r_MATS_ECEF[t][1])
            Data_MATS['z_MATS'].append(r_MATS[t][2])
            Data_MATS['z_MATS_ECEF'].append(r_MATS_ECEF[t][2])
            
            Data_MATS['x_normal_orbit'].append(normal_orbit[t][0])
            Data_MATS['x_normal_orbit_ECEF'].append(normal_orbit_ECEF[t][0])
            Data_MATS['y_normal_orbit'].append(normal_orbit[t][1])
            Data_MATS['y_normal_orbit_ECEF'].append(normal_orbit_ECEF[t][1])
            Data_MATS['z_normal_orbit'].append(normal_orbit[t][2])
            Data_MATS['z_normal_orbit_ECEF'].append(normal_orbit_ECEF[t][2])
            
            Data_MATS['vx_MATS'].append(v_MATS[t][0])
            Data_MATS['vx_MATS_ECEF'].append(v_MATS_ECEF[t][0])
            Data_MATS['vy_MATS'].append(v_MATS[t][1])
            Data_MATS['vy_MATS_ECEF'].append(v_MATS_ECEF[t][1])
            Data_MATS['vz_MATS'].append(v_MATS[t][2])
            Data_MATS['vz_MATS_ECEF'].append(v_MATS_ECEF[t][2])
            
            Data_MATS['yaw_MATS'].append(yaw_offset_angle[t])
            Data_MATS['pitch_MATS'].append(pitch_MATS[t])
            
            Data_MATS['r_optical_axis'].append(optical_axis[t][:])
            Data_MATS['r_optical_axis_ECEF'].append(optical_axis_ECEF[t][:])
            
            Data_MATS['optical_axis_RA'].append(Ra[t])
            Data_MATS['optical_axis_Dec'].append(Dec[t])
            
            Data_LP['lat_LP'].append(lat_LP[t])
            Data_LP['long_LP'].append(long_LP[t])
            Data_LP['alt_LP'].append(alt_LP[t])
            
            Data_LP['x_LP_ECEF'].append(LP_ECEF[t][0])
            Data_LP['y_LP_ECEF'].append(LP_ECEF[t][1])
            Data_LP['z_LP_ECEF'].append(LP_ECEF[t][2])
            
            Time.append(current_time[t])
        
        
        
    
    return Data_MATS, Data_LP, Time
    
  
    
    

    
def Plotter(Data_MATS, Data_LP, Time, timestep, OHB_H5_Path = False):
    """Subfunction, Plots the position and attitude data of MATS and LP.
    
    Plots both simulated data in Data_MATS and Data_LP as a function of the 
    timestamps in Time but also the data given in the file located at OHB_H5_Path.
    
    Arguments:
        Data_MATS (dict of lists): Dictionary containing lists of simulated data of MATS.
        Data_LP (dict of lists): Dictionary containing lists of simulated data of LP.
        Time (list): List containing timestamps of the simulated data in Data_MATS and Data_LP.
        OHB_H5_Path (str): Path to the .h5 file containing position, time, and attitude data.
        
    Returns:
        None
        
    """
    
    #timestep = 20 #In seconds
    timesteps = 400
    #timesteps = len(Time)
    start_from = 0
    ephemDate2MatplotDate = datestr2num('1899/12/31 12:00:00')
    
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
    """
    days = root['acoOnGnssStateJ2000_z']['receptionDate']
    milliseconds = root['acoOnGnssStateJ2000_z']['receptionTime']
    
    days_q1 = root['afoTmAreAttitudeState_0']['receptionDate']
    milliseconds_q1 = root['afoTmAreAttitudeState_0']['receptionTime']
    days_q2 = root['afoTmAreAttitudeState_1']['receptionDate']
    milliseconds_q2 = root['afoTmAreAttitudeState_1']['receptionTime']
    days_q3 = root['afoTmAreAttitudeState_2']['receptionDate']
    milliseconds_q3 = root['afoTmAreAttitudeState_2']['receptionTime']
    days_q4 = root['afoTmAreAttitudeState_3']['receptionDate']
    milliseconds_q4 = root['afoTmAreAttitudeState_3']['receptionTime']
    days_vx = root['acoOnGnssStateJ2000_vx']['receptionDate']
    milliseconds_vx = root['acoOnGnssStateJ2000_vx']['receptionTime']
    days_vy = root['acoOnGnssStateJ2000_vy']['receptionDate']
    milliseconds_vy = root['acoOnGnssStateJ2000_vy']['receptionTime']
    days_time = root['acoOnGnssStateTime']['receptionDate']
    milliseconds_time = root['acoOnGnssStateTime']['receptionTime']
    """
    
    Time_State_OHB = root['TM_acOnGnss']['acoOnGnssStateTime']['raw']
    Time_Attitude_OHB = root['afoTmMhObt']['raw']
    
    
    #timesteps = len(Time_State_OHB)
    #timesteps = 1440
    
    "Allocate Space"
    current_time_MPL_OHB = zeros((timesteps,1))
    #current_time = []
    current_time_state = []
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
    Ra_OHB = zeros((timesteps,1))
    
    Time_State_OHB_float = zeros((timesteps,1))
    Time_Attitude_OHB_float = zeros((timesteps,1))
    
    Euler_angles_SLOF_OHB = zeros((timesteps,3))
    Euler_angles_ECI_OHB = zeros((timesteps,3))
    
    optical_axis_OHB = zeros((timesteps,3))
    optical_axis_OHB_ECEF = zeros((timesteps,3))
    
    abs_lat_MATS_error_STK = zeros((timesteps,1))
    abs_lat_MATS_error_OHB = zeros((timesteps,1))
    abs_long_MATS_error_STK = zeros((timesteps,1))
    abs_long_MATS_error_OHB = zeros((timesteps,1))
    
    
    yaw_SLOF_OHB = zeros((timesteps,1))
    pitch_SLOF_OHB = zeros((timesteps,1))
    roll_SLOF_OHB = zeros((timesteps,1))
    
    z_axis_SLOF_OHB = zeros((timesteps,3))
    x_axis_SLOF_OHB = zeros((timesteps,3))
    
    for t in range(timesteps):
        
        t_OHB = round(t* timestep + start_from)
        
        
        #Time_OHB_datetime = ephem.Date(Time_OHB[t]).datetime()
        
        #current_time.append( DT.datetime(2000,1,1)+DT.timedelta(days = float(days[t_OHB]), milliseconds = float(milliseconds[t_OHB])) )
        
        Time_State_OHB_float[t] = float(Time_State_OHB[t_OHB])
        Time_Attitude_OHB_float[t] = float(Time_Attitude_OHB[t_OHB])
        
        current_time_state.append(DT.datetime(1980,1,6)+DT.timedelta(seconds = Time_State_OHB_float[t,0]-18) )
        
        current_time_attitude.append(DT.datetime(1980,1,6)+DT.timedelta(seconds = Time_Attitude_OHB_float[t,0]-18) )
        
        r_MATS_OHB[t,0] = x_MATS_OHB[t_OHB] 
        r_MATS_OHB[t,1] = y_MATS_OHB[t_OHB] 
        r_MATS_OHB[t,2] = z_MATS_OHB[t_OHB] 
        
        Vel_MATS_OHB[t,0] = vel_x_MATS_OHB[t_OHB] 
        Vel_MATS_OHB[t,1] = vel_y_MATS_OHB[t_OHB] 
        Vel_MATS_OHB[t,2] = vel_z_MATS_OHB[t_OHB] 
        
        q1_MATS_OHB[t,0] = quat1_MATS_OHB[t_OHB]
        q2_MATS_OHB[t,0] = quat2_MATS_OHB[t_OHB]
        q3_MATS_OHB[t,0] = quat3_MATS_OHB[t_OHB]
        q4_MATS_OHB[t,0] = quat4_MATS_OHB[t_OHB]
        
        
        "SLOF = Spacecraft Local Orbit Frame"
        z_SLOF = -r_MATS_OHB[t,0:3]
        #z_SLOF = -r_MATS[t,0:3]
        z_SLOF = z_SLOF / norm(z_SLOF)
        x_SLOF = Vel_MATS_OHB[t,0:3]
        x_SLOF = x_SLOF / norm(x_SLOF)
        y_SLOF = cross(z_SLOF,x_SLOF)
        y_SLOF = y_SLOF / norm(y_SLOF)
        
        
        "Create change of coordinate matrix from the SLOF basis vectors"
        dcm_SLOF_coordinate_system = array( ([x_SLOF[0], y_SLOF[0], z_SLOF[0]], [x_SLOF[1], y_SLOF[1], z_SLOF[1]], [x_SLOF[2], y_SLOF[2], z_SLOF[2]]) )
        dcm_change_of_basis_ECI_to_SLOF = transpose(dcm_SLOF_coordinate_system)
        r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_ECI_to_SLOF)
        
        #MATS_ECI = R.from_quat([q1_MATS_OHB[t_OHB], q2_MATS_OHB[t_OHB], q3_MATS_OHB[t_OHB], q4_MATS_OHB[t_OHB]])
        MATS_ECI_OHB = R.from_quat([q2_MATS_OHB[t,0], q3_MATS_OHB[t,0], q4_MATS_OHB[t,0], q1_MATS_OHB[t,0]])
       
        
        
        
        
        optical_axis_OHB[t,:] = MATS_ECI_OHB.apply([0,0,-1])
        optical_axis_OHB[t,:] = optical_axis_OHB[t,:] / norm(optical_axis_OHB[t,:])
        Dec_OHB[t] = arctan( optical_axis_OHB[t,2] / sqrt(optical_axis_OHB[t,0]**2 + optical_axis_OHB[t,1]**2) ) /pi * 180
        Ra_OHB[t] = arccos( dot( [1,0,0], [optical_axis_OHB[t,0],optical_axis_OHB[t,1],0] ) / norm([optical_axis_OHB[t,0],optical_axis_OHB[t,1],0]) ) / pi * 180
        
        if( optical_axis_OHB[t,1] < 0 ):
            Ra_OHB[t] = 360-Ra_OHB[t]
        
        
        
        
        #Euler_angles_ECI[t,:] = MATS_ECI.as_euler('xyz', degrees=True)
        
        Euler_angles_ECI_OHB[t,:] = MATS_ECI_OHB.as_euler('ZYZ', degrees=True)
        
        MATS_SLOF_OHB = r_change_of_basis_ECI_to_SLOF*MATS_ECI_OHB
        
        z_axis_SLOF_OHB[t,:] = MATS_SLOF_OHB.apply([0,0,1])
        x_axis_SLOF_OHB[t,:] = MATS_SLOF_OHB.apply([1,0,0])
        
        
        
        z_axis_SLOF_x_z_OHB = z_axis_SLOF_OHB[t,:] - (dot(z_axis_SLOF_OHB[t,:], [0,1,0]) * array([0,1,0]) )
        
        z_axis_SLOF_x_y_OHB = z_axis_SLOF_OHB[t,:] - (dot(z_axis_SLOF_OHB[t,:], [0,0,1]) * array([0,0,1]) )
        
        #pitch_SLOF[t] = arccos(dot([0,0,1],z_axis_SLOF_x_z) / (norm([0,0,1]) * norm(z_axis_SLOF_x_z))) /pi*180
        pitch_SLOF_OHB[t] = arccos(dot(z_axis_SLOF_OHB[t,:],z_axis_SLOF_x_y_OHB) / (norm(z_axis_SLOF_OHB[t,:]) * norm(z_axis_SLOF_x_y_OHB))) /pi*180
        yaw_SLOF_OHB[t] = arccos(dot([1,0,0],z_axis_SLOF_x_y_OHB) / (norm([1,0,0]) * norm(z_axis_SLOF_x_y_OHB))) /pi*180
        
        if( z_axis_SLOF_x_y_OHB[1] < 0 ):
            yaw_SLOF_OHB[t] = -yaw_SLOF_OHB[t]
        if( z_axis_SLOF_x_z_OHB[0] > 0 ):
            pitch_SLOF_OHB[t] = -pitch_SLOF_OHB[t]
        
        
        
        
        Euler_angles_SLOF_OHB[t,:] = MATS_SLOF_OHB.as_euler('ZYZ', degrees=True)
        #Euler_angles_SLOF[t,:] = MATS_SLOF.as_euler('yzx', degrees=True)
        
        
        optical_axis_OHB_ECEF[t,0], optical_axis_OHB_ECEF[t,1], optical_axis_OHB_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                    optical_axis_OHB[t,0], optical_axis_OHB[t,1], optical_axis_OHB[t,2], current_time_state[t])
            
        optical_axis_OHB_ECEF[t,:] = optical_axis_OHB_ECEF[t,:] / norm(optical_axis_OHB_ECEF[t,:])
        
        
        
        r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                    r_MATS_OHB[t,0], r_MATS_OHB[t,1], r_MATS_OHB[t,2], current_time_state[t])
        
        
        
        
        lat_MATS_OHB[t], long_MATS_OHB[t], alt_MATS_OHB[t] = _MATS_coordinates.ECEF2lla(r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2])
        
        r_LP_OHB_ECEF[t,0], r_LP_OHB_ECEF[t,1], r_LP_OHB_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2], 
                                       optical_axis_OHB_ECEF[t,0], optical_axis_OHB_ECEF[t,1], optical_axis_OHB_ECEF[t,2])
        
        lat_LP_OHB[t], long_LP_OHB[t], alt_LP_OHB[t]  = _MATS_coordinates.ECEF2lla(r_LP_OHB_ECEF[t,0], r_LP_OHB_ECEF[t,1], r_LP_OHB_ECEF[t,2])
        
        
        #R_earth_MATS[t][t] = norm(r_MATS_OHB[t,:]*1000)-alt_MATS_OHB[t]
        
        current_time_MPL_OHB[t] = date2num(current_time_state[t])
    
    

    
    ########################## Plotter ###########################################
    
    from mpl_toolkits.mplot3d import axes3d
    
    #current_time_MPL_STK = ephemDate2MatplotDate + current_time_STK[:]
    Time_MPL = [ephemDate2MatplotDate+x for x in Time]
    
    
    fig=figure(1)
    ax = fig.add_subplot(111,projection='3d')
    ax.set_xlim3d(-7000000, 7000000)
    ax.set_ylim3d(-7000000, 7000000)
    ax.set_zlim3d(-7000000, 7000000)
    #ax.scatter(r_MATS[1:,0], r_MATS[1:,1], r_MATS[1:,2])
    #ax.scatter(r_MATS_STK_ECEF[1:100,0], r_MATS_STK_ECEF[1:100,1], r_MATS_STK_ECEF[1:100,2])
    ax.scatter(Data_LP['x_LP_ECEF'][1:100], Data_LP['y_LP_ECEF'][1:100], Data_LP['z_LP_ECEF'][1:100])
    #ax.scatter(r_MATS_ECEF[1:100,0]*1000, r_MATS_ECEF[1:100,1]*1000, r_MATS_ECEF[1:100,2]*1000)
    #ax.scatter(LP_ECEF[1:100,0], LP_ECEF[1:100,1], LP_ECEF[1:100,2])
    
    figure()
    plot_date(Time_MPL[:], Data_MATS['yaw_MATS'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:],Euler_angles_SLOF_STK[1:,0], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Euler_angles_SLOF_OHB[1:,0], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Yaw in degrees [z-axis SLOF]')
    legend()
    
    
    figure()
    plot_date(Time_MPL[:], Data_MATS['pitch_MATS'][:] , markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:],Euler_angles_SLOF_STK[1:,1], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Euler_angles_SLOF_OHB[1:,1], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Pitch in degrees [intrinsic y-axis SLOF]')
    legend()
    
    figure()
    #plot_date(current_time_MPL_STK[1:],Euler_angles_SLOF_STK[1:,2], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Euler_angles_SLOF_OHB[1:,2], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Roll in degrees [intrinsic z-axis SLOF]')
    legend()
    
    ###################################
    
    figure()
    plot_date(Time_MPL[:], Data_MATS['lat_MATS'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:], lat_MATS_STK_FIXED[1:], markersize = 1, label = 'STK-Data_Fixed')
    plot_date(current_time_MPL_OHB[1:], lat_MATS_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Geodetic Latitude of MATS (Fixed) in degrees')
    legend()
    
    
    """
    for t in range(len(lat_MATS_STK_FIXED)):
        abs_lat_MATS_error_STK[t] = abs( lat_MATS_STK_FIXED[t] - Data_MATS['lat_MATS'][t] )
        abs_lat_MATS_error_OHB[t] = abs( lat_MATS_OHB[t] - Data_MATS['lat_MATS'][t] )
        
        abs_long_MATS_error_STK[t] = abs( long_MATS_STK_FIXED[t] - Data_MATS['long_MATS'][t] )
        abs_long_MATS_error_OHB[t] = abs( long_MATS_OHB[t] - Data_MATS['long_MATS'][t] )
    
    
    figure()
    plot_date(current_time_MPL_STK[1:], abs_lat_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:], abs_lat_MATS_error_OHB[1:], markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Latitude of MATS (Fixed) in degrees')
    legend()
    """
    
    figure()
    plot_date(Time_MPL[:], Data_MATS['long_MATS'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:], long_MATS_STK_FIXED[1:], markersize = 1, label = 'STK-Data_Fixed')
    plot_date(current_time_MPL_OHB[1:], long_MATS_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Longitude of MATS (Fixed) in degrees')
    legend()
    
    """
    figure()
    plot_date(current_time_MPL[1:], abs_long_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:], abs_long_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Longitude of MATS (Fixed) in degrees')
    legend()
    """
    ####################################
    
    
    total_r_MATS_error_OHB = []
    x_MATS_error_OHB = []
    y_MATS_error_OHB = []
    z_MATS_error_OHB = []
    
    total_r_LP_error_OHB = []
    x_LP_error_OHB = []
    y_LP_error_OHB = []
    z_LP_error_OHB = []
    
    r_MATS_ECEF = []
    
    r_MATS_error_OHB_RCI = []
    r_MATS_error_OHB_Radial = []
    r_MATS_error_OHB_CrossTrack = []
    r_MATS_error_OHB_InTrack = []
    
    Time_error_MPL = []
    
    for t2 in range(timesteps):
        
        for t in range(len(Time)):
            
            if( current_time_MPL_OHB[t2] == Time_MPL[t] ):
                """
                x_MATS_error_STK[t] = abs(Data_MATS['x_MATS_ECEF'][t]*1000-r_MATS_STK_FIXED*1000)            
                y_MATS_error_STK[t] = abs(Data_MATS['y_MATS_ECEF'][t]*1000-r_MATS_STK_FIXED*1000)
                z_MATS_error_STK[t] = abs(Data_MATS['z_MATS_ECEF'][t]*1000-r_MATS_STK_FIXED*1000)
                total_r_MATS_error_STK[t] = norm( (x_MATS_error_STK[t], y_MATS_error_STK[t], z_MATS_error_STK[t]) )
                """
                """
                x_MATS_error_OHB[t] = abs(Data_MATS['x_MATS_ECEF'][t]*1000-r_MATS_OHB_ECEF[t,0])
                y_MATS_error_OHB[t] = abs(Data_MATS['y_MATS_ECEF'][t]*1000-r_MATS_OHB_ECEF[t,1])
                z_MATS_error_OHB[t] = abs(Data_MATS['z_MATS_ECEF'][t]*1000-r_MATS_OHB_ECEF[t,2])
                total_r_MATS_error_OHB[t] = norm( (x_MATS_error_OHB[t], y_MATS_error_OHB[t], z_MATS_error_OHB[t]) )
                
                Time_error_MPL[t] = Time_MPL[t]
                """
                
                x_MATS_error_OHB.append( abs(Data_MATS['x_MATS_ECEF'][t]-r_MATS_OHB_ECEF[t2,0]) )
                y_MATS_error_OHB.append( abs(Data_MATS['y_MATS_ECEF'][t]-r_MATS_OHB_ECEF[t2,1]) )
                z_MATS_error_OHB.append( abs(Data_MATS['z_MATS_ECEF'][t]-r_MATS_OHB_ECEF[t2,2]) )
                total_r_MATS_error_OHB.append( norm( (x_MATS_error_OHB[len(x_MATS_error_OHB)-1], y_MATS_error_OHB[len(y_MATS_error_OHB)-1], z_MATS_error_OHB[len(z_MATS_error_OHB)-1]) ) )
                
                x_LP_error_OHB.append( abs(Data_LP['x_LP_ECEF'][t]-r_LP_OHB_ECEF[t2,0]) )
                y_LP_error_OHB.append( abs(Data_LP['y_LP_ECEF'][t]-r_LP_OHB_ECEF[t2,1]) )
                z_LP_error_OHB.append( abs(Data_LP['z_LP_ECEF'][t]-r_LP_OHB_ECEF[t2,2]) )
                total_r_LP_error_OHB.append( norm( (x_LP_error_OHB[len(x_LP_error_OHB)-1], y_LP_error_OHB[len(y_LP_error_OHB)-1], z_LP_error_OHB[len(z_LP_error_OHB)-1]) ) )
                
                #in_track = cross( normal_orbit[t], r_MATS_unit_vector[t])
                r_MATS_ECEF = ([Data_MATS['x_MATS_ECEF'][t], Data_MATS['y_MATS_ECEF'][t], Data_MATS['z_MATS_ECEF'][t]])
                r_MATS_unit_vector_ECEF = r_MATS_ECEF / norm( r_MATS_ECEF )
                v_MATS_unit_vector_ECEF = [Data_MATS['vx_MATS_ECEF'][t], Data_MATS['vy_MATS_ECEF'][t], Data_MATS['vz_MATS_ECEF'][t]] / norm( [Data_MATS['vx_MATS_ECEF'][t], Data_MATS['vy_MATS_ECEF'][t], Data_MATS['vz_MATS_ECEF'][t]] )
                change_of_basis_RCI = transpose( array( ( (r_MATS_unit_vector_ECEF[0], Data_MATS['x_normal_orbit_ECEF'][t], v_MATS_unit_vector_ECEF[0]),
                                                         (r_MATS_unit_vector_ECEF[1], Data_MATS['y_normal_orbit_ECEF'][t], v_MATS_unit_vector_ECEF[1]), 
                                                         (r_MATS_unit_vector_ECEF[2], Data_MATS['z_normal_orbit_ECEF'][t], v_MATS_unit_vector_ECEF[2]) ) ) )
                
                r_MATS_error_OHB_RCI = change_of_basis_RCI @ array( (x_MATS_error_OHB[len(x_MATS_error_OHB)-1], y_MATS_error_OHB[len(y_MATS_error_OHB)-1], z_MATS_error_OHB[len(z_MATS_error_OHB)-1]) )
                
                r_MATS_error_OHB_Radial.append( r_MATS_error_OHB_RCI[0] )
                r_MATS_error_OHB_CrossTrack.append( r_MATS_error_OHB_RCI[1] )
                r_MATS_error_OHB_InTrack.append( r_MATS_error_OHB_RCI[2] )
                
                Time_error_MPL.append( Time_MPL[t] )
                break
            
            
    
    """
    for t in range(len(r_MATS_STK_FIXED)):
        x_MATS_error_STK[t] = abs(Data_MATS['x_MATS_ECEF'][t]-r_MATS_STK_FIXED*1000)
        x_MATS_error_OHB[t] = abs(Data_MATS['x_MATS_ECEF'][t]-r_MATS_OHB_ECEF)
        
        y_MATS_error_STK[t] = abs(Data_MATS['y_MATS_ECEF'][t]-r_MATS_STK_FIXED*1000)
        y_MATS_error_OHB[t] = abs(Data_MATS['y_MATS_ECEF'][t]-r_MATS_OHB_ECEF)
        
        z_MATS_error_STK[t] = abs(Data_MATS['z_MATS_ECEF'][t]-r_MATS_STK_FIXED*1000)
        z_MATS_error_OHB[t] = abs(Data_MATS['z_MATS_ECEF'][t]-r_MATS_OHB_ECEF)
        
        total_r_MATS_error_STK[t] = norm( (x_MATS_error_STK[t], y_MATS_error_STK[t], z_MATS_error_STK[t]) )
        total_r_MATS_error_OHB[t] = norm( (x_MATS_error_OHB[t], y_MATS_error_OHB[t], z_MATS_error_OHB[t]) )
        
    
    figure()
    plot_date(current_time_MPL_STK[1:],x_MATS_error_STK[1:], markersize = 1, label = 'x')
    plot_date(current_time_MPL_STK[1:],y_MATS_error_STK[1:], markersize = 1, label = 'y')
    plot_date(current_time_MPL_STK[1:],z_MATS_error_STK[1:], markersize = 1, label = 'z')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS in m (prediction vs STK')
    legend()
    """
    
    
    
    figure()
    plot_date(Time_error_MPL[:],x_MATS_error_OHB[:], markersize = 1, label = 'x')
    plot_date(Time_error_MPL[:],y_MATS_error_OHB[:], markersize = 1, label = 'y')
    plot_date(Time_error_MPL[:],z_MATS_error_OHB[:], markersize = 1, label = 'z')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS in m (prediction vs OHB')
    legend()
    
    figure()
    plot_date(Time_error_MPL[:],total_r_MATS_error_OHB[:], markersize = 1, label = 'Total error')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS in m (prediction vs OHB')
    legend()
    
    figure()
    plot_date(Time_error_MPL[:],r_MATS_error_OHB_Radial[:], markersize = 1, label = 'Radial')
    plot_date(Time_error_MPL[:],r_MATS_error_OHB_CrossTrack[:], markersize = 1, label = 'Cross-track')
    plot_date(Time_error_MPL[:],r_MATS_error_OHB_InTrack[:], markersize = 1, label = 'Intrack')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS as RCI in m (prediction vs STK')
    legend()
    
    
    #############################################
    """
    "For STK coordinates converted from eci to ecef"
    figure()
    plot_date(current_time_MPL[1:],lat_MATS[1:]/pi*180, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL_STK[1:], lat_MATS_STK[1:], markersize = 1, label = 'STK-Data transformed')
    xlabel('Date')
    ylabel('Geodetic Latitude of MATS in degrees [WGS84 (prob)]')
    legend()
    
    figure()
    plot_date(current_time_MPL_STK[1:],abs(lat_MATS_STK[1:]-lat_MATS[1:]/pi*180), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Latitude of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],long_MATS[1:]/pi*180, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL_STK[1:], long_MATS_STK[1:], markersize = 1, label = 'STK-Data transformed')
    xlabel('Date')
    ylabel('Longitude of MATS in degrees [WGS84 (prob)]')
    legend()
    
    figure()
    plot_date(current_time_MPL_STK[1:],abs(long_MATS_STK[1:]-long_MATS[1:]/pi*180), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Longitude of MATS in degrees')
    legend()
    """
    ##############################################
    
    figure()
    plot_date(Time_MPL[:],Data_MATS['alt_MATS'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:],alt_MATS_STK_FIXED[1:], markersize = 1, label = 'STK-Data')
    #plot_date(current_time_MPL_STK[1:],alt_MATS_STK[1:], markersize = 1, label = 'STK-Data_trans')
    plot_date(current_time_MPL_OHB[1:],alt_MATS_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Altitude of MATS in degrees')
    legend()
    """
    figure()
    plot_date(current_time_MPL[1:],a_ra_MATS[1:]/pi *180, markersize = 1, label = 'Predicted')
    xlabel('Date')
    ylabel('a_ra_MATS of MATS in degrees')
    legend()
    """
    
    figure()
    plot_date(Time_MPL[:], Data_LP['lat_LP'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:], lat_LP_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:], lat_LP_OHB[1:], markersize = 1, label = 'OHB-Data')
    #plot_date(current_time_MPL[1:], - lat_LP_estimated[1:]/pi*180, markersize = 1, label = 'Predicted from orbangle and lat_MATS')
    xlabel('Date')
    ylabel('Latitude of LP in degrees')
    legend()
    
    """
    figure()
    plot_date(current_time_MPL_STK[1:],abs(lat_LP_STK[1:]-Data_LP['lat_LP'][1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:],abs(lat_LP_OHB[1:]-Data_LP['lat_LP'][1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Latitude of LP in degrees [J2000]')
    legend()
    """
    
    figure()
    plot_date(Time_MPL[:],Data_LP['long_LP'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:],long_LP_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],long_LP_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Longitude of LP in degrees')
    legend()
    
    """
    figure()
    plot_date(current_time_MPL_STK[1:],abs(long_LP_STK[1:]-Data_LP['long_LP'][1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:],abs(long_LP_OHB[1:]-Data_LP['long_LP'][1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Longitude of LP in degrees [J2000]')
    legend()
    """
    
    figure()
    plot_date(Time_MPL[:],Data_LP['alt_LP'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:],alt_LP_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],alt_LP_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Altitude of LP in degrees')
    legend()
    
    figure()
    plot_date(Time_error_MPL[:],x_LP_error_OHB[:], markersize = 1, label = 'x')
    plot_date(Time_error_MPL[:],y_LP_error_OHB[:], markersize = 1, label = 'y')
    plot_date(Time_error_MPL[:],z_LP_error_OHB[:], markersize = 1, label = 'z')
    plot_date(Time_error_MPL[:],total_r_LP_error_OHB[:], markersize = 1, label = 'Total error')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of LP in m (prediction vs OHB')
    legend()
    
    figure()
    plot_date(Time_MPL[:],Data_MATS['optical_axis_RA'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:],Ra_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Ra_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Right Ascension in degrees [J2000] (Parallax assumed negligable)')
    legend()
    
    """
    figure()
    plot_date(current_time_MPL_STK[1:],abs(Ra_STK[1:]-Data_MATS['optical_axis_RA'][1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL[1:],abs(Ra_OHB[1:]-Data_MATS['optical_axis_RA'][1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Right Ascension in degrees (STK vs predicted) [J2000] (Parallax assumed negligable)')
    legend()
    """
    """
    figure()
    plot_date(current_time_MPL_STK[1:],abs(Ra_STK[1:]-Ra[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Right Ascension in degrees, (STK vs predicted) [J2000] (Parallax assumed negligable)')
    legend()
    """
    """
    figure()
    plot_date(current_time_MPL_STK[1:],abs(Ra_STK[1:]-Ra_STK[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Right Ascension in degrees, (STK vs STK) [J2000] (Parallax assumed negligable)')
    legend()
    """
    figure()
    plot_date(Time_MPL[:],Data_MATS['optical_axis_Dec'][:], markersize = 1, label = 'Predicted')
    #plot_date(current_time_MPL_STK[1:],Dec_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Dec_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Declination in degrees [J2000] (Parallax assumed negligable)')
    legend()
    
    """
    figure()
    plot_date(current_time_MPL_STK[1:],abs(Dec_STK[1:]-Data_MATS['optical_axis_Dec'][1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:],abs(Dec_OHB[1:]-Data_MATS['optical_axis_Dec'][1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Declination in degrees (STK vs predicted) [J2000] (Parallax assumed negligable)')
    legend()
    """
    """
    figure()
    plot_date(current_time_MPL_STK[1:],abs(Dec_STK[1:]-Dec[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Declination in degrees (STK vs predicted) [J2000] (Parallax assumed negligable)')
    legend()
    """
    """
    figure()
    plot_date(current_time_MPL_STK[1:],abs(Dec_STK[1:]-Dec_STK[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Declination in degrees (STK vs STK) [J2000] (Parallax assumed negligable)')
    legend()
    """
    #figure()
    #plot_date(current_time_MPL[1:], lat_MATS[1:]-lat_LP[1:])
    #plot_date(current_time_MPL[1:], pitch_MATS[1:]-90)
    #figure()
    #plot_date(current_time_MPL[1:],r_MATS[1:][:])
    