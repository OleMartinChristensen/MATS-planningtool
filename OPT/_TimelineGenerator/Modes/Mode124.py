# -*- coding: utf-8 -*-
"""Schedules the active Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""


import ephem, sys, logging, importlib
from pylab import cross, ceil, dot, zeros, sqrt, norm, pi, arccos, arctan
from skyfield import api

from OPT._Library import Satellite_Simulator, scheduler
from OPT import _Globals
from .Mode12X import UserProvidedDateScheduler

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def Mode124(Occupied_Timeline):
    """Core function for the scheduling of Mode124.
    
    Determines if the scheduled date should be determined by simulating MATS or be user provided.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes/CMDs with entries equal to their start and end time as a list.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    Settings = OPT_Config_File.Mode124_settings()
    
    if( Settings['automatic'] == False ):
        Occupied_Timeline, comment = UserProvidedDateScheduler(Occupied_Timeline, Settings)
    elif( Settings['automatic'] == True ):
        SpottedMoonList = date_calculator()
        
        Occupied_Timeline, comment = date_select(Occupied_Timeline, SpottedMoonList)
      
    return Occupied_Timeline, comment



###############################################################################################
###############################################################################################



def date_calculator():
    """Subfunction, Simulates MATS FOV and the Moon.
    
    Determines when the Moon is entering the FOV at an vertical offset-angle equal to *#V-offset* and also being 
    located at a horizontal off-set angle equal to less than *#H-offset* when pointing at an LP altitude equal to *#pointing_altitude*. \n
    
    A timeskip equal to 1/2 an orbit of MATS is applied after a successful spotting of the Moon to save processing time. \n
    
    A timeskip equal to the time it takes for the Moon orbital position to change by *#H-offset*/4 degrees are also applied if the Moon is 
    determined to be at an horizontal off-set angle larger then the horizontal FOV of the instrument, equal to *#HFOV*. \n
    
    (# as defined in the *Configuration File*). \n
    
    Saves the date and parameters regarding the spotting of the Moon
    Also saves relevant data to an .csv file located in Output/.
    
    Arguments:
        
    Returns:
        SpottedMoonList ((:obj:`list` of :obj:`dict`)) or (str): A list containing dictionaries containing parameters for each time the Moon is spotted. Or just a date depending on 'automatic' in *Mode124_settings*.
    
    """
    
    Timeline_settings = OPT_Config_File.Timeline_settings()
    Mode124_settings = OPT_Config_File.Mode124_settings()
    
    log_timestep = Mode124_settings['log_timestep']
    Logger.debug('log_timestep: '+str(log_timestep))
    
    ##################################################
    "Constants"
    
    Mode124Iteration = _Globals.Mode124Iteration
    "Make the V_offset_Index go from 0 to len(Mode120_settings['V_offset']"
    V_offset_Index = (Mode124Iteration-1) % (len(Mode124_settings['V_offset']))
    
    V_offset = Mode124_settings['V_offset'][V_offset_Index]
    H_offset = Mode124_settings['H_offset']  
    pointing_altitude = Mode124_settings['pointing_altitude']/1000 
    
    Moon_orbital_period = 3600*24*27.32
    yaw_correction = Timeline_settings['yaw_correction']
    
    Logger.debug('H_offset set to [degrees]: '+str(H_offset))
    Logger.debug('V_offset set to [degrees]: '+str(V_offset))
    Logger.debug('Moon_orbital_period [s]: '+str(Moon_orbital_period))
    Logger.debug('yaw_correction set to: '+str(yaw_correction))
    
    TLE = OPT_Config_File.getTLE()
    Logger.debug('TLE used: '+TLE[0]+TLE[1])
    
    ##########################################################
    
    "Simulation length and timestep"
    
    timestep = Mode124_settings['timestep'] #In seconds
    Logger.info('Timestep set to [s]: '+str(timestep))
    
    duration = Mode124_settings['TimeToConsider']
    Logger.info('Duration set to [s]: '+str(duration))
    
    timesteps = int(ceil(duration / timestep)) + 2
    
    timeline_start = ephem.Date(Timeline_settings['start_date'])
    initial_time= ephem.Date( timeline_start + ephem.second*Mode124_settings['freeze_start'] )
    
    Logger.info('Initial simulation date set to: '+str(initial_time))
    
    
    "Pre-allocate space"
    r_MATS = zeros((timesteps,3))
    lat_MATS = zeros((timesteps,1))
    long_MATS = zeros((timesteps,1))
    optical_axis = zeros((timesteps,3))
    negative_normal_orbit = zeros((timesteps,3))
    r_H_offset_normal = zeros((timesteps,3))
    r_V_offset_normal = zeros((timesteps,3))
    MATS_P = zeros((timesteps,1))
    
    r_Moon = zeros((timesteps,3))
    r_MATS_2_Moon = zeros((timesteps,3))
    r_MATS_2_Moon_norm = zeros((timesteps,3))
    Moon_r_V_offset_plane = zeros((timesteps,3))
    Moon_r_H_offset_plane = zeros((timesteps,3))
    Moon_r_orbital_plane = zeros((timesteps,3))
    Moon_vert_offset = zeros((timesteps,1))
    Moon_hori_offset = zeros((timesteps,1))
    angle_between_orbital_plane_and_moon = zeros((timesteps,1))
    SpottedMoonList = []
    r_Moon_unit_vector = zeros((timesteps,3))
    
    Dec_optical_axis = zeros((timesteps,1))
    RA_optical_axis = zeros((timesteps,1))
    
    
    
    
    ts = api.load.timescale(builtin=True)
    MATS_skyfield = api.EarthSatellite(TLE[0], TLE[1])
    
    planets = api.load('de421.bsp')
    Moon = planets['Moon']
    Earth = planets['Earth']
    
    t=0
    
    
    current_time = initial_time
    
    Logger.info('')
    Logger.info('Start of simulation for Mode124')
    
    ######### SIMULATION ################
    while(current_time < initial_time+ephem.second*duration):
        
        if( t*timestep % log_timestep == 0):
            LogFlag = True
        else:
            LogFlag = False
        
        Satellite_dict = Satellite_Simulator( 
                MATS_skyfield, current_time, Timeline_settings, pointing_altitude, LogFlag, Logger )
        
        r_MATS[t] = Satellite_dict['Position [km]']
        MATS_P[t] = Satellite_dict['OrbitalPeriod [s]']
        lat_MATS[t] =  Satellite_dict['Latitude [degrees]']
        long_MATS[t] =  Satellite_dict['Longitude [degrees]']
        
        optical_axis[t] = Satellite_dict['OpticalAxis']
        Dec_optical_axis[t] = Satellite_dict['Dec_OpticalAxis [degrees]']
        RA_optical_axis[t] = Satellite_dict['RA_OpticalAxis [degrees]']
        
        ascending_node = Satellite_dict['AscendingNode']
        yaw_offset_angle = Satellite_dict['Yaw [degrees]']
        arg_of_lat = Satellite_dict['ArgOfLat [degrees]']
        
        negative_normal_orbit[t] = -Satellite_dict['OrbitNormal']
        r_H_offset_normal[t] = Satellite_dict['Normal2H_offset']
        r_V_offset_normal[t] = Satellite_dict['Normal2V_offset']
        
        
        ############# End of Calculations of orbital and pointing vectors #####
        
        current_time_datetime = ephem.Date(current_time).datetime()
        year = current_time_datetime.year
        month = current_time_datetime.month
        day = current_time_datetime.day
        hour = current_time_datetime.hour
        minute = current_time_datetime.minute
        second = current_time_datetime.second + current_time_datetime.microsecond/1000000
        
        current_time_skyfield = ts.utc(year, month, day, hour, minute, second)
        
        Moon_apparent_from_Earth = Earth.at(current_time_skyfield).observe(Moon).apparent()
        r_Moon[t,0:3] = Moon_apparent_from_Earth.position.km
        
        r_Moon_unit_vector[t,0:3] = r_Moon[t,0:3]/norm(r_Moon[t,0:3])
        
        r_MATS_2_Moon[t] = r_Moon[t]-r_MATS[t]
        r_MATS_2_Moon_norm[t] = r_MATS_2_Moon[t]/norm(r_MATS_2_Moon[t])
        
        "Calculate Dec and RA of moon"
        Dec_Moon = arctan(  r_Moon[t,2] / sqrt(r_Moon[t,0]**2 + r_Moon[t,1]**2) ) /pi * 180
        RA_Moon = arccos( dot( [1,0,0], [r_Moon[t,0],r_Moon[t,1],0] ) / norm([r_Moon[t,0],r_Moon[t,1],0]) ) / pi * 180
        
        
        if( r_Moon[t,1] < 0 ):
            RA_Moon = 360-RA_Moon
        
        "Project 'r_MATS_2_Moon' ontop of orbital plane"
        Moon_r_orbital_plane[t] = r_MATS_2_Moon_norm[t] - dot(r_MATS_2_Moon_norm[t],negative_normal_orbit[t]) * negative_normal_orbit[t]
        
        "Project 'r_MATS_2_Moon' ontop pointing H-offset and V-offset plane"
        Moon_r_V_offset_plane[t] = r_MATS_2_Moon_norm[t] - dot(r_MATS_2_Moon_norm[t],r_V_offset_normal[t]) * r_V_offset_normal[t]
        Moon_r_H_offset_plane[t] = r_MATS_2_Moon_norm[t] - dot(r_MATS_2_Moon_norm[t],r_H_offset_normal[t]) * r_H_offset_normal[t]
        
        
        "Dot product to get the Vertical and Horizontal angle offset of the Moon"
        Moon_vert_offset[t] = arccos(dot(optical_axis[t],Moon_r_V_offset_plane[t]) / (norm(optical_axis[t])*norm(Moon_r_V_offset_plane[t]))) /pi*180
        Moon_hori_offset[t] = arccos(dot(optical_axis[t],Moon_r_H_offset_plane[t]) / (norm(optical_axis[t])*norm(Moon_r_H_offset_plane[t]))) /pi*180
        
        "Get the offset angle sign correct"
        if( dot(cross(optical_axis[t],Moon_r_V_offset_plane[t]),negative_normal_orbit[t,0:3]) > 0 ):
            Moon_vert_offset[t] = -Moon_vert_offset[t]
        if( dot(cross(optical_axis[t],Moon_r_H_offset_plane[t]),r_H_offset_normal[t]) > 0 ):
            Moon_hori_offset[t] = -Moon_hori_offset[t]
        
        
        "Angle between orbital plane and moon"
        angle_between_orbital_plane_and_moon[t] = arccos( dot(r_MATS_2_Moon_norm[t], Moon_r_orbital_plane[t]) / norm(Moon_r_orbital_plane[t])) /pi*180
        
        
        if( t*timestep % log_timestep == 0 or t == 1 ):
            Logger.debug('angle_between_orbital_plane_and_moon [degrees]: '+str(angle_between_orbital_plane_and_moon[t]))
            Logger.debug('Moon_vert_offset [degrees]: '+str(Moon_vert_offset[t]))
            Logger.debug('Moon_hori_offset [degrees]: '+str(Moon_hori_offset[t]))
            
            
        
        #print('angle_between_orbital_plane_and_moon = ' + str(angle_between_orbital_plane_and_moon[t]))
        
        if(t != 0):
            "Check that the Moon is entering V-offset degrees and within the H-offset angle"
            if( Moon_vert_offset[t] <= V_offset and Moon_vert_offset[t-1] > V_offset and abs(Moon_hori_offset[t]) < H_offset):
                
                Logger.debug('')
                Logger.debug('!!!!!!!!Moon available!!!!!!!!!!')
                Logger.debug('t (loop iteration number): '+str(t))
                Logger.debug('Current time: '+str(current_time))
                Logger.debug('Orbital Period in s: '+str(MATS_P[t]))
                Logger.debug('Vector to MATS [km]: '+str(r_MATS[t,0:3]))
                Logger.debug('Latitude in radians: '+str(lat_MATS[t]))
                Logger.debug('Longitude in radians: '+str(long_MATS[t]))
                
                if( yaw_correction == True):
                    Logger.debug('ascending_node: '+str(ascending_node))
                    Logger.debug('arg_of_lat [degrees]: '+str(arg_of_lat))
                    Logger.debug('yaw_offset_angle [degrees]: '+str(yaw_offset_angle))
                
                
                
                Logger.debug('angle_between_orbital_plane_and_moon [degrees]: '+str(angle_between_orbital_plane_and_moon[t]))
                Logger.debug('Moon_vert_offset [degrees]: '+str(Moon_vert_offset[t]))
                Logger.debug('Moon_hori_offset [degrees]: '+str(Moon_hori_offset[t]))
                Logger.debug('normal_orbit: '+str(-negative_normal_orbit[t,0:3]))
                Logger.debug('r_V_offset_normal: '+str(r_V_offset_normal[t,0:3]))
                Logger.debug('r_H_offset_normal: '+str(r_H_offset_normal[t,0:3]))
                Logger.debug('optical_axis: '+str(optical_axis[t,0:3]))
                
                Logger.debug('')
                
                
                SpottedMoonList.append({ 'Date': str(current_time), 'V-offset': Moon_vert_offset[t], 'H-offset': Moon_hori_offset[t], 
                                  'long_MATS': float(long_MATS[t]), 'lat_MATS': float(lat_MATS[t]), 'Dec': Dec_Moon, 'RA': RA_Moon,
                                   'Dec FOV': Dec_optical_axis[t], 'RA FOV': RA_optical_axis[t]})
                
                Logger.debug('Jump ahead half an orbit in time')
                "Skip ahead half an orbit"
                current_time = ephem.Date(current_time+ephem.second*MATS_P[t]/2)
                Logger.debug('Current time: '+str(current_time))
                Logger.debug('')
            
        
        "To be able to make time skips when the moon is far outside the orbital plane of MATS"
        if( (angle_between_orbital_plane_and_moon[t] > H_offset and yaw_correction == False) or 
           angle_between_orbital_plane_and_moon[t] > H_offset+abs(Timeline_settings['yaw_amplitude']) and yaw_correction == True):
            
            
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
    Logger.debug('SpottedMoonList: '+str(SpottedMoonList))
    
    
    
    return SpottedMoonList



