# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 11:35:08 2018
Contains XML generator functions for all different science modes. Each function will call upon macrofunctions.
@author: David
"""

from pylab import zeros, pi, arccos
import ephem
from MATS_TIMELINE_SCIMOD_DEFAULT_PARAMS import Mode1_default, Mode2_default, Mode120_default, Mode130_default, Mode200_default, Timeline_params, getTLE


def XML_generator_Mode1(root, date, duration, relativeTime, params = Mode1_default()):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    from MATS_TIMELINE_macros import IR_night, IR_day, NLC_day, NLC_night
    
    "Load parameters from config function"
    params_default = Mode1_default()
    
    "Check if optional params were given"
    if( params != params_default):
        params_new = params_default
        "Loop through parameters given and exchange them for the default ones"
        for key in params.keys():
            params_new[key] = params[key]
        params = params_new
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', getTLE()[0], getTLE()[1])
    
    "Pre-allocate space"
    lat_MATS = zeros((duration,1))
    sun_angle = zeros((duration,1))
    
    
    R_mean = 6371
    pointing_altitude = str(params['pointing_altitude'])
    lat = params['lat']/180*pi
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+90))/pi*180 + 90
    
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(duration):
        
        
        current_time = ephem.Date(date+ephem.second*t)
        
        MATS.compute(current_time)
        
        lat_MATS[t]= MATS.sublat
        
        
        Sun.compute(current_time)
        sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        
        ############# Initial Mode setup ##########################################
        
        if( t == 0 ):
            
            "Check if night or day"
            if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                
                if( abs(lat_MATS[t]) < lat):
                    current_state = "IR_night"
                    IR_night(root,str(t+relativeTime),str(pointing_altitude))
                elif( abs(lat_MATS[t]) > lat):
                    current_state = "NLC_night"
                    NLC_night(root,str(t+relativeTime),str(pointing_altitude))
                    
            elif( sun_angle[t] < MATS_nadir_eclipse_angle ):
                
                if( abs(lat_MATS[t]) < lat):
                    current_state = "IR_day"
                    IR_day(root,str(t+relativeTime),str(pointing_altitude))
                elif( abs(lat_MATS[t]) > lat):
                    current_state = "NLC_day"
                    NLC_day(root,str(t+relativeTime),str(pointing_altitude))
                
        
        
        ############# End of Initial Mode setup ###################################
        
        
        
       
        if(t != 0):
            ####################### SCI-mode Operation planner ################
            
            
           
            #Check if night or day
            if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                
                #Check latitude
                if( abs(lat_MATS[t]) < lat and current_state != "IR_night"):
                    
                    #Check dusk/dawn and latitude boundaries
                    if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                        IR_night(root,str(t+relativeTime),pointing_altitude)
                        current_state = "IR_night"
                    elif(abs(lat_MATS[t]) < lat and abs(lat_MATS[t-1]) > lat):
                        IR_night(root,str(t+relativeTime),pointing_altitude)
                        current_state = "IR_night"
                        
                #Check latitude
                if( abs(lat_MATS[t]) > lat and current_state != "NLC_night"):
                    
                    #Check dusk/dawn and latitude boundaries
                    if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                        NLC_night(root,str(t+relativeTime),pointing_altitude)
                        current_state = "NLC_night"
                    elif(abs(lat_MATS[t]) > lat and abs(lat_MATS[t-1]) < lat):
                        NLC_night(root,str(t+relativeTime),pointing_altitude)
                        current_state = "NLC_night"
                        
            #Check if night or day#            
            if( sun_angle[t] < MATS_nadir_eclipse_angle ):
                
                #Check latitude
                if( abs(lat_MATS[t]) < lat and current_state != "IR_day"):
                    
                    #Check dusk/dawn and latitude boundaries
                    if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                        IR_day(root,str(t+relativeTime),pointing_altitude)
                        current_state = "IR_day"
                    elif(abs(lat_MATS[t]) < lat and abs(lat_MATS[t-1]) > lat):
                        IR_day(root,str(t+relativeTime),pointing_altitude)
                        current_state = "IR_day"
                        
                #Check latitude
                if( abs(lat_MATS[t]) > lat and current_state != "NLC_day"):
                    
                    #Check dusk/dawn and latitude boundaries
                    if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                        NLC_day(root,str(t+relativeTime),pointing_altitude)
                        current_state = "NLC_day"
                    elif(abs(lat_MATS[t]) > lat and abs(lat_MATS[t-1]) < lat):
                        NLC_day(root,str(t+relativeTime),pointing_altitude)
                        current_state = "NLC_day"
                        
                        
            
            ############### End of SCI-mode operation planner #################




#######################################################################################




def XML_generator_Mode2(root, date, duration, relativeTime, params = Mode2_default()):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    from MATS_TIMELINE_macros import IR_night, IR_day
    
    
    "Load parameters from config function"
    params_default = Mode2_default()
    "Check if optional params were given"
    if( params != params_default):
        params_new = params_default
        "Loop through parameters given and exchange them for the default ones"
        for key in params.keys():
            params_new[key] = params[key]
        params = params_new
        
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', getTLE()[0], getTLE()[1])
    
    "Pre-allocate space"
    sun_angle = zeros((duration,1))
    
    
    R_mean = 6371
    pointing_altitude = str(params['pointing_altitude'])
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+90))/pi*180 + 90
    
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(duration):
        
        
        current_time = ephem.Date(date+ephem.second*t)
        
        MATS.compute(current_time)
        
        Sun.compute(current_time)
        sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        
        ############# Initial Mode setup ##########################################
        
        if( t == 0 ):
            
            "Check if night or day"
            if( sun_angle[t] > MATS_nadir_eclipse_angle):
                current_state = "IR_night"
                IR_night(root,str(t+relativeTime),pointing_altitude)
            elif( sun_angle[t] < MATS_nadir_eclipse_angle):
                current_state = "IR_day"
                IR_day(root,str(t+relativeTime),pointing_altitude)
                
        
        ############# End of Initial Mode setup ###################################
        
        
        
        if(t != 0):
        ####################### SCI-mode Operation planner ################
            
            
           
            #Check if night or day
            if( sun_angle[t] > MATS_nadir_eclipse_angle and current_state != "IR_night"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle) or current_state == "NLC_night"):
                    IR_night(root,str(t+relativeTime),pointing_altitude)
                    current_state = "IR_night"
                
                    
            #Check if night or day            
            if( sun_angle[t] < MATS_nadir_eclipse_angle and current_state != "IR_day"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle) or current_state != "NLC_day"):
                    IR_day(root,str(t+relativeTime),pointing_altitude)
                    current_state = "IR_day"
                        
                         
        ############### End of SCI-mode operation planner #################





############################################################################################




def XML_generator_Mode120(root, date, duration, relativeTime, 
                       params = Mode120_default()):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    from MATS_TIMELINE_macros import Mode120_macro
    
    "Load parameters from config function"
    params_default = Mode120_default()
    "Check if optional params were given"
    if( params != params_default):
        params_new = params_default
        "Loop through parameters given and exchange them for the default ones"
        for key in params.keys():
            params_new[key] = params[key]
        params = params_new
    
    
    
    GPS_epoch = Timeline_params()['GPS_epoch']
    leapSeconds = ephem.second*Timeline_params()['leap_seconds']
    freeze_start_utc = date+ephem.second*params['freeze_start']
    freezeTime = str(int((freeze_start_utc+leapSeconds-GPS_epoch)*24*3600))
    
    FreezeDuration = str(params['freeze_duration'])
    
    pointing_altitude = str(params['pointing_altitude'])
    
    
    
    Mode120_macro(root = root, relativeTime = str(relativeTime), StartTime=str(freezeTime), 
                     FreezeDuration = FreezeDuration, pointing_altitude = pointing_altitude)




################################################################################################




def XML_generator_Mode130(root, date, duration, relativeTime, 
                       params = Mode130_default()):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    from MATS_TIMELINE_macros import Mode130_macro
    
    "Load parameters from config function"
    params_default = Mode130_default()
    "Check if optional params were given"
    if( params != params_default):
        params_new = params_default
        "Loop through parameters given and exchange them for the default ones"
        for key in params.keys():
            params_new[key] = params[key]
        params = params_new
        
    
    pointing_altitude = str(params['pointing_altitude'])
    
    
    
    Mode130_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = pointing_altitude)




##############################################################################################




def XML_generator_Mode200(root, date, duration, relativeTime, 
                       params = Mode200_default()):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    from MATS_TIMELINE_macros import Mode200_macro
    
    "Load parameters from config function"
    params_default = Mode200_default()
    "Check if optional params were given"
    if( params != params_default):
        params_new = params_default
        "Loop through parameters given and exchange the default ones"
        for key in params.keys():
            params_new[key] = params[key]
        params = params_new
    
    
    
    GPS_epoch = Timeline_params()['GPS_epoch']
    leapSeconds = ephem.second*Timeline_params()['leap_seconds']
    freeze_start_utc = date+ephem.second*params['freeze_start']
    
    pointing_altitude = str(params['pointing_altitude'])
    freezeTime = str(int((freeze_start_utc+leapSeconds-GPS_epoch)*24*3600))
    FreezeDuration = str(params['freeze_duration'])
    
    Mode200_macro(root = root, relativeTime = str(relativeTime), StartTime=str(freezeTime), 
                     FreezeDuration = FreezeDuration, pointing_altitude = pointing_altitude)




#######################################################################################################



