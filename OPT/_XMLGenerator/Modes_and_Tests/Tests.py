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


def All_Tests(root, date, duration, relativeTime, params = ['Limb_functional_test', 'Photometer_test_1', 'CCD_stability_test', 'Nadir_functional_test']):
    """ Runs all the Test functions which has their function name as a string in params.
    
    Allows the tests to be dynamically scheduled.
    
    """
    
    
    
    "Set duration to length of timeline to allow all tests to be scheduled"
    duration = _Globals.Timeline_settings['duration']
    
    if( 'Limb_functional_test' in params):
        relativeTime, date = Limb_functional_test(root, date, duration = duration, relativeTime = relativeTime)
    if( 'Photometer_test_1' in params):
        relativeTime, date = Photometer_test_1(root, date, relativeTime = relativeTime)
    if( 'CCD_stability_test' in params):
        relativeTime, date = CCD_stability_test(root, date, duration = duration, relativeTime = relativeTime)
    if( 'Nadir_functional_test' in params):
        relativeTime, date = Nadir_functional_test(root, date, duration = duration, relativeTime = relativeTime)
    
    
    

def Limb_functional_test(root, date, duration, relativeTime, params = {'ExpTimes': [1000, 2000, 4000, 8000, 16000]}):
    """Limb_functional_test. 
    
    Schedules Limb_functional_test with defined parameters and simulates MATS propagation from TLE.
    Scheduling of all daylight and nighttime commands are separated timewise and all commands for one of the two is scheduled first.
    """
    
    Logger.info('')
    Logger.info('Start of Limb_functional_test')
    
    Logger.debug('params from Science Mode List: '+str(params))
    
    
    log_timestep = 500
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    TLE = OPT_Config_File.getTLE()
    Timeline_settings = _Globals.Timeline_settings
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    duration_flag = 0
    
    JPEGQs = [101,95]
    WDWs = [7, 128]
    altitudes = [50000,70000,90000,110000,130000,160000,200000]
    ExpTimes = params['ExpTimes']
    SnapshotSpacing = 5
    
    R_mean = 6371 #km
    Altitude_defining_night = 45 #km
    Altitude_defining_day = 25 #km
    
    #lat = params['lat']/180*pi
    lat = 30
    
    Mode_name = sys._getframe(0).f_code.co_name
    
    "Estimation of the angle [degrees] between the sun and the LP when it enters eclipse"
    #NightDayAngle = arccos(R_mean/(R_mean+Altitude_defining_night))/pi*180 + 90
    
    NightAngle = arccos(R_mean/(R_mean+Altitude_defining_night))/pi*180 + 90
    DayAngle = arccos(R_mean/(R_mean+Altitude_defining_day))/pi*180 + 90
    
    Logger.debug('')
    Logger.debug('NightAngle : '+str(NightAngle))
    Logger.debug('DayAngle : '+str(DayAngle))
    
    timestep = 4
    t=0
    
    initial_relativeTime = relativeTime
    
    "Consecutively schedule all Macros for day, and then night"
    for mode in ['Day', 'Night']:
        
        "Altitudes that defines the LP"
        for altitude in altitudes:
            
            "Start looping the CCD settings and call for macros"
            for JPEGQ, WDW in zip(JPEGQs, WDWs):
                
                for key in CCD_settings.keys():
                    CCD_settings[key]['JPEGQ'] = JPEGQ
                    CCD_settings[key]['WDW'] = WDW
                
                for ExpTime in ExpTimes:
                    
                    for key in CCD_settings.keys():
                        CCD_settings[key]['TEXPMS'] = ExpTime
                    
                    ############################################################################
                    ########################## Orbit simulator #################################
                    ############################################################################
                    
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
                        
                        
                        
                        sun_angle = _Library.SunAngle( r_MATS, current_time)
                        
                        if( LogFlag == True):
                            Logger.debug('sun_angle: '+str(sun_angle))
                        
                        if( (sun_angle < DayAngle and abs(lat_LP) <= lat and mode == 'Day' ) or 
                           (sun_angle > NightAngle and abs(lat_LP) <= lat and mode == 'Night' )):
                            
                            Logger.debug('!!Break of Loop!!')
                            Logger.debug('Loop Counter (t): '+str(t))
                            Logger.debug('current_time: '+str(current_time))
                            Logger.debug('lat_MATS [degrees]: '+str(lat_MATS))
                            Logger.debug('lat_LP [degrees]: '+str(lat_LP))
                            Logger.debug('sun_angle [degrees]: '+str(sun_angle))
                            Logger.debug('mode: '+str(mode))
                            Logger.debug('')
                            
                            break
                        
                        
                            
                        "Increase Loop counter"
                        t= t+1
                        
                        "Timestep for propagation of MATS"
                        relativeTime = round(relativeTime + timestep,2)
                        
                            
                    ############################################################################
                    ########################## End of Orbit simulator ##########################
                    ############################################################################
                    
                    
                    comment = (Mode_name+', '+str(date)+', '+str(mode)+', pointing_altitude = '+str(altitude)+
                                ', ExpTime = '+str(ExpTime)+', JPEGQ = '+str(JPEGQ))
                    Logger.debug(comment)
                    
                    relativeTime = Macros.Snapshot_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, pointing_altitude = altitude, 
                                        SnapshotSpacing = SnapshotSpacing, comment = comment)
                    
                    #relativeTime = Macros.Limb_functional_test_macro(root = root, relativeTime = str(relativeTime), 
                    #                           pointing_altitude = str(altitude), ExpTime = str(ExpTime), 
                    #                           JPEGQ = JPEGQ, comment=comment)
                    
                    #"Postpone next command until at least the end of ExpTime"
                    #relativeTime = round(relativeTime + ExpTime/1000,2)
         
    
    mode_relativeTime = relativeTime - initial_relativeTime
    current_time = ephem.Date(date+ephem.second*mode_relativeTime)
    
    Logger.info('End of Limb_functional_test')
    
    return relativeTime, current_time
    

