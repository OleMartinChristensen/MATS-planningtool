# -*- coding: utf-8 -*-
"""Generates and calculates parameters for each mode, 
then calls for macros, which will generate commands in the XML-file.

Functions on the form "XML_generator_X", where the last X is any Mode:

Arguments:
    root (lxml.etree.Element):  XML tree structure. Main container object for the ElementTree API. \n
    date (ephem.Date): Starting date of the Mode. On the form of the ephem.Date class. \n
    duration (int): The duration of the mode [s]. \n
    relativeTime (int): The starting time of the mode with regard to the start of the timeline [s]. \n
    params (dict): Dictionary containing the parameters of the Mode given in the Science_Mode_Timeline.

Returns:
    None

When creating new Mode functions it is crucial that the function name is
XML_generator_Mode_name, where Mode_name is the same as the string used in the Science Mode Timeline
        
@author: David
"""


import ephem, logging, sys, pylab, importlib, skyfield.api

from Operational_Planning_Tool import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
from Operational_Planning_Tool._Library import lat_MATS_calculator, rot_arbit, params_checker, utc_to_onboardTime, lat_2_R
from .Macros import Macros
from Operational_Planning_Tool import _MATS_coordinates

Logger = logging.getLogger(OPT_Config_File.Logger_name())
#Timeline_settings = OPT_Config_File.Timeline_settings()


def XML_generator_Mode5(root, date, duration, relativeTime, params = {}):
    '''Mode5, Operational_Limb_Pointing_macro
    
    Look at fixed limb altitude in operational mode.
    CustomBinning.
            
    '''
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('CustomBinning')
    settings = OPT_Config_File.Mode5_settings()
    
    params = params_checker(params,settings)
    
    Mode_name = sys._getframe(1).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    
    #Macros.Custom_Binning_Macro(root,relativeTime, pointing_altitude=pointing_altitude, comment = comment)
    Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                           pointing_altitude=pointing_altitude, comment = comment)
                        


############################################################################################
    
