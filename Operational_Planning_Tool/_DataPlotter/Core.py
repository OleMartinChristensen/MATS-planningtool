# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:51:48 2019

@author: David
"""

from scipy.spatial.transform import Rotation as R
#from numpy import sin, pi, cos, cross, array, arccos, arctan, dot
from pylab import sin, pi, cos, cross, array, arccos, arctan, dot, tan, norm, transpose, zeros, sqrt, floor, figure, plot, plot_date, datestr2num, xlabel, ylabel, title, legend, date2num
import ephem, logging, csv, os, sys, importlib, h5py, skyfield.api
import datetime as DT

from Operational_Planning_Tool import _Library, _MATS_coordinates, _Globals

#import OPT_Config_File


OPT_Config_File = importlib.import_module(_Globals.Config_File)




def Data_Plotter():
    """
    
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
    
    #timesteps = 29
    Settings = OPT_Config_File.Timeline_settings()
    
    
    "Simulation length and timestep"
    log_timestep = 3600
    timestep = 10 #In seconds
    duration = Settings['duration']
    timesteps = int(floor(duration / timestep))+1
    timesteps = 300
    #timesteps = 10000
    start_from = 6000
    #start_from = 0
    date = ephem.Date(Settings['start_date'])
    
    yaw_correction = Settings['yaw_correction']
    
    
    ephemDate2MatplotDate = datestr2num('1899/12/31 12:00:00')
    
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
    normal_orbit = zeros((timesteps,3))
    normal_orbit_ECEF = zeros((timesteps,3))
    lat_LP_estimated = zeros((timesteps,1))
    
    optical_axis = zeros((timesteps,3))
    optical_axis_ECEF = zeros((timesteps,3))
    MATS_2_LP = zeros((timesteps,3))
    
    r_H_offset_normal = zeros((timesteps,3))
    r_V_offset_normal = zeros((timesteps,3))
    MATS_2_first_LP = zeros((timesteps,3))
    MATS_2_LP_V_offset_plane = zeros((timesteps,3))
    MATS_2_LP_H_offset_plane = zeros((timesteps,3))
    MATS_2_LP_vert_offset = zeros((timesteps,1))
    MATS_2_LP_hori_offset = zeros((timesteps,1))
    first_r_LP = zeros((timesteps,3))
    
    r_LP = zeros((timesteps,3))
    r_LP_ECEF = zeros((timesteps,3))
    
    MATS_p = zeros((timesteps,1))
    MATS_P = zeros((timesteps,1))
    yaw_offset_angle = zeros((timesteps,1))
    pitch_MATS = zeros((timesteps,1))
    yaw_offset_angle_ECI = zeros((timesteps,1))
    
    Ra = zeros((timesteps,1))
    Dec = zeros((timesteps,1))
    
    sun_angle = zeros((timesteps,1))
    lat_LP = zeros((timesteps,1))
    long_LP = zeros((timesteps,1))
    alt_LP = zeros((timesteps,1))
    normal_orbital = zeros((timesteps,3))
    orbangle_between_LP_MATS_array = zeros((timesteps,1))
    lat_flag = 0
    R_earth_MATS = zeros((timesteps,1))
    current_time = zeros((timesteps,1))
    current_time_MPL = zeros((timesteps,1))
    
    "Constants"
    R_mean = 6371 #Earth radius [km]
    #wgs84_Re = 6378.137 #Equatorial radius of wgs84 spheroid [km]
    # wgs84_Rp = 6356752.3142 #Polar radius of wgs84 spheroid [km]
    U = 398600.4418 #Earth gravitational parameter
    celestial_eq_normal = array([[0,0,1]])
    earth_north_pole = zeros((timesteps,3))
    
    
    
    LP_altitude = OPT_Config_File.Timeline_settings()['LP_pointing_altitude']/1000  #Altitude of LP at which MATS center of FOV is looking [km]
    
    
    TLE1 = OPT_Config_File.getTLE()[0]
    TLE2 = OPT_Config_File.getTLE()[1]
        
    
    MATS = ephem.readtle('MATS',TLE1,TLE2)
    #current_time[0] = date
    
    ts = skyfield.api.load.timescale()
    MATS_skyfield = skyfield.api.EarthSatellite(TLE1, TLE2)
    
    for t in range(timesteps):
        
        
        current_time[t] = ephem.Date(date+ephem.second*(timestep*t+start_from))
        
        
        
        ################### Skyfield ##############################
        current_time[t] = ephem.Date(date+ephem.second*(timestep*t+start_from))
        current_time_datetime = ephem.Date(date+ephem.second*(timestep*t+start_from)).datetime()
        year = current_time_datetime.year
        month = current_time_datetime.month
        day = current_time_datetime.day
        hour = current_time_datetime.hour
        minute = current_time_datetime.minute
        second = current_time_datetime.second + current_time_datetime.microsecond/1000000
        
        current_time_skyfield = ts.utc(year, month, day, hour, minute, second)
        
        MATS_geo = MATS_skyfield.at(current_time_skyfield)
        r_MATS[t] = MATS_geo.position.km
        MATS_distance = MATS_geo.distance().km
        MATS_subpoint = MATS_geo.subpoint()
        lat_MATS[t] = MATS_subpoint.latitude.radians
        long_MATS[t] = MATS_subpoint.longitude.radians
        alt_MATS[t] = MATS_subpoint.elevation.km
        
        
        """
        MATS.compute(current_time[t], epoch = '2000/01/01 11:58:55.816')
        
        
        
        (lat_MATS[t],long_MATS[t],alt_MATS[t],a_ra_MATS[t],a_dec_MATS[t])= (
                MATS.sublat, MATS.sublong, MATS.elevation/1000, MATS.a_ra, MATS.a_dec)
        
        
        
        ###########################################################
        #First iteration of determining MATS distance from center of Earth
        R_earth_MATS[t] = _Library.lat_2_R(lat_MATS[t]) #WGS84 radius from latitude of MATS
        
        z_MATS[t] = sin(a_dec_MATS[t])*(alt_MATS[t]+R_earth_MATS[t])
        x_MATS[t] = cos(a_dec_MATS[t])*(alt_MATS[t]+R_earth_MATS[t])* cos(a_ra_MATS[t])
        y_MATS[t] = cos(a_dec_MATS[t])*(alt_MATS[t]+R_earth_MATS[t])* sin(a_ra_MATS[t])
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        """
        
        r_MATS_unit_vector[t,0:3] = r_MATS[t,0:3] / norm(r_MATS[t,0:3])
        
        
        r_MATS_ECEF[t,0], r_MATS_ECEF[t,1], r_MATS_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                r_MATS[t,0], r_MATS[t,1], r_MATS[t,2], ephem.Date(current_time[t][0]).datetime())
        
        """
        lat_MATS[t], long_MATS[t], alt_MATS[t]  = _MATS_coordinates.ECEF2lla(r_MATS_ECEF[t,0]*1000, r_MATS_ECEF[t,1]*1000, r_MATS_ECEF[t,2]*1000)
        
        lat_MATS[t] = lat_MATS[t] / 180*pi
        long_MATS[t] = long_MATS[t] / 180*pi
        alt_MATS[t] = alt_MATS[t] / 1000
        """
        ##############################################################
        
        
        
        """
        ###########################################################
        #Second iteration of determining MATS distance from center of Earth
        R_earth_MATS[t] = _Library.lat_2_R(lat_MATS[t]) #WGS84 radius from latitude of MATS
        
        z_MATS[t] = sin(a_dec_MATS[t])*(alt_MATS[t]+R_earth_MATS[t])
        x_MATS[t] = cos(a_dec_MATS[t])*(alt_MATS[t]+R_earth_MATS[t])* cos(a_ra_MATS[t])
        y_MATS[t] = cos(a_dec_MATS[t])*(alt_MATS[t]+R_earth_MATS[t])* sin(a_ra_MATS[t])
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        
        r_MATS_unit_vector[t,0:3] = r_MATS[t,0:3] / norm(r_MATS[t,0:3])
        
        """
        r_MATS_ECEF[t,0], r_MATS_ECEF[t,1], r_MATS_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                r_MATS[t,0], r_MATS[t,1], r_MATS[t,2], ephem.Date(current_time[t][0]).datetime())
        
        """
        lat_MATS[t], long_MATS[t], alt_MATS[t]  = _MATS_coordinates.ECEF2lla(r_MATS_ECEF[t,0]*1000, r_MATS_ECEF[t,1]*1000, r_MATS_ECEF[t,2]*1000)
        
        lat_MATS[t] = lat_MATS[t] / 180*pi
        long_MATS[t] = long_MATS[t] / 180*pi
        alt_MATS[t] = alt_MATS[t] / 1000
        ################################################################
        """
        
        #Semi-Major axis of MATS, assuming circular orbit
        MATS_p[t] = norm(r_MATS[t,0:3])
        
        #Orbital Period of MATS
        MATS_P[t] = 2*pi*sqrt(MATS_p[t]**3/U)
        
        ################################################################
        
        
        #Initial Estimated pitch or elevation angle for MATS pointing using R_mean
        if(t == 0):
            orbangle_between_LP_MATS_array[t]= arccos((R_mean+LP_altitude)/(MATS_distance))/pi*180
            #orbangle_between_LP_MATS_array[t]= arccos((R_mean+LP_altitude)/(MATS_distance))/pi*180
            orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
            time_between_LP_and_MATS = MATS_P[t][0]*orbangle_between_LP_MATS/360
            timesteps_between_LP_and_MATS = int(time_between_LP_and_MATS / timestep)
        
    #for t in range(timesteps):
                
        if(t != 0):
            if( t >= timesteps_between_LP_and_MATS):
                lat_LP_estimated[t] = lat_MATS[t-timesteps_between_LP_and_MATS]
                R_earth_LP = _Library.lat_2_R(lat_LP_estimated[t][0])
            else:
                date_of_MATSlat_is_equal_2_current_LPlat = ephem.Date(current_time[t] - ephem.second * timesteps_between_LP_and_MATS * timestep).datetime()
                lat_LP_estimated[t] = _Library.lat_calculator( MATS_skyfield,date_of_MATSlat_is_equal_2_current_LPlat )
                R_earth_LP = _Library.lat_2_R(lat_LP_estimated[t][0])
            
            "Vector normal to the orbital plane of MATS"
            normal_orbit[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbit[t,0:3] = normal_orbit[t,0:3] / norm(normal_orbit[t,0:3])
            
            normal_orbit_ECEF[t,0], normal_orbit_ECEF[t,1], normal_orbit_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                normal_orbit[t,0], normal_orbit[t,1], normal_orbit[t,2], ephem.Date(current_time[t][0]).datetime())
        
            
            # More accurate estimation of pitch angle of MATS using R_earth_LP instead of R_mean
            orbangle_between_LP_MATS_array[t] = array(arccos((R_earth_LP+LP_altitude)/(MATS_distance))/pi*180)
            #orbangle_between_LP_MATS_array[t] = array(arccos((R_mean+LP_altitude)/(R_mean+alt_MATS[t]))/pi*180)
            orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
            
            
            
            pitch_MATS[t] = orbangle_between_LP_MATS + 90
            
            
            ############# Calculations of orbital and pointing vectors ############
            
            if( yaw_correction == True):
                "Calculate intersection between the orbital plane and the equator"
                ascending_node = cross(normal_orbit_ECEF[t,0:3], celestial_eq_normal)
                
                arg_of_lat = arccos( dot(ascending_node, r_MATS_ECEF[t,0:3]) / norm(r_MATS_ECEF[t,0:3]) / norm(ascending_node) ) /pi*180
                
                "To determine if MATS is moving towards the ascending node"
                if( dot(cross( ascending_node, r_MATS_ECEF[t,0:3]), normal_orbit_ECEF[t,0:3]) >= 0 ):
                    arg_of_lat = 360 - arg_of_lat
                    
                yaw_offset_angle[t] = Settings['yaw_amplitude'] * cos( arg_of_lat/180*pi - orbangle_between_LP_MATS/180*pi + Settings['yaw_phase']/180*pi )
                #yaw_offset_angle[t] = -4.11 * cos( arg_of_lat/180*pi - orbangle_between_LP_MATS/180*pi )
                #yaw_offset_angle = yaw_offset_angle[0]
                
                "Calculate intersection between the orbital plane and the equator"
                ascending_node = cross(normal_orbit[t,0:3], celestial_eq_normal)
                
                arg_of_lat = arccos( dot(ascending_node, r_MATS[t,0:3]) / norm(r_MATS[t,0:3]) / norm(ascending_node) ) /pi*180
                
                "To determine if MATS is moving towards the ascending node"
                if( dot(cross( ascending_node, r_MATS[t,0:3]), normal_orbit[t,0:3]) >= 0 ):
                    arg_of_lat = 360 - arg_of_lat
                    
                yaw_offset_angle_ECI[t] = Settings['yaw_amplitude'] * cos( arg_of_lat/180*pi - orbangle_between_LP_MATS/180*pi + Settings['yaw_phase']/180*pi )
                #yaw_offset_angle[t] = -4.11 * cos( arg_of_lat/180*pi - orbangle_between_LP_MATS/180*pi )
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
            
            r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0]*1000, r_MATS_ECEF[t][1]*1000, r_MATS_ECEF[t][2]*1000, 
                                       optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
            
            lat_LP[t], long_LP[t], alt_LP[t]  = _MATS_coordinates.ECEF2lla(r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2])
            
            Dec[t] = arctan( optical_axis[t,2] / sqrt(optical_axis[t,0]**2 + optical_axis[t,1]**2) ) /pi * 180
            Ra[t] = arccos( dot( [1,0,0], [optical_axis[t,0],optical_axis[t,1],0] ) / norm([optical_axis[t,0],optical_axis[t,1],0]) ) / pi * 180
            
            if( optical_axis[t,1] < 0 ):
                Ra[t] = 360-Ra[t]
            
            r_LP[t,0], r_LP[t,1], r_LP[t,2] = _MATS_coordinates.ecef2eci( r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2], 
                                           ephem.Date(current_time[t][0]).datetime())
                
            
            if( t == 1 ):
                first_r_LP[t] = r_LP[t]
                
            
            if( t >= 2):
                
                earth_rotation_speed = 360 / (23*3600 + 56*60+ 4) #degrees/s
                
                rot_mat = _Library.rot_arbit((earth_rotation_speed*timestep)/180*pi, [0,0,1])
                first_r_LP[t] = rot_mat @ first_r_LP[t-1]
                
                
                MATS_2_first_LP[t] = first_r_LP[t] - r_MATS[t]*1000
                #MATS_2_first_LP[t] = MATS_2_first_LP[t] / norm(MATS_2_first_LP[t])
                MATS_2_LP[t] = r_LP[t] - r_MATS[t]*1000
                #MATS_2_LP[t] = MATS_2_LP[t] / norm(MATS_2_LP[t])
                
                '''Rotate 'vector to MATS', to represent vector normal to satellite H-offset plane,
                which will be used to project stars onto it which allows the H-offset of stars to be found'''
                rot_mat = _Library.rot_arbit((orbangle_between_LP_MATS)/180*pi, normal_orbit[t,0:3])
                r_H_offset_normal[t,0:3] = (rot_mat @ r_MATS[t])
                r_H_offset_normal[t,0:3] = r_H_offset_normal[t,0:3] / norm(r_H_offset_normal[t,0:3])
                
                "If pointing direction has a Yaw defined, Rotate yaw of normal to pointing direction H-offset plane, meaning to rotate around the vector to MATS"
                rot_mat = _Library.rot_arbit(-yaw_offset_angle[t][0]/180*pi, r_MATS_unit_vector[t,0:3])
                r_H_offset_normal[t,0:3] = (rot_mat @ r_H_offset_normal[t])
                r_H_offset_normal[t,0:3] = r_H_offset_normal[t,0:3]/norm(r_H_offset_normal[t,0:3])
                
                '''Rotate orbital plane normal to make it into pointing V-offset plane normal 
                which will be used to project stars onto it which allows the V-offset of stars to be found'''
                r_V_offset_normal[t,0:3] = (rot_mat @ normal_orbit[t])
                r_V_offset_normal[t,0:3] = r_V_offset_normal[t,0:3]/norm(r_V_offset_normal[t,0:3])
                
                
                "Project 'star vectors' ontop pointing H-offset and V-offset plane"
                MATS_2_LP_V_offset_plane[t] = MATS_2_first_LP[t] - dot(MATS_2_first_LP[t],r_V_offset_normal[t,0:3]) * r_V_offset_normal[t,0:3]
    
                MATS_2_LP_H_offset_plane[t] = MATS_2_first_LP[t] - dot(MATS_2_first_LP[t],r_H_offset_normal[t]) * r_H_offset_normal[t]
    
                "Dot product to get the Vertical and Horizontal angle offset of the star in the FOV"
                MATS_2_LP_vert_offset[t] = arccos(dot(MATS_2_LP[t],MATS_2_LP_V_offset_plane[t]) / (norm(MATS_2_LP[t])) / norm(MATS_2_LP_V_offset_plane[t]) ) /pi*180
                MATS_2_LP_hori_offset[t] = arccos(dot(MATS_2_LP[t],MATS_2_LP_H_offset_plane[t]) / (norm(MATS_2_LP[t])) / norm(MATS_2_LP_H_offset_plane[t]) ) /pi*180
                
                "Determine sign of off-set angle where positive V-offset angle is when looking at higher altitude"
                if( dot(cross(MATS_2_LP[t],MATS_2_LP_V_offset_plane[t]),r_V_offset_normal[t,0:3]) > 0 ):
                    MATS_2_LP_vert_offset[t] = -MATS_2_LP_vert_offset[t]
                if( dot(cross(MATS_2_LP[t],MATS_2_LP_H_offset_plane[t]),r_H_offset_normal[t]) > 0 ):
                    MATS_2_LP_hori_offset[t] = -MATS_2_LP_hori_offset[t]
                
            
            
            
            
            
    yaw_offset_angle_error = yaw_offset_angle_ECI - yaw_offset_angle
    
    "Pre-allocate space"
    
    
    lat_MATS_STK_FIXED = zeros((timesteps,1))
    long_MATS_STK_FIXED = zeros((timesteps,1))
    alt_MATS_STK_FIXED = zeros((timesteps,1))
    lat_MATS_STK = zeros((timesteps,1))
    long_MATS_STK = zeros((timesteps,1))
    alt_MATS_STK = zeros((timesteps,1))
    
    x_MATS_STK = zeros((timesteps,1))
    y_MATS_STK = zeros((timesteps,1))
    z_MATS_STK = zeros((timesteps,1))
    r_MATS_STK = zeros((timesteps,3))
    Velx_MATS_STK = zeros((timesteps,1))
    Vely_MATS_STK = zeros((timesteps,1))
    Velz_MATS_STK = zeros((timesteps,1))
    Vel_MATS_STK = zeros((timesteps,3))
    x_MATS_STK_FIXED = zeros((timesteps,1))
    y_MATS_STK_FIXED = zeros((timesteps,1))
    z_MATS_STK_FIXED = zeros((timesteps,1))
    r_MATS_STK_FIXED = zeros((timesteps,3))
    r_MATS_STK_ECEF = zeros((timesteps,3))
    
    LP_ECEF_STK = zeros((timesteps,3))
    lat_LP_STK = zeros((timesteps,1))
    long_LP_STK = zeros((timesteps,1))
    alt_LP_STK = zeros((timesteps,1))
    
    """
    MATS_lat_STK = zeros((timesteps,1))
    MATS_long_STK = zeros((timesteps,1))
    MATS_alt_STK = zeros((timesteps,1))
    """
    
    q1_MATS_STK = zeros((timesteps,1))
    q2_MATS_STK = zeros((timesteps,1))
    q3_MATS_STK = zeros((timesteps,1))
    q4_MATS_STK = zeros((timesteps,1))
    
    Euler_angles_SLOF_STK = zeros((timesteps,3))
    Euler_angles_ECI_STK = zeros((timesteps,3))
    
    optical_axis_STK = zeros((timesteps,3))
    optical_axis_STK_ECEF = zeros((timesteps,3))
    Ra_STK = zeros((timesteps,1))
    Dec_STK = zeros((timesteps,1))
    
    Ra_STK = zeros((timesteps,1))
    Dec_STK = zeros((timesteps,1))
    
    Ra_ECI_STK = zeros((timesteps,1))
    Dec_ECI_STK = zeros((timesteps,1))
    roll_ECI_STK = zeros((timesteps,1))
    
    yaw_SLOF_STK = zeros((timesteps,1))
    pitch_SLOF_STK = zeros((timesteps,1))
    roll_SLOF_STK = zeros((timesteps,1))
    
    z_axis_SLOF_STK = zeros((timesteps,3))
    x_axis_SLOF_STK = zeros((timesteps,3))
    
    #with open('tle-54321_54321 Data_handlin_OHB_TLE.csv') as csv_file:
    with open('OHB_timeshifted2sTLE_ICRF_addedEOP.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        interestingrows=[row for idx, row in enumerate(csv_reader) if idx in range(start_from,100000)]
        line_count = 0
        row_count = 0
        for row in interestingrows:
            
            if line_count == 0:
                
                line_count += 1
                
            elif( row_count % timestep != 0):
                row_count += 1
            else:
                try:
                    x_MATS_STK[line_count-1] = row[0]
                    y_MATS_STK[line_count-1] = row[1]
                    z_MATS_STK[line_count-1] = row[2]
                    r_MATS_STK[line_count-1,0] = row[0]
                    r_MATS_STK[line_count-1,1] = row[1]
                    r_MATS_STK[line_count-1,2] = row[2]
                    
                    Velx_MATS_STK[line_count-1] = row[3]
                    Vely_MATS_STK[line_count-1] = row[4]
                    Velz_MATS_STK[line_count-1] = row[5]
                    Vel_MATS_STK[line_count-1,0] = row[3]
                    Vel_MATS_STK[line_count-1,1] = row[4]
                    Vel_MATS_STK[line_count-1,2] = row[5]
                    
                    x_MATS_STK_FIXED[line_count-1] = row[6]
                    y_MATS_STK_FIXED[line_count-1] = row[7]
                    z_MATS_STK_FIXED[line_count-1] = row[8]
                    r_MATS_STK_FIXED[line_count-1,0] = row[6]
                    r_MATS_STK_FIXED[line_count-1,1] = row[7]
                    r_MATS_STK_FIXED[line_count-1,2] = row[8]
                    
                    line_count += 1
                    row_count += 1
                except IndexError:
                    break
            
    with open('Limb_Az0_El-2166Quat_OHB_TLE.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        interestingrows=[row for idx, row in enumerate(csv_reader) if idx in range(start_from,100000)]
        line_count = 0
        row_count = 0
        for row in interestingrows:
            
            if line_count == 0:
                
                line_count += 1
                
            elif( row_count % timestep != 0):
                row_count += 1
            else:
                try:
                    q1_MATS_STK[line_count-1] = row[0]
                    q2_MATS_STK[line_count-1] = row[1]
                    q3_MATS_STK[line_count-1] = row[2]
                    q4_MATS_STK[line_count-1] = row[3]
                    line_count += 1
                    row_count += 1
                except IndexError:
                    break
                
    """
    with open('Limb_Az-176_El2166_RA_DEC.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                
                line_count += 1
            else:
                try:
                    Ra_STK[line_count-1] = row[0]
                    Dec_STK[line_count-1] = row[1]
                    line_count += 1
                except IndexError:
                    break
    """
    
    with open('Limb_Az0_El2166_RA_DEC_OHB_TLE.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        interestingrows=[row for idx, row in enumerate(csv_reader) if idx in range(start_from,100000)]
        line_count = 0
        row_count = 0
        for row in interestingrows:
            
            if line_count == 0:
                
                line_count += 1
                
            elif( row_count % timestep != 0):
                row_count += 1
            else:
                try:
                    Ra_STK[line_count-1] = row[0]
                    Dec_STK[line_count-1] = row[1]
                    line_count += 1
                    row_count += 1
                except IndexError:
                    break
    
    
    """
    R_MATS2 = array( [0,0,-1000] )
    R_MATS2 = array( [-sin(pi/6)*1000, 0, -1000*cos(pi/6)] )
    #R_MATS2 = array( [cos(pi/6)*sin(45/180*pi), cos(pi/6)*cos(45/180*pi), -sin(pi/6)] )
    R_MATS1 = array( [-1,0,0] )
    """
    """
    "STK azi: -176, el: 21.66"
    R_MATS1 = array([-4881.29,-3211.77,-3787.19]) 
    R_MATS2 = array([-6128.317075,-3305.48242,52.845877]) 
    velocity_direction = array([-0.4301,0.91727,7.497867])
    orbital_plane = cross(velocity_direction,R_MATS2)
    MATS_ECI = R.from_quat([-0.246471,0.950986,0.014485,0.186192])
    #SLOF_ECI = R.from_quat([.0.674999, -0.219479, -0.693002, 0.126306])
    
    
    "STK azi: 4, el: -21.66 (corresponds to same quaternion from STK when limb pointing is yaw =4 and negative velocity direction pitch angle = 21.66"
    R_MATS1 = array([-4881.29,-3211.77,-3787.19]) 
    R_MATS2 = array([-5963.576027, -2899.016085,2125.263181]) 
    velocity_direction = array([1.591933,1.954875,7.133624])
    orbital_plane = cross(velocity_direction,R_MATS2)
    MATS_ECI = R.from_quat([0.040543, -0.024971, -0.970654, 0.235720])
    #SLOF_ECI = R.from_quat([-0.772552, -0.236159, -0.582259, 0.091467])
    
    geoCen_lat = arctan( R_MATS2[2] / sqrt(R_MATS2[0]**2 + R_MATS2[1]**2) ) /pi*180
    """
    
    """
    orbital_plane = cross(R_MATS1,R_MATS2)
    velocity_direction = cross(orbital_plane, R_MATS2)
    """
    
    for t in range(timesteps):
        
        #orbital_plane = cross(r_MATS[t],r_MATS[t-1])
        #velocity_direction = cross(orbital_plane, r_MATS[t,0:3])
        #R_MATS2 = r_MATS[t,0:3]
        
        t_STK = t# * timestep
        
        
        "SLOF = Spacecraft Local Orbit Frame"
        z_SLOF = -r_MATS_STK[t_STK,0:3]
        #z_SLOF = -r_MATS[t,0:3]
        z_SLOF = z_SLOF / norm(z_SLOF)
        x_SLOF = Vel_MATS_STK[t_STK,0:3]
        x_SLOF = x_SLOF / norm(x_SLOF)
        y_SLOF = cross(z_SLOF,x_SLOF)
        y_SLOF = y_SLOF / norm(y_SLOF)
        
        
        
        dcm_SLOF_coordinate_system = array( ([x_SLOF[0], y_SLOF[0], z_SLOF[0]], [x_SLOF[1], y_SLOF[1], z_SLOF[1]], [x_SLOF[2], y_SLOF[2], z_SLOF[2]]) )
        dcm_change_of_basis_ECI_to_SLOF = transpose(dcm_SLOF_coordinate_system)
        r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_ECI_to_SLOF)
        quat_change_of_basis_ECI_to_SLOF = r_change_of_basis_ECI_to_SLOF.as_quat()
        
        MATS_ECI_STK = R.from_quat([q1_MATS_STK[t_STK][0], q2_MATS_STK[t_STK][0], q3_MATS_STK[t_STK][0], q4_MATS_STK[t_STK][0]])
        #MATS_ECI = R.random()
        
        
        
        """
        pitch = -pi/6
        yaw = pi/10
        roll = pi/18
        
        MATS_ECI_pitch = R.from_quat([y_SLOF[0]*sin(pitch/2), y_SLOF[1]*sin(pitch/2), y_SLOF[2]*sin(pitch/2), cos(pitch/2)])
        MATS_ECI_yaw = R.from_quat([z_SLOF[0]*sin(yaw/2), z_SLOF[1]*sin(yaw/2), z_SLOF[2]*sin(yaw/2), cos(yaw/2)])
        MATS_ECI = MATS_ECI_yaw*MATS_ECI_pitch
        
        rollAXIS = x_SLOF
        MATS_ECI_roll = R.from_quat( [rollAXIS[0]*sin(roll/2), rollAXIS[1]*sin(roll/2), rollAXIS[2]*sin(roll/2), cos(roll/2)])
        MATS_ECI = MATS_ECI_roll*MATS_ECI
        """
        
        
        optical_axis_STK[t,:] = MATS_ECI_STK.apply([0,0,-1])
        optical_axis_STK[t,:] = optical_axis_STK[t,:] / norm(optical_axis_STK[t,:])
        
        Dec_STK[t] = arctan( optical_axis_STK[t,2] / sqrt(optical_axis_STK[t,0]**2 + optical_axis_STK[t,1]**2) ) /pi * 180
        Ra_STK[t] = arccos( dot( [1,0,0], [optical_axis_STK[t,0],optical_axis_STK[t,1],0] ) / norm([optical_axis_STK[t,0],optical_axis_STK[t,1],0]) ) / pi * 180
        
        if( optical_axis_STK[t,1] < 0 ):
            Ra_STK[t] = 360-Ra_STK[t]
        
        
        
        
        #Euler_angles_ECI[t,:] = MATS_ECI.as_euler('xyz', degrees=True)
        
        Euler_angles_ECI_STK[t,:] = MATS_ECI_STK.as_euler('ZYZ', degrees=True)
        """
        Ra_ECI[t] = Euler_angles_ECI[t,0]
        Dec_ECI[t] = -90+Euler_angles_ECI[t,1]
        roll_ECI[t] = Euler_angles_ECI[t,2]
        
        if( Ra_ECI[t] < 180 ):
            Ra_ECI[t] = Ra_ECI[t]+180
        elif( Ra_ECI[t] >= 180):
            Ra_ECI[t] = Ra_ECI[t] - 180
        """
        
        
        
        MATS_SLOF_STK = r_change_of_basis_ECI_to_SLOF*MATS_ECI_STK
        
        z_axis_SLOF_STK[t,:] = MATS_SLOF_STK.apply([0,0,1])
        x_axis_SLOF_STK[t,:] = MATS_SLOF_STK.apply([1,0,0])
        
        
        
        z_axis_SLOF_x_z_STK = z_axis_SLOF_STK[t,:] - (dot(z_axis_SLOF_STK[t,:], [0,1,0]) * array([0,1,0]) )
        
        z_axis_SLOF_x_y_STK = z_axis_SLOF_STK[t,:] - (dot(z_axis_SLOF_STK[t,:], [0,0,1]) * array([0,0,1]) )
        
        #pitch_SLOF[t] = arccos(dot([0,0,1],z_axis_SLOF_x_z) / (norm([0,0,1]) * norm(z_axis_SLOF_x_z))) /pi*180
        pitch_SLOF_STK[t] = arccos(dot(z_axis_SLOF_STK[t,:],z_axis_SLOF_x_y_STK) / (norm(z_axis_SLOF_STK[t,:]) * norm(z_axis_SLOF_x_y_STK))) /pi*180
        yaw_SLOF_STK[t] = arccos(dot([1,0,0],z_axis_SLOF_x_y_STK) / (norm([1,0,0]) * norm(z_axis_SLOF_x_y_STK))) /pi*180
        
        if( z_axis_SLOF_x_y_STK[1] < 0 ):
            yaw_SLOF_STK[t] = -yaw_SLOF_STK[t]
        if( z_axis_SLOF_x_z_STK[0] > 0 ):
            pitch_SLOF_STK[t] = -pitch_SLOF_STK[t]
        
        
        
        
        Euler_angles_SLOF_STK[t,:] = MATS_SLOF_STK.as_euler('ZYZ', degrees=True)
        #Euler_angles_SLOF[t,:] = MATS_SLOF.as_euler('yzx', degrees=True)
        
        optical_axis_STK_ECEF[t,0], optical_axis_STK_ECEF[t,1], optical_axis_STK_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                optical_axis_STK[t,0], optical_axis_STK[t,1], optical_axis_STK[t,2], ephem.Date(current_time[t][0]).datetime())
        
        
        
        lat_MATS_STK_FIXED[t], long_MATS_STK_FIXED[t], alt_MATS_STK_FIXED[t]  = _MATS_coordinates.ECEF2lla(r_MATS_STK_FIXED[t,0]*1000, r_MATS_STK_FIXED[t,1]*1000, r_MATS_STK_FIXED[t,2]*1000)
        
        #lat_MATS_STK_FIXED[t] = lat_MATS_STK_FIXED[t] / pi*180
        #long_MATS_STK_FIXED[t] = long_MATS_STK_FIXED[t] / pi*180
        
        
        ######################################################################
        
        r_MATS_STK_ECEF[t,0], r_MATS_STK_ECEF[t,1], r_MATS_STK_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                r_MATS_STK[t_STK,0]*1000, r_MATS_STK[t_STK,1]*1000, r_MATS_STK[t_STK,2]*1000, ephem.Date(current_time[t][0]).datetime())
        
        lat_MATS_STK[t], long_MATS_STK[t], alt_MATS_STK[t]  = _MATS_coordinates.ECEF2lla(r_MATS_STK_ECEF[t,0], r_MATS_STK_ECEF[t,1], r_MATS_STK_ECEF[t,2])
        #lat_MATS_STK[t] = lat_MATS_STK[t] / pi*180
        #long_MATS_STK[t] = long_MATS_STK[t] / pi*180
        
        
        LP_ECEF_STK[t,0], LP_ECEF_STK[t,1], LP_ECEF_STK[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_STK_ECEF[t][0], r_MATS_STK_ECEF[t][1], r_MATS_STK_ECEF[t][2], 
                                       optical_axis_STK_ECEF[t,0], optical_axis_STK_ECEF[t,1], optical_axis_STK_ECEF[t,2])
        
        lat_LP_STK[t], long_LP_STK[t], alt_LP_STK[t]  = _MATS_coordinates.ECEF2lla(LP_ECEF_STK[t,0], LP_ECEF_STK[t,1], LP_ECEF_STK[t,2])
        #lat_LP_STK[t] = lat_LP_STK[t] / pi*180
        #long_LP_STK[t] = long_LP_STK[t] / pi*180
        
        #R_earth_MATS[t][t] = norm(r_MATS_STK[t,:]*1000)-alt_MATS_STK[t]
        
        
        
        
     
    
    OHB_data = h5py.File('MATS_scenario_sim_20190630.h5','r')
    
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
    
    
    timesteps_OHB = len(Time_State_OHB)
    timesteps_OHB = timesteps
    #timesteps = 1440
    
    "Allocate Space"
    current_time_MPL_OHB = zeros((timesteps_OHB,1))
    #current_time = []
    current_time_state = []
    current_time_attitude = []
    
    
    lat_MATS_OHB = zeros((timesteps_OHB,1))
    long_MATS_OHB = zeros((timesteps_OHB,1))
    alt_MATS_OHB = zeros((timesteps_OHB,1))
    
    q1_MATS_OHB = zeros((timesteps_OHB,1))
    q2_MATS_OHB = zeros((timesteps_OHB,1))
    q3_MATS_OHB = zeros((timesteps_OHB,1))
    q4_MATS_OHB = zeros((timesteps_OHB,1))
    
    Vel_MATS_OHB = zeros((timesteps_OHB,3))
    r_MATS_OHB = zeros((timesteps_OHB,3))
    r_MATS_OHB_ECEF = zeros((timesteps_OHB,3))
    r_MATS_OHB_ECEF2 = zeros((timesteps_OHB,3))
    optical_axis_OHB = zeros((timesteps_OHB,3))
    r_LP_ECEF_OHB = zeros((timesteps_OHB,3))
    lat_LP_OHB = zeros((timesteps_OHB,1))
    long_LP_OHB = zeros((timesteps_OHB,1))
    alt_LP_OHB = zeros((timesteps_OHB,1))
    
    Dec_OHB = zeros((timesteps_OHB,1))
    Ra_OHB = zeros((timesteps_OHB,1))
    
    Time_State_OHB_float = zeros((timesteps_OHB,1))
    Time_Attitude_OHB_float = zeros((timesteps_OHB,1))
    
    Euler_angles_SLOF_OHB = zeros((timesteps_OHB,3))
    Euler_angles_ECI_OHB = zeros((timesteps_OHB,3))
    
    optical_axis_OHB = zeros((timesteps_OHB,3))
    optical_axis_OHB_ECEF = zeros((timesteps_OHB,3))
    
    
    
    
    yaw_SLOF_OHB = zeros((timesteps_OHB,1))
    pitch_SLOF_OHB = zeros((timesteps_OHB,1))
    roll_SLOF_OHB = zeros((timesteps_OHB,1))
    
    z_axis_SLOF_OHB = zeros((timesteps_OHB,3))
    x_axis_SLOF_OHB = zeros((timesteps_OHB,3))
    
    #for t in range(timesteps_OHB):
    for t in range( timesteps_OHB ):
        
        t_OHB = t * timestep + start_from
        
        
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
        
        r_LP_ECEF_OHB[t,0], r_LP_ECEF_OHB[t,1], r_LP_ECEF_OHB[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2], 
                                       optical_axis_OHB_ECEF[t,0], optical_axis_OHB_ECEF[t,1], optical_axis_OHB_ECEF[t,2])
        
        lat_LP_OHB[t], long_LP_OHB[t], alt_LP_OHB[t]  = _MATS_coordinates.ECEF2lla(r_LP_ECEF_OHB[t,0], r_LP_ECEF_OHB[t,1], r_LP_ECEF_OHB[t,2])
        
        
        #R_earth_MATS[t][t] = norm(r_MATS_OHB[t,:]*1000)-alt_MATS_OHB[t]
        
        current_time_MPL_OHB[t] = date2num(current_time_state[t])
    
    

    
    ########################## Plotter ###########################################
    
    from mpl_toolkits.mplot3d import axes3d
    
    current_time_MPL = ephemDate2MatplotDate + current_time[:]
    
    
    
    fig=figure(1)
    ax = fig.add_subplot(111,projection='3d')
    ax.set_xlim3d(-7000000, 7000000)
    ax.set_ylim3d(-7000000, 7000000)
    ax.set_zlim3d(-7000000, 7000000)
    #ax.scatter(r_MATS[1:,0], r_MATS[1:,1], r_MATS[1:,2])
    ax.scatter(r_MATS_STK_ECEF[1:100,0], r_MATS_STK_ECEF[1:100,1], r_MATS_STK_ECEF[1:100,2])
    ax.scatter(r_LP_ECEF[1:100,0], r_LP_ECEF[1:100,1], r_LP_ECEF[1:100,2])
    #ax.scatter(r_MATS_ECEF[1:100,0]*1000, r_MATS_ECEF[1:100,1]*1000, r_MATS_ECEF[1:100,2]*1000)
    #ax.scatter(r_LP_ECEF[1:100,0], r_LP_ECEF[1:100,1], r_LP_ECEF[1:100,2])
    
    fig=figure(2)
    plot(MATS_2_LP_hori_offset[2:], MATS_2_LP_vert_offset[2:])
    xlabel('Horizontal offset in degrees')
    ylabel('Vertitcal offset in degrees')
    axes = fig.gca()
    axes.set_xlim([-2.8,2.8])
    axes.set_ylim([-2.8,2.8])
    
    figure()
    plot_date(current_time_MPL[1:],yaw_offset_angle[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],Euler_angles_SLOF_STK[1:,0], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Euler_angles_SLOF_OHB[1:,0], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Yaw in degrees [z-axis SLOF]')
    legend()
    
    
    figure()
    plot_date(current_time_MPL[1:],pitch_MATS[1:] , markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],Euler_angles_SLOF_STK[1:,1], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Euler_angles_SLOF_OHB[1:,1], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Pitch in degrees [intrinsic y-axis SLOF]')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],Euler_angles_SLOF_STK[1:,2], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Euler_angles_SLOF_OHB[1:,2], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Roll in degrees [intrinsic z-axis SLOF]')
    legend()
    
    ###################################
    
    figure()
    plot_date(current_time_MPL[1:],lat_MATS[1:]/pi*180, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:], lat_MATS_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:], lat_MATS_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Geodetic Latitude of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(lat_MATS_STK[1:]-lat_MATS[1:]/pi*180), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:],abs(lat_MATS_OHB[1:]-lat_MATS[1:]/pi*180), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Latitude of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],long_MATS[1:]/pi*180, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:], long_MATS_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:], long_MATS_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Longitude of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(long_MATS_STK[1:]-long_MATS[1:]/pi*180), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:],abs(long_MATS_OHB[1:]-long_MATS[1:]/pi*180), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Longitude of MATS in degrees')
    legend()
    
    ####################################
    
    total_r_MATS_error_STK = zeros((timesteps,1))
    total_r_MATS_error_STK_transformed = zeros((timesteps,1))
    total_r_MATS_error_OHB = zeros((timesteps,1))
    total_r_MATS_error_OHB_STK = zeros((timesteps,1))
    total_r_MATS_error_OHB_STK_transformed = zeros((timesteps,1))
    
    r_MATS_error_STK_transformed_RCI = zeros((timesteps,3))
    
    r_MATS_error_STK_transformed_ECI = abs(r_MATS*1000-r_MATS_STK*1000)
    
    
    r_MATS_error_STK = abs(r_MATS_ECEF*1000-r_MATS_STK_FIXED*1000)
    r_MATS_error_STK_transformed = abs(r_MATS_ECEF*1000-r_MATS_STK_ECEF)
    r_MATS_error_OHB = abs(r_MATS_ECEF*1000-r_MATS_OHB_ECEF)
    r_MATS_error_OHB_STK = abs(r_MATS_STK_FIXED*1000-r_MATS_OHB_ECEF)
    r_MATS_error_OHB_STK_transformed = abs(r_MATS_STK_ECEF-r_MATS_OHB_ECEF)
    
    in_track = cross( normal_orbit[t], r_MATS_unit_vector[t])
    
    
    for t in range(timesteps):
        in_track = cross( normal_orbit[t], r_MATS_unit_vector[t])
        change_of_basis_RCI = transpose( array( ( (r_MATS_unit_vector[t,0], normal_orbit[t,0], in_track[0]),
            (r_MATS_unit_vector[t,1], normal_orbit[t,1], in_track[1]), 
            (r_MATS_unit_vector[t,2], normal_orbit[t,2], in_track[2]) ) ) )
        r_MATS_error_STK_transformed_RCI[t] =  change_of_basis_RCI @ r_MATS_error_STK_transformed_ECI[t]
        
        
        total_r_MATS_error_STK[t] = norm(r_MATS_error_STK[t,:])
        total_r_MATS_error_OHB[t] = norm(r_MATS_error_OHB[t,:])
        total_r_MATS_error_OHB_STK[t] = norm(r_MATS_error_OHB_STK[t,:])
        total_r_MATS_error_STK_transformed[t] = norm(r_MATS_error_STK_transformed[t,:])
        total_r_MATS_error_OHB_STK_transformed[t] = norm(r_MATS_error_OHB_STK_transformed[t,:])
        
    
    figure()
    plot_date(current_time_MPL[1:],r_MATS_error_STK_transformed_RCI[1:,0], markersize = 1, label = 'Radial')
    plot_date(current_time_MPL[1:],r_MATS_error_STK_transformed_RCI[1:,1], markersize = 1, label = 'Cross-track')
    plot_date(current_time_MPL[1:],r_MATS_error_STK_transformed_RCI[1:,2], markersize = 1, label = 'Intrack')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS as RCI in m (prediction vs STK')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],r_MATS_error_STK[1:,0], markersize = 1, label = 'x')
    plot_date(current_time_MPL[1:],r_MATS_error_STK[1:,1], markersize = 1, label = 'y')
    plot_date(current_time_MPL[1:],r_MATS_error_STK[1:,2], markersize = 1, label = 'z')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS in m (prediction vs STK')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],r_MATS_error_STK_transformed[1:,0], markersize = 1, label = 'x')
    plot_date(current_time_MPL[1:],r_MATS_error_STK_transformed[1:,1], markersize = 1, label = 'y')
    plot_date(current_time_MPL[1:],r_MATS_error_STK_transformed[1:,2], markersize = 1, label = 'z')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS in m (prediction vs STK_transformed')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],r_MATS_error_OHB[1:,0], markersize = 1, label = 'x')
    plot_date(current_time_MPL[1:],r_MATS_error_OHB[1:,1], markersize = 1, label = 'y')
    plot_date(current_time_MPL[1:],r_MATS_error_OHB[1:,2], markersize = 1, label = 'z')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS in m (prediction vs OHB')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],r_MATS_error_OHB_STK[1:,0], markersize = 1, label = 'x')
    plot_date(current_time_MPL[1:],r_MATS_error_OHB_STK[1:,1], markersize = 1, label = 'y')
    plot_date(current_time_MPL[1:],r_MATS_error_OHB_STK[1:,2], markersize = 1, label = 'z')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS in m (STK vs OHB')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],r_MATS_error_OHB_STK_transformed[1:,0], markersize = 1, label = 'x')
    plot_date(current_time_MPL[1:],r_MATS_error_OHB_STK_transformed[1:,1], markersize = 1, label = 'y')
    plot_date(current_time_MPL[1:],r_MATS_error_OHB_STK_transformed[1:,2], markersize = 1, label = 'z')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of MATS in m (STK_transformed vs OHB')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],total_r_MATS_error_STK[1:], markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL[1:],total_r_MATS_error_OHB[1:], markersize = 1, label = 'Prediction vs OHB')
    plot_date(current_time_MPL[1:],total_r_MATS_error_OHB_STK[1:], markersize = 1, label = 'STK vs OHB')
    plot_date(current_time_MPL[1:],total_r_MATS_error_OHB_STK_transformed[1:], markersize = 1, label = 'STK_transformed vs OHB')
    plot_date(current_time_MPL[1:],total_r_MATS_error_STK_transformed[1:], markersize = 1, label = 'Prediction vs STK_transformed')
    xlabel('Date')
    ylabel('Total Absolute error in ECEF position of MATS in m')
    legend()
    
    #############################################
    """
    "For STK coordinates converted from eci to ecef"
    figure()
    plot_date(current_time_MPL[1:],lat_MATS[1:]/pi*180, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:], lat_MATS_STK[1:], markersize = 1, label = 'STK-Data transformed')
    xlabel('Date')
    ylabel('Geodetic Latitude of MATS in degrees [WGS84 (prob)]')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(lat_MATS_STK[1:]-lat_MATS[1:]/pi*180), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Latitude of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],long_MATS[1:]/pi*180, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:], long_MATS_STK[1:], markersize = 1, label = 'STK-Data transformed')
    xlabel('Date')
    ylabel('Longitude of MATS in degrees [WGS84 (prob)]')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(long_MATS_STK[1:]-long_MATS[1:]/pi*180), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Longitude of MATS in degrees')
    legend()
    """
    ##############################################
    
    figure()
    plot_date(current_time_MPL[1:],alt_MATS[1:] *1000, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],alt_MATS_STK_FIXED[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL[1:],alt_MATS_STK[1:], markersize = 1, label = 'STK-Data_trans')
    plot_date(current_time_MPL_OHB[1:],alt_MATS_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Altitude of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],a_ra_MATS[1:]/pi *180, markersize = 1, label = 'Predicted')
    xlabel('Date')
    ylabel('a_ra_MATS of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:], lat_LP[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:], lat_LP_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:], lat_LP_OHB[1:], markersize = 1, label = 'OHB-Data')
    plot_date(current_time_MPL[1:], lat_LP_estimated[1:]/pi*180, markersize = 1, label = 'Predicted from orbangle and lat_MATS')
    xlabel('Date')
    ylabel('Latitude of LP in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(lat_LP_STK[1:]-lat_LP[1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:],abs(lat_LP_OHB[1:]-lat_LP[1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Latitude of LP in degrees [J2000]')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],long_LP[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],long_LP_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],long_LP_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Longitude of LP in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(long_LP_STK[1:]-long_LP[1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:],abs(long_LP_OHB[1:]-long_LP[1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Longitude of LP in degrees [J2000]')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],alt_LP[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],alt_LP_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],alt_LP_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Altitude of LP in degrees')
    legend()
    
    
    
    
    total_r_LP_error_OHB = zeros((timesteps,1))
    
    r_LP_error_OHB = abs(r_LP_ECEF-r_LP_ECEF_OHB)
    for t in range(timesteps):
        total_r_LP_error_OHB[t] = norm(r_LP_error_OHB[t,:])
    
    figure()
    plot_date(current_time_MPL[1:],r_LP_error_OHB[1:,0], markersize = 1, label = 'x')
    plot_date(current_time_MPL[1:],r_LP_error_OHB[1:,1], markersize = 1, label = 'y')
    plot_date(current_time_MPL[1:],r_LP_error_OHB[1:,2], markersize = 1, label = 'z')
    xlabel('Date')
    ylabel('Absolute error in ECEF position of LP in m (prediction vs OHB')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],total_r_LP_error_OHB[1:], markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Total Absolute error in ECEF position of LP in m')
    legend()
    
    
    
    figure()
    plot_date(current_time_MPL[1:],Ra[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],Ra_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Ra_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Right Ascension in degrees [J2000] (Parallax assumed negligable)')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(Ra_STK[1:]-Ra[1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL[1:],abs(Ra_OHB[1:]-Ra[1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Right Ascension in degrees (STK vs predicted) [J2000] (Parallax assumed negligable)')
    legend()
    """
    figure()
    plot_date(current_time_MPL[1:],abs(Ra_STK[1:]-Ra[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Right Ascension in degrees, (STK vs predicted) [J2000] (Parallax assumed negligable)')
    legend()
    """
    """
    figure()
    plot_date(current_time_MPL[1:],abs(Ra_STK[1:]-Ra_STK[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Right Ascension in degrees, (STK vs STK) [J2000] (Parallax assumed negligable)')
    legend()
    """
    figure()
    plot_date(current_time_MPL[1:],Dec[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],Dec_STK[1:], markersize = 1, label = 'STK-Data')
    plot_date(current_time_MPL_OHB[1:],Dec_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Declination in degrees [J2000] (Parallax assumed negligable)')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(Dec_STK[1:]-Dec[1:]), markersize = 1, label = 'Prediction vs STK')
    plot_date(current_time_MPL_OHB[1:],abs(Dec_OHB[1:]-Dec[1:]), markersize = 1, label = 'Prediction vs OHB')
    xlabel('Date')
    ylabel('Absolute error in Declination in degrees (STK vs predicted) [J2000] (Parallax assumed negligable)')
    legend()
    """
    figure()
    plot_date(current_time_MPL[1:],abs(Dec_STK[1:]-Dec[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Declination in degrees (STK vs predicted) [J2000] (Parallax assumed negligable)')
    legend()
    """
    """
    figure()
    plot_date(current_time_MPL[1:],abs(Dec_STK[1:]-Dec_STK[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Declination in degrees (STK vs STK) [J2000] (Parallax assumed negligable)')
    legend()
    """
    #figure()
    #plot_date(current_time_MPL[1:], lat_MATS[1:]-lat_LP[1:])
    #plot_date(current_time_MPL[1:], pitch_MATS[1:]-90)
    #figure()
    #plot_date(current_time_MPL[1:],r_MATS[1:][:])
    