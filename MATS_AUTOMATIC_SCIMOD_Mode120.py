# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 16:19:57 2018

Part of a program to automatically generate a mission timeline from parameters
defined in SCIMOD_DEFAULT_PARAMS. The timeline consists of
science modes and their start dates expressed as a list in chronological order

@author: David
"""

import ephem
from pylab import array, cos, sin, cross, dot, zeros, sqrt, norm, pi, arccos, around, sort
from astroquery.vizier import Vizier
from MATS_AUTOMATIC_SCIMOD_date_calculator_library import rot_arbit, deg2HMS, lat_2_R
from MATS_TIMELINE_SCIMOD_DEFAULT_PARAMS import Timeline_params, getTLE, Mode120_default, Mode120_calculator_defaults
import csv



def Mode120(Occupied_Timeline):
    
    star_list = Mode120_date_calculator()
    Occupied_Timeline, Mode120_comment = Mode120_date_select(Occupied_Timeline, star_list)
    
    return Occupied_Timeline, Mode120_comment



#########################################################################################
#####################################################################################################



def Mode120_date_calculator():
#if(True):
    
    
    "Simulation length and timestep"
    timesteps = Timeline_params()['duration']
    timestep = 1 #In seconds
    
    date = Timeline_params()['start_time']
    
    "Get relevant stars"
    result = Vizier(columns=['all'], row_limit=200).query_constraints(catalog='I/239/hip_main',Vmag=Mode120_calculator_defaults()['Vmag'])
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
    
    "Calculate unit-vectors of stars"
    stars_x = cos(stars_dec)* cos(stars_ra)
    stars_y = cos(stars_dec)* sin(stars_ra)
    stars_z = sin(stars_dec)
    stars_r = array([stars_x,stars_y,stars_z])
    stars_r = stars_r.transpose()
    
    "Prepare the output"
    star_list = []
    star_list.append(['Name;'])
    star_list.append(['t1;'])
    star_list.append(['t2;'])
    star_list.append(['long1;'])
    star_list.append(['lat1;'])
    star_list.append(['long2;'])
    star_list.append(['lat2;'])
    star_list.append(['mag;'])
    star_list.append(['H_offset;'])
    star_list.append(['V_offset;'])
    star_list.append(['H_offset2;'])
    star_list.append(['V_offset2;'])
    star_list.append(['e_Hpmag;'])
    star_list.append(['Hpscat;'])
    star_list.append(['o_Hpmag;'])
    star_list.append(['Classification;'])
    
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
    
    angle_between_orbital_plane_and_star = zeros((timesteps,ROWS))
    
    "Constants"
    R_mean = 6371 #Earth radius
    U = 398600.4418 #Earth gravitational parameter
    FOV_altitude = Mode120_calculator_defaults()['default_pointing_altitude']/1000  #Altitude at which MATS center of FOV is looking
    pointing_adjustment = 3 #Angle in degrees that the pointing can be adjusted
    V_FOV = Mode120_calculator_defaults()['V_FOV'] #0.91 is actual V_FOV
    H_FOV = Mode120_calculator_defaults()['H_FOV']  #5.67 is actual H_FOV
    pitch_offset_angle = 0
    yaw_offset_angle = 0
    
    MATS = ephem.readtle('MATS',getTLE()[0],getTLE()[1])
    
    
    
    ################## Start of Simulation ########################################
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(timesteps):
        
        
        current_time = ephem.Date(date+ephem.second*timestep*t)
        
        MATS.compute(current_time)
        
        (lat_MATS[t],long_MATS[t],altitude_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
        MATS.sublat,MATS.sublong,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
        
        R = lat_2_R(lat_MATS[t])
        
        z_MATS[t] = sin(g_dec_MATS[t])*(altitude_MATS[t]+R)
        x_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R)* cos(g_ra_MATS[t])
        y_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R)* sin(g_ra_MATS[t])
       
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        
        #Semi-Major axis of MATS, assuming circular orbit
        MATS_p[t] = norm(r_MATS[t,0:3])
        
        #Orbital Period of MATS
        MATS_P[t] = 2*pi*sqrt(MATS_p[t]**3/U)
        
        #Estimated pitch or elevation angle for MATS pointing
        pitch_sensor_array[t]= array(arccos((R_mean+FOV_altitude)/(R+altitude_MATS[t]))/pi*180)
        pitch_sensor = pitch_sensor_array[t][0]
        
        
                
        if(t != 0):
            
            
            ############# Calculations of orbital and pointing vectors ############
            "Vector normal to the orbital plane of MATS"
            normal_orbital[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbital[t,0:3] = normal_orbital[t,0:3] / norm(normal_orbital[t,0:3])
            
            
            "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
            rot_mat = rot_arbit(-pi/2+(-pitch_sensor+pitch_offset_angle)/180*pi, normal_orbital[t,0:3])
            r_FOV[t,0:3] = (r_MATS[t] @ rot_mat) /2
            
            
            
            
            
            
            "Rotate yaw of pointing direction, meaning to rotate around the vector to MATS"
            rot_mat = rot_arbit(yaw_offset_angle/180*pi, r_MATS[t,0:3])
            r_FOV[t,0:3] = (r_FOV[t,0:3] @ rot_mat)
            r_FOV_unit_vector[t,0:3] = r_FOV[t,0:3]/norm(r_FOV[t,0:3])/2
            
            
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
            
            
            
            ###################### Star-mapper ####################################
            
            "Check position of stars relevant to pointing direction"
            for x in range(ROWS):
                
                "Skip star if it is not visible during this epoch"
                if(stars[x].name in skip_star_list):
                    
                    continue
                
                "Check if a star has already been spotted during this orbit."
                if( stars[x].name in spotted_star_name ):
                    
                    '''Check if not enough time has passed so that the star has not left FOV''' 
                    if((current_time - spotted_star_timestamp[spotted_star_name.index(stars[x].name)]) < ephem.second*(V_FOV*2*MATS_P[t]/360)):
                        
                        '''Check if enough time has passed so that the star is roughly in the same
                        direction as original FOV and save lat,long, Hoffset, Voffset and time. Otherwise skip star.'''
                        if( (t-spotted_star_timecounter[spotted_star_name.index(stars[x].name)])*timestep == around(MATS_P[t]*(pitch_offset_angle+V_FOV/2)/360)):
                            
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
                            
                            star_list[2].append(str(current_time)+';')
                            star_list[5].append(str(float(long_MATS[t]/pi*180))+';')
                            star_list[6].append(str(float(lat_MATS[t]/pi*180))+';')
                            star_list[10].append(str(stars_hori_offset[t][x])+';')
                            star_list[11].append(str(stars_vert_offset[t][x])+';')
                            
                        continue
                        
                        "If enough time has passed (half an orbit), the star can be removed from the exception list"
                    elif((current_time - spotted_star_timestamp[spotted_star_name.index(stars[x].name)]) >= ephem.second*(180*MATS_P[t]/360)):
                        spotted_star_timestamp.pop(spotted_star_name.index(stars[x].name))
                        spotted_star_timecounter.pop(spotted_star_name.index(stars[x].name))
                        spotted_star_name.remove(stars[x].name)
                        
                        
                
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
                
                "To be able to skip stars far outside the orbital plane of MATS"
                angle_between_orbital_plane_and_star[t][x] = arccos( dot(stars_r[0][x], stars_r_V_offset_plane[x]) / norm(stars_r_V_offset_plane[x])) /pi*180
                
                "For first loop of stars, make exception list for stars not visible during this epoch"
                if( t == 1 and abs(angle_between_orbital_plane_and_star[t][x]) > H_FOV/2+360/50):
                    skip_star_list.append(stars[x].name)
                    continue
                    
                
                
                "Check if star is in FOV"
                if( abs(stars_vert_offset[t][x]) < V_FOV/2 and abs(stars_hori_offset[t][x]) < H_FOV/2):
                    #print('Star number:',stars[x].name,'is visible at',stars_vert_offset[t][x],'degrees VFOV and', \
                         #stars_hori_offset[t][x],'degrees HFOV','during',ephem.Date(current_time))
                    
                    "Add the spotted star to the exception list and timestamp it"
                    spotted_star_name.append(stars[x].name)
                    spotted_star_timestamp.append(current_time)
                    spotted_star_timecounter.append(t) 
                    
                    
                    "Log all relevent data for the star"
                    star_list[0].append(stars[x].name+';')
                    star_list[1].append(str(current_time)+';')
                    star_list[3].append(str(float(long_MATS[t]/pi*180))+';')
                    star_list[4].append(str(float(lat_MATS[t]/pi*180))+';')
                    star_list[7].append(str(stars[x].mag)+';')
                    star_list[8].append(str(stars_hori_offset[t][x])+';')
                    star_list[9].append(str(stars_vert_offset[t][x])+';')
                    star_list[12].append(str(star_cat[x]['e_Hpmag'])+';')
                    star_list[13].append(str(star_cat[x]['Hpscat'])+';')
                    star_list[14].append(str(star_cat[x]['o_Hpmag'])+';')
                    star_list[15].append(str(star_cat[x]['SpType'])+';')
                    
                    
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
    with open('MATS_Visible_Stars.csv', 'w', newline='') as write_file:
        writer = csv.writer(write_file, dialect='excel-tab')
        writer.writerows(star_list)
    
    return(star_list)



#####################################################################################################
#####################################################################################################



def Mode120_date_select(Occupied_Timeline, star_list):
    
    if( len(star_list[0]) == 1):
        Mode120_comment = 'Stars not visible'
    
        return Occupied_Timeline, Mode120_comment
    
    star_mag = []
    star_min_mag_H_offset = []
    
    "Extract magnitudes into floats from the list"
    for x in range(len(star_list[7])-1):
        star_mag.append(float(star_list[7][x+1][:-1]))
        
    "Extract all the H-offsets for the brightest star"
    for x in range(len(star_list[7])-1):
        if( min(star_mag) == star_mag[x]):
            star_min_mag_H_offset.append( abs(float(star_list[8][x+1][:-1])))
        #Just add an arbitrary large H-offset value for stars other than the brightest
        else:
            star_min_mag_H_offset.append(10)
    
    star_min_mag_H_offset_sorted = sort(star_min_mag_H_offset)
        
    restart = True
    iterations = 0
    ## Selects date based on min H-offset and mag, if occupied, select date for next min H-offset
    while( restart == True):
        
        if( len(star_min_mag_H_offset) == iterations):
            Mode120_comment = 'No time available for Mode120'
            return Occupied_Timeline, Mode120_comment
        
        restart = False
        
        
        
        #Extract index of brightest star with minimum H-offset for first iteration, 
        #then next smallest if 2nd iterations needed and so on
        x = star_min_mag_H_offset.index(star_min_mag_H_offset_sorted[iterations])
        
        star_calibration_date = star_list[1][x+1]
        star_calibration_name = star_list[0][x+1]
        star_calibration_MATS_long = star_list[3][x+1]
        star_calibration_MATS_lat = star_list[4][x+1]
        
        
        Mode120_date = ephem.Date(ephem.Date(star_calibration_date[:-1])-ephem.second*(Mode120_default()['freeze_start']+50))
        
        Mode120_endDate = ephem.Date(Mode120_date+ephem.second* 
                                     (Timeline_params()['mode_separation']+Mode120_default()['mode_duration']))
        
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
    
    Mode120_comment = ('Star name:'+star_calibration_name+', Number of times date changed: '+str(iterations)
        +', MATS (long,lat) in degrees = ('+star_calibration_MATS_long+', '+star_calibration_MATS_lat+')')
    
    
    return Occupied_Timeline, Mode120_comment
    