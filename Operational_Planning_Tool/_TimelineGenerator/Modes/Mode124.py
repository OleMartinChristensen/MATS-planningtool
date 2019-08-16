# -*- coding: utf-8 -*-
"""Schedules the active Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""


import ephem, sys, logging, importlib
from pylab import array, cos, sin, cross, dot, zeros, sqrt, norm, pi, arccos, arctan

from Operational_Planning_Tool._Library import rot_arbit, lat_2_R, scheduler, lat_MATS_calculator
from Operational_Planning_Tool import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def Mode124(Occupied_Timeline):
    """Core function for the scheduling of Mode124.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes with entries equal to their start and end time as a list.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    dates = date_calculator()
    
    Occupied_Timeline, comment = date_select(Occupied_Timeline, dates)
      
    return Occupied_Timeline, comment



###############################################################################################
###############################################################################################



def date_calculator():
    """Subfunction, Either selects a user provided date, or simulates MATS FOV and the Moon.
    
    If 'automatic' in *Mode124_settings* is set to False, the date in *Mode124_settings* will be returned.. \n
    If 'automatic' in *Mode124_settings* is set to True. A list of dictionaries containing simulated dates is returned. 
    
    Determines when the Moon is entering the FOV at an vertical offset-angle equal to *#V-offset* and also being 
    located at a horizontal off-set angle equal to less than *#H-offset* when pointing at an LP altitude equal to *#pointing_altitude*. \n
    
    A timeskip equal to 1/2 an orbit of MATS is applied after a successful spotting of the Moon. \n
    
    Timeskips equal to the time it takes for the Moon orbital position to change by *#H-offset* degrees are also applied if the Moon is 
    determined to be at an horizontal off-set angle larger then the horizontal FOV of the instrument, equal to *#HFOV*. \n
    
    (# as defined in the *Configuration File*). \n
    
    Saves the date and parameters regarding the spotting of the Moon
    Also saves relevant data to an .csv file located in Output/.
    
    Arguments:
        
    Returns:
        dates ((:obj:`list` of :obj:`dict`)) or (str): A list containing dictionaries containing parameters for each time the Moon is spotted. Or just a date depending on 'automatic' in *Mode124_settings*.
    
    """
    
    Timeline_settings = OPT_Config_File.Timeline_settings()
    Mode124_settings = OPT_Config_File.Mode124_settings()
    
    automatic = Mode124_settings['automatic']
    Logger.info('automatic = '+str(automatic))
    
    "To either calculate when Moon is visible and schedule from that data or just schedule at a given time given by Mode124_settings['start_date']"
    if( automatic == False ):
        try:
            date = ephem.Date(Mode124_settings['start_date'])
            return date
        except:
            Logger.error('Could not get OPT_Config_File.Mode124_settings["start_date"], exiting...')
            sys.exit()
        
    elif( automatic == True ):
        
        
        
        log_timestep = Mode124_settings['log_timestep']
        Logger.debug('log_timestep: '+str(log_timestep))
        
        
        "Simulation length and timestep"
        
        timestep = Mode124_settings['timestep'] #In seconds
        Logger.info('Timestep set to [s]: '+str(timestep))
        
        duration = Timeline_settings['duration']
        Logger.info('Duration set to [s]: '+str(duration))
        
        timeline_start = ephem.Date(Timeline_settings['start_date'])
        initial_time= ephem.Date( timeline_start + ephem.second*Mode124_settings['freeze_start'] )
        
        Logger.info('Initial simulation date set to: '+str(initial_time))
        
        MATS = ephem.readtle('MATS',OPT_Config_File.getTLE()[0],OPT_Config_File.getTLE()[1])
        
        Moon = ephem.Moon()
        
        "Pre-allocate space"
        lat_MATS = zeros((duration,1))
        long_MATS = zeros((duration,1))
        altitude_MATS = zeros((duration,1))
        a_ra_MATS = zeros((duration,1))
        a_dec_MATS = zeros((duration,1))
        x_MATS = zeros((duration,1))
        y_MATS = zeros((duration,1))
        z_MATS = zeros((duration,1))
        r_MATS = zeros((duration,3))
        r_MATS_unit_vector = zeros((duration,3))
        r_FOV = zeros((duration,3))
        normal_orbit = zeros((duration,3))
        r_H_offset_normal = zeros((duration,3))
        r_V_offset_normal = zeros((duration,3))
        pitch_LP_array = zeros((duration,1))
        pitch_pointing_command_array = zeros((duration,1))
        MATS_p = zeros((duration,1))
        MATS_P = zeros((duration,1))
        
        a_ra_Moon = zeros((duration,1))
        a_dec_Moon = zeros((duration,1))
        distance_Moon = zeros((duration,1))
        x_Moon = zeros((duration,1))
        y_Moon = zeros((duration,1))
        z_Moon = zeros((duration,1))
        r_Moon = zeros((duration,3))
        r_MATS_2_Moon = zeros((duration,3))
        r_MATS_2_Moon_norm = zeros((duration,3))
        Moon_r_V_offset_plane = zeros((duration,3))
        Moon_r_H_offset_plane = zeros((duration,3))
        Moon_r_orbital_plane = zeros((duration,3))
        Moon_vert_offset = zeros((duration,1))
        Moon_hori_offset = zeros((duration,1))
        angle_between_orbital_plane_and_moon = zeros((duration,1))
        dates = []
        r_Moon_unit_vector = zeros((duration,3))
        
        
        
        "Constants"
        AU = 149597871 #km
        R_mean = 6371 #Earth radius
        U = 398600.4418 #Earth gravitational parameter
        LP_altitude = Timeline_settings['LP_pointing_altitude']/1000  #Altitude at which MATS center of FOV is looking
        pointing_altitude = Mode124_settings['pointing_altitude']/1000 
        H_offset = Mode124_settings['H_offset']  #5.67 is actual H_offset
        V_offset = Mode124_settings['V_offset'] 
        Moon_orbital_period = 3600*24*27.32
        celestial_eq_normal = array([[0,0,1]])
        yaw_correction = Timeline_settings['yaw_correction']
        
        Logger.debug('LP_altitude set to [km]: '+str(LP_altitude))
        Logger.debug('H_offset set to [degrees]: '+str(H_offset))
        Logger.debug('V_offset set to [degrees]: '+str(V_offset))
        Logger.debug('Moon_orbital_period [s]: '+str(Moon_orbital_period))
        Logger.debug('yaw_correction set to: '+str(yaw_correction))
        
        t=0
        
        
        current_time = initial_time
        
        Logger.info('')
        Logger.info('Start of simulation for Mode124')
        
        while(current_time < initial_time+ephem.second*duration):
            
            MATS.compute(current_time, epoch = '2000/01/01 11:58:55.816')
            Moon.compute(current_time, epoch = '2000/01/01 11:58:55.816')
            
            
            (lat_MATS[t],long_MATS[t],altitude_MATS[t],a_ra_MATS[t],a_dec_MATS[t])= (
            MATS.sublat,MATS.sublong,MATS.elevation/1000,MATS.a_ra,MATS.a_dec)
            
            R = lat_2_R(lat_MATS[t])
            
            z_MATS[t] = sin(a_dec_MATS[t])*(altitude_MATS[t]+R)
            x_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R)* cos(a_ra_MATS[t])
            y_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R)* sin(a_ra_MATS[t])
           
            r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
            r_MATS_unit_vector[t] = r_MATS[t]/norm(r_MATS[t])
            
            
            #Semi-Major axis of MATS, assuming circular orbit
            MATS_p[t] = norm(r_MATS[t,0:3])
            
            #Orbital Period of MATS
            MATS_P[t] = 2*pi*sqrt(MATS_p[t]**3/U)
            
            #Initial Estimated pitch or elevation angle for MATS pointing
            if(t == 0):
                pitch_LP_array[t]= array(arccos((R_mean+LP_altitude)/(R+altitude_MATS[t]))/pi*180)
                pitch_LP = pitch_LP_array[t][0]
                time_between_LP_and_MATS = MATS_P[t][0]*pitch_LP/360
                timesteps_between_LP_and_MATS = int(time_between_LP_and_MATS / timestep)
            
            (a_ra_Moon[t], a_dec_Moon[t], distance_Moon[t])= (
                    Moon.a_ra, Moon.a_dec, Moon.earth_distance*AU)
            
            z_Moon[t] = sin(a_dec_Moon[t]) * distance_Moon[t]
            x_Moon[t] = cos(a_dec_Moon[t])*cos(a_ra_Moon[t]) * distance_Moon[t]
            y_Moon[t] = cos(a_dec_Moon[t])*sin(a_ra_Moon[t]) * distance_Moon[t]
           
            r_Moon[t,0:3] = [x_Moon[t], y_Moon[t], z_Moon[t]]
            r_Moon_unit_vector[t,0:3] = r_Moon[t,0:3]/norm(r_Moon[t,0:3])
            
            r_MATS_2_Moon[t] = r_Moon[t]-r_MATS[t]
            r_MATS_2_Moon_norm[t] = r_MATS_2_Moon[t]/norm(r_MATS_2_Moon[t])
            
            
            
            if( t*timestep % log_timestep == 0 and t != 0 or t == 1 ):
                Logger.debug('')
                
                Logger.debug('t (loop iteration number): '+str(t))
                Logger.debug('Current time: '+str(current_time))
                Logger.debug('Semimajor axis in km: '+str(MATS_p[t]))
                Logger.debug('Orbital Period in s: '+str(MATS_P[t]))
                Logger.debug('Vector to MATS [km]: '+str(r_MATS[t,0:3]))
                Logger.debug('Latitude in radians: '+str(lat_MATS[t]))
                Logger.debug('Longitude in radians: '+str(long_MATS[t]))
                Logger.debug('Altitude in km: '+str(altitude_MATS[t]))
                
            
            if(t != 0):
                # More accurate estimation of lat of LP using the position of MATS at a previous time
                if( t >= timesteps_between_LP_and_MATS):
                    abs_lat_LP = abs(lat_MATS[t-timesteps_between_LP_and_MATS])
                    R_earth_LP = lat_2_R(abs_lat_LP)
                else:
                    date_of_MATSlat_is_equal_2_current_LPlat = ephem.Date(current_time - ephem.second * timesteps_between_LP_and_MATS * timestep)
                    abs_lat_LP = abs( lat_MATS_calculator( date_of_MATSlat_is_equal_2_current_LPlat ) )
                    R_earth_LP = lat_2_R(abs_lat_LP)
                    
                """
                # More accurate estimation of the Earths radius below LP
                if( abs(lat_MATS[t])-abs(lat_MATS[t-1]) > 0 ): #Moving towards poles meaning LP is equatorwards compared to MATS
                    abs_lat_LP = abs(lat_MATS[t])-pitch_LP/180*pi #absolute value of estimated latitude of LP in radians
                    R_earth_LP = lat_2_R(abs_lat_LP) #Estimated WGS84 radius of LP from latitude of MATS
                else:
                    abs_lat_LP = abs(lat_MATS[t])+pitch_LP/180*pi #absolute value of estimated latitude of LP in radians
                    R_earth_LP = lat_2_R(abs_lat_LP) #Estimated WGS84 radius of LP from latitude of MATS
                """
                
                # More accurate estimation of pitch angle of MATS using R_earth_LP instead of R_mean
                pitch_LP_array[t]= array(arccos((R_earth_LP+LP_altitude)/(R+altitude_MATS[t]))/pi*180)
                pitch_LP = pitch_LP_array[t][0]
                
                pitch_pointing_command_array[t] = array(arccos((R_earth_LP+pointing_altitude )/(R+altitude_MATS[t]))/pi*180)
                pitch_pointing_command = pitch_pointing_command_array[t][0]
                
                pitch_angle_between_command_and_LP_altitudes = pitch_LP - pitch_pointing_command
                
                
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
                        
                    yaw_offset_angle = Timeline_settings['yaw_amplitude'] * cos( arg_of_lat/180*pi - pitch_LP/180*pi + Timeline_settings['yaw_phase']/180*pi )
                    yaw_offset_angle = yaw_offset_angle[0]
                    
                    if( t*timestep % log_timestep == 0 or t == 1 ):
                        Logger.debug('ascending_node: '+str(ascending_node))
                        Logger.debug('arg_of_lat [degrees]: '+str(arg_of_lat))
                        Logger.debug('yaw_offset_angle [degrees]: '+str(yaw_offset_angle))
                        
                    
                elif( yaw_correction == False):
                    yaw_offset_angle = 0
                
                "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change"
                rot_mat = rot_arbit(pi/2+(pitch_pointing_command)/180*pi, normal_orbit[t,0:3])
                r_FOV[t,0:3] = (rot_mat @ r_MATS[t])
                
                "Rotate yaw of pointing direction, meaning to rotate around the vector to MATS"
                rot_mat = rot_arbit( (-yaw_offset_angle)/180*pi, r_MATS_unit_vector[t,0:3])
                r_FOV[t,0:3] =  rot_mat @ r_FOV[t,0:3]
                r_FOV[t,0:3] = r_FOV[t,0:3] / norm(r_FOV[t,0:3])
                
                "Calculate Dec and RA of optical axis (disregarding parallax)"
                optical_axis = r_FOV[t,0:3]
                Dec_optical_axis = arctan(  optical_axis[2] / sqrt(optical_axis[0]**2 + optical_axis[1]**2) ) /pi * 180
                Ra_optical_axis = arccos( dot( [1,0,0], [optical_axis[0],optical_axis[1],0] ) / norm([optical_axis[0],optical_axis[1],0]) ) / pi * 180
                
                
                if( optical_axis[1] < 0 ):
                    Ra_optical_axis = 360-Ra_optical_axis
                    
                "Calculate Dec and RA of optical axis (disregarding parallax)"
                optical_axis = r_MATS_2_Moon_norm[t,0:3]
                Dec = arctan(  optical_axis[2] / sqrt(optical_axis[0]**2 + optical_axis[1]**2) ) /pi * 180
                Ra = arccos( dot( [1,0,0], [optical_axis[0],optical_axis[1],0] ) / norm([optical_axis[0],optical_axis[1],0]) ) / pi * 180
                
                
                if( optical_axis[1] < 0 ):
                    Ra = 360-Ra
                
                "Rotate 'vector to MATS', to represent a vector normal to the H-offset pointing plane, includes vertical offset change (Parallax is negligable)"
                rot_mat = rot_arbit((pitch_pointing_command)/180*pi, normal_orbit[t,0:3])
                r_H_offset_normal[t,0:3] = (rot_mat @ r_MATS[t])
                
                "If pointing direction has a Yaw defined, Rotate yaw of normal to pointing direction H-offset plane, meaning to rotate around the vector to MATS"
                rot_mat = rot_arbit(-yaw_offset_angle/180*pi, r_MATS_unit_vector[t,0:3])
                r_H_offset_normal[t,0:3] = (rot_mat @ r_H_offset_normal[t])
                r_H_offset_normal[t,0:3] = r_H_offset_normal[t,0:3]/norm(r_H_offset_normal[t,0:3])
                
                "Rotate orbital plane normal to make it into pointing V-offset plane normal"
                r_V_offset_normal[t,0:3] = (rot_mat @ normal_orbit[t])
                r_V_offset_normal[t,0:3] = r_V_offset_normal[t,0:3]/norm(r_V_offset_normal[t,0:3])
                
                
                ############# End of Calculations of orbital and pointing vectors #####
                
                "Project 'r_MATS_2_Moon' ontop of orbital plane"
                Moon_r_orbital_plane[t] = r_MATS_2_Moon_norm[t] - dot(r_MATS_2_Moon_norm[t],normal_orbit[t]) * normal_orbit[t]
                
                "Project 'r_MATS_2_Moon' ontop pointing H-offset and V-offset plane"
                Moon_r_V_offset_plane[t] = r_MATS_2_Moon_norm[t] - dot(r_MATS_2_Moon_norm[t],r_V_offset_normal[t]) * r_V_offset_normal[t]
                Moon_r_H_offset_plane[t] = r_MATS_2_Moon_norm[t] - dot(r_MATS_2_Moon_norm[t],r_H_offset_normal[t]) * r_H_offset_normal[t]
                
                
                "Dot product to get the Vertical and Horizontal angle offset of the Moon"
                Moon_vert_offset[t] = arccos(dot(r_FOV[t],Moon_r_V_offset_plane[t]) / (norm(r_FOV[t])*norm(Moon_r_V_offset_plane[t]))) /pi*180
                Moon_hori_offset[t] = arccos(dot(r_FOV[t],Moon_r_H_offset_plane[t]) / (norm(r_FOV[t])*norm(Moon_r_H_offset_plane[t]))) /pi*180
                
                "Get the offset angle sign correct"
                if( dot(cross(r_FOV[t],Moon_r_V_offset_plane[t]),normal_orbit[t,0:3]) > 0 ):
                    Moon_vert_offset[t] = -Moon_vert_offset[t]
                if( dot(cross(r_FOV[t],Moon_r_H_offset_plane[t]),r_H_offset_normal[t]) > 0 ):
                    Moon_hori_offset[t] = -Moon_hori_offset[t]
                
                
                "Angle between orbital plane and moon"
                angle_between_orbital_plane_and_moon[t] = arccos( dot(r_MATS_2_Moon_norm[t], Moon_r_orbital_plane[t]) / norm(Moon_r_orbital_plane[t])) /pi*180
                
                
                if( t*timestep % log_timestep == 0 or t == 1 ):
                    Logger.debug('pitch_LP in degrees: '+str(pitch_LP))
                    Logger.debug('pitch_pointing_command in degrees: '+str(pitch_pointing_command))
                    Logger.debug('pitch_angle_between_command_and_LP_altitudes [degrees]: '+str(pitch_angle_between_command_and_LP_altitudes))
                    Logger.debug('Absolute value of latitude of LP: '+str(abs_lat_LP/pi*180))
                    Logger.debug('angle_between_orbital_plane_and_moon [degrees]: '+str(angle_between_orbital_plane_and_moon[t]))
                    Logger.debug('Moon_vert_offset [degrees]: '+str(Moon_vert_offset[t]))
                    Logger.debug('Moon_hori_offset [degrees]: '+str(Moon_hori_offset[t]))
                    Logger.debug('normal_orbit: '+str(normal_orbit[t,0:3]))
                    Logger.debug('r_H_offset_normal: '+str(r_H_offset_normal[t,0:3]))
                    Logger.debug('r_FOV [km]: '+str(r_FOV[t,0:3]))
                    Logger.debug('')
                    
                
                #print('angle_between_orbital_plane_and_moon = ' + str(angle_between_orbital_plane_and_moon[t]))
                
                "Check that the Moon is entering V-offset degrees and within the H-offset angle"
                if( Moon_vert_offset[t] <= V_offset and Moon_vert_offset[t-1] > V_offset and abs(Moon_hori_offset[t]) < H_offset):
                    
                    Logger.debug('')
                    Logger.debug('!!!!!!!!Moon available!!!!!!!!!!')
                    Logger.debug('t (loop iteration number): '+str(t))
                    Logger.debug('Current time: '+str(current_time))
                    Logger.debug('Semimajor axis in km: '+str(MATS_p[t]))
                    Logger.debug('Orbital Period in s: '+str(MATS_P[t]))
                    Logger.debug('Vector to MATS [km]: '+str(r_MATS[t,0:3]))
                    Logger.debug('Latitude in radians: '+str(lat_MATS[t]))
                    Logger.debug('Longitude in radians: '+str(long_MATS[t]))
                    Logger.debug('Altitude in km: '+str(altitude_MATS[t]))
                    
                    if( yaw_correction == True):
                        Logger.debug('ascending_node: '+str(ascending_node))
                        Logger.debug('arg_of_lat [degrees]: '+str(arg_of_lat))
                        Logger.debug('yaw_offset_angle [degrees]: '+str(yaw_offset_angle))
                    
                    Logger.debug('pitch_LP in degrees: '+str(pitch_LP))
                    Logger.debug('pitch_pointing_command in degrees: '+str(pitch_pointing_command))
                    Logger.debug('pitch_angle_between_command_and_LP_altitudes [degrees]: '+str(pitch_angle_between_command_and_LP_altitudes))
                    Logger.debug('Absolute value of latitude of LP: '+str(abs_lat_LP/pi*180))
                    Logger.debug('angle_between_orbital_plane_and_moon [degrees]: '+str(angle_between_orbital_plane_and_moon[t]))
                    Logger.debug('Moon_vert_offset [degrees]: '+str(Moon_vert_offset[t]))
                    Logger.debug('Moon_hori_offset [degrees]: '+str(Moon_hori_offset[t]))
                    Logger.debug('normal_orbit: '+str(normal_orbit[t,0:3]))
                    Logger.debug('r_H_offset_normal: '+str(r_H_offset_normal[t,0:3]))
                    Logger.debug('r_FOV: '+str(r_FOV[t,0:3]))
                    
                    Logger.debug('')
                    
                    
                    dates.append({ 'Date': str(current_time), 'V-offset': Moon_vert_offset[t], 'H-offset': Moon_hori_offset[t], 
                                      'long_MATS': float(long_MATS[t]/pi*180), 'lat_MATS': float(lat_MATS[t]/pi*180), 'Dec': Dec, 'RA': Ra,
                                       'Dec FOV': Dec_optical_axis, 'RA FOV': Ra_optical_axis})
                    
                    Logger.debug('Jump ahead half an orbit in time')
                    "Skip ahead half an orbit"
                    current_time = ephem.Date(current_time+ephem.second*MATS_P[t]/2)
                    Logger.debug('Current time: '+str(current_time))
                    Logger.debug('')
                
            
            "To be able to make time skips when the moon is far outside the orbital plane of MATS"
            if( (angle_between_orbital_plane_and_moon[t] > H_offset and yaw_correction == False) or 
               angle_between_orbital_plane_and_moon[t] > H_offset+3.8 and yaw_correction == True):
                
                
                current_time = ephem.Date(current_time+ephem.second * H_offset/4 / 360 * Moon_orbital_period)
                #if( t*timestep % floor(log_timestep/400) == 0 ):
                Logger.debug('')
                Logger.debug('angle_between_orbital_plane_and_moon [degrees]: '+str(angle_between_orbital_plane_and_moon[t]))
                Logger.debug('Moon currently not visible -> jump ahead')
                Logger.debug('current_time after jump is is: '+str(current_time))
                
                t= t + 1
            else:
                t= t + 1
                current_time = ephem.Date(current_time+ephem.second*timestep)
                
            
            
        Logger.info('End of simulation for Mode124')
        Logger.debug('dates: '+str(dates))
        
        
        ########################## Optional plotter ###########################################
        '''
        from mpl_toolkits.mplot3d import axes3d
        from pylab import figure
        
        "Orbital points to plot"
        points_2_plot_start = 0#0*24*120
        points_2_plot = points_2_plot_start+1000
        
        "Plotting of orbit and FOV"
        fig = figure(1)
        ax = fig.add_subplot(111,projection='3d')
        ax.set_xlim3d(-1, 1)
        ax.set_ylim3d(-1, 1)
        ax.set_zlim3d(-1, 1)
        
        ax.scatter(r_MATS_unit_vector[points_2_plot_start:points_2_plot,0],r_MATS_unit_vector[points_2_plot_start:points_2_plot,1],r_MATS_unit_vector[points_2_plot_start:points_2_plot,2])
        ax.scatter(r_Moon_unit_vector[points_2_plot_start:points_2_plot,0],r_Moon_unit_vector[points_2_plot_start:points_2_plot,1],r_Moon_unit_vector[points_2_plot_start:points_2_plot,2])
        
        
        ########################### END of Optional plotter ########################################
        '''
        
        return dates



