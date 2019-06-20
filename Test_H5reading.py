# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 10:360023:15 2019

@author: David
"""


import h5py, ephem, importlib
import pymap3d as pm3d
import datetime as DT
from pylab import pi, sqrt, zeros, norm, array, cross, transpose, arctan, arccos, dot
from pylab import figure, plot, plot_date, datestr2num, xlabel, ylabel, title, legend, date2num
from scipy.spatial.transform import Rotation as R

from Operational_Planning_Tool import _Library, _MATS_coordinates, _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)



OHB_data = h5py.File('MATS_scenario_sim.h5','r')

root = OHB_data['root']

x_MATS_OHB = root['acoOnGnssStateJ2000_x']['raw']
y_MATS_OHB = root['acoOnGnssStateJ2000_y']['raw']
z_MATS_OHB = root['acoOnGnssStateJ2000_z']['raw']

vel_x_MATS_OHB = root['acoOnGnssStateJ2000_vx']['raw']
vel_y_MATS_OHB = root['acoOnGnssStateJ2000_vy']['raw']
vel_z_MATS_OHB = root['acoOnGnssStateJ2000_vz']['raw']

q1_MATS_OHB = root['afoTmAreAttitudeState_0']['raw']
q2_MATS_OHB = root['afoTmAreAttitudeState_1']['raw']
q3_MATS_OHB = root['afoTmAreAttitudeState_2']['raw']
q4_MATS_OHB = root['afoTmAreAttitudeState_3']['raw']

days = root['acoOnGnssStateJ2000_z']['receptionDate']
milliseconds = root['acoOnGnssStateJ2000_z']['receptionTime']


Time_OHB = root['acoOnGnssStateTime']['raw']

timesteps = len(Time_OHB)
timesteps = 14400
current_time_MPL = zeros((timesteps,1))

x_MATS_OHB_ECEF = zeros((timesteps,1))
y_MATS_OHB_ECEF = zeros((timesteps,1))
z_MATS_OHB_ECEF = zeros((timesteps,1))
lat_MATS_OHB = zeros((timesteps,1))
long_MATS_OHB = zeros((timesteps,1))
alt_MATS_OHB = zeros((timesteps,1))

Vel_MATS_OHB = zeros((timesteps,3))
r_MATS_OHB = zeros((timesteps,3))
r_MATS_OHB_ECEF = zeros((timesteps,3))
optical_axis_OHB = zeros((timesteps,3))
r_LP_ECEF_OHB = zeros((timesteps,3))
lat_LP_OHB = zeros((timesteps,1))
long_LP_OHB = zeros((timesteps,1))
alt_LP_OHB = zeros((timesteps,1))

Dec_OHB = zeros((timesteps,1))
Ra_OHB = zeros((timesteps,1))


lat_MATS_STK = zeros((timesteps,1))
long_MATS_STK = zeros((timesteps,1))
alt_MATS_STK = zeros((timesteps,1))


Euler_angles_SLOF = zeros((timesteps,3))
Euler_angles_ECI = zeros((timesteps,3))

optical_axis_OHB = zeros((timesteps,3))
optical_axis_OHB_ECEF = zeros((timesteps,3))

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

for t in range(timesteps):
    
    t_OHB = t + 208
    #Time_OHB_datetime = ephem.Date(Time_OHB[t]).datetime()
    
    current_time = DT.datetime(2000,1,1)+DT.timedelta(days = int(days[t_OHB]), milliseconds = int(milliseconds[t_OHB]))
    
    
    r_MATS_OHB[t,0] = x_MATS_OHB[t_OHB] 
    r_MATS_OHB[t,1] = y_MATS_OHB[t_OHB] 
    r_MATS_OHB[t,2] = z_MATS_OHB[t_OHB] 
    
    Vel_MATS_OHB[t,0] = vel_x_MATS_OHB[t_OHB] 
    Vel_MATS_OHB[t,1] = vel_y_MATS_OHB[t_OHB] 
    Vel_MATS_OHB[t,2] = vel_z_MATS_OHB[t_OHB] 
    
    
    
    
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
    
    #MATS_ECI = R.from_quat([q1_MATS_OHB[t_OHB], q2_MATS_OHB[t_OHB], q3_MATS_OHB[t_OHB], q4_MATS_OHB[t_OHB]])
    MATS_ECI = R.from_quat([q2_MATS_OHB[t_OHB], q3_MATS_OHB[t_OHB], q4_MATS_OHB[t_OHB], q1_MATS_OHB[t_OHB]])
    #MATS_ECI = R.random()
    
    
    
    
    optical_axis_OHB[t,:] = MATS_ECI.apply([0,0,-1])
    optical_axis_OHB[t,:] = optical_axis_OHB[t,:] / norm(optical_axis_OHB[t,:])
    Dec_OHB[t] = arctan( optical_axis_OHB[t,2] / sqrt(optical_axis_OHB[t,0]**2 + optical_axis_OHB[t,1]**2) ) /pi * 180
    Ra_OHB[t] = arccos( dot( [1,0,0], [optical_axis_OHB[t,0],optical_axis_OHB[t,1],0] ) / norm([optical_axis_OHB[t,0],optical_axis_OHB[t,1],0]) ) / pi * 180
    
    if( optical_axis_OHB[t,1] < 0 ):
        Ra_OHB[t] = 360-Ra_OHB[t]
    
    
    
    
    #Euler_angles_ECI[t,:] = MATS_ECI.as_euler('xyz', degrees=True)
    
    Euler_angles_ECI[t,:] = MATS_ECI.as_euler('ZYZ', degrees=True)
    
    
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
            optical_axis_OHB[t,0], optical_axis_OHB[t,1], optical_axis_OHB[t,2], current_time)
    
    optical_axis_OHB_ECEF[t,:] = optical_axis_OHB_ECEF[t,:] / norm(optical_axis_OHB_ECEF[t,:])
    
    r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2] = pm3d.eci2ecef(
            x_MATS_OHB[t_OHB], y_MATS_OHB[t_OHB], z_MATS_OHB[t_OHB], current_time)
    
    
    lat_MATS_OHB[t], long_MATS_OHB[t], alt_MATS_OHB[t] = pm3d.ecef2geodetic(r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2])
    
    r_LP_ECEF_OHB[t,0], r_LP_ECEF_OHB[t,1], r_LP_ECEF_OHB[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_OHB_ECEF[t,0], r_MATS_OHB_ECEF[t,1], r_MATS_OHB_ECEF[t,2], 
                                   optical_axis_OHB_ECEF[t,0], optical_axis_OHB_ECEF[t,1], optical_axis_OHB_ECEF[t,2])
    
    lat_LP_OHB[t], long_LP_OHB[t], alt_LP_OHB[t]  = pm3d.ecef2geodetic(r_LP_ECEF_OHB[t,0], r_LP_ECEF_OHB[t,1], r_LP_ECEF_OHB[t,2])
    
    
    #R_EARTH[t] = norm(r_MATS_OHB[t,:]*1000)-alt_MATS_OHB[t]
    
    current_time_MPL[t] = date2num(current_time)



    

########################## Plotter ###########################################

from mpl_toolkits.mplot3d import axes3d





figure()
#plot_date(current_time_MPL[0:timesteps],yaw_offset_angle[0:timesteps], markersize = 1, label = 'Predicted')
plot_date(current_time_MPL[0:timesteps],Euler_angles_SLOF[0:timesteps,0], markersize = 1, label = 'OHB-Data')
xlabel('Date')
ylabel('Yaw in degrees [z-axis SLOF]')
legend()


figure()
#plot_date(current_time_MPL[0:timesteps],pitch_MATS[0:timesteps] , markersize = 1, label = 'Predicted')
plot_date(current_time_MPL[0:timesteps],Euler_angles_SLOF[0:timesteps,1], markersize = 1, label = 'OHB-Data')
xlabel('Date')
ylabel('Pitch in degrees [intrinsic y-axis SLOF]')
legend()

figure()
plot_date(current_time_MPL[0:timesteps],Euler_angles_SLOF[0:timesteps,2], markersize = 1, label = 'OHB-Data')
xlabel('Date')
ylabel('Roll in degrees [intrinsic z-axis SLOF]')
legend()

###################################





####################################

#############################################
figure()
#plot_date(current_time_MPL[0:timesteps],lat_MATS[0:timesteps]/pi*180, markersize = 1, label = 'Predicted')
plot_date(current_time_MPL[0:timesteps], lat_MATS_OHB[0:timesteps], markersize = 1, label = 'OHB-Data')
xlabel('Date')
ylabel('Geodetic Latitude of MATS in degrees [WGS84 (prob)]')
legend()



figure()
#plot_date(current_time_MPL[0:timesteps],long_MATS[0:timesteps]/pi*180, markersize = 1, label = 'Predicted')
plot_date(current_time_MPL[0:timesteps], long_MATS_OHB[0:timesteps], markersize = 1, label = 'OHB-Data')
xlabel('Date')
ylabel('Longitude of MATS in degrees [WGS84 (prob)]')
legend()


figure()
#plot_date(current_time_MPL[0:timesteps],alt_MATS[0:timesteps] *1000, markersize = 1, label = 'Predicted')
#plot_date(current_time_MPL[0:timesteps],alt_MATS_OHB_FIXED[0:timesteps], markersize = 1, label = 'OHB-Data')
plot_date(current_time_MPL[0:timesteps],alt_MATS_OHB[0:timesteps], markersize = 1, label = 'OHB-Data_trans')
xlabel('Date')
ylabel('Altitude of MATS in degrees')
legend()


figure()
#plot_date(current_time_MPL[0:timesteps], lat_LP[0:timesteps], markersize = 1, label = 'Predicted')
plot_date(current_time_MPL[0:timesteps], lat_LP_OHB[0:timesteps], markersize = 1, label = 'OHB-Data')
xlabel('Date')
ylabel('Latitude of LP in degrees')
legend()

figure()
#plot_date(current_time_MPL[0:timesteps],long_LP[0:timesteps], markersize = 1, label = 'Predicted')
plot_date(current_time_MPL[0:timesteps],long_LP_OHB[0:timesteps], markersize = 1, label = 'OHB-Data')
xlabel('Date')
ylabel('Longitude of LP in degrees')
legend()



figure()
#plot_date(current_time_MPL[0:timesteps],alt_LP[0:timesteps], markersize = 1, label = 'Predicted')
plot_date(current_time_MPL[0:timesteps],alt_LP_OHB[0:timesteps], markersize = 1, label = 'OHB-Data')
xlabel('Date')
ylabel('Altitude of LP in degrees')
legend()


figure()
#plot_date(current_time_MPL[0:timesteps],Ra[0:timesteps], markersize = 1, label = 'Predicted')
plot_date(current_time_MPL[0:timesteps],Ra_OHB[0:timesteps], markersize = 1, label = 'OHB-Data')
#plot_date(current_time_MPL[0:timesteps],Ra_STK[0:timesteps], markersize = 1)
xlabel('Date')
ylabel('Right Ascension in degrees [J2000] (Parallax assumed negligable)')
legend()


figure()
#plot_date(current_time_MPL[0:timesteps],Dec[0:timesteps], markersize = 1, label = 'Predicted')
plot_date(current_time_MPL[0:timesteps],Dec_OHB[0:timesteps], markersize = 1, label = 'OHB-Data')
#plot_date(current_time_MPL[0:timesteps],Dec_STK[0:timesteps], markersize = 1)
xlabel('Date')
ylabel('Declination in degrees [J2000] (Parallax assumed negligable)')
legend()

