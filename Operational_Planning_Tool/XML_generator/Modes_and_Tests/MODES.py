# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 11:35:08 2018

Generates and calculates parameters for each mode, and converts them to strings,
then calls for macros, which will generate commands in the XML-file.

Functions on the form "XML_generator_X", where the last X is any Mode:
    Arguments:
        root =  XML tree structure. Main container object for the ElementTree API. lxml.etree.Element class
        date = Starting date of the Mode. On the form of the ephem.Date class.
        duration = The duration of the mode [s] as an integer class.
        relativeTime = The starting time of the mode with regard to the start of the timeline [s] as an integer class
        params = Dictionary containing the parameters of the mode.
    
    Returns:
        None

When creating new Mode functions it is crucial that the function name is
XML_generator_Mode_name, where Mode_name is the same as the string used in the Science Mode Timeline
        
@author: David
"""


import ephem, logging, sys, pylab

import OPT_Config_File
from Operational_Planning_Tool.Library import rot_arbit, params_checker, utc_to_onboardTime
from .Macros import Macros

Logger = logging.getLogger(OPT_Config_File.Logger_name())


def XML_generator_Mode1(root, date, duration, relativeTime, params = {}):
    '''Generates parameters and calls for macros, which will generate commands in the XML-file
    
        Arguments:
            
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
    sqrt = pylab.sqrt
    arctan = pylab.arctan
    
    
    settings = OPT_Config_File.Mode1_settings()
    
    log_timestep = settings['log_timestep']
    Logger.info('log_timestep [s]: '+str(log_timestep))
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
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
    
    Logger.debug('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    Logger.debug('')
    
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
        
        if( t % log_timestep == 0 and t != 0 and t != 1):
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
            
            "Estimate latitude by calculating angle between xy-plane vector and z-vector (ECI)"
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
                
                
                
                "Check if night or day"
                if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                    
                    if( abs(lat_LP[t]) < lat):
                        current_state = "IR_night"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_night"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                        
                elif( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    if( abs(lat_LP[t]) < lat):
                        current_state = "IR_day"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_day"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                
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
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.info('')
                            Logger.info(current_state)
                            Logger.info('current_time: '+str(current_time))
                            Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                            #IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.nadir_on_off(root, str(t+relativeTime), nadir = '1', comment = comment)
                            
                            
                        elif(abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat):
                            current_state = "IR_night"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.info('')
                            Logger.info(current_state)
                            Logger.info('current_time: '+str(current_time))
                            Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            
                            
                            
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_night"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_night"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.info('')
                            Logger.info(current_state)
                            Logger.info('current_time: '+str(current_time))
                            Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                            #NLC_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.nadir_on_off(root, str(t+relativeTime), nadir = '1', comment = comment)
                            
                            
                        elif(abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat):
                            current_state = "NLC_night"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.info('')
                            Logger.info(current_state)
                            Logger.info('current_time: '+str(current_time))
                            Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            
                            
                            
                #Check if night or day#            
                if( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    #Check latitude
                    if( abs(lat_LP[t]) < lat and current_state != "IR_day"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle):
                            current_state = "IR_day"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.info('')
                            Logger.info(current_state)
                            Logger.info('current_time: '+str(current_time))
                            Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                            #IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.nadir_on_off(root, str(t+relativeTime), nadir = '0', comment = comment)
                            
                            
                        elif(abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat):
                            current_state = "IR_day"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.info('')
                            Logger.info(current_state)
                            Logger.info('current_time: '+str(current_time))
                            Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            
                            
                            
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_day"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle):
                            current_state = "NLC_day"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.info('')
                            Logger.info(current_state)
                            Logger.info('current_time: '+str(current_time))
                            Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                            #NLC_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            Macros.nadir_on_off(root, str(t+relativeTime), nadir = '0', comment = comment)
                            
                            
                        elif(abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat):
                            current_state = "NLC_day"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            
                            Logger.info('')
                            Logger.info(current_state)
                            Logger.info('current_time: '+str(current_time))
                            Logger.info('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.info('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                            Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                            Macros.NLC_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                            
                            
                
            
                
                
                ############### End of SCI-mode operation planner #################




#######################################################################################




def XML_generator_Mode2(root, date, duration, relativeTime, params = {}):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    settings = OPT_Config_File.Mode2_settings()
    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos
    
    log_timestep = settings['log_timestep']
    Logger.info('log_timestep [s]: '+str(log_timestep))
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
    
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
                if( (sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle) or current_state == "NLC_night"):
                    current_state = "IR_night"
                    comment = current_state+': '+str(params)
                    
                    Logger.info('')
                    Logger.info('current_time: '+str(current_time))
                    Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                    Macros.IR_night(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    
                    
                    
            #Check if night or day            
            if( sun_angle[t] < MATS_nadir_eclipse_angle and current_state != "IR_day"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle) or current_state != "NLC_day"):
                    current_state = "IR_day"
                    comment = current_state+': '+str(params)
                    
                    Logger.info('')
                    Logger.info('current_time: '+str(current_time))
                    Logger.info('sun_angle [degrees]: '+str(sun_angle[t]))
                    Macros.IR_day(root,str(t+relativeTime),str(pointing_altitude), comment = comment)
                    
                    
                    
                 
        ############### End of SCI-mode operation planner #################





############################################################################################

################################################################################################



def XML_generator_Mode100(root, date, duration, relativeTime, params = {}):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    settings = OPT_Config_File.Mode100_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    
    pointing_altitude_from = params['pointing_altitude_from']
    pointing_altitude_to = params['pointing_altitude_to']
    pointing_altitude_interval = params['pointing_altitude_interval']
    
    number_of_altitudes = round( (pointing_altitude_to - pointing_altitude_from) / pointing_altitude_interval +1 )
    
    pointing_altitudes = [pointing_altitude_from + x*pointing_altitude_interval for x in range(number_of_altitudes)]
    
    duration_flag = 0
    initial_relativeTime = relativeTime
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    for pointing_altitude in pointing_altitudes:
        mode_relativeTime = relativeTime - initial_relativeTime
        
        if(mode_relativeTime > duration and duration_flag == 0):
            Logger.warning('Warning!! The scheduled time for the mode has ran out.')
            #input('Enter anything to ackknowledge and continue:\n')
            duration_flag = 1
        
        relativeTime = Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = str(pointing_altitude), comment = comment)
        relativeTime = round(float(relativeTime) + params['pointing_duration'], 1)



##############################################################################################

##############################################################################################



def XML_generator_Mode110(root, date, duration, relativeTime, params = {}):
    "Mode110"
    
    settings = OPT_Config_File.Mode110_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
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
    "Generates and calculates parameters and calls for macros, which will generate commands in the XML-file"
    
    settings = OPT_Config_File.Mode120_settings()
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    #freezeTime = str(int((freeze_start_utc+leapSeconds-GPS_epoch)*24*3600))
    
    freezeTime = str(utc_to_onboardTime(freeze_start_utc))
    
    FreezeDuration = params['freeze_duration']
    
    pointing_altitude = params['pointing_altitude']
    
    
    Logger.info('freeze_start_utc: '+str(freeze_start_utc))
    Logger.info('freezeTime [GPS]: '+freezeTime)
    Logger.info('FreezeDuration: '+str(FreezeDuration))
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Mode_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                     FreezeDuration = str(FreezeDuration), pointing_altitude = str(pointing_altitude), comment = comment)




################################################################################################




############################################################################################




def XML_generator_Mode121(root, date, duration, relativeTime, 
                       params = {}):
    "Generates and calculates parameters and calls for macros, which will generate commands in the XML-file"
    
    
    settings = OPT_Config_File.Mode121_settings()
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    freezeTime = str(utc_to_onboardTime(freeze_start_utc))
    
    FreezeDuration = params['freeze_duration']
    
    pointing_altitude = params['pointing_altitude']
    
    Logger.info('freeze_start_utc: '+str(freeze_start_utc))
    Logger.info('freezeTime [GPS]: '+freezeTime)
    Logger.info('FreezeDuration: '+str(FreezeDuration))
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Mode_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                     FreezeDuration = str(FreezeDuration), pointing_altitude = str(pointing_altitude), comment = comment)




################################################################################################

############################################################################################




def XML_generator_Mode122(root, date, duration, relativeTime, 
                       params = {}):
    "Generates and calculates parameters and calls for macros, which will generate commands in the XML-file"
    
    
    settings = OPT_Config_File.Mode122_settings()
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    freezeTime = str(utc_to_onboardTime(freeze_start_utc))
    
    FreezeDuration = params['freeze_duration']
    
    pointing_altitude = params['pointing_altitude']
    
    Logger.info('freeze_start_utc: '+str(freeze_start_utc))
    Logger.info('freezeTime [GPS]: '+freezeTime)
    Logger.info('FreezeDuration: '+str(FreezeDuration))
    
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    for ExpTime in params['ExpTimes']:
        ExpInt = ExpTime + 1
        relativeTime = Mode_macro(root = root, relativeTime = str(relativeTime), freezeTime=freezeTime, 
                     FreezeDuration = str(FreezeDuration), pointing_altitude = str(pointing_altitude), 
                     ExpInt = str(ExpInt), ExpTime = str(ExpTime), comment = comment)
        relativeTime = round(float(relativeTime) + params['session_duration'], 1)




################################################################################################


def XML_generator_Mode130(root, date, duration, relativeTime, 
                       params = {}):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    
    settings = OPT_Config_File.Mode130_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = str(pointing_altitude), comment = comment)




##############################################################################################


################################################################################################



def XML_generator_Mode131(root, date, duration, relativeTime, 
                       params = {}):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    settings = OPT_Config_File.Mode131_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    
    Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = str(pointing_altitude), comment = comment)




##############################################################################################

################################################################################################



def XML_generator_Mode132(root, date, duration, relativeTime, 
                       params = {}):
    "Generates parameters and calls for macros, which will generate commands in the XML-file"
    
    
    settings = OPT_Config_File.Mode132_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
        
    pointing_altitude = params['pointing_altitude']
    
    Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    for ExpTime in params['ExpTimes']:
        ExpInt = ExpTime + 1
        relativeTime = Mode_macro(root = root, relativeTime = str(relativeTime), pointing_altitude = str(pointing_altitude), 
                   ExpInt = str(ExpInt), ExpTime = str(ExpTime), comment = comment)
        relativeTime = round(float(relativeTime) + params['session_duration'], 1)
        



##############################################################################################


def XML_generator_Mode200(root, date, duration, relativeTime, 
                       params = {}):
    "Generates and calculates parameters, and convert them to strings, then and calls for macros, which will generate commands in the XML-file"
    
    
    settings = OPT_Config_File.Mode200_settings()
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    Logger.debug('params from Science Mode List: '+str(params))
    params = params_checker(params,settings)
    Logger.info('params after params_checker function: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    freezeTime = str(utc_to_onboardTime(freeze_start_utc))
    
    FreezeDuration = params['freeze_duration']
    
    pointing_altitude = str(params['pointing_altitude'])
    
    
    Logger.info('freeze_start_utc: '+str(freeze_start_utc))
    Logger.info('freezeTime [GPS]: '+freezeTime)
    Logger.info('FreezeDuration: '+str(FreezeDuration))
    
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
    #Logger.info('params after params_checker function: '+str(params))
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    Mode_name_macro(root = root, relativeTime = str(relativeTime), comment = comment)
'''

#######################################################################################################





