# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 16:19:57 2018

Part of a program to automatically generate a mission timeline from parameters
defined in OPT_Config_File. The timeline consists of
science modes and their start dates expressed as a list in chronological order

@author: David
"""

import logging, sys
import ephem
from pylab import array, cos, sin, cross, dot, zeros, sqrt, norm, pi, arccos, around, floor
from astroquery.vizier import Vizier
from Operational_Planning_Tool.OPT_library import rot_arbit, deg2HMS, lat_2_R, scheduler
from OPT_Config_File import Timeline_settings, getTLE, Mode120_settings, Logger_name, Version
import csv, os



def Mode120(Occupied_Timeline):
    
    Logger = logging.getLogger(Logger_name())
    
    automatic = Mode120_settings()['automatic']
    
    Logger.info('automatic = '+str(automatic))
    
    #To either calculate when stars are visible and schedule from that data or just schedule at a given time given by Mode120_settings()['date']
    if( Mode120_settings()['automatic'] == 1 ):
        star_list = Mode120_date_calculator()
        Occupied_Timeline, Mode120_comment = Mode120_date_select(Occupied_Timeline, star_list)
    else:
        try:
            date = Mode120_settings()['date']
        except:
            Logger.error('OPT_Config_File.Mode120_settings()["date"] is wrongly formatted or the date is occupied')
            sys.exit()
            
        endDate = ephem.Date(date+ephem.second* 
                             (Timeline_settings()['mode_separation']+Mode120_settings()['mode_duration']))
        
        ############### Start of availability schedueler ##########################
        
        date, endDate, iterations = scheduler(Occupied_Timeline, date, endDate)
        
        ############### End of availability schedueler ##########################
        
        if(iterations != 0):
            Logger.warning('User Specified date was occupied and got postponed!! Enter anything to ackknowledge and continue')
            input()
            
            
        Occupied_Timeline['Mode120'] = (date, endDate)
        Mode120_comment = 'Mode120 scheduled using a user set date, the date got postponed '+str(iterations)+' times'
        
        
        
    
    return Occupied_Timeline, Mode120_comment



#########################################################################################
#####################################################################################################



def Mode120_date_calculator():
#if(True):
    
    
    "Simulation length and timestep"
    
    Logger = logging.getLogger(Logger_name())
    log_timestep = Mode120_settings()['log_timestep']
    Logger.debug('log_timestep: '+str(log_timestep))

    
    timestep = Mode120_settings()['timestep'] #In seconds
    Logger.info('timestep set to: '+str(timestep)+' s')
    
    duration = Timeline_settings()['duration']
    Logger.info('Duration set to: '+str(duration)+' s')
    
    timesteps = int(floor(duration / timestep))
    Logger.info('Total number of timesteps set to: '+str(timesteps)+' s')
    
    date = Timeline_settings()['start_time']
    Logger.info('date set to: '+str(date))
    
    
    "Get relevant stars"
    result = Vizier(columns=['all'], row_limit=200).query_constraints(catalog='I/239/hip_main',Vmag=Mode120_settings()['Vmag'])
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
    stars_r_V_offset_plane = zeros((ROWS,3))
    stars_r_H_offset_plane = zeros((ROWS,3))
    stars_vert_offset = zeros((timesteps,ROWS))
    stars_hori_offset = zeros((timesteps,ROWS))
    stars_offset = zeros((timesteps,ROWS))
    normal_orbital = zeros((timesteps,3))
    r_V_offset_normal = zeros((timesteps,3))
    r_H_offset_normal = zeros((timesteps,3))
    pitch_LP_array = zeros((timesteps,1))
    pitch_pointing_command_array = zeros((timesteps,1))
    star_counter = 0
    spotted_star_name = []
    spotted_star_timestamp = []
    spotted_star_timecounter = []
    skip_star_list = []
    MATS_p = zeros((timesteps,1))
    MATS_P = zeros((timesteps,1))
    
    angle_between_orbital_plane_and_star = zeros((timesteps,ROWS))
    
    "Constants"
    R_mean = 6371 #Earth radius [km]
    #wgs84_Re = 6378.137 #Equatorial radius of wgs84 spheroid [km]
   # wgs84_Rp = 6356752.3142 #Polar radius of wgs84 spheroid [km]
    Logger.info('Earth radius used [km]: '+str(R_mean))
    
    U = 398600.4418 #Earth gravitational parameter
    
    LP_altitude = Mode120_settings()['LP_pointing_altitude']/1000  #Altitude at which MATS center of FOV is looking [km]
    Logger.info('LP_altitude set to [km]: '+str(LP_altitude))
    
    pointing_altitude = Mode120_settings()['pointing_altitude']/1000 
    
    
    
    #extended_Re = wgs84_Re + LP_altitude #Equatorial radius of extended wgs84 spheroid
    #f_e = (wgs84_Re - wgs84_Rp) / Re_extended #Flattening of extended wgs84 spheroid
    
    
    H_offset = Mode120_settings()['H_offset']  #5.67 is actual H_FOV
    Logger.info('H_offset set to [degrees]: '+str(H_offset))
    
    pitch_offset_angle = 0
    yaw_offset_angle = 0
    
    
    
    Logger.info('TLE used: '+getTLE()[0]+getTLE()[1])
    MATS = ephem.readtle('MATS',getTLE()[0],getTLE()[1])
    
    Logger.info('')
    Logger.info('Start of simulation of MATS for Mode120')
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
            pitch_LP_array[t]= array(arccos((R_mean+LP_altitude)/(R+altitude_MATS[t]))/pi*180)
            pitch_LP = pitch_LP_array[t][0]
        
        if( t*timestep % log_timestep == 0 ):
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
                abs_lat_LP = abs(lat_MATS[t])-pitch_LP/180*pi #absolute value of estimated latitude of LP in radians
                R_LP = lat_2_R(abs_lat_LP) #Estimated WGS84 radius of LP from latitude of MATS
            else:
                abs_lat_LP = abs(lat_MATS[t])+pitch_LP/180*pi #absolute value of estimated latitude of LP in radians
                R_LP = lat_2_R(abs_lat_LP) #Estimated WGS84 radius of LP from latitude of MATS
                
            
            pitch_LP_array[t]= array(arccos((R_LP+LP_altitude)/(R+altitude_MATS[t]))/pi*180)
            pitch_LP = pitch_LP_array[t][0]
            
            pitch_pointing_command_array[t] = array(arccos((R_LP+pointing_altitude )/(R+altitude_MATS[t]))/pi*180)
            pitch_pointing_command = pitch_pointing_command_array[t][0]
            
            pitch_angle_command = pitch_LP - pitch_pointing_command
            
            
            
            ############# Calculations of orbital and pointing vectors ############
            "Vector normal to the orbital plane of MATS"
            normal_orbital[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbital[t,0:3] = normal_orbital[t,0:3] / norm(normal_orbital[t,0:3])
            
            
            "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
            rot_mat = rot_arbit(-pi/2+(-pitch_LP+pitch_offset_angle)/180*pi, normal_orbital[t,0:3])
            r_FOV[t,0:3] = (r_MATS[t] @ rot_mat) /2
            
            
            #rot_mat2 = rot_arbit(pi/2+(pitch_LP+pitch_offset_angle)/180*pi, normal_orbital[t,0:3])
            #r_FOV2[t,0:3] = (rot_mat2 @ r_MATS[t]) /2
            #r_FOV_unit_vector2[t,0:3] = r_FOV2[t,0:3]/norm(r_FOV2[t,0:3])
            
            "Rotate yaw of pointing direction, meaning to rotate around the vector to MATS"
            rot_mat = rot_arbit(yaw_offset_angle/180*pi, r_MATS[t,0:3])
            r_FOV[t,0:3] = (r_FOV[t,0:3] @ rot_mat)
            r_FOV_unit_vector[t,0:3] = r_FOV[t,0:3]/norm(r_FOV[t,0:3])
            
            
            '''Rotate 'vector to MATS', to represent vector normal to satellite H-offset plane,
            which will be used to project stars onto it which allows the H-offset of stars to be found'''
            rot_mat = rot_arbit((-pitch_LP)/180*pi, normal_orbital[t,0:3])
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
                Logger.debug('R_LP [km]: '+str(R_LP))
                Logger.debug('FOV pitch in degrees: '+str(pitch_LP))
                Logger.debug('pitch_angle_command [degrees]: '+str(pitch_angle_command))
                Logger.debug('Absolute value of latitude of LP: '+str(abs_lat_LP/pi*180))
                Logger.debug('Pointing direction of FOV: '+str(r_FOV_unit_vector[t,0:3]))
                #Logger.debug('Pointing direction of FOV2: '+str(r_FOV_unit_vector2[t,0:3]))
                Logger.debug('Orthogonal direction to H-offset plane: '+str(r_H_offset_normal[t,0:3]))
                Logger.debug('Orthogonal direction to V-offset plane: '+str(r_V_offset_normal[t,0:3]))
                Logger.debug('Orthogonal direction to the orbital plane: '+str(normal_orbital[t,0:3]))
                Logger.debug('')
            
            
            ###################### Star-mapper ####################################
            
            "Check position of stars relevant to pointing direction"
            for x in range(ROWS):
                
                "Skip star if it is not visible during this epoch"
                if(stars[x].name in skip_star_list):
                    continue
                
                "Check if a star has already been spotted during this orbit."
                if( stars[x].name in spotted_star_name ):
                    
                    '''Check if not enough time has passed so that the star has not left FOV''' 
                    if((current_time - spotted_star_timestamp[spotted_star_name.index(stars[x].name)]) < ephem.second*(pitch_angle_command*2*MATS_P[t]/360)):
                        
                        time_passed_since_spotted = (t-spotted_star_timecounter[spotted_star_name.index(stars[x].name)])*timestep
                        time_until_in_direction_of_original_optical_axis = around(MATS_P[t]*(pitch_offset_angle+pitch_angle_command)/360)
                        
                        #
                        #Logger.debug('Already spotted star name: '+str(stars[x].name))
                        #Logger.debug('time_passed_since_spotted: '+str(time_passed_since_spotted))
                        #Logger.debug('time_until_in_direction_of_original_optical_axis: '+str(time_until_in_direction_of_original_optical_axis))
                        #Logger.debug('')
                        
                        '''Check if enough time has passed so that the star is roughly in the same
                        direction as original FOV and save lat,long, Hoffset, Voffset and time. Otherwise skip star.'''
                        if( abs(time_passed_since_spotted - time_until_in_direction_of_original_optical_axis) < timestep/2):
                            
                            "Project 'star vectors' ontop pointing H-offset and V-offset plane"
                            stars_r_V_offset_plane[x] = stars_r[0][x] - dot(stars_r[0][x],r_V_offset_normal[t,0:3]) * r_V_offset_normal[t,0:3]
                
                            stars_r_H_offset_plane[x] = stars_r[0][x] - ((dot(stars_r[0][x],r_H_offset_normal[t]) * r_H_offset_normal[t]) / ((norm(r_H_offset_normal[t]))**2))
                
                            "Dot product to get the Vertical and Horizontal angle offset of the star in the FOV"
                            stars_vert_offset[t][x] = arccos(dot(r_FOV[t],stars_r_V_offset_plane[x]) / (norm(r_FOV[t]) * norm(stars_r_V_offset_plane[x]))) /pi*180
                            stars_hori_offset[t][x] = arccos(dot(r_FOV[t],stars_r_H_offset_plane[x]) / (norm(r_FOV[t]) * norm(stars_r_H_offset_plane[x]))) /pi*180
                            
                            "Determine sign of off-set angle where positive V-offset angle is when looking at higher altitude"
                            if( dot(cross(r_FOV[t],stars_r_V_offset_plane[x]),r_V_offset_normal[t,0:3]) > 0 ):
                                stars_vert_offset[t][x] = -stars_vert_offset[t][x]
                            if( dot(cross(r_FOV[t],stars_r_H_offset_plane[x]),r_H_offset_normal[t]) > 0 ):
                                stars_hori_offset[t][x] = -stars_hori_offset[t][x]
                            
                            star_list_excel[2].append(str(current_time)+';')
                            star_list_excel[5].append(str(float(long_MATS[t]/pi*180))+';')
                            star_list_excel[6].append(str(float(lat_MATS[t]/pi*180))+';')
                            star_list_excel[10].append(str(stars_hori_offset[t][x])+';')
                            star_list_excel[11].append(str(stars_vert_offset[t][x])+';')
                            
                        continue
                        
                        "If enough time has passed (half an orbit), the star can be removed from the exception list"
                    elif((current_time - spotted_star_timestamp[spotted_star_name.index(stars[x].name)]) >= ephem.second*(180*MATS_P[t]/360)):
                        spotted_star_timestamp.pop(spotted_star_name.index(stars[x].name))
                        spotted_star_timecounter.pop(spotted_star_name.index(stars[x].name))
                        spotted_star_name.remove(stars[x].name)
                        continue
                        
                        
                
                "Total angle offset of the star compared to MATS's FOV"
                stars_offset[t][x] = arccos(dot(r_FOV[t],stars_r[0][x]) / (norm(r_FOV[t]) * norm(stars_r[0][x]))) /pi*180
                
                "Project 'star vectors' ontop pointing H-offset and V-offset plane"
                stars_r_V_offset_plane[x] = stars_r[0][x] - (dot(stars_r[0][x],r_V_offset_normal[t,0:3]) * r_V_offset_normal[t,0:3])
                
                stars_r_H_offset_plane[x] = stars_r[0][x] - (dot(stars_r[0][x],r_H_offset_normal[t]) * r_H_offset_normal[t]) 
                
                "Dot product to get the Vertical and Horizontal angle offset of the star in the FOV"
                stars_vert_offset[t][x] = arccos(dot(r_FOV[t],stars_r_V_offset_plane[x]) / (norm(r_FOV[t]) * norm(stars_r_V_offset_plane[x]))) /pi*180
                stars_hori_offset[t][x] = arccos(dot(r_FOV[t],stars_r_H_offset_plane[x]) / (norm(r_FOV[t]) * norm(stars_r_H_offset_plane[x]))) /pi*180
                
                "Determine sign of off-set angle where positive V-offset angle is when looking at higher altitude"
                if( dot(cross(r_FOV[t],stars_r_V_offset_plane[x]),r_V_offset_normal[t,0:3]) > 0 ):
                    stars_vert_offset[t][x] = -stars_vert_offset[t][x]
                if( dot(cross(r_FOV[t],stars_r_H_offset_plane[x]),r_H_offset_normal[t]) > 0 ):
                    stars_hori_offset[t][x] = -stars_hori_offset[t][x]
                
                #"To be able to skip stars far outside the orbital plane of MATS"
                #angle_between_orbital_plane_and_star[t][x] = arccos( dot(stars_r[0][x], stars_r_V_offset_plane[x]) / norm(stars_r_V_offset_plane[x])) /pi*180
                
                
                "To be able to skip stars far outside the orbital plane of MATS"
                if( t == 1 ):
                    "For first loop of stars, calculate angle between stars and orbital plane"
                    angle_between_orbital_plane_and_star[t][x] = arccos( dot(stars_r[0][x], stars_r_V_offset_plane[x]) / norm(stars_r_V_offset_plane[x])) /pi*180
                    
                    "Make exception list for stars not visible during this epoch (relativiely far outside of orbital plane)"
                    if( abs(angle_between_orbital_plane_and_star[t][x]) > H_offset+(duration)/(365*24*3600)*360 ):
                        Logger.debug('Skip star: '+stars[x].name+', with angle_between_orbital_plane_and_star of: '+str(angle_between_orbital_plane_and_star[t][x])+' degrees')
                        skip_star_list.append(stars[x].name)
                        continue
                
                
                "Check that the star is at an V-offset angle equal to pitch_angle_command"
                if( stars_vert_offset[t][x] < pitch_angle_command and stars_vert_offset[t-1][x] > pitch_angle_command and abs(stars_hori_offset[t][x]) < H_offset):
                    #print('Star number:',stars[x].name,'is visible at',stars_vert_offset[t][x],'degrees VFOV and', \
                         #stars_hori_offset[t][x],'degrees HFOV','during',ephem.Date(current_time))
                    
                    if( t % log_timestep == 0):
                        Logger.debug('Star: '+stars[x].name+', with H-offset: '+str(stars_hori_offset[t][x])+' V-offset: '+str(stars_vert_offset[t][x])+' in degrees is available')
                    
                    "Add the spotted star to the exception list and timestamp it"
                    spotted_star_name.append(stars[x].name)
                    spotted_star_timestamp.append(current_time)
                    spotted_star_timecounter.append(t) 
                    
                    
                    "Log all relevent data for the star"
                    star_list_excel[0].append(stars[x].name+';')
                    star_list_excel[1].append(str(current_time)+';')
                    star_list_excel[3].append(str(float(long_MATS[t]/pi*180))+';')
                    star_list_excel[4].append(str(float(lat_MATS[t]/pi*180))+';')
                    star_list_excel[7].append(str(stars[x].mag)+';')
                    star_list_excel[8].append(str(stars_hori_offset[t][x])+';')
                    star_list_excel[9].append(str(stars_vert_offset[t][x])+';')
                    star_list_excel[12].append(str(star_cat[x]['e_Hpmag'])+';')
                    star_list_excel[13].append(str(star_cat[x]['Hpscat'])+';')
                    star_list_excel[14].append(str(star_cat[x]['o_Hpmag'])+';')
                    star_list_excel[15].append(str(star_cat[x]['SpType'])+';')
                    
                    "Log data of star relevant to filtering process"
                    star_list.append({ 'Date': str(current_time), 'V-offset': stars_vert_offset[t][x], 'H-offset': stars_hori_offset[t][x], 
                                      'long_MATS': float(long_MATS[t]/pi*180), 'lat_MATS': float(lat_MATS[t]/pi*180), 'Vmag': stars[x].mag, 'Name': stars[x].name })
                    
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
    
    "Write spotted stars to file"
    try:
        os.mkdir('Output')
    except:
        pass
    
    while(True):
        try:
            with open('Output\\'+sys._getframe(1).f_code.co_name+'_Visible_Stars_'+Version()+'.csv', 'w', newline='') as write_file:
                writer = csv.writer(write_file, dialect='excel-tab')
                writer.writerows(star_list_excel)
            Logger.info('Available Stars data saved to: '+'Output\\'+sys._getframe(1).f_code.co_name+'_Visible_Stars_'+Version()+'.csv')
            break
        except PermissionError:
            Logger.error('Output\\'+sys._getframe(1).f_code.co_name+'_Visible_Stars_'+Version()+'.csv cannot be overwritten. Please close it')
            data = input('Enter anything to try again or 1 to exit')
            if( data == '1'):
                sys.exit()
    
    Logger.debug('Visible star list to be filtered:')
    for x in range(len(star_list)):
        Logger.debug(str(star_list[x]))
    Logger.debug('')
    
    Logger.debug('Exit '+str(__name__))
    Logger.debug('')
    
    
    return(star_list)



#####################################################################################################
#####################################################################################################



def Mode120_date_select(Occupied_Timeline, star_list):
    
    Logger = logging.getLogger(Logger_name())
    Logger.info('Start of filtering function')
    
    if( len(star_list) == 0):
        Mode120_comment = 'Stars not visible (Empty star_list)'
        Logger.info(Mode120_comment)
    
        return Occupied_Timeline, Mode120_comment
    
    star_min_mag_H_offset = []
    
    star_H_offset = [star_list[x]['H-offset'] for x in range(len(star_list))]
    #print('star_H_offset')
    #print(star_H_offset)
    star_V_offset = [star_list[x]['V-offset'] for x in range(len(star_list))]
    star_date = [star_list[x]['Date'] for x in range(len(star_list))]
    star_mag = [star_list[x]['Vmag'] for x in range(len(star_list))]
    star_name = [star_list[x]['Name'] for x in range(len(star_list))]
    star_long = [star_list[x]['long_MATS'] for x in range(len(star_list))]
    star_lat = [star_list[x]['lat_MATS'] for x in range(len(star_list))]
    
    star_mag_sorted = [abs(x) for x in star_mag]
    star_mag_sorted.sort()
    
    Logger.info('Brightest star magnitude: '+str(min(star_mag)))
    
    "Extract all the H-offsets for the brightest star"
    for x in range(len(star_list)):
        if( min(star_mag) == star_mag[x]):
            star_min_mag_H_offset.append( star_H_offset[x])
            
        #Just add an arbitrary large H-offset value for stars other than the brightest to keep the list the same length
        else:
            star_min_mag_H_offset.append(100)
    
    
    
    #star_H_offset_abs = [abs(x) for x in star_H_offset]
    star_H_offset_abs = [abs(x) for x in star_min_mag_H_offset]
    #star_H_offset_sorted = star_H_offset_abs
    star_H_offset_sorted = [abs(x) for x in star_min_mag_H_offset]
    star_H_offset_sorted.sort()
    Logger.debug('star_H_offset_abs: '+str(star_H_offset_abs))
    Logger.debug('star_H_offset_sorted: '+str(star_H_offset_sorted))
    
    
    restart = True
    iterations = 0
    ## Selects date based on min H-offset, if occupied, select date for next min H-offset
    while( restart == True):
        
        ## If all available dates for the brightest star is occupied, no Mode120 will be schedueled
        if( len(star_min_mag_H_offset) == iterations):
            Mode120_comment = 'No available time for Mode120 using the brightest available star'
            Logger.info(Mode120_comment)
            return Occupied_Timeline, Mode120_comment
        
        restart = False
        
        #Extract index of  minimum H-offset for first iteration, 
        #then next smallest if 2nd iterations needed and so on
        x = star_H_offset_abs.index(star_H_offset_sorted[iterations])
        
        Mode120_date = star_date[x]
        
        Mode120_date = ephem.Date(ephem.Date(Mode120_date)-ephem.second*(Mode120_settings()['freeze_start']))
        
        Mode120_endDate = ephem.Date(Mode120_date+ephem.second* 
                                     (Timeline_settings()['mode_separation']+Mode120_settings()['mode_duration']))
        
        ## Extract Occupied dates and if they clash, restart loop and select new date
        for busy_dates in Occupied_Timeline.values():
            if( busy_dates == []):
                continue
            else:
                if( busy_dates[0] <= Mode120_date <= busy_dates[1] or 
                       busy_dates[0] <= Mode120_endDate <= busy_dates[1]):
                    
                    iterations = iterations + 1
                    restart = True
                    break
    
    
    Occupied_Timeline['Mode120'] = (Mode120_date, Mode120_endDate)
    
    Mode120_comment = ('Star name:'+star_name[x]+', V-offset: '+str(star_V_offset[x])+' H-offset: '+str(star_H_offset[x])+', Number of times date changed: '+str(iterations)
        +', MATS (long,lat) in degrees = ('+str(star_long[x])+', '+str(star_lat[x])+')')
    
    
    return Occupied_Timeline, Mode120_comment
    