def XML_generator_Mode1(root, date, duration, relativeTime, params = {}):
    """Mode1, Operational_Limb_Pointing_macro
    
    Simulates MATS and the LP with or without yaw movement to be able to predict and schedule commands in the XML-file.
    Look at fixed limb altitude in operational mode.
    High resolution UV binning for latitudes +-lat degrees latitude polewards.
    Disable exposure on UV channels for +-lat degrees latitude equatorwards.
    Stop/Start Nadir at dusk/dawn below MATS.
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
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('HighResUV')
    settings = OPT_Config_File.Mode1_2_settings()
    #Timeline_settings = OPT_Config_File.Timeline_settings()
    Timeline_settings = _Globals.Timeline_settings
    
    params = params_checker(params,settings)
    
    timestep = params['timestep']
    TEXPMS_UV = CCD_settings['CCD_48']['TEXPMS']
    TEXPMS_nadir = CCD_settings['CCD_64']['TEXPMS']
    
    log_timestep = params['log_timestep']
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
    
    "Pre-allocate space"
    lat_MATS = zeros((duration,1))
    
    altitude_MATS = zeros((duration,1))
    a_ra_MATS = zeros((duration,1))
    a_dec_MATS = zeros((duration,1))
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
    MATS_P = zeros((duration,1))
    MATS_p = zeros((duration,1))
    pitch_LP = zeros((duration,1))
    
    sun_angle = zeros((duration,1))
    lat_LP = zeros((duration,1))
    normal_orbital = zeros((duration,3))
    orbangle_between_LP_MATS_array = zeros((duration,1))
    
    
    U = 398600.4418 #Earth gravitational parameter
    R_mean = 6371
    pointing_altitude = Timeline_settings['LP_pointing_altitude']
    lat = params['lat']
    Earth_north = array([[0,0,1]])
    
    #Earth_north = pm3d.ecef2eci(0,0,1,date)
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+pointing_altitude/1000))/pi*180 + 90
    
    Logger.debug('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    Logger.debug('')
    
    ts = skyfield.api.load.timescale()
    MATS_skyfield = skyfield.api.EarthSatellite(OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(int(duration/timestep)):
        
        current_time = ephem.Date(date+ephem.second*timestep*t)
        
        """
        #Skyfield
        current_time_datetime = ephem.Date(current_time).datetime()
        year = current_time_datetime.year
        month = current_time_datetime.month
        day = current_time_datetime.day
        hour = current_time_datetime.hour
        minute = current_time_datetime.minute
        second = current_time_datetime.second + current_time_datetime.microsecond/1000000
        current_time_skyfield = ts.utc(year, month, day, hour, minute, second)
        
        MATS_geocentric = MATS_skyfield.at(current_time_skyfield)
        r_MATS[t] = MATS_geocentric.position.km
        MATS_subpoint = MATS_geocentric.subpoint()
        lat_MATS[t] = MATS_subpoint.latitude.radians
        altitude_MATS[t] = MATS_subpoint.elevation.km
        
        R_earth_MATS = lat_2_R(lat_MATS[t])
        """
        
        MATS.compute(current_time, epoch='2000/01/01 11:58:55.816')
        
        
        (lat_MATS[t],altitude_MATS[t],a_ra_MATS[t],a_dec_MATS[t])= (
        MATS.sublat,MATS.elevation/1000,MATS.a_ra,MATS.a_dec)
        
        R_earth_MATS = lat_2_R(lat_MATS[t])
        
        z_MATS[t] = sin(a_dec_MATS[t])*(altitude_MATS[t]+R_earth_MATS)
        x_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R_earth_MATS)* cos(a_ra_MATS[t])
        y_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R_earth_MATS)* sin(a_ra_MATS[t])
        
        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
        
        #r_MATS_ECEF[t,0], r_MATS_ECEF[t,1], r_MATS_ECEF[t,2] = _MATS_coordinates.eci2ecef(
        #        r_MATS[t,0]*1000, r_MATS[t,1]*1000, r_MATS[t,2]*1000, ephem.Date(current_time).datetime())
        
        
        r_MATS_unit_vector[t,0:3] = r_MATS[t,0:3] / norm(r_MATS[t,0:3])
        
        #Semi-Major axis of MATS, assuming circular orbit
        MATS_p[t] = norm(r_MATS[t,0:3])
        
        #Orbital Period of MATS
        MATS_P[t] = 2*pi*sqrt(MATS_p[t]**3/U)
        
        if( t == 0):
            orbangle_between_LP_MATS_array[t]= arccos((R_mean+pointing_altitude/1000)/(R_earth_MATS+altitude_MATS[t]))/pi*180
            orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
        
        
        Sun.compute(current_time, epoch='2000/01/01 11:58:55.816')
        sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        
        
        
        if( t % log_timestep == 0 and t != 0 and t != 1):
            Logger.debug('')
            Logger.debug('current_time: '+str(current_time))
            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
            
        
        if( t != 0):
            
            time_between_LP_and_MATS = MATS_P[t][0]*orbangle_between_LP_MATS/360
            timesteps_between_LP_and_MATS = int(time_between_LP_and_MATS / timestep)
            
            "More accurate estimation of lat of LP using the position of MATS at a previous time"
            if( t >= timesteps_between_LP_and_MATS):
                lat_LP[t] = lat_MATS[t-timesteps_between_LP_and_MATS]/pi*180
                R_earth_LP = lat_2_R(lat_LP[t] /180*pi)
            else:
                date_of_MATSlat_is_equal_2_current_LPlat = ephem.Date(current_time - ephem.second * timesteps_between_LP_and_MATS * timestep)
                lat_LP[t] = lat_MATS_calculator( date_of_MATSlat_is_equal_2_current_LPlat )/pi*180
                R_earth_LP = lat_2_R(lat_LP[t]/180*pi)
                
            orbangle_between_LP_MATS_array[t]= arccos((R_earth_LP+pointing_altitude/1000)/(R_earth_MATS+altitude_MATS[t]))/pi*180
            pitch_LP = orbangle_between_LP_MATS_array[t][0] + 90
            
            
            
            "Vector normal to the orbital plane of MATS"
            normal_orbital[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
            normal_orbital[t,0:3] = normal_orbital[t,0:3] / norm(normal_orbital[t,0:3])
            
            
            "Rotate 'vector to MATS', to represent pointing direction, (Parallax is negligable)"
            rot_mat = rot_arbit((pitch_LP)/180*pi, normal_orbital[t,0:3])
            optical_axis[t,0:3] = rot_mat @ r_MATS[t]
            optical_axis[t,0:3] = optical_axis[t,0:3] / norm(optical_axis[t,0:3])
            
            "Calculate intersection between the orbital plane and the equator"
            ascending_node = cross(normal_orbital[t,0:3], Earth_north)
            
            arg_of_lat = arccos( dot(ascending_node, r_MATS[t,0:3]) / norm(r_MATS[t,0:3]) / norm(ascending_node) ) /pi*180
            
            "To determine if MATS is moving towards the ascending node"
            if( dot(cross( ascending_node, r_MATS[t,0:3]), normal_orbital[t,0:3]) >= 0 ):
                arg_of_lat = 360 - arg_of_lat
                
            if( Timeline_settings['yaw_correction'] == True ):
                yaw_offset_angle = Timeline_settings['yaw_amplitude'] * cos( arg_of_lat/180*pi - orbangle_between_LP_MATS/180*pi + Timeline_settings['yaw_phase']/180*pi )
                yaw_offset_angle = yaw_offset_angle[0]
            elif( Timeline_settings['yaw_correction'] == False  ):
                yaw_offset_angle = 0
                
            
            if( t % log_timestep == 0 or t == 1 ):
                Logger.debug('ascending_node: '+str(ascending_node))
                Logger.debug('arg_of_lat [degrees]: '+str(arg_of_lat))
                Logger.debug('yaw_offset_angle [degrees]: '+str(yaw_offset_angle))
                Logger.debug('')
            
            "Rotate yaw of pointing direction, meaning to rotate around the vector to MATS"
            rot_mat = rot_arbit( (-yaw_offset_angle)/180*pi, r_MATS_unit_vector[t,0:3])
            optical_axis[t,0:3] = rot_mat @ optical_axis[t,0:3]
            optical_axis[t,0:3] = optical_axis[t,0:3] / norm(optical_axis[t,0:3])
            
            """
            optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                optical_axis[t,0]*1000, optical_axis[t,1]*1000, optical_axis[t,2]*1000, ephem.Date(current_time).datetime())
            
            LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0]*1000, r_MATS_ECEF[t][1]*1000, r_MATS_ECEF[t][2]*1000, 
                                       optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
            
            lat_LP[t], long_LP[t], alt_LP[t]  = _MATS_coordinates.ECEF2lla(LP_ECEF[t,0], LP_ECEF[t,1], LP_ECEF[t,2])
            """
            
            
            
            
            
            
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
                        #Macros.Mode1_macro(root,t*timestep+relativeTime, pointing_altitude=pointing_altitude, UV_on = False, nadir_on = True, comment = comment)
                        CCD_settings['CCD_48']['TEXPMS'] = 0
                        CCD_settings['CCD_64']['TEXPMS'] = TEXPMS_nadir
                        Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                                   pointing_altitude=pointing_altitude, comment = comment)
                        
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_night_UV_on"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        #Macros.Mode1_macro(root,t*timestep+relativeTime, pointing_altitude=pointing_altitude, UV_on = True, nadir_on = True, comment = comment)
                        CCD_settings['CCD_48']['TEXPMS'] = TEXPMS_UV
                        CCD_settings['CCD_64']['TEXPMS'] = TEXPMS_nadir
                        Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                                   pointing_altitude=pointing_altitude, comment = comment)
                        
                        
                elif( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    if( abs(lat_LP[t]) < lat):
                        current_state = "NLC_day_UV_off"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        #Macros.Mode1_macro(root,t*timestep+relativeTime,pointing_altitude, UV_on = False, nadir_on = False, comment = comment)
                        CCD_settings['CCD_48']['TEXPMS'] = 0
                        CCD_settings['CCD_64']['TEXPMS'] = 0
                        Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                                   pointing_altitude=pointing_altitude, comment = comment)
                        
                    elif( abs(lat_LP[t]) > lat):
                        current_state = "NLC_day_UV_on"
                        comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                        #Macros.Mode1_macro(root,t*timestep+relativeTime,pointing_altitude, UV_on = True, nadir_on = False, comment = comment)
                        CCD_settings['CCD_48']['TEXPMS'] = TEXPMS_UV
                        CCD_settings['CCD_64']['TEXPMS'] = 0
                        Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                                   pointing_altitude=pointing_altitude, comment = comment)
                        
                        
                Logger.debug(current_state)
                Logger.debug('')
            
            
            ############# End of Initial Mode setup ###################################
            
            
            if( t != 1):
                ####################### SCI-mode Operation planner ################
                
                #Check if night or day
                if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                    
                    #Check latitude
                    if( abs(lat_LP[t]) < lat and current_state != "NLC_night_UV_off"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( (sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle) or
                           ( abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat ) ):
                            
                            Logger.debug('')
                            current_state = "NLC_night_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            #Macros.Mode1_macro(root, t*timestep+relativeTime, pointing_altitude, UV_on = False, nadir_on = True, comment = comment)
                            CCD_settings['CCD_48']['TEXPMS'] = 0
                            CCD_settings['CCD_64']['TEXPMS'] = TEXPMS_nadir
                            Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                                   pointing_altitude=pointing_altitude, comment = comment)
                            
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Logger.debug('')
                            #IR_night(root,str(t+relativeTime),pointing_altitude, comment = comment)
                            
                            
                            
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_night_UV_on"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( (sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle) or
                           ( abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat )):
                            
                            Logger.debug('')
                            current_state = "NLC_night_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            #Macros.Mode1_macro(root, t*timestep+relativeTime, pointing_altitude=pointing_altitude, UV_on = True, nadir_on = True, comment = comment)
                            CCD_settings['CCD_48']['TEXPMS'] = TEXPMS_UV
                            CCD_settings['CCD_64']['TEXPMS'] = TEXPMS_nadir
                            Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                                   pointing_altitude=pointing_altitude, comment = comment)
                            
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Logger.debug('')
                            #Mode1_macro(root,str(t+relativeTime),pointing_altitude, comment = comment)
                            
                            
                            
                            
                #Check if night or day#            
                if( sun_angle[t] < MATS_nadir_eclipse_angle ):
                    
                    #Check latitude
                    if( abs(lat_LP[t]) < lat and current_state != "NLC_day_UV_off"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( (sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle) or
                           (abs(lat_LP[t]) < lat and abs(lat_LP[t-1]) > lat) ):
                            
                            Logger.debug('')
                            current_state = "NLC_day_UV_off"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            #Macros.Mode1_macro(root, t*timestep+relativeTime, pointing_altitude=pointing_altitude, UV_on = False, nadir_on = False, comment = comment)
                            CCD_settings['CCD_48']['TEXPMS'] = 0
                            CCD_settings['CCD_64']['TEXPMS'] = 0
                            Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                                   pointing_altitude=pointing_altitude, comment = comment)
                            
                            
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Logger.debug('')
                            #IR_day(root,str(t+relativeTime),pointing_altitude, comment = comment)
                            
                            
                        
                        
                    #Check latitude
                    if( abs(lat_LP[t]) > lat and current_state != "NLC_day_UV_on"):
                        
                        #Check dusk/dawn and latitude boundaries
                        if( (sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle) or
                           (abs(lat_LP[t]) > lat and abs(lat_LP[t-1]) < lat) ):
                            
                            Logger.debug('')
                            current_state = "NLC_day_UV_on"
                            comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                            #Macros.Mode1_macro(root, t*timestep+relativeTime, pointing_altitude=pointing_altitude, UV_on = True, nadir_on = False, comment = comment)
                            CCD_settings['CCD_48']['TEXPMS'] = TEXPMS_UV
                            CCD_settings['CCD_64']['TEXPMS'] = 0
                            Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                                   pointing_altitude=pointing_altitude, comment = comment)
                            
                            
                            Logger.debug(current_state)
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                            Logger.debug('')
                            #Mode1_macro(root,str(t+relativeTime),pointing_altitude, comment = comment)
                            
                            
                
                
                ############### End of SCI-mode operation planner #################
                
    

#######################################################################################

def XML_generator_Mode2(root, date, duration, relativeTime, params = {}):
    """Mode2, Operational_Limb_Pointing_macro
    
    Simulates MATS to be able to schedule commands in the XML-file.
    Look at fixed limb altitude in operational mode.
    High-resolution IR binning. 
    Stop/Start Nadir at dusk/dawn below MATS.
    
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('HighResIR')
    settings = OPT_Config_File.Mode1_2_settings()
    #Timeline_settings = OPT_Config_File.Timeline_settings()
    Timeline_settings = _Globals.Timeline_settings
    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos
    
    params = params_checker(params,settings)
    
    timestep = params['timestep']
    TEXPMS_nadir = CCD_settings['CCD_64']['TEXPMS']
    
    log_timestep = params['log_timestep']
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    Sun = ephem.Sun(date)
    MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
    
    "Pre-allocate space"
    sun_angle = zeros((duration,1))
    
    
    R_mean = 6371000
    pointing_altitude = Timeline_settings['LP_pointing_altitude']
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+pointing_altitude))/pi*180 + 90
    Logger.debug('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(int(duration/timestep)):
        
        
        current_time = ephem.Date(date+ephem.second*timestep*t)
        
        MATS.compute(current_time, epoch = '2000/01/01 11:58:55.816')
        
        Sun.compute(current_time, '2000/01/01 11:58:55.816')
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
                #Macros.Mode1_macro(root,t*timestep+relativeTime, pointing_altitude=pointing_altitude, nadir_on = True, comment = comment)
                CCD_settings['CCD_64']['TEXPMS'] = TEXPMS_nadir
                Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                       pointing_altitude=pointing_altitude, comment = comment)
                
            elif( sun_angle[t] < MATS_nadir_eclipse_angle):
                current_state = "IR_day"
                comment = current_state+': '+str(params)
                #Macros.Mode1_macro(root,t*timestep+relativeTime, pointing_altitude=pointing_altitude, nadir_on = False, comment = comment)
                CCD_settings['CCD_64']['TEXPMS'] = 0
                Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                       pointing_altitude=pointing_altitude, comment = comment)
        
        ############# End of Initial Mode setup ###################################
        
        
        
        if(t != 0):
        ####################### SCI-mode Operation planner ################
            
            
           
            #Check if night or day
            if( sun_angle[t] > MATS_nadir_eclipse_angle and current_state != "IR_night"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] > MATS_nadir_eclipse_angle and sun_angle[t-1] < MATS_nadir_eclipse_angle) ):
                    
                    Logger.debug('')
                    current_state = "IR_night"
                    comment = current_state+': '+str(params)
                    #Macros.Mode1_macro(root, t*timestep+relativeTime, pointing_altitude=pointing_altitude, nadir_on = True, comment = comment)
                    CCD_settings['CCD_64']['TEXPMS'] = TEXPMS_nadir
                    Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                           pointing_altitude=pointing_altitude, comment = comment)
                    
                    Logger.debug('current_time: '+str(current_time))
                    Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                    Logger.debug('')
                    
                    
            #Check if night or day            
            if( sun_angle[t] < MATS_nadir_eclipse_angle and current_state != "IR_day"):
                
                #Check dusk/dawn boundaries and if NLC is active
                if( (sun_angle[t] < MATS_nadir_eclipse_angle and sun_angle[t-1] > MATS_nadir_eclipse_angle) ):
                    
                    Logger.debug('')
                    current_state = "IR_day"
                    comment = current_state+': '+str(params)
                    #Macros.Mode1_macro(root, t*timestep+relativeTime, pointing_altitude=pointing_altitude, nadir_on = False, comment = comment)
                    CCD_settings['CCD_64']['TEXPMS'] = 0
                    Macros.Operational_Limb_Pointing_macro(root, t*timestep+relativeTime, CCD_settings, 
                                                           pointing_altitude=pointing_altitude, comment = comment)
                    
                    Logger.debug('current_time: '+str(current_time))
                    Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                    Logger.debug('')
                    
                    
                    
                 
        ############### End of SCI-mode operation planner #################
    
    

