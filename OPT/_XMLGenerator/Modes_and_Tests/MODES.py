# -*- coding: utf-8 -*-
"""Contain Mode functions which generates and calculates parameters for each mode, 
then calls for Macros/Commands functions located in the *Macros_Commands* package, which will in turn write commands to the XML tree object *root*.

Functions on the form "X", where the last X is any Mode:

    **Arguments:**
        **root** (*lxml.etree.Element*):  XML tree structure. Main container object for the ElementTree API. \n
        **date** (*ephem.Date*): Starting date of the Mode. On the form of the ephem.Date class. \n
        **duration** (*int*): The duration of the mode [s]. \n
        **relativeTime** (*int*): The starting time of the mode with regard to the start of the timeline [s]. \n
        **params** (*dict*): Dictionary containing the settings of the Mode given in the *Science_Mode_Timeline*.

    **Returns:**
        None

When creating new Mode functions it is crucial that the function name is
Mode_name, where Mode_name is the same as the string used in the *Science Mode Timeline*
        
@author: David
"""


import ephem, logging, sys, pylab, importlib, skyfield.api

from OPT import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
from OPT._Library import Satellite_Simulator, params_checker, utc_to_onboardTime, SunAngle
from .Macros_Commands import Macros, Commands

Logger = logging.getLogger(OPT_Config_File.Logger_name())
#Timeline_settings = OPT_Config_File.Timeline_settings()


def Mode5(root, date, duration, relativeTime, params = {}):
    '''Mode5
    
    **Macro:** Operational_Limb_Pointing_macro \n
    **CCD_Macro:** CustomBinning \n
            
    '''
    
    pointing_altitude = _Globals.Timeline_settings['LP_pointing_altitude']
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('CustomBinning')
    settings = OPT_Config_File.Operational_Science_Mode_settings()
    
    params = params_checker(params, settings, Logger)
    
    Mode_name = sys._getframe(1).f_code.co_name.replace('','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    #pointing_altitude = params['pointing_altitude']
    
    #Macros.Custom_Binning_Macro(root,relativeTime, pointing_altitude=pointing_altitude, comment = comment)
    Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                           pointing_altitude=pointing_altitude, comment = comment)
                        


############################################################################################
    
