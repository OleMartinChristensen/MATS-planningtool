# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 13:48:04 2018

Part of a program to automatically generate a mission timeline from parameters
defined in SCIMOD_DEFAULT_PARAMS. The timeline consists of
science modes and their start dates expressed as a list in chronological order

@author: David
"""


import ephem
from pylab import array, cos, sin, cross, dot, zeros, sqrt, norm, pi, arccos
from MATS_AUTOMATIC_SCIMOD_date_calculator_library import rot_arbit, lat_2_R
from MATS_TIMELINE_SCIMOD_DEFAULT_PARAMS import Timeline_params, getTLE, Mode200_default, Mode200_calculator_defaults




def Mode200(Occupied_Timeline):
    
    Moon_list = Mode200_date_calculator()
    
    Occuipied_Timeline, Mode200_comment = Mode200_date_select(Occupied_Timeline, Moon_list)
    
    return Occupied_Timeline, Mode200_comment



###############################################################################################
###############################################################################################



def Mode200_date_calculator():
#if(True):
    
    
    "Simulation length and timestep"
    duration = Timeline_params()['duration']
    timestep = Mode200_calculator_defaults()['timestep'] #In seconds
    
    
    date = Timeline_params()['start_time']
    
    
    
    MATS = ephem.readtle('MATS',getTLE()[0],getTLE()[1])
    
    Moon = ephem.Moon()
    
    "Pre-allocate space"
    lat_MATS = zeros((duration,1))
    long_MATS = zeros((duration,1))
    altitude_MATS = zeros((duration,1))
    g_ra_MATS = zeros((duration,1))
    g_dec_MATS = zeros((duration,1))
    x_MATS = zeros((duration,1))
    y_MATS = zeros((duration,1))
    z_MATS = zeros((duration,1))
    r_MATS = zeros((duration,3))
    r_MATS_norm = zeros((duration,3))
    r_FOV = zeros((duration,3))
    normal_orbit = zeros((duration,3))
    normal_azi = zeros((duration,3))
    normal_azi_norm = zeros((duration,3))
    ele = zeros((duration,1))
    MATS_p = zeros((duration,1))
    MATS_P = zeros((duration,1))
    
    g_ra_Moon = zeros((duration,1))
    g_dec_Moon = zeros((duration,1))
    distance_Moon = zeros((duration,1))
    x_Moon = zeros((duration,1))
    y_Moon = zeros((duration,1))
    z_Moon = zeros((duration,1))
    r_Moon = zeros((duration,3))
    r_MATS_2_Moon = zeros((duration,3))
    r_MATS_2_Moon_norm = zeros((duration,3))
    Moon_r_el = zeros((duration,3))
    Moon_r_ra = zeros((duration,3))
    Moon_vert_offset = zeros((duration,1))
    Moon_hori_offset = zeros((duration,1))
    angle_between_orbital_plane_and_moon = zeros((duration,1))
    Moon_list = []
        
    
    
    "Constants"
    AU = 149597871 #km
    R_mean = 6371 #Earth radius
    U = 398600.4418 #Earth gravitational parameter
    FOV_altitude = Mode200_calculator_defaults()['default_pointing_altitude']/1000  #Altitude at which MATS center of FOV is looking
    pointing_adjustment = 3 #Angle in degrees that the pointing can be adjusted
    V_FOV = Mode200_calculator_defaults()['V_FOV'] #0.91 is actual V_FOV
    H_FOV = Mode200_calculator_defaults()['H_FOV']  #5.67 is actual H_FOV
    V_offset = 0
    H_offset = 0
    
    
    t=0
    
    current_time = date
    
    
    while(current_time < date+ephem.second*duration):
        
        MATS.compute(current_time)
        Moon.compute(current_time)
        
        
        (lat_MATS[t],long_MATS[t],altitude_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
        MATS.sublat,MATS.sublong,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
        
        R = lat_2_R(lat_MATS[t])
        
        z_MATS[t] = sin(g_dec_MATS[t])*(altitude_MATS[t]+R)
        x_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R)* cos(g_ra_MATS[t])
        y_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R)* sin(g_ra_MATS[t])
       
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        r_MATS_norm[t] = r_MATS[t]/norm(r_MATS[t])
        
        
        #Semi-Major axis of MATS, assuming circular orbit
        MATS_p[t] = norm(r_MATS[t,0:3])
        
        #Orbital Period of MATS
        MATS_P[t] = 2*pi*sqrt(MATS_p[t]**3/U)
        
        #Estimated pitch or elevation angle for MATS pointing
        ele[t]= array(arccos((R_mean+FOV_altitude)/(R+altitude_MATS[t]))/pi*180)
        el = ele[t][0]
        
        (g_ra_Moon[t],g_dec_Moon[t],distance_Moon[t])= (Moon.g_ra,Moon.g_dec,Moon.earth_distance*AU)
        
        z_Moon[t] = sin(g_dec_Moon[t]) * distance_Moon[t]
        x_Moon[t] = cos(g_dec_Moon[t])*cos(g_ra_Moon[t]) * distance_Moon[t]
        y_Moon[t] = cos(g_dec_Moon[t])*sin(g_ra_Moon[t]) * distance_Moon[t]
       
        r_Moon[t,0:3] = [x_Moon[t], y_Moon[t], z_Moon[t]]
        
        r_MATS_2_Moon[t] = r_Moon[t]-r_MATS[t]
        r_MATS_2_Moon_norm[t] = r_MATS_2_Moon[t]/norm(r_MATS_2_Moon[t])
                
        if(t != 0):
            
            
            ############# Calculations of orbital and pointing vectors ############
            "Vector normal to the orbital plane of MATS"
            normal_orbit[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbit[t,0:3] = normal_orbit[t,0:3] / norm(normal_orbit[t,0:3])
            
            "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change"
            rot_mat = rot_arbit(-pi/2+(-el+V_offset)/180*pi, normal_orbit[t,0:3])
            r_FOV[t,0:3] = (r_MATS[t] @ rot_mat)
            
            "Rotate 'vector to MATS', to represent a vector normal to the azimuth pointing plane, includes vertical offset change (Parallax is negligable)"
            rot_mat = rot_arbit((-el+V_offset)/180*pi, normal_orbit[t,0:3])
            normal_azi[t,0:3] = (r_MATS[t] @ rot_mat) /2
            normal_azi_norm[t,0:3] = normal_azi[t,0:3] / norm(normal_azi[t,0:3])
            
            ############# End of Calculations of orbital and pointing vectors #####
            
            "Project 'r_MATS_2_Moon' ontop pointing azimuth and elevation plane"
            Moon_r_el[t] = r_MATS_2_Moon_norm[t] - dot(r_MATS_2_Moon_norm[t],normal_orbit[t]) * normal_orbit[t]
            Moon_r_ra[t] = r_MATS_2_Moon_norm[t] - dot(r_MATS_2_Moon_norm[t],normal_azi_norm[t]) * normal_azi_norm[t]
            
            
            "Dot product to get the Vertical and Horizontal angle offset of the Moon"
            Moon_vert_offset[t] = arccos(dot(r_FOV[t],Moon_r_el[t]) / (norm(r_FOV[t])*norm(Moon_r_el[t]))) /pi*180
            Moon_hori_offset[t] = arccos(dot(r_FOV[t],Moon_r_ra[t]) / (norm(r_FOV[t])*norm(Moon_r_ra[t]))) /pi*180
            
            "Get the offset angle sign correct"
            if( dot(cross(r_FOV[t],Moon_r_el[t]),normal_orbit[t,0:3]) > 0 ):
                Moon_vert_offset[t] = -Moon_vert_offset[t]
            if( dot(cross(r_FOV[t],Moon_r_ra[t]),normal_azi[t]) > 0 ):
                Moon_hori_offset[t] = -Moon_hori_offset[t]
            
            
            "Angle between orbital plane and moon"
            angle_between_orbital_plane_and_moon[t] = arccos( dot(r_MATS_2_Moon_norm[t], Moon_r_el[t]) / norm(Moon_r_el[t])) /pi*180
            
            #print('angle_between_orbital_plane_and_moon = ' + str(angle_between_orbital_plane_and_moon[t]))
            
            "Save data when Moon is visible in specified FOV. V-offset is defined as the maximum that the moon can move in one timestep"
            #if(abs(Moon_vert_offset[t]) <= timestep/MATS_P[t]*360 and abs(Moon_hori_offset[t]) < H_FOV/2):
            if(abs(Moon_vert_offset[t]) <= V_FOV/2 and abs(Moon_hori_offset[t]) < H_FOV/2):
                
                Moon_list.append({ 'Date': str(current_time), 'V-offset': Moon_vert_offset[t], 'H-offset': Moon_hori_offset[t]})
                current_time = ephem.Date(current_time+ephem.second*MATS_P[t]/2)
                
            
        
        "To be able to make time skips when the moon is far outside the orbital plane of MATS"
        if( angle_between_orbital_plane_and_moon[t] > H_FOV/2):
            t= t + 1
            current_time = ephem.Date(current_time+ephem.second * H_FOV/4 / 360 * 3600*24*31)
        else:
            t= t + 1
            current_time = ephem.Date(current_time+ephem.second*timestep)
            
        
        
    return Moon_list



###############################################################################################
###############################################################################################



def Mode200_date_select(Occupied_Timeline, Moon_list):
    
    if( len(Moon_list) == 0):
        
        Mode200_comment = 'Moon not visible'
    
        return Occupied_Timeline, Mode200_comment
    
    Moon_H_offset = [Moon_list[x]['H-offset'] for x in range(len(Moon_list))]
    Moon_V_offset = [Moon_list[x]['V-offset'] for x in range(len(Moon_list))]
    Moon_date = [Moon_list[x]['Date'] for x in range(len(Moon_list))]
    
    Moon_H_offset_sorted = [abs(x) for x in Moon_H_offset]
    Moon_H_offset_sorted.sort()
    
    print(Moon_list)
    
    restart = True
    iterations = 0
    ## Selects date based on min H-offset, if occupied, select date for next min H-offset
    while( restart == True):
        
        if( len(Moon_H_offset) == iterations):
            Mode200_comment = 'No time available for Mode200'
            return Occupied_Timeline, Mode200_comment
        
        restart = False
        
        
        
        
        #Extract index of  minimum H-offset for first iteration, 
        #then next smallest if 2nd iterations needed and so on
        x = Moon_H_offset.index(Moon_H_offset_sorted[iterations])
        
        Moon200_date = Moon_date[x]
        
        Moon200_date = ephem.Date(ephem.Date(Moon200_date)-ephem.second*(Mode200_default()['freeze_start']+50))
        
        Mode200_endDate = ephem.Date(Moon200_date+ephem.second* 
                                     (Timeline_params()['mode_separation']+Mode200_default()['mode_duration']))
        
        ## Extract Occupied dates and if they clash, restart loop and select new date
        for busy_dates in Occupied_Timeline.values():
            if( busy_dates == []):
                continue
            else:
                if( busy_dates[0] <= Moon200_date <= busy_dates[1] or 
                       busy_dates[0] <= Mode200_endDate <= busy_dates[1]):
                    
                    iterations = iterations + 1
                    restart = True
                    break
        
    Occupied_Timeline['Mode200'] = (Moon200_date, Mode200_endDate)
    
    Mode200_comment = 'VFOV: '+str(Moon_V_offset[x])+' HFOV: '+str(Moon_H_offset[x])+', Number of times date changed: '+str(iterations)
    
    
    return Occupied_Timeline, Mode200_comment