################################################################################################



def XML_generator_Mode100(root, date, duration, relativeTime, params = {}):
    """ Mode100, Operational_Limb_Pointing_macro
    
    Successively point at altitudes from X-Y in Operational Mode in intervals of Z with increasing Exposure Times.
    Where X is *pointing_altitude_from*, Y is *pointing_altitude_to, and Z is *pointing_altitude_interval*.
    All defined in OPT_Config_File.Mode100_settings. 
    BinnedCalibration.
    
    """
    
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
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
    ExpTimeUV = params['Exp_Time_UV']
    ExpTimeIR = params['Exp_Time_IR']
    ExpTime_step = params['ExpTime_step']
    
    number_of_altitudes = int( abs( (pointing_altitude_to - pointing_altitude_from) / pointing_altitude_interval +1 ) )
    pointing_altitudes = [pointing_altitude_from + x*pointing_altitude_interval for x in range(number_of_altitudes)]
    
    #Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    initial_relativeTime = relativeTime
    duration_flag = 0
    x = 0
    "Schedule macros for steadily increasing pointing altitudes and exposure times"
    for pointing_altitude in pointing_altitudes:
        mode_relativeTime = relativeTime - initial_relativeTime
        CCD_settings['CCD_48']['TEXPMS'] = ExpTimeUV + x * ExpTime_step
        CCD_settings['CCD_9']['TEXPMS'] = ExpTimeIR + x * ExpTime_step
        CCD_settings['CCD_6']['TEXPMS'] = ExpTimeIR + x * ExpTime_step
        
        if(mode_relativeTime > duration and duration_flag == 0):
            Logger.warning('Warning!! The scheduled time for '+Mode_name+' has ran out.')
            #input('Enter anything to ackknowledge and continue:\n')
            duration_flag = 1
        
        #relativeTime = Mode_macro(root, round(relativeTime,2), CCD_settings, 
        #                          pointing_altitude = pointing_altitude, comment = comment)
        relativeTime = Macros.Operational_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, 
                                  pointing_altitude = pointing_altitude, comment = comment)
        
        relativeTime = relativeTime + params['pointing_duration']
        
        x += 1



