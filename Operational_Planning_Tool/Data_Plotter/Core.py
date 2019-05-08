# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:51:48 2019

@author: David
"""

from scipy.spatial.transform import Rotation as R
from numpy import sin, pi, cos, cross, array, arccos, arctan, dot
from pylab import norm, transpose, zeros, sqrt
import ephem

from Operational_Planning_Tool import Library




def Data_Plotter(data):
    
    timesteps = 29
    
    "Pre-allocate space"
    lat_MATS = zeros((timesteps,1))
    long_MATS = zeros((timesteps,1))
    altitude_MATS = zeros((timesteps,1))
    g_ra_MATS = zeros((timesteps,1))
    g_dec_MATS = zeros((timesteps,1))
    x_MATS = zeros((timesteps,1))
    y_MATS = zeros((timesteps,1))
    z_MATS = zeros((timesteps,1))
    r_MATS = zeros((timesteps,3))
    
    Euler_angles_SLOF = zeros((timesteps,3))
    Euler_angles_ECI = zeros((timesteps,3))
    
    optical_axis = zeros((timesteps,3))
    Ra = zeros((timesteps,1))
    Dec = zeros((timesteps,1))
    
    Ra_ECI = zeros((timesteps,1))
    Dec_ECI = zeros((timesteps,1))
    roll_ECI = zeros((timesteps,1))
    
    yaw_SLOF = zeros((timesteps,1))
    pitch_SLOF = zeros((timesteps,1))
    roll_SLOF = zeros((timesteps,1))
    
    z_axis_SLOF = zeros((timesteps,3))
    x_axis_SLOF = zeros((timesteps,3))
    
    TLE1 = '1 26702U 01007A   18231.91993126  .00000590  00000-0  00000-0 0  9994'
    TLE2= '2 26702 97.61000 65.95030 0000001 0.000001 359.9590 14.97700580100  4'
        
    
    MATS = ephem.readtle('MATS',TLE1,TLE2)
    current_time = ephem.Date('2018/9/3 08:00:40')
    
    for t in range(timesteps):
        
        MATS.compute(current_time)
        current_time = ephem.Date(current_time+ephem.second*2)
        
        (lat_MATS[t],long_MATS[t],altitude_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
                MATS.sublat,MATS.sublong,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
        
        R_earth = Library.lat_2_R(lat_MATS[t]) #WGS84 radius from latitude of MATS
        
        z_MATS[t] = sin(g_dec_MATS[t])*(altitude_MATS[t]+R_earth)
        x_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_earth)* cos(g_ra_MATS[t])
        y_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_earth)* sin(g_ra_MATS[t])
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        
        "dcm = Directional cosine matrix, ECI = Earth-centered Inertial"
        
        
        #yaw = R.from_quat([0, 0, sin(pi/20), cos(pi/20)])
        #pitch = R.from_quat([sin(pi/20), cos(pi/20)*sin(pi/8)*, 0, cos(pi/8)])
        """
        R_MATS2 = array( [0,0,-1000] )
        R_MATS2 = array( [-sin(pi/6)*1000, 0, -1000*cos(pi/6)] )
        #R_MATS2 = array( [cos(pi/6)*sin(45/180*pi), cos(pi/6)*cos(45/180*pi), -sin(pi/6)] )
        R_MATS1 = array( [-1,0,0] )
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
        orbital_plane = cross(R_MATS1,R_MATS2)
        velocity_direction = cross(orbital_plane, R_MATS2)
        """
        
        if( t != 0):
            #orbital_plane = cross(r_MATS[t],r_MATS[t-1])
            #velocity_direction = cross(orbital_plane, r_MATS[t,0:3])
            #R_MATS2 = r_MATS[t,0:3]
            
            "SLOF = Spacecraft Local Orbit Frame"
            y_SLOF = orbital_plane
            y_SLOF = y_SLOF / norm(y_SLOF)
            z_SLOF = -R_MATS2
            #z_SLOF = -r_MATS[t,0:3]
            z_SLOF = z_SLOF / norm(z_SLOF)
            x_SLOF = cross(y_SLOF,z_SLOF)
            x_SLOF = x_SLOF / norm(x_SLOF)
            """
            "SLOF = Spacecraft Local Orbit Frame"
            z_SLOF = -R_MATS2
            #z_SLOF = -r_MATS[t,0:3]
            z_SLOF = z_SLOF / norm(z_SLOF)
            x_SLOF = velocity_direction
            x_SLOF = x_SLOF / norm(x_SLOF)
            y_SLOF = cross(z_SLOF,x_SLOF)
            y_SLOF = y_SLOF / norm(y_SLOF)
            """
            '''
            "SLOF = Spacecraft Local Orbit Frame"
            y_SLOF = orbital_plane
            y_SLOF = y_SLOF / norm(y_SLOF)
            z_SLOF = -R_MATS2
            #z_SLOF = -r_MATS[t,0:3]
            z_SLOF = z_SLOF / norm(z_SLOF)
            x_SLOF = cross(y_SLOF,z_SLOF)
            x_SLOF = x_SLOF / norm(x_SLOF)
            '''
            
            dcm_SLOF_coordinate_system = array( ([x_SLOF[0], y_SLOF[0], z_SLOF[0]], [x_SLOF[1], y_SLOF[1], z_SLOF[1]], [x_SLOF[2], y_SLOF[2], z_SLOF[2]]) )
            dcm_change_of_basis_ECI_to_SLOF = transpose(dcm_SLOF_coordinate_system)
            r_change_of_basis_ECI_to_SLOF = R.from_dcm(dcm_change_of_basis_ECI_to_SLOF)
            quat_change_of_basis_ECI_to_SLOF = r_change_of_basis_ECI_to_SLOF.as_quat()
            
            
            "Define a pitch, yaw, roll rotation"
            pitch = -pi/6
            yaw = pi/10
            roll = pi/18
            
            
            r_pitch = R.from_quat([0, sin(-pi/8), 0, cos(-pi/8)])
            r_yaw = R.from_quat([0, 0, sin(pi/20), cos(pi/20)])
            r_roll = R.from_quat([sin(pi/16), 0, 0, cos(pi/16)])
            #r_roll = R.from_euler('Z', 25, degrees=True)
            #MATS_ECI = r_pitch * r_roll
            #MATS_ECI = r_yaw * MATS_ECI
            
            #MATS_ECI = r_pitch * r_roll
            #MATS_ECI = r_yaw * MATS_ECI
            
            #MATS_ECI = r_yaw * r_pitch
            #MATS_ECI = r_roll * MATS_ECI
            
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
            
            
            optical_axis[t,:] = MATS_ECI.apply([0,0,-1])
            Dec[t] = arctan( optical_axis[t,2] / sqrt(optical_axis[t,0]**2 + optical_axis[t,1]**2) ) /pi * 180
            Ra[t] = arccos( dot( [1,0,0], [optical_axis[t,0],optical_axis[t,1],0] ) / norm([optical_axis[t,0],optical_axis[t,1],0]) ) / pi * 180
            
            if( optical_axis[t,1] < 0 ):
                Ra[t] = 360-Ra[t]
            
            
            
            
            #Euler_angles_ECI[t,:] = MATS_ECI.as_euler('xyz', degrees=True)
            
            Euler_angles_ECI[t,:] = MATS_ECI.as_euler('ZYZ', degrees=True)
            
            Ra_ECI[t] = Euler_angles_ECI[t,0]
            Dec_ECI[t] = -90+Euler_angles_ECI[t,1]
            roll_ECI[t] = Euler_angles_ECI[t,2]
            
            if( Ra_ECI[t] < 180 ):
                Ra_ECI[t] = Ra_ECI[t]+180
            elif( Ra_ECI[t] >= 180):
                Ra_ECI[t] = Ra_ECI[t] - 180
                
            
            
            """
            if( abs(Euler_angles_ECI[t,0]) >= 0.1):
                
                Euler_angles_ECI[t,:] = MATS_ECI.as_euler('ZYX', degrees=True)
                yaw_ECI[t] = Euler_angles_ECI[t,0]
                pitch_ECI[t] = Euler_angles_ECI[t,1]
                roll_ECI[t] = Euler_angles_ECI[t,2]
            """
            #MATS_ECI = R.from_euler('yzx',[-pi/4,pi/10,pi/20])
            
            
            
            MATS_SLOF = r_change_of_basis_ECI_to_SLOF*MATS_ECI
            
            z_axis_SLOF[t,:] = MATS_SLOF.apply([0,0,1])
            x_axis_SLOF[t,:] = MATS_SLOF.apply([1,0,0])
            
            
            
            "Project 'star vectors' ontop pointing H-offset and V-offset plane"
            z_axis_SLOF_x_z = z_axis_SLOF[t,:] - (dot(z_axis_SLOF[t,:], [0,1,0]) * array([0,1,0]) )
            
            z_axis_SLOF_x_y = z_axis_SLOF[t,:] - (dot(z_axis_SLOF[t,:], [0,0,1]) * array([0,0,1]) )
            
            #pitch_SLOF[t] = arccos(dot([0,0,1],z_axis_SLOF_x_z) / (norm([0,0,1]) * norm(z_axis_SLOF_x_z))) /pi*180
            pitch_SLOF[t] = arccos(dot(z_axis_SLOF[t,:],z_axis_SLOF_x_y) / (norm(z_axis_SLOF[t,:]) * norm(z_axis_SLOF_x_y))) /pi*180
            yaw_SLOF[t] = arccos(dot([1,0,0],z_axis_SLOF_x_y) / (norm([1,0,0]) * norm(z_axis_SLOF_x_y))) /pi*180
            
            if( z_axis_SLOF_x_y[1] < 0 ):
                yaw_SLOF[t] = -yaw_SLOF[t]
            if( z_axis_SLOF_x_z[0] > 0 ):
                pitch_SLOF[t] = -pitch_SLOF[t]
            
            #roll?
            
            
            Euler_angles_SLOF[t,:] = MATS_SLOF.as_euler('ZYZ', degrees=True)
            #Euler_angles_SLOF[t,:] = MATS_SLOF.as_euler('yzx', degrees=True)
            """
            pitch_SLOF[t] = Euler_angles_SLOF[t,0]
            yaw_SLOF[t] = Euler_angles_SLOF[t,1]
            roll_SLOF[t] = Euler_angles_SLOF[t,2]
            
            
            if( abs(Euler_angles_SLOF[t,2]) >= 0.1):
                Euler_angles_SLOF[t,:] = MATS_SLOF.as_euler('yzx', degrees=True)
                pitch_SLOF[t]= Euler_angles_SLOF[t,0]
                yaw_SLOF[t] = Euler_angles_SLOF[t,1]
                roll_SLOF[t] = Euler_angles_SLOF[t,2]
            """
            #Euler_angles_SLOF[t,:] = MATS_SLOF.as_euler('XZY', degrees=True)
            #Euler_angles_SLOF = MATS_SLOF.as_euler('zxy', degrees=True)
            #print(Euler_angles_SLOF)
            
            
            
            
            
            #yaw_SLOF = Euler_angles_SLOF[0]
            #pitch_SLOF = Euler_angles_SLOF[1]
            
            """
            #r_yaw_SLOF = R.from_quat([z_SLOF[0]*sin(yaw_SLOF/180*pi/2), z_SLOF[1]*sin(yaw_SLOF/180*pi/2), z_SLOF[2]*sin(yaw_SLOF/180*pi/2), cos(yaw_SLOF/180*pi/2)])
            r_yaw_SLOF = R.from_quat([0, 0, sin(yaw_SLOF/180*pi/2), cos(yaw_SLOF/180*pi/2)])
            #dcm_yaw_SLOF = yaw_SLOF.as_dcm()
            
            "pitch_plane coordinate system expressed in SLOF"
            y_pitchPlane = r_yaw_SLOF.apply([0,1,0])
            y_pitchPlane = y_pitchPlane / norm(y_pitchPlane)
            z_pitchPlane = [0,0,1]
            z_pitchPlane = z_pitchPlane / norm(z_pitchPlane)
            x_pitchPlane = [1,0,0]
            x_pitchPlane = x_pitchPlane / norm(x_pitchPlane)
            '''
            y_pitchPlane = r_yaw_SLOF.apply(-orbital_plane)
            y_pitchPlane = y_pitchPlane / norm(y_pitchPlane)
            z_pitchPlane = -R_MATS2
            z_pitchPlane = z_pitchPlane / norm(z_pitchPlane)
            x_pitchPlane = cross(y_pitchPlane,z_pitchPlane)
            x_pitchPlane = x_pitchPlane / norm(x_pitchPlane)
            '''
            
            dcm_pitchPlane_coordinate_system = array( ([x_pitchPlane[0], y_pitchPlane[0], z_pitchPlane[0]], [x_pitchPlane[1], y_pitchPlane[1], z_pitchPlane[1]], [x_pitchPlane[2], y_pitchPlane[2], z_pitchPlane[2]]) )
            dcm_change_of_basis_SLOF_to_pitchPlane = transpose(dcm_pitchPlane_coordinate_system)
            
            
            
            r_change_of_basis_SLOF_to_pitchPlane = R.from_dcm(dcm_change_of_basis_SLOF_to_pitchPlane)
            quat_change_of_basis_SLOF_to_pitchPlane = r_change_of_basis_SLOF_to_pitchPlane.as_quat()
            
            r_MATS_pitchPlane_from_SLOF = R.from_quat(quat_change_of_basis_SLOF_to_pitchPlane)
            
            '''
            dcm_pitchPlane = change_of_basis_SLOF_to_pitchPlane @ dcm_SLOF
            MATS_pitchPlane = R.from_dcm(dcm_pitchPlane)
            '''
            
            Euler_angles_pitchPlane = r_MATS_pitchPlane_from_SLOF.as_euler('yzx', degrees=True)
            
            #pitch = Euler_angles_pitchPlane[0][0]
            pitch = Euler_angles_pitchPlane[0]
            """