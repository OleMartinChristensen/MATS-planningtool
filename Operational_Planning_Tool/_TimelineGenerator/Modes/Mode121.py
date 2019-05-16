# -*- coding: utf-8 -*-
"""Schedules the active Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""


import logging, sys
import ephem
from pylab import array, cos, sin, cross, dot, zeros, sqrt, norm, pi, arccos, floor, arctan
from astroquery.vizier import Vizier

from Operational_Planning_Tool._Library import rot_arbit, deg2HMS, lat_2_R
from OPT_Config_File import Timeline_settings, getTLE, Mode121_settings, Logger_name

Logger = logging.getLogger(Logger_name())


def Mode121(Occupied_Timeline):
    """Core function for the scheduling of Mode121.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes with entries equal to their start and end time as a list.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    date_magnitude_array = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, date_magnitude_array)
    
    
    return Occupied_Timeline, comment
    


##################################################################################################
##################################################################################################



def date_calculator():
    """Subfunction, Simulates MATS FOV and stars.
    
    Simuates the FOV and visible stars for one orbit then skips ahead for *Timeskip* amount of days (as defined in OPT_Config_File). 
    Saves the date, pointing RA and Dec, and the magnitude of the brightest visible star at each timestep.
    
    Arguments:
        
    Returns:
        (array): Array containing date in first column and brightest magnitude visible in the second. Contains current Dec and RA in 3rd and 4th column respectively.
    
    """
    
    Settings = Mode121_settings()
    
    "Simulation length and timestep"
    log_timestep = Settings['log_timestep']
    Logger.debug('log_timestep: '+str(log_timestep))

    timestep = Settings['timestep'] #In seconds
    Logger.info('timestep set to: '+str(timestep)+' s')
    
    duration = Timeline_settings()['duration']
    Logger.info('Duration set to: '+str(duration)+' s')
    
    timesteps = int(floor(duration / timestep))
    Logger.info('Total number of timesteps set to: '+str(timesteps)+' s')
    
    timeline_start = ephem.Date(Timeline_settings()['start_date'])
    
    initial_time = ephem.Date( timeline_start + ephem.second*Settings['freeze_start'] )
    Logger.info('initial_time set to: '+str(initial_time))
    
    
    "Get relevant stars"
    result = Vizier(columns=['all'], row_limit=2500).query_constraints(catalog='I/239/hip_main',Vmag=Settings['Vmag'])
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
        stars[t].compute(epoch='2000')
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
    "Array containing date in first column and brightest magnitude visible in the second. Contains current Dec and RA in 3rd and 4th column"
    date_magnitude_array = zeros((timesteps,4))
    "Set magntidues arbitrary large, which will correspond to no star being visible"
    date_magnitude_array[:,1] = 100
    
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
    normal_orbit = zeros((timesteps,3))
    r_V_offset_normal = zeros((timesteps,3))
    r_H_offset_normal = zeros((timesteps,3))
    pitch_sensor_array = zeros((timesteps,1))
    pitch_LP_array = zeros((timesteps,1))
    star_counter = 0
    skip_star_list = []
    MATS_p = zeros((timesteps,1))
    MATS_P = zeros((timesteps,1))
    brightest_star_per_timestep = []
    
    angle_between_orbital_plane_and_star = zeros((timesteps,ROWS))
    
    "Constants"
    celestial_eq_normal = array([[0,0,1]])
    R_mean = 6371 #Earth radius [km]
    #wgs84_Re = 6378.137 #Equatorial radius of wgs84 spheroid [km]
    # wgs84_Rp = 6356752.3142 #Polar radius of wgs84 spheroid [km]
    U = 398600.4418 #Earth gravitational parameter
    LP_altitude = Timeline_settings()['LP_pointing_altitude']/1000  #Altitude at which MATS center of FOV is looking [km]
    pointing_altitude = Settings['pointing_altitude']/1000 
    #extended_Re = wgs84_Re + LP_altitude #Equatorial radius of extended wgs84 spheroid
    #f_e = (wgs84_Re - wgs84_Rp) / Re_extended #Flattening of extended wgs84 spheroid
    V_FOV = Settings['V_FOV']
    H_FOV = Settings['H_FOV']  #5.67 is actual H_FOV
    
    pitch_offset_angle = 0
    yaw_correction = Timeline_settings()['yaw_correction']
    
    Logger.debug('Earth radius used [km]: '+str(R_mean))
    Logger.debug('LP_altitude set to [km]: '+str(LP_altitude))
    Logger.debug('H_FOV set to [degrees]: '+str(H_FOV))
    Logger.debug('V_FOV set to [degrees]: '+str(V_FOV))
    Logger.debug('yaw_correction set to: '+str(yaw_correction))
    
    
    
    
    Logger.debug('TLE used: '+getTLE()[0]+getTLE()[1])
    MATS = ephem.readtle('MATS',getTLE()[0],getTLE()[1])
    
    "Loop counter"
    t=0
    
    time_skip_counter = 0
    timeskip = Settings['TimeSkip'] #Days to skip ahead after each completed orbit
    current_time = initial_time
    
    Logger.info('')
    Logger.info('Start of simulation of MATS for Mode121')
    
    
    ################## Start of Simulation ########################################
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    while(current_time < timeline_start+ephem.second*duration):
        
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
            pitch_sensor_array[t]= array(arccos((R_mean+pointing_altitude)/(R+altitude_MATS[t]))/pi*180)
            pitch_sensor = pitch_sensor_array[t][0]
        
        if( (t*timestep % log_timestep == 0 or t == 1) and t != 0 ):
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
                
            # More accurate estimation of pitch angle of MATS using R_LP instead of R_mean
            pitch_LP_array[t]= array(arccos((R_LP+LP_altitude)/(R+altitude_MATS[t]))/pi*180)
            pitch_LP = pitch_LP_array[t][0]
            
            pitch_sensor_array[t]= array(arccos((R_LP+pointing_altitude)/(R+altitude_MATS[t]))/pi*180)
            pitch_sensor = pitch_sensor_array[t][0]
            
            
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
                    
                yaw_offset_angle = Timeline_settings()['yaw_amplitude'] * cos( arg_of_lat/180*pi - pitch_LP/180*pi + Timeline_settings()['yaw_phase']/180*pi )
                yaw_offset_angle = yaw_offset_angle[0]
                
                if( t*timestep % log_timestep == 0 or t == 1 ):
                    Logger.debug('ascending_node: '+str(ascending_node))
                    Logger.debug('arg_of_lat [degrees]: '+str(arg_of_lat))
                    Logger.debug('yaw_offset_angle [degrees]: '+str(yaw_offset_angle))
                
            elif( yaw_correction == False):
                yaw_offset_angle = 0
            
            
            "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
            rot_mat = rot_arbit(pi/2+(pitch_sensor+pitch_offset_angle)/180*pi, normal_orbit[t,0:3])
            r_FOV[t,0:3] = (rot_mat @ r_MATS[t] ) /2
            
            
            #rot_mat2 = rot_arbit(pi/2+(pitch_sensor+pitch_offset_angle)/180*pi, normal_orbit[t,0:3])
            #r_FOV2[t,0:3] = (rot_mat2 @ r_MATS[t]) /2
            #r_FOV_unit_vector2[t,0:3] = r_FOV2[t,0:3]/norm(r_FOV2[t,0:3])
            
            "Rotate yaw of pointing direction, meaning to rotate around the vector to MATS"
            rot_mat = rot_arbit(-yaw_offset_angle/180*pi, r_MATS[t,0:3])
            r_FOV[t,0:3] = (rot_mat @ r_FOV[t,0:3] )
            r_FOV_unit_vector[t,0:3] = r_FOV[t,0:3]/norm(r_FOV[t,0:3])
            
            
            '''Rotate 'vector to MATS', to represent vector normal to satellite H-offset plane,
            which will be used to project stars onto it which allows the H-offset of stars to be found'''
            rot_mat = rot_arbit((pitch_sensor)/180*pi, normal_orbit[t,0:3])
            r_H_offset_normal[t,0:3] = ( rot_mat @ r_MATS[t] )
            r_H_offset_normal[t,0:3] = r_H_offset_normal[t,0:3] / norm(r_H_offset_normal[t,0:3])
            
            "If pointing direction has a Yaw defined, Rotate yaw of normal to pointing direction H-offset plane, meaning to rotate around the vector to MATS"
            rot_mat = rot_arbit(-yaw_offset_angle/180*pi, r_MATS[t,0:3])
            r_H_offset_normal[t,0:3] = (rot_mat @ r_H_offset_normal[t,0:3])
            r_H_offset_normal[t,0:3] = r_H_offset_normal[t,0:3]/norm(r_H_offset_normal[t,0:3])
            
            "Rotate orbital plane normal to make it into pointing V-offset plane normal"
            r_V_offset_normal[t,0:3] = (rot_mat @ normal_orbit[t,0:3])
            r_V_offset_normal[t,0:3] = r_V_offset_normal[t,0:3]/norm(r_V_offset_normal[t,0:3])
            
            "Calculate Dec and RA of optical axis (disregarding parallax)"
            optical_axis = r_FOV_unit_vector[t,0:3]
            Dec = arctan( sqrt(optical_axis[0]**2 + optical_axis[1]**2) / optical_axis[2] ) /pi * 180
            Ra = arccos( dot( [1,0,0], [optical_axis[0],optical_axis[1],0] ) / norm([optical_axis[0],optical_axis[1],0]) ) / pi * 180
            
            if( optical_axis[1] < 0 ):
                Ra = 360-Ra
            
            if( t*timestep % log_timestep == 0 or t == 1 ):
                Logger.debug('Current time: '+str(current_time))
                Logger.debug('R_LP [km]: '+str(R_LP))
                
                Logger.debug('FOV pitch in degrees: '+str(pitch_sensor))
                Logger.debug('Absolute value of latitude of LP: '+str(abs_lat_LP/pi*180))
                Logger.debug('Pointing direction of FOV: '+str(r_FOV_unit_vector[t,0:3]))
                #Logger.debug('Pointing direction of FOV2: '+str(r_FOV_unit_vector2[t,0:3]))
                Logger.debug('Orthogonal direction to H-offset plane: '+str(r_H_offset_normal[t,0:3]))
                Logger.debug('Orthogonal direction to V-offset plane: '+str(r_V_offset_normal[t,0:3]))
                Logger.debug('Orthogonal direction to the orbital plane: '+str(normal_orbit[t,0:3]))
                Logger.debug('')
            
            
            ############# End of Calculations of orbital and pointing vectors #####
            
            "Add current date to date_magnitude_array"
            date_magnitude_array[t-1,0] = current_time 
            "Add optical axis Dec and RA to date_magnitude_array"
            date_magnitude_array[t-1,2] = Dec
            date_magnitude_array[t-1,3] = Ra
            
            ###################### Star-mapper ####################################
            
            "Check position of stars relevant to pointing direction"
            for x in range(ROWS):
                
                "Skip star if it is not visible during this epoch"
                if(stars[x].name in skip_star_list):
                    continue
                    
                
                
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
                    
                    if( t % log_timestep == 0 or t == 1 ):
                        Logger.debug('Current time: '+str(current_time))
                        Logger.debug('Star: '+stars[x].name+', with H-offset: '+str(stars_hori_offset[t][x])+' V-offset: '+str(stars_vert_offset[t][x])+' in degrees is visible')
                    
                    "Check if it is the brightest star spotted in the current FOV at the current date, and if so, replace the current value"
                    if( stars[x].mag < date_magnitude_array[t-1,1] ):
                        date_magnitude_array[t-1,1] = stars[x].mag
                        
                    
                    star_counter = star_counter + 1
                    
            ######################### End of star_mapper #############################
        
        "Increment time with timestep or jump ahead in time if a whole orbit was completed"
        if( (current_time - initial_time)/ephem.second > (timeskip/ephem.second * time_skip_counter + MATS_P[t] * (time_skip_counter+1)) ):
            "If one orbit has passed -> increment 'current_time' with 'timeskip' amount of days"
            time_skip_counter = time_skip_counter + 1
            current_time = ephem.Date(current_time + timeskip)
        else:
            "Else just increment the current_time with timestep"
            current_time = ephem.Date(current_time + ephem.second * timestep)
        
        "Loop counter"
        t = t + 1
        
    ################## End of Simulation ########################################
    
    
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
    ax.scatter(normal_orbit[points_2_plot_start:points_2_plot,0]/2, normal_orbit[points_2_plot_start:points_2_plot,1]/2, normal_orbit[points_2_plot_start:points_2_plot,2]/2)
    ax.scatter(r_H_offset_normal[points_2_plot_start:points_2_plot,0]/2, r_H_offset_normal[points_2_plot_start:points_2_plot,1]/2, r_H_offset_normal[points_2_plot_start:points_2_plot,2]/2)
    '''
    ########################### END of Optional plotter ########################################
    
    
    Logger.debug('brightest_star_per_timestep: '+str(brightest_star_per_timestep))
    
    return(date_magnitude_array)
    



##################################################################################################
##################################################################################################



def date_select(Occupied_Timeline, date_magnitude_array):
    """Subfunction, Schedules a simulated date.
    
    A date is selected for when the brightest star visible; has the faintest magntitude compared
    to other brightest stars visible at other timesteps.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes together with their start and end time in a list. The list is empty if the Mode is unscheduled.
        date_magnitude_array (array): Array containing date in first column and brightest magnitude visible in the second. Contains Dec and RA in 3rd and 4th column respectively.
        
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    Logger.info('Start of filtering function')
    
    settings = Mode121_settings()
    
    "Get the name of the parent function, which is always defined as the name of the mode"
    Mode_name = sys._getframe(1).f_code.co_name
    
    arbitraryLowNumber = -100
    
    restart = True
    
    loop_counter = 0
    
    "Loop for maximum magnitude visible until the date chosen is not occupied"
    while(restart == True):
        
        restart = False
        
        index_max_mag = date_magnitude_array[:,1].argmax()
        value_max_mag = date_magnitude_array[:,1].max()
        
        "If the all the magnitudes have been set arbitrary low -> No Date available -> Exit"
        if(value_max_mag == arbitraryLowNumber):
            comment = 'No available time for '+Mode_name
            Logger.warning(comment)
            #input('Enter anything to ackknowledge and continue')
            return Occupied_Timeline, comment
        
        date_max_mag = date_magnitude_array[index_max_mag,0]
        dec_max_mag = date_magnitude_array[index_max_mag,2]
        RA_max_mag = date_magnitude_array[index_max_mag,3]
        
        date = ephem.Date(ephem.Date(date_max_mag)-ephem.second*(settings['freeze_start']))
        endDate = ephem.Date(date+ephem.second*settings['mode_duration'])
        
        "Extract the start and end date of each scheduled mode"
        for busy_dates in Occupied_Timeline.values():
            if( busy_dates == []):
                continue
            else:
                "Extract the start and end date of each instance of a scheduled mode"
                for busy_date in busy_dates:
                    
                    "If the planned date collides with any already scheduled ones -> post-pone and restart loop"
                    if( busy_date[0] <= date < busy_date[1] or 
                           busy_date[0] < endDate <= busy_date[1] or
                           (date < busy_date[0] and endDate > busy_date[1])):
                        
                        restart = True
                        "Set the current maximum magnitude arbitrary small to allow a new maximum magnitude date to be chosen in next loop"
                        date_magnitude_array[index_max_mag,1] = arbitraryLowNumber
                        loop_counter = loop_counter +1
                        break
                
        
    comment = 'Number of times date changed: ' + str(loop_counter)+', faintest magnitude visible (100 equals no stars visible): '+str(value_max_mag)+', Dec (J2000): '+str(dec_max_mag)+', RA (J2000): '+str(RA_max_mag)
    Occupied_Timeline[Mode_name].append((date,endDate))
    
    return Occupied_Timeline, comment
        