##############################################################################################

##############################################################################################



def XML_generator_Mode110(root, date, duration, relativeTime, params = {}):
    """Mode110, Operational_Sweep_macro
    
    Scan atmosphere from X to Y altitudes with a rate of Z.
    Where X, Y, Z is defined in OPT_Config_File.Mode110_settings.
    BinnedCalibration.
    
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    settings = OPT_Config_File.Mode110_settings()
    
    params = params_checker(params,settings)
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude_from = params['pointing_altitude_from']
    pointing_altitude_to = params['pointing_altitude_to']
    sweep_rate = params['sweep_rate']
    
    #Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Macros.Operational_Sweep_macro(root, round(relativeTime,2), CCD_settings, 
               pointing_altitude_from = pointing_altitude_from, 
               pointing_altitude_to = pointing_altitude_to, sweep_rate = sweep_rate, 
               comment = comment)


#######################################################################################################

def XML_generator_Mode12X(root, date, duration, relativeTime, 
                       params, CCD_settings):
    """Mode12X, where X is 1,2,3....
    
    Snapshot_Inertial_macro
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir.
    
    """
    
    Timeline_settings = _Globals.Timeline_settings
    
    Mode_name = sys._getframe(1).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    
    Snapshot_relativeTime = relativeTime + params['freeze_start'] + params['SnapshotTime']
    
    FreezeTime = utc_to_onboardTime(freeze_start_utc)
    
    FreezeDuration = params['freeze_duration']
    
    pointing_altitude = params['pointing_altitude']
    
    SnapshotSpacing = params['SnapshotSpacing']
    
    Logger.debug('freeze_start_utc: '+str(freeze_start_utc))
    Logger.debug('FreezeTime [GPS]: '+ str(FreezeTime))
    Logger.debug('FreezeDuration: '+str(FreezeDuration))
    
    Macros.Snapshot_Inertial_macro(root, round(relativeTime,2), CCD_settings, FreezeTime=FreezeTime, 
                     FreezeDuration = FreezeDuration, pointing_altitude = pointing_altitude, LP_pointing_altitude = Timeline_settings['LP_pointing_altitude'], 
                     SnapshotSpacing = SnapshotSpacing, Snapshot_relativeTime = Snapshot_relativeTime, comment = comment)




################################################################################################


def XML_generator_Mode120(root, date, duration, relativeTime, 
                       params = {}):
    """Mode120
    
    Snapshot_Inertial_macro
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir.
    Used for star calibration.
    Full CCD readout.
    
    """
    
    settings = OPT_Config_File.Mode120_settings()
    params = params_checker(params,settings)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    XML_generator_Mode12X(root, date, duration, relativeTime, 
                                  params = params, CCD_settings = CCD_settings)


################################################################################################


##############################################################################################


def XML_generator_Mode121(root, date, duration, relativeTime, 
                       params = {}):
    """Mode121
    
    Snapshot_Inertial_macro
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir.
    Full CCD readout.
    
    """
    
    settings = OPT_Config_File.Mode121_settings()
    params = params_checker(params,settings)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    XML_generator_Mode12X(root, date, duration, relativeTime, 
                       params = params, CCD_settings = CCD_settings)


############################################################################################




def XML_generator_Mode122(root, date, duration, relativeTime, 
                       params = {}):
    """Mode122
    
    Snapshot_Inertial_macro
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir.
    BinnedCalibration.
    """
    
    settings = OPT_Config_File.Mode122_settings()
    params = params_checker(params,settings)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    ExpTimeUV= params['Exp_Time_UV']
    ExpTimeIR = params['Exp_Time_IR']
    CCD_settings['CCD_48']['TEXPMS'] = ExpTimeUV
    CCD_settings['CCD_9']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCD_6']['TEXPMS'] = ExpTimeIR
    
    XML_generator_Mode12X(root, date, duration, relativeTime, 
                        params = params, CCD_settings = CCD_settings)
    

################################################################################################

############################################################################################




def XML_generator_Mode123(root, date, duration, relativeTime, 
                       params = {}):
    """Mode123
    
    Snapshot_Inertial_macro
    Stare at a point in inertial reference frame and take one Snapshot with each CCD except nadir.
    Low pixel binning.
    
    """
    
    settings = OPT_Config_File.Mode123_settings()
    params = params_checker(params,settings)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('LowPixel')
    ExpTimeUV= params['Exp_Time_UV']
    ExpTimeIR = params['Exp_Time_IR']
    CCD_settings['CCD_48']['TEXPMS'] = ExpTimeUV
    CCD_settings['CCD_9']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCD_6']['TEXPMS'] = ExpTimeIR
    
    XML_generator_Mode12X(root, date, duration, relativeTime, 
                        params = params, CCD_settings = CCD_settings)
    



##############################################################################################


def XML_generator_Mode124(root, date, duration, relativeTime, 
                       params = {}):
    """Mode124
    
    Snapshot_Inertial_macro
    Stare at a point in inertial reference frame and take one Snapshot with each CCD except Nadir. 
    Used for moon calibration.
    FullReadout
    """
    
    
    settings = OPT_Config_File.Mode124_settings()
    params = params_checker(params,settings)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    XML_generator_Mode12X(root, date, duration, relativeTime, 
                        params = params, CCD_settings = CCD_settings)

##############################################################################################



################################################################################################


def XML_generator_Mode130(root, date, duration, relativeTime, 
                       params = {}):
    """Mode130
    
    Snapshot_Limb_Pointing_macro
    Look at fixed limb altitude and take Snapshots with all CCD except nadir.
    Full CCD readout.
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    settings = OPT_Config_File.Mode130_settings()
    
    params = params_checker(params,settings)
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    SnapshotSpacing = params['SnapshotSpacing']
    
    #Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Macros.Snapshot_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, pointing_altitude = pointing_altitude, 
               SnapshotSpacing = SnapshotSpacing, comment = comment)