def Mode1(root, date, duration, relativeTime, params = {}):
    """Mode1
    
    **Macro:** Operational_Limb_Pointing_macro \n
    **CCD_Macro:** HighResUV \n
    
    Disable exposure on UV channels for +-lat degrees latitude equatorwards.
    Stop/Start Nadir at dusk/dawn below MATS.
    Simulates MATS and the LP with or without yaw movement to be able to predict and schedule commands in the XML-file.
    
    """
    
    #from OPT_Config_File import Mode1_settings, getTLE
    #from pylab import zeros, pi, arccos, sin ,cos, norm, cross, sqrt, arctan
    
    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos
    norm = pylab.norm
    dot = pylab.dot
    array = pylab.array
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('HighResUV')
    settings = OPT_Config_File.Operational_Science_Mode_settings()
    Timeline_settings = _Globals.Timeline_settings
    
    params = params_checker(params, settings, Logger)
    
    timestep = params['timestep']
    TEXPMS_16 = CCD_settings['CCDSEL_16']['TEXPMS']
    TEXPMS_32 = CCD_settings['CCDSEL_32']['TEXPMS']
    TEXPMS_nadir = CCD_settings['CCDSEL_64']['TEXPMS']
    
    log_timestep = params['log_timestep']
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    TLE = OPT_Config_File.getTLE()
    
    "Pre-allocate space"
    lat_MATS = zeros((duration,1))
    r_MATS = zeros((duration,3))
    r_MATS_ECEF = zeros((duration,3))
    r_MATS_unit_vector = zeros((duration,3))
    optical_axis = zeros((duration,3))
    lat_LP = zeros((duration,1))
    MATS_P = zeros((duration,1))
    
    r_Sun = zeros((duration,3))
    r_Sun_unit_vector = zeros((duration,3))
    
    sun_angle = zeros((duration,1))
    lat_LP = zeros((duration,1))
    
    R_mean = 6371000 #Radius of Earth in m
    pointing_altitude = Timeline_settings['LP_pointing_altitude']
    lat = params['lat']
    
    heightAboveSurface = 20000 #Altitude in km where sun is deemed to reflect in atmosphere, determining night and day below satellite"
    
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+heightAboveSurface))/pi*180 + 90
    
    Logger.debug('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    Logger.debug('')
    
    
    MATS_skyfield = skyfield.api.EarthSatellite(TLE[0], TLE[1])
    
    new_relativeTime = relativeTime
    current_time = ephem.Date(date)
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(int(duration/timestep)):
        
        if( t != 0):
            "Incremented time from scheduling CMDs"
            CMD_scheduling_delay = (new_relativeTime-relativeTime)
            "Increment with timestep each loop and add any added time from CMD scheduling"
            current_time = ephem.Date( current_time + ephem.second*(timestep + CMD_scheduling_delay) )
            #current_time = ephem.Date( current_time+ephem.second*(new_relativeTime-relativeTime) )
            relativeTime = new_relativeTime + timestep
        
        new_relativeTime = relativeTime
        
        if( t*timestep % log_timestep == 0):
            LogFlag = True
        else:
            LogFlag = False
        
        Satellite_dict = Satellite_Simulator( 
                    MATS_skyfield, current_time, Timeline_settings, pointing_altitude/1000, LogFlag, Logger )
        
        r_MATS[t] = Satellite_dict['Position [km]']
        MATS_P[t] = Satellite_dict['OrbitalPeriod [s]']
        lat_MATS[t] =  Satellite_dict['Latitude [degrees]']
        optical_axis[t] = Satellite_dict['OpticalAxis']
        lat_LP[t] = Satellite_dict['EstimatedLatitude_LP [degrees]']
        
        sun_angle[t] = SunAngle( r_MATS[t], current_time)
        
        #MATS.compute(current_time, epoch = '2000/01/01 11:58:55.816')
        #Sun.compute(current_time, epoch = '2000/01/01 11:58:55.816')
        #sun_angle[t]= ephem.separation(Sun,MATS)/pi*180
        
        if( t*timestep % log_timestep == 0):
            Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
        
        ############# Initial Mode setup ##########################################
        
        if( t == 0 ):
            
            
            "Check if night or day"
            if( sun_angle[t] > MATS_nadir_eclipse_angle ):
                
                if( abs(lat_LP[t]) < lat):
                    current_state = "NLC_night_UV_off"
                    comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                    #new_relativeTime = Macros.Mode1_macro(root,relativeTime, pointing_altitude=pointing_altitude, UV_on = False, nadir_on = True, comment = comment)
                    CCD_settings['CCDSEL_16']['TEXPMS'] = 0
                    CCD_settings['CCDSEL_32']['TEXPMS'] = 0
                    CCD_settings['CCDSEL_64']['TEXPMS'] = TEXPMS_nadir
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                               pointing_altitude=pointing_altitude, comment = comment)
                    
                elif( abs(lat_LP[t]) > lat):
                    current_state = "NLC_night_UV_on"
                    comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                    #new_relativeTime = Macros.Mode1_macro(root,relativeTime, pointing_altitude=pointing_altitude, UV_on = True, nadir_on = True, comment = comment)
                    CCD_settings['CCDSEL_16']['TEXPMS'] = TEXPMS_16
                    CCD_settings['CCDSEL_32']['TEXPMS'] = TEXPMS_32
                    CCD_settings['CCDSEL_64']['TEXPMS'] = TEXPMS_nadir
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                               pointing_altitude=pointing_altitude, comment = comment)
                    
                    
            elif( sun_angle[t] < MATS_nadir_eclipse_angle ):
                
                if( abs(lat_LP[t]) < lat):
                    current_state = "NLC_day_UV_off"
                    comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                    #new_relativeTime = Macros.Mode1_macro(root,relativeTime,pointing_altitude, UV_on = False, nadir_on = False, comment = comment)
                    CCD_settings['CCDSEL_16']['TEXPMS'] = 0
                    CCD_settings['CCDSEL_32']['TEXPMS'] = 0
                    CCD_settings['CCDSEL_64']['TEXPMS'] = 0
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                               pointing_altitude=pointing_altitude, comment = comment)
                    
                elif( abs(lat_LP[t]) > lat):
                    current_state = "NLC_day_UV_on"
                    comment = current_state+': '+str(current_time)+', parameters: '+str(params)
                    #new_relativeTime = Macros.Mode1_macro(root,relativeTime,pointing_altitude, UV_on = True, nadir_on = False, comment = comment)
                    CCD_settings['CCDSEL_16']['TEXPMS'] = TEXPMS_16
                    CCD_settings['CCDSEL_32']['TEXPMS'] = TEXPMS_32
                    CCD_settings['CCDSEL_64']['TEXPMS'] = 0
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                               pointing_altitude=pointing_altitude, comment = comment)
                    
                    
            Logger.debug(current_state)
            Logger.debug('')
        
        
        ############# End of Initial Mode setup ###################################
        
        
        if( t != 0):
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
                        #new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude, UV_on = False, nadir_on = True, comment = comment)
                        CCD_settings['CCDSEL_16']['TEXPMS'] = 0
                        CCD_settings['CCDSEL_32']['TEXPMS'] = 0
                        CCD_settings['CCDSEL_64']['TEXPMS'] = TEXPMS_nadir
                        new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                               pointing_altitude=pointing_altitude, comment = comment)
                        
                        Logger.debug(current_state)
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]))
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
                        #new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, UV_on = True, nadir_on = True, comment = comment)
                        CCD_settings['CCDSEL_16']['TEXPMS'] = TEXPMS_16
                        CCD_settings['CCDSEL_32']['TEXPMS'] = TEXPMS_32
                        CCD_settings['CCDSEL_64']['TEXPMS'] = TEXPMS_nadir
                        new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                               pointing_altitude=pointing_altitude, comment = comment)
                        
                        Logger.debug(current_state)
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]))
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
                        #new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, UV_on = False, nadir_on = False, comment = comment)
                        CCD_settings['CCDSEL_16']['TEXPMS'] = 0
                        CCD_settings['CCDSEL_32']['TEXPMS'] = 0
                        CCD_settings['CCDSEL_64']['TEXPMS'] = 0
                        new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                               pointing_altitude=pointing_altitude, comment = comment)
                        
                        
                        Logger.debug(current_state)
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]))
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
                        #new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, UV_on = True, nadir_on = False, comment = comment)
                        CCD_settings['CCDSEL_16']['TEXPMS'] = TEXPMS_16
                        CCD_settings['CCDSEL_32']['TEXPMS'] = TEXPMS_32
                        CCD_settings['CCDSEL_64']['TEXPMS'] = 0
                        new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                               pointing_altitude=pointing_altitude, comment = comment)
                        
                        
                        Logger.debug(current_state)
                        Logger.debug('current_time: '+str(current_time))
                        Logger.debug('lat_MATS [degrees]: '+str(lat_MATS[t]))
                        Logger.debug('lat_LP [degrees]: '+str(lat_LP[t]))
                        Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                        Logger.debug('')
                        #Mode1_macro(root,str(t+relativeTime),pointing_altitude, comment = comment)
                        
                        
            
            
            ############### End of SCI-mode operation planner #################
            
    

