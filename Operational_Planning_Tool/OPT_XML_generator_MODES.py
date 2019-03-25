# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 11:35:08 2018

Generates and calculates parameters for each mode, and converts them to strings,
then calls for macros, which will generate commands in the XML-file.

Functions on the form "XML_generator_X", where the last X is any Mode:
    Input:
        root =  XML tree structure. Main container object for the ElementTree API. lxml.etree.Element class
        date = Starting date of the Mode. On the form of the ephem.Date class.
        duration = The duration of the mode [s] as an integer class.
        relativeTime = The starting time of the mode with regard to the start of the timeline [s] as an integer class
        params = Dictionary containing the parameters of the mode.
    Output:
        None

When creating new Mode functions it is crucial that the function name is
XML_generator_"Mode_name", where Mode_name is the same as the string used in the Science Mode Timeline

 
@author: David
"""


import ephem, logging
from OPT_Config_File import Logger_name, Timeline_settings
from Operational_Planning_Tool.OPT_library import rot_arbit
Logger = logging.getLogger(Logger_name())


def XML_generator_Mode1(root, date, duration, relativeTime, params = {}):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    from OPT_Config_File import Mode1_settings, getTLE
    from Operational_Planning_Tool.OPT_XML_generator_macros import IR_night, IR_day, NLC_day, NLC_night
    from pylab import zeros, pi, arccos, sin ,cos, norm, cross, sqrt, arctan
    
    log_timestep = Mode1_settings()['log_timestep']
    Logger.info('log_timestep [s]: '+str(log_timestep))
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,Mode1_settings)
    Logger.info('params after params_checker function: '+str(params))
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', getTLE()[0], getTLE()[1])
    
    "Pre-allocate space"
    lat_MATS = zeros((duration,1))
    altitude_MATS = zeros((duration,1))
    g_ra_MATS = zeros((duration,1))
    g_dec_MATS = zeros((duration,1))
    x_MATS = zeros((duration,1))
    y_MATS = zeros((duration,1))
    z_MATS = zeros((duration,1))
    r_MATS = zeros((duration,3))
    r_LP_direction = zeros((duration,3))
    sun_angle = zeros((duration,1))
    lat_LP = zeros((duration,1))
    normal_orbital = zeros((duration,3))
    orbangle_between_LP_MATS_array = zeros((duration,1))
    
    #"Estimated latitude difference between MATS and the LP"
    #lat_diff_LP_MATS = 20/180*pi
    
    R_mean = 6371
    pointing_altitude = params['pointing_altitude']
    lat = params['lat']/180*pi
    
    
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+90))/pi*180 + 90
    
    Logger.info('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(duration):
        
        current_time = ephem.Date(date+ephem.second*t)
        
        MATS.compute(current_time)
        
        
        (lat_MATS[t],altitude_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
        MATS.sublat,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
        
        z_MATS[t] = sin(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)
        x_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* cos(g_ra_MATS[t])
        y_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* sin(g_ra_MATS[t])
       
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        
        orbangle_between_LP_MATS_array[t]= arccos((R_mean+pointing_altitude/1000)/(R_mean+altitude_MATS[t]))/pi*180
        orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
        
        Sun.compute(current_time)
        sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        if( t % log_timestep == 0 and t != 0):
            Logger.info('')
            Logger.info('current_time: '+str(current_time))
            Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
            
            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
            
        
        
        ############# Initial Mode setup ##########################################
        '''
        if( t == 0 ):
            
            "Check if night or day"
            if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                
                if( abs(lat_MATS[t]) < lat):
                    current_state = "IR_night"
                    comment = current_state+': '+str(params)
                    IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                elif( abs(lat_MATS[t]) > lat):
                    current_state = "NLC_night"
                    comment = current_state+': '+str(params)
                    NLC_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    
            elif( sun_angle[t] < MATS_nadir_eclipse_angle ):
                
                if( abs(lat_MATS[t]) < lat):
                    current_state = "IR_day"
                    comment = current_state+': '+str(params)
                    IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                elif( abs(lat_MATS[t]) > lat):
                    current_state = "NLC_day"
                    comment = current_state+': '+str(params)
                    NLC_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                
        
        '''
        ############# End of Initial Mode setup ###################################
        
        if( t != 0):
            
            "Vector normal to the orbital plane of MATS"
            normal_orbital[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbital[t,0:3] = normal_orbital[t,0:3] / norm(normal_orbital[t,0:3])
            
            
            "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
            rot_mat = rot_arbit(orbangle_between_LP_MATS/180*pi, normal_orbital[t,0:3])
            r_LP_direction[t,0:3] = rot_mat @ r_MATS[t]
            
            "Estimate latitude by calculating angle between xy-plane vector and z-vector"
            r_LP__direction_xy = sqrt(r_LP_direction[t,0]**2+r_LP_direction[t,1]**2)
            lat_LP[t] = arctan(r_LP_direction[t,2]/r_LP__direction_xy)
            
            '''
            if( abs(lat_MATS[t])-abs(lat_MATS[t-1]) > 0 ):
                lat_LP[t] = lat_MATS[t] - lat_diff_LP_MATS * sign(lat_MATS[t])
            elif( abs(lat_MATS[t])-abs(lat_MATS[t-1]) < 0 ):
                lat_LP[t] = lat_MATS[t] + lat_diff_LP_MATS * sign(lat_MATS[t])
            '''
            
            ############# Initial Mode setup ##########################################
            
            if( t == 1 ):
                
                "Check if night or day"
                if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                    
                    if( abs(lat_LP[t]) < lat):
                        current_state = "IR_night"
                        comment = current_state+': '+str(params)
                        IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_night"
                        comment = current_state+': '+str(params)
                        NLC_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                        
                elif( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    if( abs(lat_LP[t]) < lat):
                        current_state = "IR_day"
                        comment = current_state+': '+str(params)
                        IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_day"
                        comment = current_state+': '+str(params)
                        NLC_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                
                Logger.info('')
                '''
                Logger.info(str(r_MATS[t,0:3]))
                Logger.info(str(r_LP_direction[t,0:3]))
                Logger.info(str(orbangle_between_LP_MATS_array[t]))
                '''
                Logger.info('current_time: '+str(current_time))
                Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                Logger.info(current_state)
            
            
            ############# End of Initial Mode setup ###################################
            
            
            
           
            if( t != 1):
                ####################### SCI-mode Operation planner ################
                
                
                    
                        
               
                #Check if night or day
                if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                    
                    #Check latitude
                    if( abs(lat_LP[t]) < lat and current_state != "IR_night"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "IR_night"
                            comment = current_state+': '+str(params)
                            IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                        elif(abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat):
                            current_state = "IR_night"
                            comment = current_state+': '+str(params)
                            IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_night"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_night"
                            comment = current_state+': '+str(params)
                            NLC_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                        elif(abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat):
                            current_state = "NLC_night"
                            comment = current_state+': '+str(params)
                            NLC_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            
                #Check if night or day#            
                if( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    #Check latitude
                    if( abs(lat_LP[t]) < lat and current_state != "IR_day"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle):
                            current_state = "IR_day"
                            comment = current_state+': '+str(params)
                            IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                        elif(abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat):
                            current_state = "IR_day"
                            comment = current_state+': '+str(params)
                            IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_day"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_day"
                            comment = current_state+': '+str(params)
                            NLC_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                        elif(abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat):
                            current_state = "NLC_day"
                            comment = current_state+': '+str(params)
                            NLC_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            
                
            if( t % log_timestep == 0):
                Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                Logger.info(current_state)
                
                
                ############### End of SCI-mode operation planner #################




#######################################################################################




def XML_generator_Mode2(root, date, duration, relativeTime, params = {}):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    
    from OPT_Config_File import Mode2_settings, getTLE
    from Operational_Planning_Tool.OPT_XML_generator_macros import IR_night, IR_day
    from pylab import zeros, pi, arccos
    
    log_timestep = Mode2_settings()['log_timestep']
    Logger.info('log_timestep [s]: '+str(log_timestep))
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,Mode2_settings)
    Logger.info('params after params_checker function: '+str(params))
    
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', getTLE()[0], getTLE()[1])
    
    "Pre-allocate space"
    sun_angle = zeros((duration,1))
    
    
    R_mean = 6371
    pointing_altitude = params['pointing_altitude']
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+90))/pi*180 + 90
    Logger.info('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(duration):
        
        
        current_time = ephem.Date(date+ephem.second*t)
        
        MATS.compute(current_time)
        
        Sun.compute(current_time)
        sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        if( t % log_timestep == 0):
            Logger.info('')
            Logger.info('current_time: '+str(current_time))
            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
        
        ############# Initial Mode setup ##########################################
        
        if( t == 0 ):
            
            "Check if night or day"
            if( sun_angle[t] > MATS_nadir_eclipse_angle):
                current_state = "IR_night"
                comment = current_state+': '+str(params)
                IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
            elif( sun_angle[t] < MATS_nadir_eclipse_angle):
                current_state = "IR_day"
                comment = current_state+': '+str(params)
                IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                
        
        ############# End of Initial Mode setup ###################################
        
        
        
        if(t != 0):
        ####################### SCI-mode Operation planner ################
            
            
           
            #Check if night or day
            if( sun_angle[t] > MATS_nadir_eclipse_angle and current_state != "IR_night"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle) or current_state == "NLC_night"):
                    current_state = "IR_night"
                    comment = current_state+': '+str(params)
                    IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                
                    
            #Check if night or day            
            if( sun_angle[t] < MATS_nadir_eclipse_angle and current_state != "IR_day"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle) or current_state != "NLC_day"):
                    current_state = "IR_day"
                    comment = current_state+': '+str(params)
                    IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                        
        
        if( t % log_timestep == 0):
            Logger.info(current_state)
                 
        ############### End of SCI-mode operation planner #################





############################################################################################




def XML_generator_Mode120(root, date, duration, relativeTime, 
                       params = {}):
    "Generates and calculates parameters and calls for macros, which will generate commands in the XML-file"
    
    
    from OPT_Config_File import Mode120_settings
    from Operational_Planning_Tool.OPT_XML_generator_macros import Mode120_macro
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,Mode120_settings)
    Logger.info('params after params_checker function: '+str(params))
    
    comment = 'Mode 120 starting date: '+str(date)+', '+str(params)
    
    GPS_epoch = Timeline_settings()['GPS_epoch']
    leapSeconds = ephem.second*Timeline_settings()['leap_seconds']
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    freezeTime = str(int((freeze_start_utc+leapSeconds-GPS_epoch)*24*3600))
    
    FreezeDuration = str(params['freeze_duration'])
    
    pointing_altitude = str(params['pointing_altitude'])
    
    Logger.info('GPS_epoch: '+str(GPS_epoch))
    Logger.info('freeze_start_utc: '+str(freeze_start_utc))
    Logger.info('freezeTime [GPS]: '+freezeTime)
    Logger.info('FreezeDuration: '+FreezeDuration)
    
    Mode120_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                     FreezeDuration = FreezeDuration, pointing_altitude = pointing_altitude, comment = comment)




################################################################################################




def XML_generator_Mode130(root, date, duration, relativeTime, 
                       params = {}):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    
    from OPT_Config_File import Mode130_settings
    from Operational_Planning_Tool.OPT_XML_generator_macros import Mode130_macro
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,Mode130_settings)
    Logger.info('params after params_checker function: '+str(params))
    
    comment = 'Mode 130 starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = str(params['pointing_altitude'])
    
    
    
    Mode130_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = pointing_altitude, comment = comment)




##############################################################################################




def XML_generator_Mode200(root, date, duration, relativeTime, 
                       params = {}):
    "Generates and calculates parameters, and convert them to strings, then and calls for macros, which will generate commands in the XML-file"
    
    
    from OPT_Config_File import Mode200_settings
    from Operational_Planning_Tool.OPT_XML_generator_macros import Mode200_macro
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,Mode200_settings)
    Logger.info('params after params_checker function: '+str(params))
    
    comment = 'Mode 200 starting date: '+str(date)+', '+str(params)
    
    
    GPS_epoch = Timeline_settings()['GPS_epoch']
    leapSeconds = ephem.second*Timeline_settings()['leap_seconds']
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    
    pointing_altitude = str(params['pointing_altitude'])
    freezeTime = str(int((freeze_start_utc+leapSeconds-GPS_epoch)*24*3600))
    FreezeDuration = str(params['freeze_duration'])
    
    Logger.info('GPS_epoch: '+str(GPS_epoch))
    Logger.info('freeze_start_utc: '+str(freeze_start_utc))
    Logger.info('freezeTime [GPS]: '+freezeTime)
    Logger.info('FreezeDuration: '+FreezeDuration)
    
    Mode200_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                     FreezeDuration = FreezeDuration, pointing_altitude = pointing_altitude, comment = comment)



##############################################################################################



def XML_generator_Limb_functional_test(root, date, duration, relativeTime, params = {'ExpTimes': [1,2,4,8,16]}):
    """Limb_functional_test. Schedules Limb_functional_test with defined parameters and simulates MATS propagation from TLE.
    Scheduling of all daylight and nighttime commands are separated and all commands for one is scheduled first.
    """
    
    from Operational_Planning_Tool.OPT_XML_generator_macros import Limb_functional_test_macro
    from OPT_Config_File import getTLE
    from pylab import dot, arccos, zeros, pi, sin, cos, arctan, cross, norm, sqrt
    #from OPT_Config_File import Mode=X=_settings
    
    Logger.debug('params from Science Mode List: '+str(params))
    #params = params_checker(params,Mode=X=_settings)
    
    log_timestep = 500
    Logger.info('log_timestep [s]: '+str(log_timestep))
    
    duration_flag = 0
    
    JPEGQs = ['101','95']
    
    ExpTimes = params['ExpTimes']
    
    initial_relativeTime = relativeTime
    
    for mode in ['Day', 'Night']:
        
        "Altitudes that defines the LP"
        for altitude in [50000,70000,90000,110000,130000,160000,200000]:
            
            #"Variable to alert the program when a new altitude is set"
            #flag_pointing = 'Not Pointed'
            
            for JPEGQ in JPEGQs:
                
                
                
                for ExpTime in ExpTimes:
                    
                    ############################################################################
                    ########################## Orbit simulator #################################
                    ############################################################################
                    
                    Sun = ephem.Sun(date)
                    MATS = ephem.readtle('MATS', getTLE()[0], getTLE()[1])
                    
                    "Pre-allocate space"
                    lat_MATS = zeros((duration,1))
                    lat_LP = zeros((duration,1))
                    sun_angle = zeros((duration,1))
                    altitude_MATS = zeros((duration,1))
                    g_ra_MATS = zeros((duration,1))
                    g_dec_MATS = zeros((duration,1))
                    x_MATS = zeros((duration,1))
                    y_MATS = zeros((duration,1))
                    z_MATS = zeros((duration,1))
                    r_MATS = zeros((duration,3))
                    r_LP_direction = zeros((duration,3))
                    normal_orbital = zeros((duration,3))
                    orbangle_between_LP_MATS_array = zeros((duration,1))
                    
                    g_ra_Sun = zeros((duration,1))
                    g_dec_Sun = zeros((duration,1))
                    x_Sun = zeros((duration,1))
                    y_Sun = zeros((duration,1))
                    z_Sun = zeros((duration,1))
                    r_Sun_direction = zeros((duration,3))
                    
                    R_mean = 6371
                    altitude_km = altitude/1000
                    
                    #lat = params['lat']/180*pi
                    lat = 30/180*pi
                    
                    #Estimation of the angle [degrees] between the sun and the FOV position when it enters eclipse
                    LP_eclipse_angle = arccos(R_mean/(R_mean+altitude_km))/pi*180 + 90
                    
                    
                    
                    Logger.info('')
                    Logger.info('LP_eclipse_angle : '+str(LP_eclipse_angle))
                    
                    t=0
                    
                    "Calculate the current angle between MATS and the Sun and the latitude of the LP"
                    "and Loop until it is either day or night and the right latitude"
                    while(True):
                        
                        
                        mode_relativeTime = relativeTime - initial_relativeTime
                        current_time = ephem.Date(date+ephem.second*mode_relativeTime)
                        
                        if(mode_relativeTime > duration and duration_flag == 0):
                            Logger.warning('Warning!! The scheduled time for the mode has ran out.')
                            input('Enter anything to continue:\n')
                            duration_flag = 1
                        
                        MATS.compute(current_time)
                        
                        
                        (lat_MATS[t],altitude_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
                        MATS.sublat,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
                        
                        z_MATS[t] = sin(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)
                        x_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* cos(g_ra_MATS[t])
                        y_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* sin(g_ra_MATS[t])
                       
                        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
                        
                        orbangle_between_LP_MATS_array[t]= arccos((R_mean+altitude/1000)/(R_mean+altitude_MATS[t]))/pi*180
                        orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
                        
                        Sun.compute(current_time)
                        
                        (g_ra_Sun[t],g_dec_Sun[t])= (Sun.g_ra,Sun.g_dec)
                        
                        z_Sun[t] = sin(g_dec_Sun[t])
                        x_Sun[t] = cos(g_dec_Sun[t])* cos(g_ra_Sun[t])
                        y_Sun[t] = cos(g_dec_Sun[t])* sin(g_ra_Sun[t])
                       
                        r_Sun_direction[t,0:3] = [x_Sun[t], y_Sun[t], z_Sun[t]]
                        
                        
                        
                        #sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
                        
                        if( t != 0):
                            "Vector normal to the orbital plane of MATS"
                            normal_orbital[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
                            normal_orbital[t,0:3] = normal_orbital[t,0:3] / norm(normal_orbital[t,0:3])
                            
                            "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
                            rot_mat = rot_arbit(orbangle_between_LP_MATS/180*pi, normal_orbital[t,0:3])
                            r_LP_direction[t,0:3] = rot_mat @ r_MATS[t]
                            
                            "Estimate latitude by calculating angle between xy-plane vector and z-vector"
                            r_LP__direction_xy = sqrt(r_LP_direction[t,0]**2+r_LP_direction[t,1]**2)
                            lat_LP[t] = arctan(r_LP_direction[t,2]/r_LP__direction_xy)
                            
                            "Calculate angle between LP and the Sun"
                            sun_angle[t] = arccos(dot(r_Sun_direction[t,0:3],r_LP_direction[t,0:3])/norm(r_LP_direction[t,0:3]))/pi*180
                            
                            if( t % log_timestep == 0 or t == 1):
                                Logger.info('')
                                Logger.info('current_time: '+str(current_time))
                                Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                                Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                                Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                                Logger.info('mode: '+str(mode))
                                Logger.info('')
                            
                            if( (sun_angle[t] < LP_eclipse_angle and abs(lat_LP[t]) <= lat and mode == 'Day' ) or 
                               (sun_angle[t] > LP_eclipse_angle and abs(lat_LP[t]) <= lat and mode == 'Night' )):
                                
                                Logger.info('!!Break of Loop!!')
                                Logger.info('Loop Counter (t): '+str(t))
                                Logger.info('current_time: '+str(current_time))
                                Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                                Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                                Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                                Logger.info('mode: '+str(mode))
                                
                                Logger.info('')
                                break
                            
                            
                            
                        "Increase Loop counter"
                        t= t+1
                        
                        "Timestep for propagation of MATS"
                        relativeTime = round(relativeTime + 4,2)
                        
                            
                    ############################################################################
                    ########################## End of Orbit simulator ##########################
                    ############################################################################
                    
                    Logger.info('Limb_functional_test_macro: relativeTime = '+str(relativeTime)+', pointing_altitude = '+str(altitude)+
                                ', ExpTime = '+str(ExpTime)+', JPEGQ = '+str(JPEGQ))
                    
                    
                    
                    relativeTime = Limb_functional_test_macro(root = root, relativeTime = str(relativeTime), 
                                               pointing_altitude = str(altitude), ExpTime = str(ExpTime), 
                                               JPEGQ = JPEGQ)
                    
                    
                    
                    #"To only Schedule pointing command once per altitude"
                    #if( ExpTime == ExpTimes[0] and JPEGQ == JPEGQs[0]):
                    #    flag_pointing = 'Pointed'
                    
                    "Postpone next command until at least the end of ExpTime"
                    relativeTime = round(float(relativeTime) + ExpTime/1000,2)
                
    

#############################################################################################



def XML_generator_Photometer_test_1(root, date, duration, relativeTime, params = {'ExpTimes': [1,2,4,8,16]}):
    "Photometer_test_1"
    
    from Operational_Planning_Tool.OPT_XML_generator_macros import Photometer_test_1_macro
    #from OPT_Config_File import getTLE
    #from pylab import pi, sqrt
    #from OPT_Config_File import Mode=X=_settings
    
    #params = params_checker(params,Mode=X=_settings)
    
    '''
    MATS = ephem.readtle('MATS', getTLE()[0], getTLE()[1])
    MATS.compute(date)
    MATS_altitude = MATS.elevation/1000
    U = 398600.4418 #Earth gravitational parameter
    
    #Semi-Major axis of MATS, assuming circular orbit
    #MATS_p = norm(r_MATS[t,0:3])
    MATS_p = 2*(MATS_altitude+6371)
    
    #Orbital Period of MATS
    MATS_P = 2*pi*sqrt(MATS_p**3/U)
    '''
    
    Logger.info('')
    
    ExpTimes = params['ExpTimes']
    
    initial_relativeTime = relativeTime
    
    
    
    Photometer_test_1_duration = duration
    
    while( True ):
        mode_relativeTime = round(relativeTime - initial_relativeTime,2)
        
        if( mode_relativeTime >= Photometer_test_1_duration):
            Logger.info('End of Photometer_test_1')
            break
            
        for ExpTime in ExpTimes:
            ExpInt = ExpTime +1
            Logger.info('Photometer_test_1_macro: relativeTime = '+str(relativeTime)+
                                ', ExpTime = '+str(ExpTime)+', ExpInt = '+str(ExpInt))
            relativeTime = Photometer_test_1_macro(root, relativeTime = str(relativeTime), ExpTime = str(ExpTime), ExpInt = str(ExpInt))
            relativeTime = float(relativeTime)




##############################################################################################


##############################################################################################



def XML_generator_Nadir_functional_test(root, date, duration, relativeTime, params = {'ExpTimes': [1,2,4,8,16]}):
    "Nadir_functional_test"
    
    from Operational_Planning_Tool.OPT_XML_generator_macros import Nadir_functional_test_macro
    from OPT_Config_File import getTLE
    from pylab import zeros, pi, sin, cos, arccos
    
    Logger.debug('params from Science Mode List: '+str(params))
    #params = params_checker(params,Mode=X=_settings)
    
    log_timestep = 100
    Logger.info('log_timestep [s]: '+str(log_timestep))
    
    duration_flag = 0
    
    JPEGQs = ['101','95']
    
    altitude = 92500
    
    ExpTimes = params['ExpTimes']
    
    initial_relativeTime = relativeTime
    
    for mode in ['Day', 'Night']:
        
        for JPEGQ in JPEGQs:
            
            for ExpTime in ExpTimes:
                
                ############################################################################
                ########################## Orbit simulator #################################
                ############################################################################
                
                Sun = ephem.Sun(date)
                MATS = ephem.readtle('MATS', getTLE()[0], getTLE()[1])
                
                "Pre-allocate space"
                lat_MATS = zeros((duration,1))
                sun_angle = zeros((duration,1))
                altitude_MATS = zeros((duration,1))
                g_ra_MATS = zeros((duration,1))
                g_dec_MATS = zeros((duration,1))
                x_MATS = zeros((duration,1))
                y_MATS = zeros((duration,1))
                z_MATS = zeros((duration,1))
                r_MATS = zeros((duration,3))
                
                R_mean = 6371
                altitude_km = altitude/1000
                
                #Estimation of the angle [degrees] between the sun and the FOV position when it enters eclipse
                nadir_eclipse_angle = arccos(R_mean/(R_mean+altitude_km))/pi*180 + 90
                
                #lat = params['lat']/180*pi
                lat = 30/180*pi
                
                Logger.info('')
                Logger.info('nadir_eclipse_angle : '+str(nadir_eclipse_angle))
                
                t=0
                
                "Calculate the current angle between MATS and the Sun"
                "and Loop until it is either day or night and the right latitude"
                while(True):
                    
                    
                    mode_relativeTime = relativeTime - initial_relativeTime
                    current_time = ephem.Date(date+ephem.second*mode_relativeTime)
                    
                    if(mode_relativeTime > duration and duration_flag == 0):
                        Logger.warning('Warning!! The scheduled time for the mode has ran out.')
                        input('Enter anything to continue:\n')
                        duration_flag = 1
                    
                    MATS.compute(current_time)
                    
                    
                    (lat_MATS[t],altitude_MATS[t],g_ra_MATS[t],g_dec_MATS[t])= (
                    MATS.sublat,MATS.elevation/1000,MATS.g_ra,MATS.g_dec)
                    
                    z_MATS[t] = sin(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)
                    x_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* cos(g_ra_MATS[t])
                    y_MATS[t] = cos(g_dec_MATS[t])*(altitude_MATS[t]+R_mean)* sin(g_ra_MATS[t])
                   
                    r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
                    
                    sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
                    
                    
                    if( t % log_timestep == 0 or t == 1):
                        Logger.info('')
                        Logger.info('current_time: '+str(current_time))
                        Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                        Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                        Logger.info('mode: '+str(mode))
                        Logger.info('')
                    
                    if( (sun_angle[t] < nadir_eclipse_angle and abs(lat_MATS[t]) <= lat and mode == 'Day' ) or 
                       (sun_angle[t] > nadir_eclipse_angle and abs(lat_MATS[t]) <= lat and mode == 'Night' )):
                        
                        Logger.info('!!Break of Loop!!')
                        Logger.info('Loop Counter (t): '+str(t))
                        Logger.info('current_time: '+str(current_time))
                        Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                        Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                        Logger.info('mode: '+str(mode))
                        
                        Logger.info('')
                        break
                        
                        
                        
                    "Increase Loop counter"
                    t= t+1
                    
                    "Timestep for propagation of MATS"
                    relativeTime = round(relativeTime + 4,1)
                    
                        
                ############################################################################
                ########################## End of Orbit simulator ##########################
                ############################################################################
                
                Logger.info('Limb_functional_test_macro: relativeTime = '+str(relativeTime)+', pointing_altitude = '+str(altitude)+
                            ', ExpTime = '+str(ExpTime)+', JPEGQ = '+str(JPEGQ))
                
                
                
                relativeTime = Nadir_functional_test_macro(root = root, relativeTime = str(relativeTime), 
                                           pointing_altitude = str(altitude), ExpTime = str(ExpTime), 
                                           JPEGQ = JPEGQ)
                
                
                
                #"To only Schedule pointing command once per altitude"
                #if( ExpTime == ExpTimes[0] and JPEGQ == JPEGQs[0]):
                #    flag_pointing = 'Pointed'
                
                "Postpone next command until at least the end of ExpTime"
                relativeTime = round(float(relativeTime) + ExpTime/1000,2)



#######################################################################################################




##############################################################################################


'''
def XML_generator_Mode=X=(root, date, duration, relativeTime, params = {}):
    "This is a template for a new mode. Exchange 'Mode=X=' for the name of the new mode"
    
    from Operational_Planning_Tool.OPT_XML_generator_macros import Mode=X=_macro
    from OPT_Config_File import Mode=X=_settings
    
    #params = params_checker(params,Mode=X=_settings)
    
    
    Mode=X=_macro()
'''

#######################################################################################################






def params_checker(params, Mode_settings):
    '''Function to check what parameters are given in the Science Mode Timeline List and fill in any missing from the Config File.
    Inputs:
        params: Dictionary containing the parameters given in the Science Mode Timeline List.
        Mode_settings: Function to the settings given in OPT_Config_File of the current Mode"
    Output:
        params: Dictionary containing parameters given in the Science Mode List together with any parameters missing, '
        which are give in OPT_Config_File
    '''
    
    
    "Check if optional params were given"
    if( params != Mode_settings()):
        params_new = Mode_settings()
        "Loop through parameters given and exchange the settings ones"
        for key in params.keys():
            params_new[key] = params[key]
        params = params_new
    return params

