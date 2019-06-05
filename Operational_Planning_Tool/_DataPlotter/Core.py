# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:51:48 2019

@author: David
"""

from scipy.spatial.transform import Rotation as R
#from numpy import sin, pi, cos, cross, array, arccos, arctan, dot
from pylab import sin, pi, cos, cross, array, arccos, arctan, dot, norm, transpose, zeros, sqrt, floor, figure, plot, plot_date, datestr2num, xlabel, ylabel, title, legend
import ephem, logging, csv, os, sys, importlib
import pymap3d as pm3d



#import OPT_Config_File
from Operational_Planning_Tool import _Library, _MATS_coordinates, _Globals

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
    date = ephem.Date(Settings['start_date'])
    
    yaw_correction = Settings['yaw_correction']
    
    ephemDate2MatplotDate = datestr2num('1899/12/31 12:00:00')
    
    "Pre-allocate space"
    lat_MATS = zeros((timesteps,1))
    long_MATS = zeros((timesteps,1))
    alt_MATS = zeros((timesteps,1))
    g_ra_MATS = zeros((timesteps,1))
    g_dec_MATS = zeros((timesteps,1))
    x_MATS = zeros((timesteps,1))
    y_MATS = zeros((timesteps,1))
    z_MATS = zeros((timesteps,1))
    r_MATS = zeros((timesteps,3))
    r_MATS_unit_vector = zeros((timesteps,3))
    r_MATS_ECEF = zeros((timesteps,3))
    normal_orbit = zeros((timesteps,3))
    abs_lat_LP = zeros((timesteps,1))
    
    optical_axis = zeros((timesteps,3))
    optical_axis_ECEF = zeros((timesteps,3))
    
    LP_ECEF = zeros((timesteps,3))
    
    MATS_p = zeros((timesteps,1))
    MATS_P = zeros((timesteps,1))
    yaw_offset_angle = zeros((timesteps,1))
    pitch_MATS = zeros((timesteps,1))
    
    Ra = zeros((timesteps,1))
    Dec = zeros((timesteps,1))
    
    sun_angle = zeros((timesteps,1))
    lat_LP = zeros((timesteps,1))
    long_LP = zeros((timesteps,1))
    alt_LP = zeros((timesteps,1))
    normal_orbital = zeros((timesteps,3))
    orbangle_between_LP_MATS_array = zeros((timesteps,1))
    
    current_time = zeros((timesteps,1))
    
    "Constants"
    R_mean = 6371 #Earth radius [km]
    #wgs84_Re = 6378.137 #Equatorial radius of wgs84 spheroid [km]
    # wgs84_Rp = 6356752.3142 #Polar radius of wgs84 spheroid [km]
    U = 398600.4418 #Earth gravitational parameter
    celestial_eq_normal = array([[0,0,1]])
    
    
    
    
    LP_altitude = OPT_Config_File.Timeline_settings()['LP_pointing_altitude']/1000  #Altitude of LP at which MATS center of FOV is looking [km]
    LP_altitude = 227
    
    TLE1 = OPT_Config_File.getTLE()[0]
    TLE2 = OPT_Config_File.getTLE()[1]
        
    
    MATS = ephem.readtle('MATS',TLE1,TLE2)
    current_time[0] = date
    
    for t in range(timesteps):
        
        MATS.compute(current_time[t])
        try:
            current_time[t+1] = ephem.Date(current_time[t]+ephem.second*timestep)
        except IndexError:
            pass
        
        (lat_MATS[t],long_MATS[t],alt_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
                MATS.sublat,MATS.sublong,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
        
        R_earth = _Library.lat_2_R(lat_MATS[t]) #WGS84 radius from latitude of MATS
        
        z_MATS[t] = sin(g_dec_MATS[t])*(alt_MATS[t]+R_earth)
        x_MATS[t] = cos(g_dec_MATS[t])*(alt_MATS[t]+R_earth)* cos(g_ra_MATS[t])
        y_MATS[t] = cos(g_dec_MATS[t])*(alt_MATS[t]+R_earth)* sin(g_ra_MATS[t])
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        
        r_MATS_unit_vector[t,0:3] = r_MATS[t,0:3] / norm(r_MATS[t,0:3])
        
        r_MATS_ECEF[t,0], r_MATS_ECEF[t,1], r_MATS_ECEF[t,2] = pm3d.eci2ecef(
                r_MATS[t,0], r_MATS[t,1], r_MATS[t,2], ephem.Date(current_time[t][0]).datetime())
        
        #Initial Estimated pitch or elevation angle for MATS pointing using R_mean
        if(t == 0):
            orbangle_between_LP_MATS_array[t]= arccos((R_mean+LP_altitude/1000)/(R_mean+alt_MATS[t]))/pi*180
            orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
            
            
        
        
                
        if(t != 0):
            
            # More accurate estimation of the Earths radius below LP
            if( abs(lat_MATS[t])-abs(lat_MATS[t-1]) > 0 ): #Moving towards poles meaning LP is equatorwards compared to MATS
                abs_lat_LP[t] = abs(lat_MATS[t])-orbangle_between_LP_MATS/180*pi #absolute value of estimated latitude of LP in radians
                R_LP = _Library.lat_2_R(abs_lat_LP[t][0]) #Estimated WGS84 radius of LP from latitude
            else:
                abs_lat_LP[t] = abs(lat_MATS[t])+orbangle_between_LP_MATS/180*pi #absolute value of estimated latitude of LP in radians
                R_LP = _Library.lat_2_R(abs_lat_LP[t][0]) #Estimated WGS84 radius of LP from latitude
            
            
            
            # More accurate estimation of pitch angle of MATS using R_LP instead of R_mean
            orbangle_between_LP_MATS_array[t] = array(arccos((R_LP+LP_altitude)/(R_earth+alt_MATS[t]))/pi*180)
            orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
            
            pitch_MATS[t] = orbangle_between_LP_MATS + 90
            
            ############# Calculations of orbital and pointing vectors ############
            "Vector normal to the orbital plane of MATS"
            normal_orbit[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbit[t,0:3] = normal_orbit[t,0:3] / norm(normal_orbit[t,0:3])
            
            if( yaw_correction == True):
                "Calculate intersection between the orbital plane and the equator"
                ascending_node = cross(normal_orbit[t,0:3], celestial_eq_normal)
                
                arg_of_lat = arccos( dot(ascending_node, r_MATS[t,0:3]) / norm(r_MATS[t,0:3]) / norm(ascending_node) ) /pi*180
                
                "To determine if MATS is moving towards the ascending node"
                if( dot(cross( ascending_node, r_MATS[t,0:3]), normal_orbit[t,0:3]) >= 0 ):
                    arg_of_lat = 360 - arg_of_lat
                    
                yaw_offset_angle[t] = Settings['yaw_amplitude'] * cos( arg_of_lat/180*pi - orbangle_between_LP_MATS/180*pi + Settings['yaw_phase']/180*pi )
                #yaw_offset_angle = yaw_offset_angle[0]
                
                
            elif( yaw_correction == False):
                yaw_offset_angle[t] = 4
            
            "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
            rot_mat = _Library.rot_arbit(pitch_MATS[t][0]/180*pi, normal_orbit[t,0:3])
            optical_axis[t,0:3] = (rot_mat @ r_MATS[t])
            optical_axis[t,0:3] = optical_axis[t,0:3] / norm(optical_axis[t,0:3])
            
            "Rotate yaw of pointing direction, meaning to rotate around the vector to MATS"
            rot_mat = _Library.rot_arbit( (-yaw_offset_angle[t][0])/180*pi, r_MATS_unit_vector[t,0:3])
            optical_axis[t,0:3] = rot_mat @ optical_axis[t,0:3]
            optical_axis[t,0:3] = optical_axis[t,0:3]/norm(optical_axis[t,0:3])
            
            optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2] = pm3d.eci2ecef(
                optical_axis[t,0], optical_axis[t,1], optical_axis[t,2], ephem.Date(current_time[t][0]).datetime())
            
            LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0]*1000, r_MATS_ECEF[t][1]*1000, r_MATS_ECEF[t][2]*1000, 
                                       optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
            
            lat_LP[t], long_LP[t], alt_LP[t]  = pm3d.ecef2geodetic(LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2])
            
            Dec[t] = arctan( optical_axis[t,2] / sqrt(optical_axis[t,0]**2 + optical_axis[t,1]**2) ) /pi * 180
            Ra[t] = arccos( dot( [1,0,0], [optical_axis[t,0],optical_axis[t,1],0] ) / norm([optical_axis[t,0],optical_axis[t,1],0]) ) / pi * 180
        
            if( optical_axis[t,1] < 0 ):
                Ra[t] = 360-Ra[t]
            
            
            
    
    
    "Pre-allocate space"
    lat_MATS_OHB = zeros((timesteps,1))
    long_MATS_OHB = zeros((timesteps,1))
    alt_MATS_OHB = zeros((timesteps,1))
    
    x_MATS_OHB = zeros((timesteps,1))
    y_MATS_OHB = zeros((timesteps,1))
    z_MATS_OHB = zeros((timesteps,1))
    r_MATS_OHB = zeros((timesteps,3))
    Velx_MATS_OHB = zeros((timesteps,1))
    Vely_MATS_OHB = zeros((timesteps,1))
    Velz_MATS_OHB = zeros((timesteps,1))
    Vel_MATS_OHB = zeros((timesteps,3))
    x_MATS_OHB_ECEF = zeros((timesteps,1))
    y_MATS_OHB_ECEF = zeros((timesteps,1))
    z_MATS_OHB_ECEF = zeros((timesteps,1))
    r_MATS_OHB_ECEF = zeros((timesteps,3))
    
    LP_ECEF_OHB = zeros((timesteps,3))
    lat_LP_OHB = zeros((timesteps,1))
    long_LP_OHB = zeros((timesteps,1))
    alt_LP_OHB = zeros((timesteps,1))
    
    """
    MATS_lat_OHB = zeros((timesteps,1))
    MATS_long_OHB = zeros((timesteps,1))
    MATS_alt_OHB = zeros((timesteps,1))
    """
    
    q1_MATS_OHB = zeros((timesteps,1))
    q2_MATS_OHB = zeros((timesteps,1))
    q3_MATS_OHB = zeros((timesteps,1))
    q4_MATS_OHB = zeros((timesteps,1))
    
    Euler_angles_SLOF = zeros((timesteps,3))
    Euler_angles_ECI = zeros((timesteps,3))
    
    optical_axis_OHB = zeros((timesteps,3))
    optical_axis_OHB_ECEF = zeros((timesteps,3))
    Ra_OHB = zeros((timesteps,1))
    Dec_OHB = zeros((timesteps,1))
    
    Ra_STK = zeros((timesteps,1))
    Dec_STK = zeros((timesteps,1))
    
    Ra_ECI = zeros((timesteps,1))
    Dec_ECI = zeros((timesteps,1))
    roll_ECI = zeros((timesteps,1))
    
    yaw_SLOF = zeros((timesteps,1))
    pitch_SLOF = zeros((timesteps,1))
    roll_SLOF = zeros((timesteps,1))
    
    z_axis_SLOF = zeros((timesteps,3))
    x_axis_SLOF = zeros((timesteps,3))
    
    with open('tle-29702_29702 Data_handlin.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                
                line_count += 1
            else:
                x_MATS_OHB[line_count-1] = row[0]
                y_MATS_OHB[line_count-1] = row[1]
                z_MATS_OHB[line_count-1] = row[2]
                r_MATS_OHB[line_count-1,0] = row[0]
                r_MATS_OHB[line_count-1,1] = row[1]
                r_MATS_OHB[line_count-1,2] = row[2]
                
                Velx_MATS_OHB[line_count-1] = row[3]
                Vely_MATS_OHB[line_count-1] = row[4]
                Velz_MATS_OHB[line_count-1] = row[5]
                Vel_MATS_OHB[line_count-1,0] = row[3]
                Vel_MATS_OHB[line_count-1,1] = row[4]
                Vel_MATS_OHB[line_count-1,2] = row[5]
                
                x_MATS_OHB_ECEF[line_count-1] = row[6]
                y_MATS_OHB_ECEF[line_count-1] = row[7]
                z_MATS_OHB_ECEF[line_count-1] = row[8]
                r_MATS_OHB_ECEF[line_count-1,0] = row[6]
                r_MATS_OHB_ECEF[line_count-1,1] = row[7]
                r_MATS_OHB_ECEF[line_count-1,2] = row[8]
                
                line_count += 1
            
    with open('Limb_Az4_El-2166Quat.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                
                line_count += 1
            else:
                q1_MATS_OHB[line_count-1] = row[0]
                q2_MATS_OHB[line_count-1] = row[1]
                q3_MATS_OHB[line_count-1] = row[2]
                q4_MATS_OHB[line_count-1] = row[3]
                line_count += 1
                
    with open('Limb_Az-176_El2166_RA_DEC.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                
                line_count += 1
            else:
                Ra_STK[line_count-1] = row[0]
                Dec_STK[line_count-1] = row[1]
                line_count += 1
    
    
    
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
    
    
    "STK azi: 4, el: -21.66 (corresponds to same quaternion from OHB when limb pointing is yaw =4 and negative velocity direction pitch angle = 21.66"
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
        
        
        
        
        "SLOF = Spacecraft Local Orbit Frame"
        z_SLOF = -r_MATS_OHB[t,0:3]
        #z_SLOF = -r_MATS[t,0:3]
        z_SLOF = z_SLOF / norm(z_SLOF)
        x_SLOF = Vel_MATS_OHB[t,0:3]
        x_SLOF = x_SLOF / norm(x_SLOF)
        y_SLOF = cross(z_SLOF,x_SLOF)
        y_SLOF = y_SLOF / norm(y_SLOF)
        
        
        
        dcm_SLOF_coordinate_system = array( ([x_SLOF[0], y_SLOF[0], z_SLOF[0]], [x_SLOF[1], y_SLOF[1], z_SLOF[1]], [x_SLOF[2], y_SLOF[2], z_SLOF[2]]) )
        dcm_change_of_basis_ECI_to_SLOF = transpose(dcm_SLOF_coordinate_system)
        r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_ECI_to_SLOF)
        quat_change_of_basis_ECI_to_SLOF = r_change_of_basis_ECI_to_SLOF.as_quat()
        
        MATS_ECI = R.from_quat([q1_MATS_OHB[t][0], q2_MATS_OHB[t][0], q3_MATS_OHB[t][0], q4_MATS_OHB[t][0]])
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
        
        
        optical_axis_OHB[t,:] = MATS_ECI.apply([0,0,-1])
        optical_axis_OHB[t,:] = optical_axis_OHB[t,:] / norm(optical_axis_OHB[t,:])
        Dec_OHB[t] = arctan( optical_axis_OHB[t,2] / sqrt(optical_axis_OHB[t,0]**2 + optical_axis_OHB[t,1]**2) ) /pi * 180
        Ra_OHB[t] = arccos( dot( [1,0,0], [optical_axis_OHB[t,0],optical_axis_OHB[t,1],0] ) / norm([optical_axis_OHB[t,0],optical_axis_OHB[t,1],0]) ) / pi * 180
        
        if( optical_axis_OHB[t,1] < 0 ):
            Ra_OHB[t] = 360-Ra_OHB[t]
        
        
        
        
        #Euler_angles_ECI[t,:] = MATS_ECI.as_euler('xyz', degrees=True)
        
        Euler_angles_ECI[t,:] = MATS_ECI.as_euler('ZYZ', degrees=True)
        """
        Ra_ECI[t] = Euler_angles_ECI[t,0]
        Dec_ECI[t] = -90+Euler_angles_ECI[t,1]
        roll_ECI[t] = Euler_angles_ECI[t,2]
        
        if( Ra_ECI[t] < 180 ):
            Ra_ECI[t] = Ra_ECI[t]+180
        elif( Ra_ECI[t] >= 180):
            Ra_ECI[t] = Ra_ECI[t] - 180
        """
        
        
        
        MATS_SLOF = r_change_of_basis_ECI_to_SLOF*MATS_ECI
        
        z_axis_SLOF[t,:] = MATS_SLOF.apply([0,0,1])
        x_axis_SLOF[t,:] = MATS_SLOF.apply([1,0,0])
        
        
        
        z_axis_SLOF_x_z = z_axis_SLOF[t,:] - (dot(z_axis_SLOF[t,:], [0,1,0]) * array([0,1,0]) )
        
        z_axis_SLOF_x_y = z_axis_SLOF[t,:] - (dot(z_axis_SLOF[t,:], [0,0,1]) * array([0,0,1]) )
        
        #pitch_SLOF[t] = arccos(dot([0,0,1],z_axis_SLOF_x_z) / (norm([0,0,1]) * norm(z_axis_SLOF_x_z))) /pi*180
        pitch_SLOF[t] = arccos(dot(z_axis_SLOF[t,:],z_axis_SLOF_x_y) / (norm(z_axis_SLOF[t,:]) * norm(z_axis_SLOF_x_y))) /pi*180
        yaw_SLOF[t] = arccos(dot([1,0,0],z_axis_SLOF_x_y) / (norm([1,0,0]) * norm(z_axis_SLOF_x_y))) /pi*180
        
        if( z_axis_SLOF_x_y[1] < 0 ):
            yaw_SLOF[t] = -yaw_SLOF[t]
        if( z_axis_SLOF_x_z[0] > 0 ):
            pitch_SLOF[t] = -pitch_SLOF[t]
        
        
        
        
        Euler_angles_SLOF[t,:] = MATS_SLOF.as_euler('ZYZ', degrees=True)
        #Euler_angles_SLOF[t,:] = MATS_SLOF.as_euler('yzx', degrees=True)
        
        optical_axis_OHB_ECEF[t,0], optical_axis_OHB_ECEF[t,1], optical_axis_OHB_ECEF[t,2] = pm3d.eci2ecef(
                optical_axis_OHB[t,0], optical_axis_OHB[t,1], optical_axis_OHB[t,2], ephem.Date(current_time[t][0]).datetime())
        
        
        
        LP_ECEF_OHB[t,0], LP_ECEF_OHB[t,1], LP_ECEF_OHB[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_OHB_ECEF[t][0]*1000, r_MATS_OHB_ECEF[t][1]*1000, r_MATS_OHB_ECEF[t][2]*1000, 
                                       optical_axis_OHB_ECEF[t,0], optical_axis_OHB_ECEF[t,1], optical_axis_OHB_ECEF[t,2])
        
        lat_LP_OHB[t], long_LP_OHB[t], alt_LP_OHB[t]  = pm3d.ecef2geodetic(LP_ECEF_OHB[t,0], LP_ECEF_OHB[t,1], LP_ECEF_OHB[t,2])
        
        
        
        
        r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2] = pm3d.eci2ecef(
                r_MATS_OHB[t,0]*1000, r_MATS_OHB[t,1]*1000, r_MATS_OHB[t,2]*1000, ephem.Date(current_time[t][0]).datetime())
        
        lat_MATS_OHB[t], long_MATS_OHB[t], alt_MATS_OHB[t]  = pm3d.ecef2geodetic(r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2], deg = True)
        
        
    ########################## Plotter ###########################################
    
    from mpl_toolkits.mplot3d import axes3d
    
    current_time_MPL = ephemDate2MatplotDate + current_time[:]
    
    fig=figure(1)
    ax = fig.add_subplot(111,projection='3d')
    ax.set_xlim3d(-7000000, 7000000)
    ax.set_ylim3d(-7000000, 7000000)
    ax.set_zlim3d(-7000000, 7000000)
    #ax.scatter(r_MATS[1:,0], r_MATS[1:,1], r_MATS[1:,2])
    ax.scatter(r_MATS_OHB_ECEF[1:100,0], r_MATS_OHB_ECEF[1:100,1], r_MATS_OHB_ECEF[1:100,2])
    ax.scatter(LP_ECEF[1:100,0], LP_ECEF[1:100,1], LP_ECEF[1:100,2])
    
    
    figure()
    plot_date(current_time_MPL[1:],yaw_offset_angle[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],Euler_angles_SLOF[1:,0], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Yaw in degrees [z-axis SLOF]')
    legend()
    
    
    figure()
    plot_date(current_time_MPL[1:],pitch_MATS[1:] , markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],Euler_angles_SLOF[1:,1], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Pitch in degrees [intrinsic y-axis SLOF]')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],Euler_angles_SLOF[1:,2], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Roll in degrees [intrinsic z-axis SLOF]')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],lat_MATS[1:]/pi*180, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:], lat_MATS_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Latitude of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],long_MATS[1:]/pi*180, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:], long_MATS_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Longitude of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],alt_MATS[1:] *1000, markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],alt_MATS_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Altitude of MATS in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:], lat_LP[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:], lat_LP_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Latitude of LP in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],long_LP[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],long_LP_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Longitude of LP in degrees')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],alt_LP[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],alt_LP_OHB[1:], markersize = 1, label = 'OHB-Data')
    xlabel('Date')
    ylabel('Altitude of LP in degrees')
    legend()
    
    
    figure()
    plot_date(current_time_MPL[1:],Ra[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],Ra_OHB[1:], markersize = 1, label = 'OHB-Data')
    plot_date(current_time_MPL[1:],Ra_STK[1:], markersize = 1)
    xlabel('Date')
    ylabel('Right Ascension in degrees [J2000] (Parallax assumed negligable)')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(Ra_OHB[1:]-Ra[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Right Ascension in degrees [J2000] (Parallax assumed negligable)')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],Dec[1:], markersize = 1, label = 'Predicted')
    plot_date(current_time_MPL[1:],Dec_OHB[1:], markersize = 1, label = 'OHB-Data')
    plot_date(current_time_MPL[1:],Dec_STK[1:], markersize = 1)
    xlabel('Date')
    ylabel('Declination in degrees [J2000] (Parallax assumed negligable)')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:],abs(Dec_OHB[1:]-Dec[1:]), markersize = 1, label = 'Abs Error')
    xlabel('Date')
    ylabel('Absolute error in Declination in degrees [J2000] (Parallax assumed negligable)')
    legend()
    
    figure()
    plot_date(current_time_MPL[1:], lat_MATS[1:]/pi*180-lat_LP[1:])
    plot_date(current_time_MPL[1:], pitch_MATS[1:]-90)
    #figure()
    #plot_date(current_time_MPL[1:],r_MATS[1:][:])