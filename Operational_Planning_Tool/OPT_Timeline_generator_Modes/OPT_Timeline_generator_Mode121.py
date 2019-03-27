# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 16:22:16 2018

@author: David
"""


import logging, sys
import ephem
from pylab import array, cos, sin, cross, dot, zeros, sqrt, norm, pi, arccos, around, floor
from astroquery.vizier import Vizier
from Operational_Planning_Tool.OPT_library import rot_arbit, deg2HMS, lat_2_R
from OPT_Config_File import Timeline_settings, getTLE, Mode121_settings, Logger_name, Version
import csv, os





def Mode121(Occupied_Timeline):
    
    date_magnitude_array = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, date_magnitude_array)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    
    Logger = logging.getLogger(Logger_name())
    
    "Simulation length and timestep"
    
    Logger = logging.getLogger(Logger_name())
    log_timestep = Mode121_settings()['log_timestep']
    Logger.debug('log_timestep: '+str(log_timestep))

    
    timestep = Mode121_settings()['timestep'] #In seconds
    Logger.info('timestep set to: '+str(timestep)+' s')
    
    duration = Timeline_settings()['duration']
    Logger.info('Duration set to: '+str(duration)+' s')
    
    timesteps = int(floor(duration / timestep))
    timesteps = int(floor(1000 / timestep))
    Logger.info('Total number of timesteps set to: '+str(timesteps)+' s')
    
    date = Timeline_settings()['start_time']
    Logger.info('date set to: '+str(date))
    
    
    "Get relevant stars"
    result = Vizier(columns=['all'], row_limit=2500).query_constraints(catalog='I/239/hip_main',Vmag=Mode121_settings()['Vmag'])
    star_cat = result[0]
    ROWS = star_cat[0][:].count()
    stars = []
    stars_dec = zeros((ROWS,1))
    stars_ra = zeros((ROWS,1))
    
    "Insert stars into Pyephem"
    for t in range(ROWS):
        s = "{},f|M|F7,{},{},{},2000"
        s = s.format(star_cat[t]['HIP'], deg2HMS(ra=star_cat[t]['_RA.icrs']), deg2HMS(dec=star_cat[t]['_DE.icrs']), star_cat[t]['Vmag'])
        stars.append(ephem.readdb(s))
        stars[t].compute(epoch='2018')
        stars_dec[t] = stars[t].dec
        stars_ra[t] = stars[t].ra
    
    Logger.debug('')
    Logger.debug('List of stars used: '+str(star_cat))
    Logger.debug('')
    
    "Calculate unit-vectors of stars"
    stars_x = cos(stars_dec)* cos(stars_ra)
    stars_y = cos(stars_dec)* sin(stars_ra)
    stars_z = sin(stars_dec)
    stars_r = array([stars_x,stars_y,stars_z])
    stars_r = stars_r.transpose()
    
    "Prepare the excel file output"
    star_list_excel = []
    star_list_excel.append(['Name;'])
    star_list_excel.append(['t1;'])
    star_list_excel.append(['t2;'])
    star_list_excel.append(['long1;'])
    star_list_excel.append(['lat1;'])
    star_list_excel.append(['long2;'])
    star_list_excel.append(['lat2;'])
    star_list_excel.append(['mag;'])
    star_list_excel.append(['H_offset;'])
    star_list_excel.append(['V_offset;'])
    star_list_excel.append(['H_offset2;'])
    star_list_excel.append(['V_offset2;'])
    star_list_excel.append(['e_Hpmag;'])
    star_list_excel.append(['Hpscat;'])
    star_list_excel.append(['o_Hpmag;'])
    star_list_excel.append(['Classification;'])
    
    "Prepare the output"
    star_list = []
    
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
    r_FOV = zeros((timesteps,3))
    r_FOV_unit_vector = zeros((timesteps,3))
    r_FOV2 = zeros((timesteps,3))
    r_FOV_unit_vector2 = zeros((timesteps,3))
    r_FOV_norm = zeros((timesteps,3))
    r_azi_norm = zeros((timesteps,3))
    stars_r_V_offset_plane = zeros((ROWS,3))
    stars_r_H_offset_plane = zeros((ROWS,3))
    stars_vert_offset = zeros((timesteps,ROWS))
    stars_hori_offset = zeros((timesteps,ROWS))
    stars_offset = zeros((timesteps,ROWS))
    normal_orbital = zeros((timesteps,3))
    r_V_offset_normal = zeros((timesteps,3))
    r_H_offset_normal = zeros((timesteps,3))
    pitch_sensor_array = zeros((timesteps,1))
    star_counter = 0
    spotted_star_name = []
    spotted_star_timestamp = []
    spotted_star_timecounter = []
    skip_star_list = []
    MATS_p = zeros((timesteps,1))
    MATS_P = zeros((timesteps,1))
    spotted_stars = zeros((timesteps,1))
    brightest_star_per_timestep = []
    
    "Array containing date in first column and brightest magnitude spotted in the second"
    date_magnitude_array = zeros((timesteps,2))+100
    "Set magntidues arbitrary large"
    date_magnitude_array[:,1] = 100
    
    angle_between_orbital_plane_and_star = zeros((timesteps,ROWS))
    
    "Constants"
    R_mean = 6371 #Earth radius [km]
    #wgs84_Re = 6378.137 #Equatorial radius of wgs84 spheroid [km]
   # wgs84_Rp = 6356752.3142 #Polar radius of wgs84 spheroid [km]
    Logger.info('Earth radius used [km]: '+str(R_mean))
    
    U = 398600.4418 #Earth gravitational parameter
    
    LP_altitude = Mode121_settings()['default_pointing_altitude']/1000  #Altitude at which MATS center of FOV is looking [km]
    Logger.info('LP_altitude set to [km]: '+str(LP_altitude))
    
    #extended_Re = wgs84_Re + LP_altitude #Equatorial radius of extended wgs84 spheroid
    #f_e = (wgs84_Re - wgs84_Rp) / Re_extended #Flattening of extended wgs84 spheroid
    
    pointing_adjustment = 3 #Angle in degrees that the pointing can be adjusted
    V_FOV = Mode121_settings()['V_FOV'] #0.91 is actual V_FOV
    H_FOV = Mode121_settings()['H_FOV']  #5.67 is actual H_FOV
    Logger.info('V_FOV set to [degrees]: '+str(V_FOV))
    Logger.info('H_FOV set to [degrees]: '+str(H_FOV))
    
    pitch_offset_angle = 0
    yaw_offset_angle = 0
    
    
    
    Logger.info('TLE used: '+getTLE()[0]+getTLE()[1])
    MATS = ephem.readtle('MATS',getTLE()[0],getTLE()[1])
    
    Logger.info('')
    Logger.info('Start of simulation of MATS for Mode121')
    ################## Start of Simulation ########################################
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(timesteps):
        
        
        current_time = ephem.Date(date+ephem.second*timestep*t)
        
        MATS.compute(current_time)
        
        (lat_MATS[t],long_MATS[t],altitude_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
        MATS.sublat,MATS.sublong,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
        
        R = lat_2_R(lat_MATS[t]) #WGS84 radius from latitude of MATS
        
        z_MATS[t] = sin(g_dec_MATS[t])*(altitude_MATS[t]+R)
        x_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R)* cos(g_ra_MATS[t])
        y_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R)* sin(g_ra_MATS[t])
       
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        
        #Semi-Major axis of MATS, assuming circular orbit
        MATS_p[t] = norm(r_MATS[t,0:3])
        
        #Orbital Period of MATS
        MATS_P[t] = 2*pi*sqrt(MATS_p[t]**3/U)
        
        
        #Initial Estimated pitch or elevation angle for MATS pointing
        if(t == 0):
            pitch_sensor_array[t]= array(arccos((R_mean+LP_altitude)/(R+altitude_MATS[t]))/pi*180)
            pitch_sensor = pitch_sensor_array[t][0]
        
        if( t*timestep % log_timestep == 0 or t == 1 and t != 0 ):
            Logger.debug('')
            
            Logger.debug('t (loop iteration number): '+str(t))
            Logger.debug('Current time: '+str(current_time))
            Logger.debug('Semimajor axis in km: '+str(MATS_p[t]))
            Logger.debug('Orbital Period in s: '+str(MATS_P[t]))
            Logger.debug('Vector to MATS [km]: '+str(r_MATS[t,0:3]))
            Logger.debug('Latitude in degrees: '+str(lat_MATS[t]/pi*180))
            Logger.debug('Longitude in degrees: '+str(long_MATS[t]/pi*180))
            Logger.debug('Altitude in km: '+str(altitude_MATS[t]))
            Logger.debug('R (WGS84 Earth radius for MATS) [km]: '+str(R))
                
        if(t != 0):
            
            # More accurate estimation of pitch angle of MATS
            if( abs(lat_MATS[t])-abs(lat_MATS[t-1]) > 0 ): #Moving towards poles meaning LP is equatorwards compared to MATS
                abs_lat_LP = abs(lat_MATS[t])-pitch_sensor/180*pi #absolute value of estimated latitude of LP in radians
                R_LP = lat_2_R(abs_lat_LP) #Estimated WGS84 radius of LP from latitude of MATS
            else:
                abs_lat_LP = abs(lat_MATS[t])+pitch_sensor/180*pi #absolute value of estimated latitude of LP in radians
                R_LP = lat_2_R(abs_lat_LP) #Estimated WGS84 radius of LP from latitude of MATS
                
            
            pitch_sensor_array[t]= array(arccos((R_LP+LP_altitude)/(R+altitude_MATS[t]))/pi*180)
            pitch_sensor = pitch_sensor_array[t][0]
            
            
            ############# Calculations of orbital and pointing vectors ############
            "Vector normal to the orbital plane of MATS"
            normal_orbital[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbital[t,0:3] = normal_orbital[t,0:3] / norm(normal_orbital[t,0:3])
            
            
            "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
            rot_mat = rot_arbit(-pi/2+(-pitch_sensor+pitch_offset_angle)/180*pi, normal_orbital[t,0:3])
            r_FOV[t,0:3] = (r_MATS[t] @ rot_mat) /2
            
            
            #rot_mat2 = rot_arbit(pi/2+(pitch_sensor+pitch_offset_angle)/180*pi, normal_orbital[t,0:3])
            #r_FOV2[t,0:3] = (rot_mat2 @ r_MATS[t]) /2
            #r_FOV_unit_vector2[t,0:3] = r_FOV2[t,0:3]/norm(r_FOV2[t,0:3])
            
            "Rotate yaw of pointing direction, meaning to rotate around the vector to MATS"
            rot_mat = rot_arbit(yaw_offset_angle/180*pi, r_MATS[t,0:3])
            r_FOV[t,0:3] = (r_FOV[t,0:3] @ rot_mat)
            r_FOV_unit_vector[t,0:3] = r_FOV[t,0:3]/norm(r_FOV[t,0:3])
            
            
            '''Rotate 'vector to MATS', to represent vector normal to satellite H-offset plane,
            which will be used to project stars onto it which allows the H-offset of stars to be found'''
            rot_mat = rot_arbit((-pitch_sensor)/180*pi, normal_orbital[t,0:3])
            r_H_offset_normal[t,0:3] = (r_MATS[t] @ rot_mat)
            r_H_offset_normal[t,0:3] = r_H_offset_normal[t,0:3] / norm(r_H_offset_normal[t,0:3])
            
            "If pointing direction has a Yaw defined, Rotate yaw of normal to pointing direction H-offset plane, meaning to rotate around the vector to MATS"
            rot_mat = rot_arbit(yaw_offset_angle/180*pi, r_MATS[t,0:3])
            r_H_offset_normal[t,0:3] = (r_H_offset_normal[t,0:3] @ rot_mat)
            r_H_offset_normal[t,0:3] = r_H_offset_normal[t,0:3]/norm(r_H_offset_normal[t,0:3])
            
            "Rotate orbital plane normal to make it into pointing V-offset plane normal"
            r_V_offset_normal[t,0:3] = (normal_orbital[t,0:3] @ rot_mat)
            r_V_offset_normal[t,0:3] = r_V_offset_normal[t,0:3]/norm(r_V_offset_normal[t,0:3])
            
            if( t*timestep % log_timestep == 0 or t == 1 ):
                Logger.debug('Current time: '+str(current_time))
                Logger.debug('R_LP [km]: '+str(R_LP))
                
                Logger.debug('FOV pitch in degrees: '+str(pitch_sensor))
                Logger.debug('Absolute value of latitude of LP: '+str(abs_lat_LP/pi*180))
                Logger.debug('Pointing direction of FOV: '+str(r_FOV_unit_vector[t,0:3]))
                #Logger.debug('Pointing direction of FOV2: '+str(r_FOV_unit_vector2[t,0:3]))
                Logger.debug('Orthogonal direction to H-offset plane: '+str(r_H_offset_normal[t,0:3]))
                Logger.debug('Orthogonal direction to V-offset plane: '+str(r_V_offset_normal[t,0:3]))
                Logger.debug('Orthogonal direction to the orbital plane: '+str(normal_orbital[t,0:3]))
                Logger.debug('')
            
#            '''Rotate 'vector to MATS', to represent vector normal to satellite yaw plane,
#            which will be used to rotate the yaw of the pointing'''
#            rot_mat = rot_arbit((-pitch_sensor)/180*pi, normal_orbital[t,0:3])
#            r_azi_norm[t,0:3] = (r_MATS[t] @ rot_mat)
#            r_azi_norm[t,0:3] = r_azi_norm[t,0:3] / norm(r_azi_norm[t,0:3])
#            
#            "Rotate horizontal offset of pointing direction, around satellite yaw plane"
#            rot_mat = rot_arbit(yaw_offset_angle/180*pi, r_azi_norm[t,0:3])
#            r_FOV[t,0:3] = (r_FOV[t,0:3] @ rot_mat)
#            r_FOV_unit_vector[t,0:3] = r_FOV[t,0:3]/norm(r_FOV[t,0:3])/2
#            
#            "Rotate orbital plane normal to match pointing V-offset plane normal"
#            r_V_offset_normal[t,0:3] = (normal_orbital[t,0:3] @ rot_mat)
#            
#            '''Rotate pointing vector 90 degrees in the pointing elevation plane to get a vector,
#            which is normal to pointing azimuth plane'''
#            rot_mat = rot_arbit(pi/2, r_V_offset_normal[t,0:3])
#            r_FOV_norm[t,0:3] = (r_FOV[t,0:3] @ rot_mat)
#            r_FOV_norm[t,0:3] = r_FOV_norm[t,0:3] / norm(r_FOV_norm[t,0:3])
            
            
            ############# End of Calculations of orbital and pointing vectors #####
            
            "Add current date to date_magnitude_array"
            date_magnitude_array[t-1,0] = current_time 
            
            ###################### Star-mapper ####################################
            
            "Check position of stars relevant to pointing direction"
            for x in range(ROWS):
                
                "Skip star if it is not visible during this epoch"
                if(stars[x].name in skip_star_list):
                    
                    continue
                '''
                "Check if a star has already been spotted during this orbit."
                if( stars[x].name in spotted_star_name ):
                    
                    'Check if not enough time has passed so that the star has not left FOV'
                    if((current_time - spotted_star_timestamp[spotted_star_name.index(stars[x].name)]) < ephem.second*(V_FOV*2*MATS_P[t]/360)):
                        
                        continue
                        
                        "If enough time has passed (half an orbit), the star can be removed from the exception list"
                    elif((current_time - spotted_star_timestamp[spotted_star_name.index(stars[x].name)]) >= ephem.second*(180*MATS_P[t]/360)):
                        spotted_star_timestamp.pop(spotted_star_name.index(stars[x].name))
                        spotted_star_timecounter.pop(spotted_star_name.index(stars[x].name))
                        spotted_star_name.remove(stars[x].name)
                        continue
                '''        
                
                
                "Project 'star vectors' ontop pointing H-offset and V-offset plane"
                stars_r_V_offset_plane[x] = stars_r[0][x] - (dot(stars_r[0][x],r_V_offset_normal[t,0:3]) * r_V_offset_normal[t,0:3])
                
                stars_r_H_offset_plane[x] = stars_r[0][x] - (dot(stars_r[0][x],r_H_offset_normal[t]) * r_H_offset_normal[t]) 
                
                "Dot product to get the Vertical and Horizontal angle offset of the star in the FOV"
                stars_vert_offset[t][x] = arccos(dot(r_FOV[t],stars_r_V_offset_plane[x]) / (norm(r_FOV[t]) * norm(stars_r_V_offset_plane[x]))) /pi*180
                stars_hori_offset[t][x] = arccos(dot(r_FOV[t],stars_r_H_offset_plane[x]) / (norm(r_FOV[t]) * norm(stars_r_H_offset_plane[x]))) /pi*180
                
                
                
                "For first loop of stars, make exception list for stars not visible during this epoch"
                if( t == 1 ):
                    
                    "To be able to skip stars far outside the orbital plane of MATS"
                    angle_between_orbital_plane_and_star[t][x] = arccos( dot(stars_r[0][x], stars_r_V_offset_plane[x]) / norm(stars_r_V_offset_plane[x])) /pi*180
                    
                    if( abs(angle_between_orbital_plane_and_star[t][x]) > H_FOV/2+(duration*2)/(365*24*3600)*360):
                        Logger.debug('Skip star: '+stars[x].name+', with angle_between_orbital_plane_and_star of: '+str(angle_between_orbital_plane_and_star[t][x])+' degrees')
                        skip_star_list.append(stars[x].name)
                        continue
                
                
                "Check if star is in FOV"
                if( abs(stars_vert_offset[t][x]) < V_FOV/2 and abs(stars_hori_offset[t][x]) < H_FOV/2):
                    #print('Star number:',stars[x].name,'is visible at',stars_vert_offset[t][x],'degrees VFOV and', \
                         #stars_hori_offset[t][x],'degrees HFOV','during',ephem.Date(current_time))
                    
                    if( t % log_timestep == 0 or t == 1 or True):
                        Logger.debug('Current time: '+str(current_time))
                        Logger.debug('Star: '+stars[x].name+', with H-offset: '+str(stars_hori_offset[t][x])+' V-offset: '+str(stars_vert_offset[t][x])+' in degrees is visible')
                    
                    "Check if it is the brightest star spotted in the current FOV at the current date, and if so, replace the currently value"
                    if( stars[x].mag < date_magnitude_array[t-1,1] ):
                        date_magnitude_array[t-1,1] = stars[x].mag
                        
                    
                    star_counter = star_counter + 1
                    
            ######################### End of star_mapper #############################
        
    
    
    ########################## Optional plotter ###########################################
    '''
    from mpl_toolkits.mplot3d import axes3d
    
    "Orbital points to plot"
    points_2_plot_start = 0#0*24*120
    points_2_plot = points_2_plot_start+200
    
    "Plotting of orbit and FOV"
    fig = figure(1)
    ax = fig.add_subplot(111,projection='3d')
    ax.set_xlim3d(-7000, 7000)
    ax.set_ylim3d(-7000, 7000)
    ax.set_zlim3d(-7000, 7000)
    
    ax.scatter(x_MATS[points_2_plot_start:points_2_plot],y_MATS[points_2_plot_start:points_2_plot],z_MATS[points_2_plot_start:points_2_plot])
    ax.scatter(r_FOV[points_2_plot_start:points_2_plot,0],r_FOV[points_2_plot_start:points_2_plot,1],r_FOV[points_2_plot_start:points_2_plot,2])
    
    "Plotting of stars and FOV unit-vectors"
    fig = figure(2)
    ax = fig.add_subplot(111,projection='3d')
    ax.scatter(stars_r[0][:,0],stars_r[0][:,1],stars_r[0][:,2])
    ax.scatter(r_FOV_unit_vector[points_2_plot_start:points_2_plot,0],r_FOV_unit_vector[points_2_plot_start:points_2_plot,1],r_FOV_unit_vector[points_2_plot_start:points_2_plot,2])
    ax.scatter(r_V_offset_normal[points_2_plot_start:points_2_plot,0]/2, r_V_offset_normal[points_2_plot_start:points_2_plot,1]/2, r_V_offset_normal[points_2_plot_start:points_2_plot,2]/2)
    ax.scatter(normal_orbital[points_2_plot_start:points_2_plot,0]/2, normal_orbital[points_2_plot_start:points_2_plot,1]/2, normal_orbital[points_2_plot_start:points_2_plot,2]/2)
    ax.scatter(r_H_offset_normal[points_2_plot_start:points_2_plot,0]/2, r_H_offset_normal[points_2_plot_start:points_2_plot,1]/2, r_H_offset_normal[points_2_plot_start:points_2_plot,2]/2)
    '''
    ########################### END of Optional plotter ########################################
    
    
    Logger.info('brightest_star_per_timestep: '+str(brightest_star_per_timestep))
    
    return(date_magnitude_array)
    



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, date_magnitude_array):
    
    from Operational_Planning_Tool.OPT_library import scheduler
    
    Logger = logging.getLogger(Logger_name())
    Logger.info('Start of filtering function')
    
    loop_counter = 0
    
    "Loop for maximum magnitude until the date chosen is not occupied"
    while(True):
        index_max_mag = date_magnitude_array[:,1].argmax()
        value_max_mag = date_magnitude_array[:,1].max()
    
        date_max_mag = date_magnitude_array[index_max_mag,0]
        
        date = ephem.Date(ephem.Date(date_max_mag)-ephem.second*(Mode121_settings()['freeze_start']))
        endDate = ephem.Date(date+ephem.second* 
                                     (Timeline_settings()['mode_separation']+Timeline_settings()['mode_duration']))
        
        irrelevant1, irrelevant2, iterations = scheduler(Occupied_Timeline, date, endDate)
        
        "Break loop if scheduler function determines the date to be available and within the scheduled timeline, else try next faintest magntitude"
        if( iterations == 0 and date >= Timeline_settings()['start_time']):
            break
        else:
            "Set the current maximum magnitude arbitrary small to allow a new maximum magnitude date to be chosen in next loop"
            date_magnitude_array[index_max_mag,1] = -100
            loop_counter = loop_counter +1
            
    
    
    
    comment = 'Number of times date changed: ' + str(loop_counter)+', faintest magnitude visible: '+str(value_max_mag)
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    Occupied_Timeline[Mode_name] = (date,endDate)
    
    return Occupied_Timeline, comment