###############################################################################################
###############################################################################################



def date_select(Occupied_Timeline, SpottedMoonList):
    """Subfunction, Schedules a simulated date.
    
    A date is selected for which the Moon is visible at an minimum amount of H-offset in the FOV.
    If the date is occupied a date will be selected with the 2nd least amount of H-offset and so on.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes together with their start and end time in a list. The list is empty if the Mode is unscheduled.
        SpottedMoonList ((:obj:`list` of :obj:`dict`)): A list containing dictionaries containing parameters for each time the Moon is spotted.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    Logger.info('Start of filtering function')
    
    Mode124_settings = OPT_Config_File.Mode124_settings()
    
    if( len(SpottedMoonList) == 0):
        
        comment = 'Moon not visible (SpottedMoonList is empty)'
        Logger.warning('')
        Logger.warning(comment)
        #input('Enter anything to acknowledge and continue\n')
        return Occupied_Timeline, comment
    
    Moon_H_offset = [SpottedMoonList[x]['H-offset'] for x in range(len(SpottedMoonList))]
    Moon_V_offset = [SpottedMoonList[x]['V-offset'] for x in range(len(SpottedMoonList))]
    Moon_date = [SpottedMoonList[x]['Date'] for x in range(len(SpottedMoonList))]
    MATS_long = [SpottedMoonList[x]['long_MATS'] for x in range(len(SpottedMoonList))]
    MATS_lat = [SpottedMoonList[x]['lat_MATS'] for x in range(len(SpottedMoonList))]
    
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
        
        endDate = ephem.Date(date+ephem.second*(Mode124_settings['freeze_start'] + Mode124_settings['freeze_duration'] + OPT_Config_File.Timeline_settings()['mode_separation']) )
        
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
        
    comment = ('V-offset: '+str(round(Moon_V_offset[x][0],2))+', H-offset: '+str(round(Moon_H_offset[x][0],2))+', Times date changed: '+str(iterations)+
                                      ', MATS (long,lat) in degrees = ('+str(round(MATS_long[x],2))+', '+str(round(MATS_lat[x],2))+'), Moon Dec (J2000) [degrees]: '+
                                      str(round(SpottedMoonList[x]['Dec'],2))+', Moon RA (J2000) [degrees]: '+str(round(SpottedMoonList[x]['RA'],2))+', OpticalAxis Dec = '+str(round(SpottedMoonList[x]['Dec FOV'][0],2))+
                                      ', Optical Axis RA = '+str(round(SpottedMoonList[x]['RA FOV'][0],2)) )
    
    
    Occupied_Timeline['Mode124'].append( (date, endDate) )
    
    return Occupied_Timeline, comment