#############################################################################################

#############################################################################################



def Photometer_test_1(root, date, relativeTime, duration = 5400, params = {'ExpTimes': [1000,2000,4000,8000,16000]}):
    """Photometer_test_1
    
    Sets the payload in operational mode and then cycles PM settings as defined in the Test.
    """
    
    
    #params = params_checker(params,Mode=X=_settings)
    
    Logger.info('')
    Logger.info('Start of Photometer_test_1')
    
    Logger.debug('')
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    ExpTimes = params['ExpTimes']
    
    initial_relativeTime = relativeTime
    
    session_duration = 120
    
    Mode_name = sys._getframe(0).f_code.co_name
    
    Photometer_test_1_duration = duration
    
    Timeline_settings = _Globals.Timeline_settings
    pointing_altitude = Timeline_settings['LP_pointing_altitude']
    
    "Start looping the TEXPMS for the Photometer and call for macros"
    while( True ):
        mode_relativeTime = round(relativeTime - initial_relativeTime,2)
        
        if( mode_relativeTime >= Photometer_test_1_duration):
            break
            
        for ExpTime in ExpTimes:
            ExpInt = ExpTime + 500
            
            
            comment = (Mode_name+', '+str(date)+
                                ', ExpTime = '+str(ExpTime)+', ExpInt = '+str(ExpInt))
            
            Logger.debug(comment)
            
            relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime = relativeTime, pointing_altitude = pointing_altitude, CCD_settings = CCD_settings, comment = comment)
            Commands.TC_pafPM(root, relativeTime = relativeTime, TEXPMS = ExpTime, TEXPIMS = ExpInt, comment = comment)
            
            "Postpone Next PM settings"
            relativeTime = relativeTime + session_duration
            
    
    mode_relativeTime = relativeTime - initial_relativeTime
    current_time = ephem.Date(date+ephem.second*mode_relativeTime)
    
    Logger.info('End of Photometer_test_1')
    
    return relativeTime, current_time
    




##############################################################################################

##############################################################################################



