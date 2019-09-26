# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 12:34:33 2019

Generates and calculates parameters for each Test, and converts them to strings,
then calls for macros, which will generate commands in the XML-file.

Functions on the form "X", where the last X is any Test:
    Arguments:
        root =  XML tree structure. Main container object for the ElementTree API. lxml.etree.Element class \n
        date = Starting date of the Test. On the form of the ephem.Date class. \n
        duration = The duration of the Test [s] as an integer class. \n
        relativeTime = The starting time of the Test with regard to the start of the timeline [s] as an integer class. \n
        params = Dictionary containing the parameters of the Test given in the Science_Mode_Timeline. \n
    
    Returns:
        None

When creating new Test functions it is crucial that the function name is
Test_name, where Test_name is the same as the string used in the Science Mode Timeline

@author: David
"""

import ephem, logging, sys, importlib, skyfield.api
from pylab import dot, arccos, zeros, pi, sin, cos, arctan, cross, norm, sqrt

from OPT import _Globals, _Library, _MATS_coordinates

OPT_Config_File = importlib.import_module(_Globals.Config_File)
#from OPT_Config_File import Logger_name, Timeline_settings, getTLE

from .Macros_Commands import Macros, Commands

Logger = logging.getLogger(OPT_Config_File.Logger_name())




def Limb_functional_test(root, date, duration, relativeTime, params = {'ExpTimes': [1000, 2000, 4000, 8000, 16000]}):
    """Limb_functional_test. 
    
    Schedules Limb_functional_test with defined parameters and simulates MATS propagation from TLE.
    Scheduling of all daylight and nighttime commands are separated timewise and all commands for one of the two is scheduled first.
    """
    
    
    
    Logger.debug('params from Science Mode List: '+str(params))
    #params = params_checker(params,Mode=X=_settings)
    
    log_timestep = 500
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    TLE = OPT_Config_File.getTLE()
    Timeline_settings = _Globals.Timeline_settings
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    duration_flag = 0
    
    JPEGQs = ['101','95']
    altitudes = [50000,70000,90000,110000,130000,160000,200000]
    ExpTimes = params['ExpTimes']
    SnapshotSpacing = 5
    
    R_mean = 6371
    Extra_Height_To_Make_Sure_it_is_Nighttime_Daytime = 50
    
    #lat = params['lat']/180*pi
    lat = 30
    
    "Estimation of the angle [degrees] between the sun and the LP when it enters eclipse"
    LP_Day_angle = arccos(R_mean/(R_mean))/pi*180 + 90
    LP_Night_angle = arccos(R_mean/(R_mean+Extra_Height_To_Make_Sure_it_is_Nighttime_Daytime))/pi*180 + 90
    
    
    Logger.debug('')
    Logger.debug('LP_Day_angle : '+str(LP_Day_angle))
    Logger.debug('LP_Night_angle : '+str(LP_Night_angle))
    
    
    initial_relativeTime = relativeTime
    
    for mode in ['Day', 'Night']:
        
        "Altitudes that defines the LP"
        for altitude in altitudes:
            
            for JPEGQ in JPEGQs:
                CCD_settings['JPEGQ'] = JPEGQ
                
                for ExpTime in ExpTimes:
                    
                    CCD_settings['TEXPMS'] = ExpTime
                    
                    ############################################################################
                    ########################## Orbit simulator #################################
                    ############################################################################
                    
                    
                    "Pre-allocate space"
                    """
                    r_MATS_ECEF = zeros((duration,3))
                    optical_axis_ECEF = zeros((duration,3))
                    optical_axis = zeros((duration,3))
                    r_LP_ECEF = zeros((duration,3))
                    r_LP = zeros((duration,3))
                    
                    r_LP_direction = zeros((duration,3))
                    
                    Normal2V_offset = zeros((duration,3))
                    
                    lat_MATS = zeros((duration,1))
                    lat_LP = zeros((duration,1))
                    sun_angle = zeros((duration,1))
                    r_MATS = zeros((duration,3))
                    """
                    
                    timestep = 4
                    t=0
                    
                    MATS_skyfield = skyfield.api.EarthSatellite(TLE[0], TLE[1])
                    
                    
                    "Calculate the current angle between MATS and the Sun and the latitude of the LP"
                    "and Loop until it is either day or night and the right latitude"
                    while(True):
                        
                        mode_relativeTime = relativeTime - initial_relativeTime
                        current_time = ephem.Date(date+ephem.second*mode_relativeTime)
                        current_time_datetime = current_time.datetime()
                        
                        if(mode_relativeTime > duration and duration_flag == 0):
                            Logger.warning('Warning!! The scheduled time for the Test has ran out.')
                            #input('Enter anything to continue:\n')
                            duration_flag = 1
                        
                        if( t*timestep % log_timestep == 0):
                            LogFlag = True
                        else:
                            LogFlag = False
                        
                        Satellite_dict = _Library.Satellite_Simulator( 
                                    MATS_skyfield, current_time, Timeline_settings, altitude/1000, LogFlag, Logger )
                        
                        r_MATS = Satellite_dict['Position [km]']
                        lat_MATS = Satellite_dict['Latitude [degrees]']
                        lat_LP = Satellite_dict['EstimatedLatitude_LP [degrees]']
                        Normal2V_offset = Satellite_dict['Normal2V_offset']
                        pitch = Satellite_dict['Pitch [degrees]']
                        
                        "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
                        rot_mat = _Library.rot_arbit((pitch-90)/180*pi, Normal2V_offset)
                        r_LP_direction = rot_mat @ r_MATS
                        
                        
                        
                        """
                        r_MATS_ECEF[t,0], r_MATS_ECEF[t,1], r_MATS_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                                    r_MATS[t,0], r_MATS[t,1], r_MATS[t,2], current_time_datetime)
                        
                        optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2] = _MATS_coordinates.eci2ecef(
                                optical_axis[t,0], optical_axis[t,1], optical_axis[t,2], current_time_datetime)
                        
                        
                        r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2] = _MATS_coordinates.ecef2tanpoint(r_MATS_ECEF[t][0]*1000, r_MATS_ECEF[t][1]*1000, r_MATS_ECEF[t][2]*1000, 
                                                   optical_axis_ECEF[t,0], optical_axis_ECEF[t,1], optical_axis_ECEF[t,2])
                        
                        r_LP[t,0], r_LP[t,1], r_LP[t,2] = _MATS_coordinates.ecef2eci( r_LP_ECEF[t,0], r_LP_ECEF[t,1], r_LP_ECEF[t,2], 
                                                       current_time_datetime)
                        
                        """
                        sun_angle = _Library.SunAngle( r_LP_direction, current_time)
                        
                        if( LogFlag == True):
                            Logger.debug('sun_angle: '+str(sun_angle))
                        
                        if( (sun_angle < LP_Day_angle and abs(lat_LP) <= lat and mode == 'Day' ) or 
                           (sun_angle > LP_Night_angle and abs(lat_LP) <= lat and mode == 'Night' )):
                            
                            Logger.debug('!!Break of Loop!!')
                            Logger.debug('Loop Counter (t): '+str(t))
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle))
                            Logger.debug('mode: '+str(mode))
                            Logger.debug('')
                            
                            Mode_name = sys._getframe(0).f_code.co_name
                            comment = Mode_name+', '+str(date)+', '+str(mode)
                            break
                        
                        
                            
                        "Increase Loop counter"
                        t= t+1
                        
                        "Timestep for propagation of MATS"
                        relativeTime = round(relativeTime + timestep,2)
                        
                            
                    ############################################################################
                    ########################## End of Orbit simulator ##########################
                    ############################################################################
                    
                    Logger.debug('Limb_functional_test_macro: relativeTime = '+str(relativeTime)+', pointing_altitude = '+str(altitude)+
                                ', ExpTime = '+str(ExpTime)+', JPEGQ = '+str(JPEGQ))
                    
                    relativeTime = Macros.Snapshot_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, pointing_altitude = altitude, 
                                        SnapshotSpacing = SnapshotSpacing, comment = comment)
                    
                    #relativeTime = Macros.Limb_functional_test_macro(root = root, relativeTime = str(relativeTime), 
                    #                           pointing_altitude = str(altitude), ExpTime = str(ExpTime), 
                    #                           JPEGQ = JPEGQ, comment=comment)
                    
                    "Postpone next command until at least the end of ExpTime"
                    relativeTime = round(relativeTime + ExpTime/1000,2)
                
    

#############################################################################################

#############################################################################################



def Photometer_test_1(root, date, duration, relativeTime, params = {'ExpTimes': [1000,2000,4000,8000,16000]}):
    """Photometer_test_1
    
    Sets the payload in operational mode and then cycles PM settings as defined in the mode.
    """
    
    
    #params = params_checker(params,Mode=X=_settings)
    
    
    Logger.debug('')
    
    ExpTimes = params['ExpTimes']
    
    initial_relativeTime = relativeTime
    
    Photometer_test_1_duration = duration
    
    relativeTime = Commands.TC_pafMode(root, relativeTime, mode = 1)
    
    while( True ):
        mode_relativeTime = round(relativeTime - initial_relativeTime,2)
        
        if( mode_relativeTime >= Photometer_test_1_duration):
            Logger.info('End of Photometer_test_1')
            break
            
        for ExpTime in ExpTimes:
            ExpInt = ExpTime +1000
            
            Mode_name = sys._getframe(0).f_code.co_name
            comment = Mode_name+', '+str(date)+', '+str(params)
            
            Logger.debug('Photometer_test_1_macro: relativeTime = '+str(relativeTime)+
                                ', ExpTime = '+str(ExpTime)+', ExpInt = '+str(ExpInt))
            Commands.TC_pafPM(root, relativeTime = relativeTime, TEXPMS = ExpTime, TEXPIMS = ExpInt, comment = comment)
            
            "Postpone Next PM settings"
            relativeTime = relativeTime + 120
            




##############################################################################################

##############################################################################################



def Nadir_functional_test(root, date, duration, relativeTime, params = {'ExpTimes': [1000,2000,4000,8000,16000]}):
    """Nadir_functional_test
    """
    
    
    Logger.debug('params from Science Mode List: '+str(params))
    #params = params_checker(params,Mode=X=_settings)
    
    Timeline_settings = _Globals.Timeline_settings
    
    log_timestep = 100
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    duration_flag = 0
    
    JPEGQs = ['101','95']
    
    altitude = Timeline_settings['LP_pointing_altitude']
    
    ExpTimes = params['ExpTimes']
    
    initial_relativeTime = relativeTime
    
    for mode in ['Day', 'Night']:
        
        for JPEGQ in JPEGQs:
            
            for ExpTime in ExpTimes:
                
                ############################################################################
                ########################## Orbit simulator #################################
                ############################################################################
                
                Sun = ephem.Sun(date)
                MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
                
                "Pre-allocate space"
                lat_MATS = zeros((duration,1))
                sun_angle = zeros((duration,1))
                altitude_MATS = zeros((duration,1))
                a_ra_MATS = zeros((duration,1))
                a_dec_MATS = zeros((duration,1))
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
                
                Logger.debug('')
                Logger.debug('nadir_eclipse_angle : '+str(nadir_eclipse_angle))
                
                t=0
                timestep = 4
                
                "Calculate the current angle between MATS and the Sun"
                "and Loop until it is either day or night and the right latitude"
                while(True):
                    
                    mode_relativeTime = relativeTime - initial_relativeTime
                    current_time = ephem.Date(date+ephem.second*mode_relativeTime)
                    
                    if(mode_relativeTime > duration and duration_flag == 0):
                        Logger.warning('Warning!! The scheduled time for the Test has ran out.')
                        #input('Enter anything to continue:\n')
                        duration_flag = 1
                    
                    MATS.compute(current_time)
                    
                    (lat_MATS[t],altitude_MATS[t],a_ra_MATS[t],a_dec_MATS[t])= (
                    MATS.sublat,MATS.elevation/1000,MATS.a_ra,MATS.a_dec)
                    
                    z_MATS[t] = sin(a_dec_MATS[t])*(altitude_MATS[t]+R_mean)
                    x_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R_mean)* cos(a_ra_MATS[t])
                    y_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R_mean)* sin(a_ra_MATS[t])
                   
                    r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
                    
                    sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
                    
                    
                    if( t*timestep % log_timestep == 0 == 0 or t == 1):
                        Logger.debug('')
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                        Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                        Logger.debug('mode: '+str(mode))
                        Logger.debug('')
                    
                    if( (sun_angle[t] < nadir_eclipse_angle and abs(lat_MATS[t]) <= lat and mode == 'Day' ) or 
                       (sun_angle[t] > nadir_eclipse_angle and abs(lat_MATS[t]) <= lat and mode == 'Night' )):
                        
                        Logger.debug('!!Break of Loop!!')
                        Logger.debug('Loop Counter (t): '+str(t))
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                        Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                        Logger.debug('mode: '+str(mode))
                        
                        Logger.debug('')
                        break
                        
                        
                    "Increase Loop counter"
                    t= t+1
                    
                    "Timestep for propagation of MATS"
                    relativeTime = round(relativeTime + timestep,1)
                    
                        
                ############################################################################
                ########################## End of Orbit simulator ##########################
                ############################################################################
                
                Logger.debug('Limb_functional_test_macro: relativeTime = '+str(relativeTime)+', pointing_altitude = '+str(altitude)+
                            ', ExpTime = '+str(ExpTime)+', JPEGQ = '+str(JPEGQ))
                
                relativeTime = Macros.Nadir_functional_test_macro(root = root, relativeTime = str(relativeTime), 
                                           pointing_altitude = str(altitude), ExpTime = str(ExpTime), 
                                           JPEGQ = JPEGQ)
                
                
                "Postpone next command until at least the end of ExpTime"
                relativeTime = round(float(relativeTime) + ExpTime/1000,2)



#######################################################################################################




'''
def Limb_functional_test(root, date, duration, relativeTime, params = {'ExpTimes': [1,2,4,8,16]}):
    """Limb_functional_test. 
    
    Schedules Limb_functional_test with defined parameters and simulates MATS propagation from TLE.
    Scheduling of all daylight and nighttime commands are separated timewise and all commands for one of the two is scheduled first.
    """
    
    
    
    Logger.debug('params from Science Mode List: '+str(params))
    #params = params_checker(params,Mode=X=_settings)
    
    log_timestep = 500
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    duration_flag = 0
    
    JPEGQs = ['101','95']
    
    ExpTimes = params['ExpTimes']
    
    initial_relativeTime = relativeTime
    
    for mode in ['Day', 'Night']:
        
        "Altitudes that defines the LP"
        for altitude in [50000,70000,90000,110000,130000,160000,200000]:
            
            for JPEGQ in JPEGQs:
                
                for ExpTime in ExpTimes:
                    
                    ############################################################################
                    ########################## Orbit simulator #################################
                    ############################################################################
                    
                    Sun = ephem.Sun(date)
                    MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
                    
                    "Pre-allocate space"
                    lat_MATS = zeros((duration,1))
                    lat_LP = zeros((duration,1))
                    sun_angle = zeros((duration,1))
                    altitude_MATS = zeros((duration,1))
                    a_ra_MATS = zeros((duration,1))
                    a_dec_MATS = zeros((duration,1))
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
                    
                    "Estimation of the angle [degrees] between the sun and the LP when it enters eclipse"
                    LP_eclipse_angle = arccos(R_mean/(R_mean+altitude_km))/pi*180 + 90
                    
                    Logger.debug('')
                    Logger.debug('LP_eclipse_angle : '+str(LP_eclipse_angle))
                    
                    timestep = 4
                    t=0
                    
                    "Calculate the current angle between MATS and the Sun and the latitude of the LP"
                    "and Loop until it is either day or night and the right latitude"
                    while(True):
                        
                        mode_relativeTime = relativeTime - initial_relativeTime
                        current_time = ephem.Date(date+ephem.second*mode_relativeTime)
                        
                        if(mode_relativeTime > duration and duration_flag == 0):
                            Logger.warning('Warning!! The scheduled time for the Test has ran out.')
                            #input('Enter anything to continue:\n')
                            duration_flag = 1
                        
                        MATS.compute(current_time)
                        
                        
                        (lat_MATS[t],altitude_MATS[t],a_ra_MATS[t],a_dec_MATS[t])= (
                        MATS.sublat,MATS.elevation/1000,MATS.a_ra,MATS.a_dec)
                        
                        z_MATS[t] = sin(a_dec_MATS[t])*(altitude_MATS[t]+R_mean)
                        x_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R_mean)* cos(a_ra_MATS[t])
                        y_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R_mean)* sin(a_ra_MATS[t])
                       
                        r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
                        
                        orbangle_between_LP_MATS_array[t]= arccos((R_mean+altitude/1000)/(R_mean+altitude_MATS[t]))/pi*180
                        orbangle_between_LP_MATS = orbangle_between_LP_MATS_array[t][0]
                        
                        Sun.compute(current_time)
                        
                        (g_ra_Sun[t],g_dec_Sun[t])= (Sun.g_ra,Sun.g_dec)
                        
                        z_Sun[t] = sin(g_dec_Sun[t])
                        x_Sun[t] = cos(g_dec_Sun[t])* cos(g_ra_Sun[t])
                        y_Sun[t] = cos(g_dec_Sun[t])* sin(g_ra_Sun[t])
                       
                        r_Sun_direction[t,0:3] = [x_Sun[t], y_Sun[t], z_Sun[t]]
                        
                        
                        if( t != 0):
                            "Vector normal to the orbital plane of MATS"
                            normal_orbital[t,0:3] = cross(r_MATS[t],r_MATS[t-1])
                            normal_orbital[t,0:3] = normal_orbital[t,0:3] / norm(normal_orbital[t,0:3])
                            
                            "Rotate 'vector to MATS', to represent pointing direction, includes vertical offset change (Parallax is negligable)"
                            rot_mat = _Library.rot_arbit(orbangle_between_LP_MATS/180*pi, normal_orbital[t,0:3])
                            r_LP_direction[t,0:3] = rot_mat @ r_MATS[t]
                            
                            "Estimate latitude by calculating angle between xy-plane vector and z-vector"
                            r_LP__direction_xy = sqrt(r_LP_direction[t,0]**2+r_LP_direction[t,1]**2)
                            lat_LP[t] = arctan(r_LP_direction[t,2]/r_LP__direction_xy)
                            
                            "Calculate angle between LP and the Sun"
                            sun_angle[t] = arccos(dot(r_Sun_direction[t,0:3],r_LP_direction[t,0:3])/norm(r_LP_direction[t,0:3]))/pi*180
                            
                            
                            if( (sun_angle[t] < LP_eclipse_angle and abs(lat_LP[t]) <= lat and mode == 'Day' ) or 
                               (sun_angle[t] > LP_eclipse_angle and abs(lat_LP[t]) <= lat and mode == 'Night' )):
                                
                                Logger.debug('!!Break of Loop!!')
                                Logger.debug('Loop Counter (t): '+str(t))
                                Logger.debug('current_time: '+str(current_time))
                                Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                                Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                                Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                                Logger.debug('mode: '+str(mode))
                                Logger.debug('')
                                
                                Mode_name = sys._getframe(0).f_code.co_name
                                comment = Mode_name+', '+str(date)+', '+str(params)
                                break
                            
                            elif( t*timestep % log_timestep == 0 or t == 1):
                                Logger.debug('')
                                Logger.debug('current_time: '+str(current_time))
                                Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                                Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]/pi*180))
                                Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                                Logger.debug('mode: '+str(mode))
                                Logger.debug('')
                            
                            
                        "Increase Loop counter"
                        t= t+1
                        
                        "Timestep for propagation of MATS"
                        relativeTime = round(relativeTime + timestep,2)
                        
                            
                    ############################################################################
                    ########################## End of Orbit simulator ##########################
                    ############################################################################
                    
                    Logger.debug('Limb_functional_test_macro: relativeTime = '+str(relativeTime)+', pointing_altitude = '+str(altitude)+
                                ', ExpTime = '+str(ExpTime)+', JPEGQ = '+str(JPEGQ))
                    
                    relativeTime = Macros.Limb_functional_test_macro(root = root, relativeTime = str(relativeTime), 
                                               pointing_altitude = str(altitude), ExpTime = str(ExpTime), 
                                               JPEGQ = JPEGQ, comment=comment)
                    
                    "Postpone next command until at least the end of ExpTime"
                    relativeTime = round(float(relativeTime) + ExpTime/1000,2)
                
    
'''
#############################################################################################


'''
def Photometer_test_1(root, date, duration, relativeTime, params = {'ExpTimes': [1,2,4,8,16]}):
    """Photometer_test_1
    """
    
    
    #params = params_checker(params,Mode=X=_settings)
    
    """
    MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
    MATS.compute(date)
    MATS_altitude = MATS.elevation/1000
    U = 398600.4418 #Earth gravitational parameter
    
    #Semi-Major axis of MATS, assuming circular orbit
    #MATS_p = norm(r_MATS[t,0:3])
    MATS_p = 2*(MATS_altitude+6371)
    
    #Orbital Period of MATS
    MATS_P = 2*pi*sqrt(MATS_p**3/U)
    """
    
    Logger.debug('')
    
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
            
            Mode_name = sys._getframe(0).f_code.co_name
            comment = Mode_name+', '+str(date)+', '+str(params)
            
            Logger.debug('Photometer_test_1_macro: relativeTime = '+str(relativeTime)+
                                ', ExpTime = '+str(ExpTime)+', ExpInt = '+str(ExpInt))
            relativeTime = Macros.Photometer_test_1_macro(root, relativeTime = str(relativeTime), ExpTime = str(ExpTime), ExpInt = str(ExpInt), comment = comment)
            
            "Postpone Next PM settings"
            relativeTime = round(float(relativeTime) + 120-OPT_Config_File.Timeline_settings()['CMD_separation'],2)
            
'''



##############################################################################################


##############################################################################################
'''


def Nadir_functional_test(root, date, duration, relativeTime, params = {'ExpTimes': [1,2,4,8,16]}):
    """Nadir_functional_test
    """
    
    
    Logger.debug('params from Science Mode List: '+str(params))
    #params = params_checker(params,Mode=X=_settings)
    
    log_timestep = 100
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
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
                MATS = ephem.readtle('MATS', OPT_Config_File.getTLE()[0], OPT_Config_File.getTLE()[1])
                
                "Pre-allocate space"
                lat_MATS = zeros((duration,1))
                sun_angle = zeros((duration,1))
                altitude_MATS = zeros((duration,1))
                a_ra_MATS = zeros((duration,1))
                a_dec_MATS = zeros((duration,1))
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
                
                Logger.debug('')
                Logger.debug('nadir_eclipse_angle : '+str(nadir_eclipse_angle))
                
                t=0
                timestep = 4
                
                "Calculate the current angle between MATS and the Sun"
                "and Loop until it is either day or night and the right latitude"
                while(True):
                    
                    mode_relativeTime = relativeTime - initial_relativeTime
                    current_time = ephem.Date(date+ephem.second*mode_relativeTime)
                    
                    if(mode_relativeTime > duration and duration_flag == 0):
                        Logger.warning('Warning!! The scheduled time for the Test has ran out.')
                        #input('Enter anything to continue:\n')
                        duration_flag = 1
                    
                    MATS.compute(current_time)
                    
                    (lat_MATS[t],altitude_MATS[t],a_ra_MATS[t],a_dec_MATS[t])= (
                    MATS.sublat,MATS.elevation/1000,MATS.a_ra,MATS.a_dec)
                    
                    z_MATS[t] = sin(a_dec_MATS[t])*(altitude_MATS[t]+R_mean)
                    x_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R_mean)* cos(a_ra_MATS[t])
                    y_MATS[t] = cos(a_dec_MATS[t])*(altitude_MATS[t]+R_mean)* sin(a_ra_MATS[t])
                   
                    r_MATS[t,0:3] = [x_MATS[t], y_MATS[t], z_MATS[t]]
                    
                    sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
                    
                    
                    if( t*timestep % log_timestep == 0 == 0 or t == 1):
                        Logger.debug('')
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                        Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                        Logger.debug('mode: '+str(mode))
                        Logger.debug('')
                    
                    if( (sun_angle[t] < nadir_eclipse_angle and abs(lat_MATS[t]) <= lat and mode == 'Day' ) or 
                       (sun_angle[t] > nadir_eclipse_angle and abs(lat_MATS[t]) <= lat and mode == 'Night' )):
                        
                        Logger.debug('!!Break of Loop!!')
                        Logger.debug('Loop Counter (t): '+str(t))
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]/pi*180))
                        Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                        Logger.debug('mode: '+str(mode))
                        
                        Logger.debug('')
                        break
                        
                        
                    "Increase Loop counter"
                    t= t+1
                    
                    "Timestep for propagation of MATS"
                    relativeTime = round(relativeTime + timestep,1)
                    
                        
                ############################################################################
                ########################## End of Orbit simulator ##########################
                ############################################################################
                
                Logger.debug('Limb_functional_test_macro: relativeTime = '+str(relativeTime)+', pointing_altitude = '+str(altitude)+
                            ', ExpTime = '+str(ExpTime)+', JPEGQ = '+str(JPEGQ))
                
                relativeTime = Macros.Nadir_functional_test_macro(root = root, relativeTime = str(relativeTime), 
                                           pointing_altitude = str(altitude), ExpTime = str(ExpTime), 
                                           JPEGQ = JPEGQ)
                
                
                "Postpone next command until at least the end of ExpTime"
                relativeTime = round(float(relativeTime) + ExpTime/1000,2)



#######################################################################################################
'''