#######################################################################################

def Mode2(root, date, duration, relativeTime, params = {}):
    """Mode2
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: HighResIR (High-resolution IR binning). \n
    
    Stop/Start Nadir at dusk/dawn below MATS.
    Simulates MATS to determine when a point below MATS is at night or daytime.
    
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('HighResIR')
    settings = OPT_Config_File.Operational_Science_Mode_settings()
    #Timeline_settings = OPT_Config_File.Timeline_settings()
    Timeline_settings = _Globals.Timeline_settings
    zeros = pylab.zeros
    pi = pylab.pi
    arccos = pylab.arccos
    
    params = params_checker(params, settings, Logger)
    
    timestep = params['timestep']
    TEXPMS_nadir = CCD_settings['CCDSEL_64']['TEXPMS']
    
    log_timestep = params['log_timestep']
    Logger.debug('log_timestep [s]: '+str(log_timestep))
    
    
    TLE = OPT_Config_File.getTLE()
    
    
    "Pre-allocate space"
    sun_angle = zeros((duration,1))
    r_MATS = zeros((duration,3))
    
    R_mean = 6371000 #Radius of Earth in m
    pointing_altitude = Timeline_settings['LP_pointing_altitude']
    
    heightAboveSurface = 20000 #Altitude in m where sun is deemed to reflect in atmosphere, determining night and day below satellite"
    
    #Estimation of the angle between the sun and the FOV position when it enters eclipse
    MATS_nadir_eclipse_angle = arccos(R_mean/(R_mean+heightAboveSurface))/pi*180 + 90
    Logger.debug('MATS_nadir_eclipse_angle : '+str(MATS_nadir_eclipse_angle))
    
    
    MATS_skyfield = skyfield.api.EarthSatellite(TLE[0], TLE[1])
    
    new_relativeTime = relativeTime
    current_time = ephem.Date(date)
    
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    for t in range(int(duration/timestep)):
        
        if( t != 0):
            CMD_scheduling_delay = (new_relativeTime-relativeTime)
            "Increment with timestep each loop and add any added time if new_relativeTime was changed"
            current_time = ephem.Date( current_time + ephem.second*(timestep + CMD_scheduling_delay) )
            #current_time = ephem.Date( current_time+ephem.second*(new_relativeTime-relativeTime) )
            
            relativeTime = new_relativeTime + timestep
        
        new_relativeTime = relativeTime
        
        #relativeTime = relativeTime + t * timestep
        #current_time = ephem.Date(date+ephem.second*timestep*t)
        
        if( t*timestep % log_timestep == 0):
            LogFlag = True
        else:
            LogFlag = False
        
        Satellite_dict = Satellite_Simulator( 
                    MATS_skyfield, current_time, Timeline_settings, pointing_altitude/1000, LogFlag, Logger )
        
        r_MATS[t] = Satellite_dict['Position [km]']
        sun_angle[t] = SunAngle( r_MATS[t], current_time)
        
        
        
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
                #new_relativeTime = Macros.Mode1_macro(root,relativeTime, pointing_altitude=pointing_altitude, nadir_on = True, comment = comment)
                CCD_settings['CCDSEL_64']['TEXPMS'] = TEXPMS_nadir
                new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                       pointing_altitude=pointing_altitude, comment = comment)
                
            elif( sun_angle[t] < MATS_nadir_eclipse_angle):
                current_state = "IR_day"
                comment = current_state+': '+str(params)
                #new_relativeTime = Macros.Mode1_macro(root,relativeTime, pointing_altitude=pointing_altitude, nadir_on = False, comment = comment)
                CCD_settings['CCDSEL_64']['TEXPMS'] = 0
                new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
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
                    #new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, nadir_on = True, comment = comment)
                    CCD_settings['CCDSEL_64']['TEXPMS'] = TEXPMS_nadir
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
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
                    #new_relativeTime = Macros.Mode1_macro(root, relativeTime, pointing_altitude=pointing_altitude, nadir_on = False, comment = comment)
                    CCD_settings['CCDSEL_64']['TEXPMS'] = 0
                    new_relativeTime = Macros.Operational_Limb_Pointing_macro(root, relativeTime, CCD_settings, 
                                                           pointing_altitude=pointing_altitude, comment = comment)
                    
                    Logger.debug('current_time: '+str(current_time))
                    Logger.debug('sun_angle [degrees]: '+str(sun_angle[t]))
                    Logger.debug('')
                    
                    
                    
                 
        ############### End of SCI-mode operation planner #################
    
    

################################################################################################



def Mode100(root, date, duration, relativeTime, params = {}):
    """ Mode100
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: BinnedCalibration with configurable exposure time of UV and IR CCDs. \n
    
    Successively point at altitudes from X-Y in Operational Mode in intervals of Z with increasing Exposure Times.
    Where X is *pointing_altitude_from*, Y is *pointing_altitude_to, and Z is *pointing_altitude_interval*.
    All defined in *Mode100_settings*.
    
    """
    
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    settings = OPT_Config_File.Mode100_settings()
    
    
    params = params_checker(params, settings, Logger)
    
    Mode_name = sys._getframe(0).f_code.co_name
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
        CCD_settings['CCDSEL_16']['TEXPMS'] = ExpTimeUV + x * ExpTime_step
        CCD_settings['CCDSEL_32']['TEXPMS'] = ExpTimeUV + x * ExpTime_step
        CCD_settings['CCDSEL_1']['TEXPMS'] = ExpTimeIR + x * ExpTime_step
        CCD_settings['CCDSEL_8']['TEXPMS'] = ExpTimeIR + x * ExpTime_step
        CCD_settings['CCDSEL_2']['TEXPMS'] = ExpTimeIR + x * ExpTime_step
        CCD_settings['CCDSEL_4']['TEXPMS'] = ExpTimeIR + x * ExpTime_step
        
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



def Mode110(root, date, duration, relativeTime, params = {}):
    """Mode110
    
    **Macro**: Operational_Sweep_macro. \n
    **CCD_Macro**: BinnedCalibration with configurable exposure time of UV and IR CCDs. \n
    
    
    Scan atmosphere from X to Y altitudes with a rate of Z.
    Where X, Y, Z is defined in *Mode110_settings*.
    
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    settings = OPT_Config_File.Mode110_settings()
    
    params = params_checker(params, settings, Logger)
    
    ExpTimeUV= params['Exp_Time_UV']
    ExpTimeIR = params['Exp_Time_IR']
    CCD_settings['CCDSEL_16']['TEXPMS'] = ExpTimeUV
    CCD_settings['CCDSEL_32']['TEXPMS'] = ExpTimeUV
    CCD_settings['CCDSEL_1']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCDSEL_8']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCDSEL_2']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCDSEL_4']['TEXPMS'] = ExpTimeIR
    
    Mode_name = sys._getframe(0).f_code.co_name
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