###############################################################################################
###############################################################################################



def date_select(Occupied_Timeline, dates):
    """Subfunction, Either schedules a user provided date or a simulated date.
    
    If automatic in *Mode124_settings* is set to False, the date is user provided. It will be postponed until available. \n
    If automatic in *Mode124_settings* is set to True. A list of dictionaries containing simulated dates is provided. 
    A date is selected for which the Moon is visible at an minimum amount of H-offset in the FOV.
    If the date is occupied a date will be selected with the 2nd least amount of H-offset and so on.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes together with their start and end time in a list. The list is empty if the Mode is unscheduled.
        dates ((:obj:`list` of :obj:`dict`)): A list containing dictionaries containing parameters for each time the Moon is spotted.
        dates (ephem.Date): A user provided date for the to schedule the Mode.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    Logger.info('Start of filtering function')
    
    Mode124_settings = OPT_Config_File.Mode124_settings()
    automatic = Mode124_settings['automatic']
    
    "Either schedules a user provided date or filters and schedules calculated dates"
    if( automatic == False ):
        
        endDate = ephem.Date(dates+ephem.second*Mode124_settings['mode_duration'])
        
        ############### Start of availability schedueler ##########################
        
        date, endDate, iterations = scheduler(Occupied_Timeline, dates, endDate)
        
        ############### End of availability schedueler ##########################
        
        if(iterations != 0):
            Logger.warning('User Specified date was occupied and got postponed!!')
            #input()
            
            
        Occupied_Timeline['Mode124'].append( (date, endDate) )
        comment = 'Mode124 scheduled using a user given date, the date got postponed '+str(iterations)+' times'
        
        
    elif( automatic == True ):
        
        if( len(dates) == 0):
            
            comment = 'Moon not visible (dates is empty)'
            Logger.warning('')
            Logger.warning(comment)
            #input('Enter anything to acknowledge and continue\n')
            return Occupied_Timeline, comment
        
        Moon_H_offset = [dates[x]['H-offset'] for x in range(len(dates))]
        Moon_V_offset = [dates[x]['V-offset'] for x in range(len(dates))]
        Moon_date = [dates[x]['Date'] for x in range(len(dates))]
        Moon_long = [dates[x]['long_MATS'] for x in range(len(dates))]
        Moon_lat = [dates[x]['lat_MATS'] for x in range(len(dates))]
        
        Moon_H_offset_abs = [abs(x) for x in Moon_H_offset]
        Moon_H_offset_sorted = [abs(x) for x in Moon_H_offset]
        Moon_H_offset_sorted.sort()
        
        
        restart = True
        iterations = 0
        ## Selects date based on min H-offset, if occupied, select date for next min H-offset
        while( restart == True):
            
            if( len(Moon_H_offset) == iterations):
                comment = 'No time available for Mode124'
                Logger.error('')
                Logger.error(comment)
                #input('Enter anything to ackknowledge and continue')
                return Occupied_Timeline, comment
            
            restart = False
            
            
            #Extract index of  minimum H-offset for first iteration, 
            #then next smallest if 2nd iterations needed and so on
            x = Moon_H_offset_abs.index(Moon_H_offset_sorted[iterations])
            
            date = Moon_date[x]
            
            date = ephem.Date(ephem.Date(date)-ephem.second*(Mode124_settings['freeze_start']))
            
            endDate = ephem.Date(date+ephem.second*Mode124_settings['mode_duration'])
            
            #Check that the scheduled date is not before the start of the timeline
            if( date < ephem.Date(OPT_Config_File.Timeline_settings()['start_date']) ):
                iterations = iterations + 1
                restart = True
                continue
            
            ## Extract Occupied dates and if they clash, restart loop and select new date
            for busy_dates in Occupied_Timeline.values():
                if( busy_dates == []):
                    continue
                else:
                    "Extract the start and end date of each instance of a scheduled mode"
                    for busy_date in busy_dates:
                        
                        if( busy_date[0] <= date <= busy_date[1] or 
                               busy_date[0] <= endDate <= busy_date[1] or
                           (date < busy_date[0] and endDate > busy_date[1])):
                            
                            iterations = iterations + 1
                            restart = True
                            break
            
        Occupied_Timeline['Mode124'].append( (date, endDate) )
        
        comment = ('V-offset: '+str(Moon_V_offset[x])+' H-offset: '+str(Moon_H_offset[x])+', Number of times date changed: '+str(iterations)+
                                          ', MATS (long,lat) in degrees = ('+str(Moon_long[x])+', '+str(Moon_lat[x])+'), Moon Dec (J2000) [degrees]: '+
                                          str(dates[x]['Dec'])+', Moon RA (J2000) [degrees]: '+str(dates[x]['RA'])+', Dec = '+str(dates[x]['Dec FOV'])+
                                          ', RA = '+str(dates[x]['RA FOV']))
        
    
    return Occupied_Timeline, comment