##############################################################################################

def XML_generator_Mode131(root, date, duration, relativeTime, 
                       params = {}):
    """Mode131, FullReadout_Operational_Limb_Pointing_macro
    
    Look at fixed limb altitude in operational mode.
    Full CCD readout.
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    settings = OPT_Config_File.Mode131_settings()
    
    params = params_checker(params,settings)
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    TEXPIMS = params['Exposure_Interval']
    
    Macros.FullReadout_Operational_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, 
                                                       TEXPIMS = TEXPIMS, pointing_altitude = pointing_altitude, comment = comment)


################################################################################################

##############################################################################################

def XML_generator_Mode132_133(root, date, duration, relativeTime, 
                       params, CCD_settings):
    """Mode132, Mode133
    
    Operational_Limb_Pointing_macro
    Look at fixed limb altitude in operational mode with changing exposure times.
    """
    
    Mode_name = sys._getframe(1).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    
    for ExpTimeUV,ExpTimeIR in zip( params['Exp_Times_UV'], params['Exp_Times_IR'] ):
        
        CCD_settings['CCD_48']['TEXPMS'] = ExpTimeUV
        CCD_settings['CCD_9']['TEXPMS'] = ExpTimeIR
        CCD_settings['CCD_6']['TEXPMS'] = ExpTimeIR
        relativeTime = Macros.Operational_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, 
                                  pointing_altitude = pointing_altitude, comment = comment)
        
        relativeTime = relativeTime + params['session_duration']
        

################################################################################################




def XML_generator_Mode132(root, date, duration, relativeTime, 
                       params = {}):
    """Mode132
    
    Operational_Limb_Pointing_macro
    Look at fixed limb altitude in operational mode with changing exposure times.
    BinnedCalibration.
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    settings = OPT_Config_File.Mode132_settings()
    
    params = params_checker(params,settings)
    
    XML_generator_Mode132_133(root, date, duration, relativeTime, 
                       params = params, CCD_settings = CCD_settings)



##############################################################################################

################################################################################################



def XML_generator_Mode133(root, date, duration, relativeTime, 
                       params = {}):
    """Mode133, Operational_Limb_Pointing_macro
    
    Look at fixed limb altitude in operational mode with changing exposure times.
    Low pixel binning.
    
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('LowPixel')
    settings = OPT_Config_File.Mode133_settings()
    
    params = params_checker(params,settings)
    
    XML_generator_Mode132_133(root, date, duration, relativeTime, 
                       params = params, CCD_settings = CCD_settings)
        



##############################################################################################

##############################################################################################

def XML_generator_Mode160(root, date, duration, relativeTime, 
                       params = {}):
    """Mode160, Operational_Limb_Pointing_macro
    
    Look at fixed limb altitude in Operational Mode.
    CustomBinning.
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('CustomBinning')
    settings = OPT_Config_File.Mode160_settings()
    
    params = params_checker(params,settings)
    
    Mode_name = sys._getframe(0).f_code.co_name.replace('XML_generator_','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    
    Macros.Operational_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings,
                                pointing_altitude = pointing_altitude, comment = comment)


################################################################################################

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