def Mode12X(root, date, duration, relativeTime, 
                       params, CCD_settings):
    """Mode12X, where X is 1,2,3....
    
    **Macro**: Snapshot_Inertial_macro. \n
    
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir.
    
    """
    
    Timeline_settings = _Globals.Timeline_settings
    
    Mode_name = sys._getframe(1).f_code.co_name.replace('','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    freeze_start_utc = ephem.Date(date+ephem.second*params['freeze_start'])
    
    Snapshot_relativeTime = relativeTime + params['freeze_start'] + params['SnapshotTime']
    
    FreezeTime = utc_to_onboardTime(freeze_start_utc, Timeline_settings['GPS_epoch'], Timeline_settings['leapSeconds'])
    
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


def Mode120(root, date, duration, relativeTime, 
                       params = {}):
    """Mode120
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: FullReadout \n
    
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir.
    Used for star calibration.
    
    """
    
    settings = OPT_Config_File.Mode120_settings()
    params = params_checker(params, settings, Logger)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    Mode12X(root, date, duration, relativeTime, 
                                  params = params, CCD_settings = CCD_settings)


################################################################################################


##############################################################################################


def Mode121(root, date, duration, relativeTime, 
                       params = {}):
    """Mode121
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: FullReadout \n
    
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir.
    
    """
    
    settings = OPT_Config_File.Mode121_settings()
    params = params_checker(params, settings, Logger)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    Mode12X(root, date, duration, relativeTime, 
                       params = params, CCD_settings = CCD_settings)


############################################################################################




def Mode122(root, date, duration, relativeTime, 
                       params = {}):
    """Mode122
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: BinnedCalibration with configurable exposure time of UV and IR CCDs. \n
    
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir.
    
    """
    
    settings = OPT_Config_File.Mode122_settings()
    params = params_checker(params, settings, Logger)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    ExpTimeUV= params['Exp_Time_UV']
    ExpTimeIR = params['Exp_Time_IR']
    CCD_settings['CCDSEL_16']['TEXPMS'] = ExpTimeUV
    CCD_settings['CCDSEL_32']['TEXPMS'] = ExpTimeUV
    CCD_settings['CCDSEL_1']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCDSEL_8']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCDSEL_2']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCDSEL_4']['TEXPMS'] = ExpTimeIR
    
    Mode12X(root, date, duration, relativeTime, 
                        params = params, CCD_settings = CCD_settings)
    