def Nadir_functional_test(root, date, duration, relativeTime, params = {'ExpTimes': [1000,2000,4000,8000,16000]}):
    """Nadir_functional_test
    
    Schedules Nadir_functional_test with defined parameters and simulates MATS propagation from TLE.
    Scheduling of all daylight and nighttime commands are separated timewise and all commands for one of the two is scheduled first.
    """
    
    Logger.info('')
    Logger.info('Start of Nadir_functional_test')
    
    Logger.debug('params from Science Mode List: '+str(params))
    
    Timeline_settings = _Globals.Timeline_settings
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    altitude = Timeline_settings['LP_pointing_altitude']
    
    ExpTimes = params['ExpTimes']
    
    log_timestep = 500
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    duration_flag = 0
    
    JPEGQs = [101,95]
    WDWs = [7, 128]
    
    
    initial_relativeTime = relativeTime
    
    TLE = OPT_Config_File.getTLE()
    MATS_skyfield = skyfield.api.EarthSatellite(TLE[0], TLE[1])
    
    Altitude_defining_night = 45 #km
    Altitude_defining_day = 25 #km
    R_mean = 6371
    
    #Estimation of the angle [degrees] between the sun and the FOV position when it enters eclipse
    NightAngle = arccos(R_mean/(R_mean+Altitude_defining_night))/pi*180 + 90
    DayAngle = arccos(R_mean/(R_mean+Altitude_defining_day))/pi*180 + 90
           
    Logger.debug('')
    Logger.debug('DayAngle : '+str(DayAngle))
    Logger.debug('NightAngle : '+str(NightAngle))
    Logger.debug('')
    
    withinLat = 30
    
    Mode_name = sys._getframe(0).f_code.co_name
    
    t=0
    timestep = 4
    
    #latMargin = 360/5400 * timestep * 5 #Overly estimated change of latitude per timestep
    
    "Start looping the CCD nadir settings and call for macros"
    for mode in ['Day', 'Night']:
        
        for JPEGQ, WDW in zip(JPEGQs, WDWs):
            
            CCD_settings['CCDSEL_64']['JPEGQ'] = JPEGQ
            CCD_settings['CCDSEL_64']['WDW'] = WDW
            
            for ExpTime in ExpTimes:
                
                CCD_settings['CCDSEL_64']['TEXPMS'] = ExpTime
                
                ############################################################################
                ########################## Orbit simulator #################################
                ############################################################################
                
                #for lat in [-30, 0, 30]:
                
                "Calculate the current angle between MATS and the Sun"
                "and Loop until it is either day or night and the right latitude"
                while(True):
                    
                    mode_relativeTime = relativeTime - initial_relativeTime
                    current_time = ephem.Date(date+ephem.second*mode_relativeTime)
                    
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
                    
                    
                    sun_angle = _Library.SunAngle( r_MATS, current_time)
                    
                    
                    if( t*timestep % log_timestep == 0 == 0 or t == 1):
                        Logger.debug('')
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS))
                        Logger.debug('sun_angle [degrees]: '+str(sun_angle))
                        Logger.debug('mode: '+str(mode))
                        Logger.debug('')
                    
                    #if( (sun_angle < DayAngle and lat-latMargin <= lat_MATS <= lat+latMargin and mode == 'Day' ) or 
                    #   (sun_angle > NightAngle and lat-latMargin <= lat_MATS <= lat+latMargin and mode == 'Night' )):
                    if( (sun_angle < DayAngle and abs(lat_MATS) < withinLat and mode == 'Day' ) or 
                        (sun_angle > NightAngle and abs(lat_MATS) < withinLat and mode == 'Night' )):
                        
                        Logger.debug('!!Break of Loop!!')
                        Logger.debug('Loop Counter (t): '+str(t))
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS))
                        Logger.debug('sun_angle [degrees]: '+str(sun_angle))
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
                
                
                comment = (Mode_name+', '+str(date)+', '+', pointing_altitude = '+str(altitude)+
                            ', ExpTime = '+str(ExpTime)+', JPEGQ = '+str(JPEGQ))
                
                Logger.debug(comment)
                
                relativeTime = Macros.NadirSnapshot_Limb_Pointing_macro(root = root, relativeTime = relativeTime, 
                                           pointing_altitude = altitude, CCD_settings = CCD_settings, 
                                           comment = comment)
                
                
                #"Postpone next command until at least the end of ExpTime"
                #relativeTime = round(float(relativeTime) + ExpTime/1000,2)
                
                    
    mode_relativeTime = relativeTime - initial_relativeTime
    current_time = ephem.Date(date+ephem.second*mode_relativeTime)
    
    Logger.info('End of Nadir_functional_test')
    
    return relativeTime, current_time


#######################################################################################################

def CCD_stability_test(root, date, duration, relativeTime, params = {'ExpTimes': [1000, 2000, 4000, 8000, 16000, 32000]}):
    """CCD_stability_test. 
    
    Schedules CCD_stability_test with defined parameters and simulates MATS propagation from TLE.
    """
    
    Logger.info('')
    Logger.info('Start of CCD_stability_test')
    
    Logger.debug('params from Science Mode List: '+str(params))
    #params = params_checker(params,Mode=X=_settings)
    
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    
    JPEGQs = [101]
    WDWs = [7]
    altitudes = [200000]
    ExpTimes = params['ExpTimes']
    SnapshotSpacing = 5
    
    initial_relativeTime = relativeTime
    
    Mode_name = sys._getframe(0).f_code.co_name
    
    "Loop thorugh pointing altitudes"
    for altitude in altitudes:
        
        "Start looping the CCD settings and call for macros"
        for JPEGQ, WDW in zip(JPEGQs, WDWs):
            
            "Set all CCDs"
            for key in CCD_settings.keys():
                CCD_settings[key]['JPEGQ'] = JPEGQ
                CCD_settings[key]['WDW'] = WDW
            
            for ExpTime in ExpTimes:
                
                for key in CCD_settings.keys():
                    CCD_settings[key]['TEXPMS'] = ExpTime
                
                
                
                comment = (Mode_name+', '+str(date)+', pointing_altitude = '+str(altitude)+
                            ', ExpTime = '+str(ExpTime)+', JPEGQ = '+str(JPEGQ))
                
                Logger.debug(comment)
                
                relativeTime = Macros.Snapshot_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, pointing_altitude = altitude, 
                                    SnapshotSpacing = SnapshotSpacing, comment = comment)
                
                #"Postpone next command until at least the end of ExpTime"
                #relativeTime = round(relativeTime + ExpTime/1000,2)
     
    
    mode_relativeTime = relativeTime - initial_relativeTime
    current_time = ephem.Date(date+ephem.second*mode_relativeTime)
    
    Logger.info('End of CCD_stability_test')
    
    return relativeTime, current_time
    

#############################################################################################

#############################################################################################

