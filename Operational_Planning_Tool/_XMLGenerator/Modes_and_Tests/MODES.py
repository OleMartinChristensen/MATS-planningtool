# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 11:35:08 2018

Generates and calculates parameters for each mode, and converts them to strings,
then calls for macros, which will generate commands in the XML-file.

Functions on the form "XML_generator_X", where the last X is any Mode:
    Arguments:
        root =  XML tree structure. Main container object for the ElementTree API. lxml.etree.Element class \n
        date = Starting date of the Mode. On the form of the ephem.Date class. \n
        duration = The duration of the mode [s] as an integer class. \n
        relativeTime = The starting time of the mode with regard to the start of the timeline [s] as an integer class \n
        params = Dictionary containing the parameters of the Mode given in the Science_Mode_Timeline.
    
    Returns:
        None

When creating new Mode functions it is crucial that the function name is
XML_generator_Mode_name, where Mode_name is the same as the string used in the Science Mode Timeline
        
@author: David
"""


import ephem, logging, sys, pylab
import pymap3d as pm3d

import OPT_Config_File
from Operational_Planning_Tool._Library import rot_arbit, params_checker, utc_to_onboardTime
from .Macros import Macros
from Operational_Planning_Tool import _MATS_coordinates

Logger = logging.getLogger(OPT_Config_File.Logger_name())


def XML_generator_Mode1(root, date, duration, relativeTime, params = {}):
    '''Simulates MATS and the LP without yaw movement to be able to schedule commands in the XML-file.
    
    High resolution UV binning for latitudes +-45 degrees latitude polewards.
    Disable exposure on UV channels for +-45 degrees latitude equatorwards.
    Stop/Start Nadir at dusk/dawn.
            
    '''
    
    #from OPT_Config_File import Mode1_settings, getTLE
    #from pylab import zeros, pi, arccos, sin ,cos, norm, cross, sqrt, arctan
    
    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos
    sin = pylab.sin
    cos = pylab.cos
    norm = pylab.norm
    cross = pylab.cross
    
    
    settings = OPT_Config_File.Mode_1_2_3_4_settings()
    
    timestep = settings['timestep']
    
    log_timestep = settings['log_timestep']
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
    
    "Pre-allocate space"
    lat_MATS = zeros((duration,1))
    
    altitude_MATS = zeros((duration,1))
    g_ra_MATS = zeros((duration,1))
    g_dec_MATS = zeros((duration,1))
    x_MATS = zeros((duration,1))
    y_MATS = zeros((duration,1))
    z_MATS = zeros((duration,1))
    r_MATS = zeros((duration,3))
    r_MATS_ECEF = zeros((duration,3))
    optical_axis = zeros((duration,3))
    optical_axis_ECEF = zeros((duration,3))
    LP_ECEF = zeros((duration,3))
    lat_LP = zeros((duration,1))
    long_LP = zeros((duration,1))
    alt_LP = zeros((duration,1))
    
    sun_angle = zeros((duration,1))
    lat_LP = zeros((duration,1))
    normal_orbital = zeros((duration,3))
    orbangle_between_LP_MATS_array = zeros((duration,1))
    
    #"Estimated latitude difference between MATS and the LP"
    #lat_diff_LP_MATS = 20/180*pi
    
    R_mean = 6371
    pointing_altitude = OPT_Config_File.Timeline_settings()['LP_pointing_altitude']
    lat = params['lat']
    
    
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+90))/pi*180 + 90
    
    Logger.debug('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    Logger.debug('')
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(int(duration/timestep)):
        
        current_time = ephem.Date(date+ephem.second*timestep*t)
        
        MATS.compute(current_time)
        
        
        (lat_MATS[t],altitude_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
        MATS.sublat,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
        
        z_MATS[t] = sin(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)
        x_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* cos(g_ra_MATS[t])
        y_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* sin(g_ra_MATS[t])
       
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        r_MATS_ECEF[t,0], r_MATS_ECEF[t,1], r_MATS_ECEF[t,2] = pm3d.eci2ecef(
                (r_MATS[t,0]*1000, r_MATS[t,1]*1000, r_MATS[t,2]*1000), ephem.Date(current_time).datetime())
        
        orbangle_between_LP_MATS_array[t]= arccos((R_mean+pointing_altitude/1000)/(R_mean+altitude_MATS[t]))/pi*180
        orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
        
        Sun.compute(current_time)
        sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        if( t % log_timestep == 0 and t != 0 and t != 1):
            Logger.debug('')
            Logger.debug('current_time: '+str(current_time))
            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
            
        
        if( t != 0):
            
            "Vector normal to the orbital plane of MATS"
            normal_orbital[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbital[t,0:3] = normal_orbital[t,0:3] / norm(normal_orbital[t,0:3])
            
            
            "Rotate 'vector to MATS', to represent pointing direction, (Parallax is negligable)"
            rot_mat = rot_arbit((orbangle_between_LP_MATS+90)/180*pi, normal_orbital[t,0:3])
            optical_axis[t,0:3] = rot_mat @ r_MATS[t]
            optical_axis[t,0:3] = optical_axis[t,0:3] / norm(optical_axis[t,0:3])
            
            optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2] = pm3d.eci2ecef(
                (optical_axis[t,0]*1000, optical_axis[t,1]*1000, optical_axis[t,2]*1000), ephem.Date(current_time).datetime())
            
            LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0]*1000, r_MATS_ECEF[t][1]*1000, r_MATS_ECEF[t][2]*1000, 
                                       optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
            
            lat_LP[t], long_LP[t], alt_LP[t]  = pm3d.ecef2geodetic(LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2], deg = True)
            
            """
            "Estimate latitude by calculating angle between xy-plane vector and z-vector (ECI)"
            r_LP__direction_xy = sqrt(optical_axis[t,0]**2+optical_axis[t,1]**2)
            lat_LP[t] = arctan(optical_axis[t,2]/r_LP__direction_xy)
            """
            '''
            if( abs(lat_MATS[t])-abs(lat_MATS[t-1]) > 0 ):
                lat_LP[t] = lat_MATS[t] - lat_diff_LP_MATS * sign(lat_MATS[t])
            elif( abs(lat_MATS[t])-abs(lat_MATS[t-1]) < 0 ):
                lat_LP[t] = lat_MATS[t] + lat_diff_LP_MATS * sign(lat_MATS[t])
            '''
            
            ############# Initial Mode setup ##########################################
            
            if( t == 1 ):
                
                Logger.debug('')
                '''
                Logger.debug(str(r_MATS[t,0:3]))
                Logger.debug(str(optical_axis[t,0:3]))
                Logger.debug(str(orbangle_between_LP_MATS_array[t]))
                '''
                Logger.debug('current_time: '+str(current_time))
                Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                Logger.debug('r_MATS_ECEF: '+str(r_MATS_ECEF[t,0]))
                
                
                "Check if night or day"
                if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                    
                    if( abs(lat_LP[t]) < lat):
                        current_state = "NLC_night_UV_off"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_night(root, str(t+relativeTime), str(pointing_altitude), UV_on = False, comment = comment)
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_night_UV_on"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_night(root,str(t+relativeTime),str(pointing_altitude), UV_on = True, comment = comment)
                        
                elif( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    if( abs(lat_LP[t]) < lat):
                        current_state = "NLC_day_UV_off"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), UV_on = False, comment = comment)
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_day_UV_on"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), UV_on = True, comment = comment)
                
                Logger.debug(current_state)
            
            
            ############# End of Initial Mode setup ###################################
            
            
            
           
            if( t != 1):
                ####################### SCI-mode Operation planner ################
                
                
                
                
                
                #Check if night or day
                if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                    
                    #Check latitude
                    if( abs(lat_LP[t]) < lat and current_state != "NLC_night_UV_off"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_night_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            #IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.NLC_nadir_on_off(root, str(t+relativeTime), nadir_on = True, comment = comment)
                            
                            
                        if(abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat):
                            current_state = "NLC_night_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_night(root,str(t+relativeTime),str(pointing_altitude), UV_on = False, comment = comment)
                            
                            
                            
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_night_UV_on"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_night_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            #NLC_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.NLC_nadir_on_off(root, str(t+relativeTime), nadir_on = 'True', comment = comment)
                            
                            
                        if(abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat):
                            current_state = "NLC_night_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_night(root,str(t+relativeTime),str(pointing_altitude), UV_on = True, comment = comment)
                            
                            
                            
                #Check if night or day#            
                if( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    #Check latitude
                    if( abs(lat_LP[t]) < lat and current_state != "NLC_day_UV_off"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle):
                            current_state = "NLC_day_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            #IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.NLC_nadir_on_off(root, str(t+relativeTime), nadir_on = False, comment = comment)
                            
                            
                        if(abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat):
                            current_state = "NLC_day_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), UV_on = False, comment = comment)
                            
                            
                            
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_day_UV_on"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_day_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            #NLC_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.NLC_nadir_on_off(root, str(t+relativeTime), nadir_on = False, comment = comment)
                            
                            
                        if(abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat):
                            current_state = "NLC_day_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), UV_on = True, comment = comment)
                            
                            
                
            
                
                
                ############### End of SCI-mode operation planner #################
                
    
    
    
    
    


#######################################################################################




def XML_generator_Mode2(root, date, duration, relativeTime, params = {}):
    """Simulates MATS and the LP without yaw movement to be able to schedule commands in the XML-file.
    
    High-resolution IR binning. Stop/Start Nadir at dusk/dawn.
    """
    
    settings = OPT_Config_File.Mode_1_2_3_4_settings()
    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos
    
    timestep = settings['timestep']
    
    log_timestep = settings['log_timestep']
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
    
    "Pre-allocate space"
    sun_angle = zeros((duration,1))
    
    
    R_mean = 6371
    pointing_altitude = OPT_Config_File.Timeline_settings()['LP_pointing_altitude']
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+90))/pi*180 + 90
    Logger.debug('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(int(duration/timestep)):
        
        
        current_time = ephem.Date(date+ephem.second*timestep*t)
        
        MATS.compute(current_time)
        
        Sun.compute(current_time)
        sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        if( t % log_timestep == 0):
            Logger.debug('')
            Logger.debug('current_time: '+str(current_time))
            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
        
        ############# Initial Mode setup ##########################################
        
        if( t == 0 ):
            
            "Check if night or day"
            if( sun_angle[t] > MATS_nadir_eclipse_angle):
                current_state = "IR_night"
                comment = current_state+': '+str(params)
                Macros.IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                
                
            elif( sun_angle[t] < MATS_nadir_eclipse_angle):
                current_state = "IR_day"
                comment = current_state+': '+str(params)
                Macros.IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                
        
        ############# End of Initial Mode setup ###################################
        
        
        
        if(t != 0):
        ####################### SCI-mode Operation planner ################
            
            
           
            #Check if night or day
            if( sun_angle[t] > MATS_nadir_eclipse_angle and current_state != "IR_night"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle) ):
                    current_state = "IR_night"
                    comment = current_state+': '+str(params)
                    
                    Logger.debug('')
                    Logger.debug('current_time: '+str(current_time))
                    Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                    Macros.IR_nadir_on_off(root, str(t+relativeTime), nadir_on = True, comment = comment)
                    #Macros.IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    
                    
                    
            #Check if night or day            
            if( sun_angle[t] < MATS_nadir_eclipse_angle and current_state != "IR_day"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle) ):
                    current_state = "IR_day"
                    comment = current_state+': '+str(params)
                    
                    Logger.debug('')
                    Logger.debug('current_time: '+str(current_time))
                    Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                    Macros.IR_nadir_on_off(root, str(t+relativeTime), nadir_on = False, comment = comment)
                    #Macros.IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    
                    
                    
                 
        ############### End of SCI-mode operation planner #################
    
    




############################################################################################
def XML_generator_Mode3(root, date, duration, relativeTime, params = {}):
    """Simulates MATS and the LP with yaw movement to be able to schedule commands in the XML-file.
    
    High resolution UV binning for latitudes +-45 degrees latitude polewards.
    Disable exposure on UV channels for +-45 degrees latitude equatorwards.
    Stop/Start Nadir at dusk/dawn.
    """
    
    #from OPT_Config_File import Mode1_settings, getTLE
    #from pylab import zeros, pi, arccos, sin ,cos, norm, cross, sqrt, arctan
    
    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos
    sin = pylab.sin
    cos = pylab.cos
    norm = pylab.norm
    cross = pylab.cross
    sqrt = pylab.sqrt
    arctan = pylab.arctan
    dot = pylab.dot
    array = pylab.array
    
    settings = OPT_Config_File.Mode_1_2_3_4_settings()
    
    timestep = settings['timestep']
    
    log_timestep = settings['log_timestep']
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
    
    "Pre-allocate space"
    lat_MATS = zeros((duration,1))
    
    altitude_MATS = zeros((duration,1))
    g_ra_MATS = zeros((duration,1))
    g_dec_MATS = zeros((duration,1))
    x_MATS = zeros((duration,1))
    y_MATS = zeros((duration,1))
    z_MATS = zeros((duration,1))
    r_MATS = zeros((duration,3))
    r_MATS_ECEF = zeros((duration,3))
    r_MATS_unit_vector = zeros((duration,3))
    optical_axis = zeros((duration,3))
    optical_axis_ECEF = zeros((duration,3))
    LP_ECEF = zeros((duration,3))
    lat_LP = zeros((duration,1))
    long_LP = zeros((duration,1))
    alt_LP = zeros((duration,1))
    
    sun_angle = zeros((duration,1))
    lat_LP = zeros((duration,1))
    normal_orbital = zeros((duration,3))
    orbangle_between_LP_MATS_array = zeros((duration,1))
    
    #"Estimated latitude difference between MATS and the LP"
    #lat_diff_LP_MATS = 20/180*pi
    
    R_mean = 6371
    pointing_altitude = OPT_Config_File.Timeline_settings()['LP_pointing_altitude']
    lat = params['lat']
    celestial_eq_normal = array([[0,0,1]])
    
    
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+90))/pi*180 + 90
    
    Logger.debug('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    Logger.debug('')
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(int(duration/timestep)):
        
        current_time = ephem.Date(date+ephem.second*timestep*t)
        
        MATS.compute(current_time)
        
        
        (lat_MATS[t],altitude_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
        MATS.sublat,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
        
        z_MATS[t] = sin(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)
        x_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* cos(g_ra_MATS[t])
        y_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* sin(g_ra_MATS[t])
       
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        r_MATS_ECEF[t,0], r_MATS_ECEF[t,1], r_MATS_ECEF[t,2] = pm3d.eci2ecef(
                (r_MATS[t,0]*1000, r_MATS[t,1]*1000, r_MATS[t,2]*1000), ephem.Date(current_time).datetime())
        
        r_MATS_unit_vector[t,0:3] = r_MATS[t,0:3] / norm(r_MATS[t,0:3])
        
        orbangle_between_LP_MATS_array[t]= arccos((R_mean+pointing_altitude/1000)/(R_mean+altitude_MATS[t]))/pi*180
        orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
        
        Sun.compute(current_time)
        sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        if( t % log_timestep == 0 and t != 0 and t != 1):
            Logger.debug('')
            Logger.debug('current_time: '+str(current_time))
            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
            
        
        if( t != 0):
            
            "Vector normal to the orbital plane of MATS"
            normal_orbital[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbital[t,0:3] = normal_orbital[t,0:3] / norm(normal_orbital[t,0:3])
            
            
            "Rotate 'vector to MATS', to represent pointing direction, (Parallax is negligable)"
            rot_mat = rot_arbit((orbangle_between_LP_MATS+90)/180*pi, normal_orbital[t,0:3])
            optical_axis[t,0:3] = rot_mat @ r_MATS[t]
            optical_axis[t,0:3] = optical_axis[t,0:3] / norm(optical_axis[t,0:3])
            
            "Calculate intersection between the orbital plane and the equator"
            ascending_node = cross(normal_orbital[t,0:3], celestial_eq_normal)
            
            arg_of_lat = arccos( dot(ascending_node, r_MATS[t,0:3]) / norm(r_MATS[t,0:3]) / norm(ascending_node) ) /pi*180
            
            "To determine if MATS is moving towards the ascending node"
            if( dot(cross( ascending_node, r_MATS[t,0:3]), normal_orbital[t,0:3]) >= 0 ):
                arg_of_lat = 360 - arg_of_lat
                
            yaw_offset_angle = OPT_Config_File.Timeline_settings()['yaw_amplitude'] * cos( arg_of_lat/180*pi - orbangle_between_LP_MATS/180*pi + OPT_Config_File.Timeline_settings()['yaw_phase']/180*pi )
            yaw_offset_angle = yaw_offset_angle[0]
            
            if( t % log_timestep == 0 or t == 1 ):
                Logger.debug('ascending_node: '+str(ascending_node))
                Logger.debug('arg_of_lat [degrees]: '+str(arg_of_lat))
                Logger.debug('yaw_offset_angle [degrees]: '+str(yaw_offset_angle))
            
            "Rotate yaw of pointing direction, meaning to rotate around the vector to MATS"
            rot_mat = rot_arbit( (-yaw_offset_angle)/180*pi, r_MATS_unit_vector[t,0:3])
            optical_axis[t,0:3] = rot_mat @ optical_axis[t,0:3]
            optical_axis[t,0:3] = optical_axis[t,0:3] / norm(optical_axis[t,0:3])
            
            optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2] = pm3d.eci2ecef(
                (optical_axis[t,0]*1000, optical_axis[t,1]*1000, optical_axis[t,2]*1000), ephem.Date(current_time).datetime())
            
            LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0]*1000, r_MATS_ECEF[t][1]*1000, r_MATS_ECEF[t][2]*1000, 
                                       optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
            
            lat_LP[t], long_LP[t], alt_LP[t]  = pm3d.ecef2geodetic(LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2], deg = True)
            
            """
            "Estimate latitude by calculating angle between xy-plane vector and z-vector (ECI)"
            r_LP__direction_xy = sqrt(optical_axis[t,0]**2+optical_axis[t,1]**2)
            lat_LP[t] = arctan(optical_axis[t,2]/r_LP__direction_xy)
            """
            '''
            if( abs(lat_MATS[t])-abs(lat_MATS[t-1]) > 0 ):
                lat_LP[t] = lat_MATS[t] - lat_diff_LP_MATS * sign(lat_MATS[t])
            elif( abs(lat_MATS[t])-abs(lat_MATS[t-1]) < 0 ):
                lat_LP[t] = lat_MATS[t] + lat_diff_LP_MATS * sign(lat_MATS[t])
            '''
            
            ############# Initial Mode setup ##########################################
            
            if( t == 1 ):
                
                Logger.debug('')
                '''
                Logger.debug(str(r_MATS[t,0:3]))
                Logger.debug(str(optical_axis[t,0:3]))
                Logger.debug(str(orbangle_between_LP_MATS_array[t]))
                '''
                Logger.debug('current_time: '+str(current_time))
                Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                Logger.debug('r_MATS_ECEF: '+str(r_MATS_ECEF[t,0]))
                
                
                "Check if night or day"
                if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                    
                    if( abs(lat_LP[t]) < lat):
                        current_state = "NLC_night_UV_off"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_night(root,str(t+relativeTime),str(pointing_altitude), UV_on = False, comment = comment)
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_night_UV_on"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_night(root,str(t+relativeTime),str(pointing_altitude), UV_on = True, comment = comment)
                        
                elif( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    if( abs(lat_LP[t]) < lat):
                        current_state = "NLC_day_UV_off"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), UV_on = False, comment = comment)
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_day_UV_on"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), UV_on = True, comment = comment)
                
                Logger.debug(current_state)
            
            
            ############# End of Initial Mode setup ###################################
            
            
            
           
            if( t != 1):
                ####################### SCI-mode Operation planner ################
                
                
                
                
                
                #Check if night or day
                if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                    
                    #Check latitude
                    if( abs(lat_LP[t]) < lat and current_state != "NLC_night_UV_off"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_night_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            #IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.NLC_nadir_on_off(root, str(t+relativeTime), nadir_on = True, comment = comment)
                            
                            
                        if(abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat):
                            current_state = "NLC_night_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_night(root,str(t+relativeTime),str(pointing_altitude), UV_on = False, comment = comment)
                            
                            
                            
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_night_UV_on"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_night_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            #NLC_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.NLC_nadir_on_off(root, str(t+relativeTime), nadir_on = True, comment = comment)
                            
                            
                        if(abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat):
                            current_state = "NLC_night_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_night(root,str(t+relativeTime),str(pointing_altitude), UV_on = True, comment = comment)
                            
                            
                            
                #Check if night or day#            
                if( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    #Check latitude
                    if( abs(lat_LP[t]) < lat and current_state != "NLC_day_UV_off"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle):
                            current_state = "NLC_day_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            #IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.NLC_nadir_on_off(root, str(t+relativeTime), nadir_on = False, comment = comment)
                            
                            
                        if(abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat):
                            current_state = "NLC_day_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), UV_on = False, comment = comment)
                            
                            
                            
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_day_UV_on"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_day_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            #NLC_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.NLC_nadir_on_off(root, str(t+relativeTime), nadir_on = False, comment = comment)
                            
                            
                        if(abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat):
                            current_state = "NLC_day_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.debug('')
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), UV_on = True, comment = comment)
                            
                            
                
            
                
                
                ############### End of SCI-mode operation planner #################
                
    
    
    
    
    


#######################################################################################

def XML_generator_Mode4(root, date, duration, relativeTime, params = {}):
    """Simulates MATS and the LP with yaw movement to be able to schedule commands in the XML-file.
    
    High-resolution IR binning. Stop/Start Nadir at dusk/dawn.
    
    """
    
    settings = OPT_Config_File.Mode_1_2_3_4_settings()
    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos
    
    timestep = settings['timestep']
    
    log_timestep = settings['log_timestep']
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
    
    "Pre-allocate space"
    sun_angle = zeros((duration,1))
    
    
    R_mean = 6371
    pointing_altitude = OPT_Config_File.Timeline_settings()['LP_pointing_altitude']
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+90))/pi*180 + 90
    Logger.debug('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(int(duration/timestep)):
        
        
        current_time = ephem.Date(date+ephem.second*timestep*t)
        
        MATS.compute(current_time)
        
        Sun.compute(current_time)
        sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        if( t % log_timestep == 0):
            Logger.debug('')
            Logger.debug('current_time: '+str(current_time))
            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
        
        ############# Initial Mode setup ##########################################
        
        if( t == 0 ):
            
            "Check if night or day"
            if( sun_angle[t] > MATS_nadir_eclipse_angle):
                current_state = "IR_night"
                comment = current_state+': '+str(params)
                Macros.IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                
                
            elif( sun_angle[t] < MATS_nadir_eclipse_angle):
                current_state = "IR_day"
                comment = current_state+': '+str(params)
                Macros.IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                
        
        ############# End of Initial Mode setup ###################################
        
        
        
        if(t != 0):
        ####################### SCI-mode Operation planner ################
            
            
           
            #Check if night or day
            if( sun_angle[t] > MATS_nadir_eclipse_angle and current_state != "IR_night"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle) ):
                    current_state = "IR_night"
                    comment = current_state+': '+str(params)
                    
                    Logger.debug('')
                    Logger.debug('current_time: '+str(current_time))
                    Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                    Macros.IR_nadir_on_off(root, str(t+relativeTime), nadir_on = True, comment = comment)
                    #Macros.IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    
                    
                    
            #Check if night or day            
            if( sun_angle[t] < MATS_nadir_eclipse_angle and current_state != "IR_day"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle) ):
                    current_state = "IR_day"
                    comment = current_state+': '+str(params)
                    
                    Logger.debug('')
                    Logger.debug('current_time: '+str(current_time))
                    Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                    Macros.IR_nadir_on_off(root, str(t+relativeTime), nadir_on = False, comment = comment)
                    #Macros.IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    
                    
                    
                 
        ############### End of SCI-mode operation planner #################
    
    

################################################################################################



def XML_generator_Mode100(root, date, duration, relativeTime, params = {}):
    """ Mode100
    
    Successively point at altitudes from X-Y in Z intervals with steadily increasing Exposure Times.
    Where X is *pointing_altitude_from*, Y is *pointing_altitude_to, and Z is *pointing_altitude_interval*.
    All defined in OPT_Config_File.Mode100_settings. Standard binning, stop Nadir.
    
    """
    
    
    
    settings = OPT_Config_File.Mode100_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    
    pointing_altitude_from = params['pointing_altitude_from']
    pointing_altitude_to = params['pointing_altitude_to']
    pointing_altitude_interval = params['pointing_altitude_interval']
    ExpTimeUV = params['Exp_Time_and_Interval_UV'][0]
    ExpIntUV =  params['Exp_Time_and_Interval_UV'][1]
    ExpTimeIR = params['Exp_Time_and_Interval_IR'][0]
    ExpIntIR =  params['Exp_Time_and_Interval_IR'][1]
    ExpTime_interval = params['ExpTime_interval']
    
    number_of_altitudes = int( (pointing_altitude_to - pointing_altitude_from) / pointing_altitude_interval +1 )
    
    pointing_altitudes = [pointing_altitude_from + x*pointing_altitude_interval for x in range(number_of_altitudes)]
    
    duration_flag = 0
    initial_relativeTime = relativeTime
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    "Schedule macros for steadily increasing pointing altitudes and exposure times"
    for pointing_altitude in pointing_altitudes:
        mode_relativeTime = relativeTime - initial_relativeTime
        
        if(mode_relativeTime > duration and duration_flag == 0):
            Logger.warning('Warning!! The scheduled time for '+Mode_name+' has ran out.')
            #input('Enter anything to ackknowledge and continue:\n')
            duration_flag = 1
        
        relativeTime = Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = str(pointing_altitude),  ExpTimeUV = str(ExpTimeUV), 
                                              ExpIntUV = str(ExpIntUV), ExpTimeIR = str(ExpTimeIR), ExpIntIR = str(ExpIntIR), comment = comment)
        relativeTime = round(float(relativeTime) + params['pointing_duration'], 1)
        
        ExpTimeUV = ExpTimeUV + ExpTime_interval
        ExpIntUV = ExpIntUV + ExpTime_interval
        ExpTimeIR = ExpTimeIR + ExpTime_interval
        ExpIntIR = ExpIntIR + ExpTime_interval



##############################################################################################

##############################################################################################



def XML_generator_Mode110(root, date, duration, relativeTime, params = {}):
    """Mode110
    
    Scan atmosphere from X to Y altitudes with a rate of Z.
    Where X, Y, Z is defined in OPT_Config_File.Mode110_settings.
    Standard binning, Stop Nadir.
    
    """
    
    settings = OPT_Config_File.Mode110_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude_from = params['pointing_altitude_from']
    pointing_altitude_to = params['pointing_altitude_to']
    sweep_rate = params['sweep_rate']
    sweep_start = params['sweep_start']
    
    relativeTime_sweep_start = sweep_start + relativeTime
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude_from = str(pointing_altitude_from), 
                  pointing_altitude_to = str(pointing_altitude_to), sweep_rate = str(sweep_rate), 
                  relativeTime_sweep_start = str(relativeTime_sweep_start), comment = comment)


#######################################################################################################



def XML_generator_Mode120(root, date, duration, relativeTime, 
                       params = {}):
    """Mode120
    
    Stare at a point in inertial reference frame and take a Snapshot using Full CCD readout. Stop Nadir
    Used for star calibration.
    """
    
    settings = OPT_Config_File.Mode120_settings()
    
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    #freezeTime = str(int((freeze_start_utc+leapSeconds-GPS_epoch)*24*3600))
    
    Snapshot_relativeTime = relativeTime + params['freeze_start'] + params['SnapshotTime']
    
    freezeTime = str(utc_to_onboardTime(freeze_start_utc))
    
    FreezeDuration = params['freeze_duration']
    
    pointing_altitude = params['pointing_altitude']
    
    
    Logger.debug('freeze_start_utc: '+str(freeze_start_utc))
    Logger.debug('freezeTime [GPS]: '+freezeTime)
    Logger.debug('FreezeDuration: '+str(FreezeDuration))
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Mode_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                     FreezeDuration = str(FreezeDuration), pointing_altitude = str(pointing_altitude), 
                     Snapshot_relativeTime = str(Snapshot_relativeTime), comment = comment)




################################################################################################




############################################################################################




def XML_generator_Mode121(root, date, duration, relativeTime, 
                       params = {}):
    """Mode121
    
    Stare at a point in inertial reference frame in the orbital plane using standard binning.
    """
    
    settings = OPT_Config_File.Mode121_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    "Get Mode name as string"
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    Snapshot_relativeTime = relativeTime + params['freeze_start'] + params['SnapshotTime']
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    freezeTime = str(utc_to_onboardTime(freeze_start_utc))
    
    FreezeDuration = params['freeze_duration']
    
    pointing_altitude = params['pointing_altitude']
    
    Logger.debug('freeze_start_utc: '+str(freeze_start_utc))
    Logger.debug('freezeTime [GPS]: '+freezeTime)
    Logger.debug('FreezeDuration: '+str(FreezeDuration))
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    for (ExpTimeUV,ExpIntUV),(ExpTimeIR,ExpIntIR)  in zip( params['Exp_Times_and_Intervals_UV'], params['Exp_Times_and_Intervals_IR'] ):
        
        Mode_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                     FreezeDuration = str(FreezeDuration), pointing_altitude = str(pointing_altitude), 
                     ExpIntUV = str(ExpIntUV), ExpTimeUV = str(ExpTimeUV), ExpIntIR = str(ExpIntIR), ExpTimeIR = str(ExpTimeIR), 
                     Snapshot_relativeTime = str(Snapshot_relativeTime), comment = comment)




################################################################################################

############################################################################################




def XML_generator_Mode122(root, date, duration, relativeTime, 
                       params = {}):
    """Mode122
    
    Stare at a point in inertial reference frame in the orbital plane using one single pixel,
    for several different exposure times, set in *OPT_Config_File.Mode122_settings*.
    
    """
    
    settings = OPT_Config_File.Mode122_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    Snapshot_relativeTime = relativeTime + params['freeze_start'] + params['SnapshotTime']
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    freezeTime = str(utc_to_onboardTime(freeze_start_utc))
    
    FreezeDuration = params['freeze_duration']
    
    pointing_altitude = params['pointing_altitude']
    
    Logger.debug('freeze_start_utc: '+str(freeze_start_utc))
    Logger.debug('freezeTime [GPS]: '+freezeTime)
    Logger.debug('FreezeDuration: '+str(FreezeDuration))
    
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    for (ExpTimeUV,ExpIntUV),(ExpTimeIR,ExpIntIR)  in zip( params['Exp_Times_and_Intervals_UV'], params['Exp_Times_and_Intervals_IR'] ):
        
        relativeTime = Mode_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                                  FreezeDuration = str(FreezeDuration), pointing_altitude = str(pointing_altitude), 
                                  ExpIntUV = str(ExpIntUV), ExpTimeUV = str(ExpTimeUV), ExpIntIR = str(ExpIntIR), ExpTimeIR = str(ExpTimeIR), 
                                  Snapshot_relativeTime = str(Snapshot_relativeTime), comment = comment)
    
    """
    for ExpTime, ExpInt in params['Exp_Times_n_Intervals']:
        
        relativeTime = Mode_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                     FreezeDuration = str(FreezeDuration), pointing_altitude = str(pointing_altitude), 
                     ExpInt = str(ExpInt), ExpTime = str(ExpTime), comment = comment)
        relativeTime = round(float(relativeTime) + params['session_duration'], 1)
    """



################################################################################################


def XML_generator_Mode130(root, date, duration, relativeTime, 
                       params = {}):
    """Mode130
    
    Look at fixed limb altitude and take Snapshots with all CCD except nadir with Full CCD readout.
    """
    
    settings = OPT_Config_File.Mode130_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = str(pointing_altitude), comment = comment)




##############################################################################################


################################################################################################



def XML_generator_Mode131(root, date, duration, relativeTime, 
                       params = {}):
    """Mode131
    
    Look at fixed limb altitude. Standard Binning.
    """
    
    settings = OPT_Config_File.Mode131_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    for (ExpTimeUV,ExpIntUV),(ExpTimeIR,ExpIntIR)  in zip( params['Exp_Times_and_Intervals_UV'], params['Exp_Times_and_Intervals_IR'] ):
         
        relativeTime = Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = str(pointing_altitude), 
                   ExpIntUV = str(ExpIntUV), ExpTimeUV = str(ExpTimeUV), ExpIntIR = str(ExpIntIR), ExpTimeIR = str(ExpTimeIR), comment = comment)
        
        relativeTime = round(float(relativeTime) + params['session_duration'], 1)
        
    
    #Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = str(pointing_altitude), comment = comment)




##############################################################################################

################################################################################################



def XML_generator_Mode132(root, date, duration, relativeTime, 
                       params = {}):
    """Mode132
    
    Look at fixed limb altitude for several different exposure times, set in *OPT_Config_File.Mode132_settings*. 
    Bin all pixels to one single pixel.
    
    """
    
    settings = OPT_Config_File.Mode132_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
        
    pointing_altitude = params['pointing_altitude']
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    for (ExpTimeUV,ExpIntUV),(ExpTimeIR,ExpIntIR)  in zip( params['Exp_Times_and_Intervals_UV'], params['Exp_Times_and_Intervals_IR'] ):
        
        relativeTime = Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = str(pointing_altitude), 
                   ExpIntUV = str(ExpIntUV), ExpTimeUV = str(ExpTimeUV), ExpIntIR = str(ExpIntIR), ExpTimeIR = str(ExpTimeIR), comment = comment)
        
        relativeTime = round(float(relativeTime) + params['session_duration'], 1)
        



##############################################################################################


def XML_generator_Mode200(root, date, duration, relativeTime, 
                       params = {}):
    """Mode200
    
    Stare at a point in inertial reference frame using standard binning. Stop Nadir
    Used for moon calibration.
    """
    
    settings = OPT_Config_File.Mode200_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    freezeTime = str(utc_to_onboardTime(freeze_start_utc))
    
    FreezeDuration = params['freeze_duration']
    
    pointing_altitude = str(params['pointing_altitude'])
    
    
    Logger.debug('freeze_start_utc: '+str(freeze_start_utc))
    Logger.debug('freezeTime [GPS]: '+freezeTime)
    Logger.debug('FreezeDuration: '+str(FreezeDuration))
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Mode_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                     FreezeDuration = str(FreezeDuration), pointing_altitude = pointing_altitude, comment = comment)



##############################################################################################




##############################################################################################


'''
def XML_generator_=X=(root, date, duration, relativeTime, params = {}):
    "This is a template for a new mode or test. Exchange '=X=' for the name of the new mode/test"
    
    
    settings = OPT_Config_File.=X=_settings()
    
    
    Logger.debug('params from Science Mode List: '+str(params))
    #params = params_checker(params,=X=_settings)
    #Logger.debug('params after params_checker function: '+str(params))
    Logger.info('params used: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    Mode_name_macro(root = root, relativeTime = str(relativeTime), comment = comment)
'''

#######################################################################################################