################################################################################################

############################################################################################




def Mode123(root, date, duration, relativeTime, 
                       params = {}):
    """Mode123
    
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: LowPixel with configurable exposure time of UV and IR CCDs. \n
    
    Stare at a point in inertial reference frame and take a Snapshot with each CCD except nadir.
    
    
    """
    
    settings = OPT_Config_File.Mode123_settings()
    params = params_checker(params, settings, Logger)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('LowPixel')
    ExpTimeUV= params['Exp_Time_UV']
    ExpTimeIR = params['Exp_Time_IR']
    CCD_settings['CCDSEL_16']['TEXPMS'] = ExpTimeUV
    CCD_settings['CCDSEL_32']['TEXPMS'] = ExpTimeUV
    CCD_settings['CCDSEL_1']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCDSEL_8']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCDSEL_2']['TEXPMS'] = ExpTimeIR
    CCD_settings['CCDSEL_4']['TEXPMS'] = ExpTimeIR
    
    Mode12X(root, date, duration, relativeTime, 
                        params = params, CCD_settings = CCD_settings)
    



##############################################################################################


def Mode124(root, date, duration, relativeTime, 
                       params = {}):
    """Mode124
    
    **Macro**: Snapshot_Inertial_macro. \n
    **CCD_Macro**: FullReadout. \n
    
    Stare at a point in inertial reference frame and take one Snapshot with each CCD except Nadir. 
    Used for moon calibration.
    """
    
    
    settings = OPT_Config_File.Mode124_settings()
    params = params_checker(params, settings, Logger)
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    
    Mode12X(root, date, duration, relativeTime, 
                        params = params, CCD_settings = CCD_settings)

##############################################################################################



################################################################################################


def Mode130(root, date, duration, relativeTime, 
                       params = {}):
    """Mode130
    
    **Macro**: Snapshot_Limb_Pointing_macro. \n
    **CCD_Macro**: FullReadout. \n
    
    Look at fixed limb altitude and take Snapshots with all CCD except nadir.
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    settings = OPT_Config_File.Mode130_settings()
    
    params = params_checker(params, settings, Logger)
    
    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    SnapshotSpacing = params['SnapshotSpacing']
    
    #Mode_macro = getattr(Macros,Mode_name+'_macro')
    
    Macros.Snapshot_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, pointing_altitude = pointing_altitude, 
               SnapshotSpacing = SnapshotSpacing, comment = comment)



##############################################################################################

def Mode131(root, date, duration, relativeTime, 
                       params = {}):
    """Mode131
    
    **Macro**: FullReadout_Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: FullReadout. \n
    
    Look at fixed limb altitude in operational mode.
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('FullReadout')
    settings = OPT_Config_File.Mode131_settings()
    
    params = params_checker(params, settings, Logger)
    
    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    TEXPIMS = params['Exposure_Interval']
    
    Macros.FullReadout_Operational_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, 
                                                       TEXPIMS = TEXPIMS, pointing_altitude = pointing_altitude, comment = comment)


################################################################################################

##############################################################################################

def Mode132_133(root, date, duration, relativeTime, 
                       params, CCD_settings):
    """Mode132 and Mode133
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    
    Look at fixed limb altitude in operational mode with a set of exposure times for UV and IR CCDs.
    """
    
    Mode_name = sys._getframe(1).f_code.co_name.replace('','')
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    
    for ExpTimeUV,ExpTimeIR in zip( params['Exp_Times_UV'], params['Exp_Times_IR'] ):
        
        CCD_settings['CCDSEL_16']['TEXPMS'] = ExpTimeUV
        CCD_settings['CCDSEL_32']['TEXPMS'] = ExpTimeUV
        CCD_settings['CCDSEL_1']['TEXPMS'] = ExpTimeIR
        CCD_settings['CCDSEL_8']['TEXPMS'] = ExpTimeIR
        CCD_settings['CCDSEL_2']['TEXPMS'] = ExpTimeIR
        CCD_settings['CCDSEL_4']['TEXPMS'] = ExpTimeIR
        relativeTime = Macros.Operational_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings, 
                                  pointing_altitude = pointing_altitude, comment = comment)
        
        relativeTime = relativeTime + params['session_duration']
        

################################################################################################




def Mode132(root, date, duration, relativeTime, 
                       params = {}):
    """Mode132
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: BinnedCalibration with changing exposure times for UV and IR CCDs. \n
    
    Look at fixed limb altitude in operational mode for a set duration with each exposure time.
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('BinnedCalibration')
    settings = OPT_Config_File.Mode132_settings()
    
    params = params_checker(params, settings, Logger)
    
    Mode132_133(root, date, duration, relativeTime, 
                       params = params, CCD_settings = CCD_settings)



##############################################################################################

################################################################################################



def Mode133(root, date, duration, relativeTime, 
                       params = {}):
    """Mode133,
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: LowPixel with changing exposure times for UV and IR CCDs. \n
    
    Look at fixed limb altitude in operational mode for a set duration with each exposure time.
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('LowPixel')
    settings = OPT_Config_File.Mode133_settings()
    
    params = params_checker(params, settings, Logger)
    
    Mode132_133(root, date, duration, relativeTime, 
                       params = params, CCD_settings = CCD_settings)
        



##############################################################################################

##############################################################################################

def Mode134(root, date, duration, relativeTime, 
                       params = {}):
    """Mode134, Operational_Limb_Pointing_macro.
    
    **Macro**: Operational_Limb_Pointing_macro. \n
    **CCD_Macro**: CustomBinning \n
    
    Look at fixed limb altitude in Operational Mode.
    """
    
    CCD_settings = OPT_Config_File.CCD_macro_settings('CustomBinning')
    settings = OPT_Config_File.Mode134_settings()
    
    params = params_checker(params, settings, Logger)
    
    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    pointing_altitude = params['pointing_altitude']
    
    Macros.Operational_Limb_Pointing_macro(root, round(relativeTime,2), CCD_settings,
                                pointing_altitude = pointing_altitude, comment = comment)


################################################################################################

##############################################################################################




##############################################################################################


def X(root, date, duration, relativeTime, params = {}):
    """This is a template for a new mode or test. Exchange 'X' for the name of the new mode/test"
    
    Currently this template mode only schedules a *TC_acfLimbPointingAltitudeOffset* CMD.
    """
    
    "Calls for settings stated in the Configuration File"
    #settings = OPT_Config_File.X_settings()
    "Calls for CCD settings for a specific CCD macro, here the CCD macro is 'CustomBinning'"
    CCD_settings = OPT_Config_File.CCD_macro_settings('CustomBinning')
    
    "Compares settings given in the Science Mode Timeline to settings given in the Configuration File"
    #params = params_checker(params,settings)
    
    
    Mode_name = sys._getframe(0).f_code.co_name
    comment = Mode_name+' starting date: '+str(date)+', '+str(params)
    
    Commands.TC_acfLimbPointingAltitudeOffset(root, round(relativeTime,2), Initial = 120000, 
                                              Final = 120000, Rate = 0, comment = comment)
    
    "A call for the macro called Operational_Limb_Pointing_macro"
    Macros.Operational_Limb_Pointing_macro(root = root, relativeTime = round(relativeTime,2), CCD_settings = CCD_settings,
                                pointing_altitude = 120000, comment = comment)
    
    




#######################################################################################################





