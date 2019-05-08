# -*- coding: utf-8 -*
"""Contains functions used by the Operational Planning Tool .
"""

import ephem
from pylab import cos, sin, sqrt, array, arccos, pi, floor, around

import OPT_Config_File


def rot_arbit(angle, u_v):
    """Takes an angle in radians and a unit vector and outputs a rotation matrix around that vector"
    
    Arguments:
        angle (int): Angle in radians.
        u_v (list): Unit vector
        
    Returns:
        (array): Rotation matrix
    
    """
    
    rot_mat = array([(cos(angle)+u_v[0]**2*(1-cos(angle)), \
    u_v[0]*u_v[1]*(1-cos(angle))-u_v[2]*sin(angle), \
    u_v[0]*u_v[2]*(1-cos(angle))+u_v[1]*sin(angle)), \
    \
    (u_v[1]*u_v[0]*(1-cos(angle))+u_v[2]*sin(angle), \
    cos(angle)+u_v[1]**2*(1-cos(angle)), \
    u_v[1]*u_v[2]*(1-cos(angle))-u_v[0]*sin(angle)), \
    \
    (u_v[2]*u_v[0]*(1-cos(angle))-u_v[1]*sin(angle), \
    u_v[2]*u_v[1]*(1-cos(angle))+u_v[0]*sin(angle), \
    cos(angle)+u_v[2]**2*(1-cos(angle)))])
    
    return rot_mat

def deg2HMS(ra='', dec='', roundOf=False):
    """Takes a declination or a RAAN angle in degrees and converts it to DMS or HMS format respectively
    
    Only one (and only one!) of the inputs (ra or dec) shall be provided.
    
    Arguments:
        ra (str): RAAN angle in degrees.
        dec (str): Declination angle in degrees.
        roundOf (bool): True for rounding of seconds to nearest integer. False for seconds with decimals.
        
    Returns:
        (str): RAAN or Declination angle in HMS format.
        
    """
    
    RA, DEC, rs, ds = '', '', '', ''
    
    if dec:
        if str(dec)[0] == '-':
            ds, dec = '-', abs(dec)
        deg = int(dec)
        decM = abs(int((dec-deg)*60))
        if roundOf:
            decS = int((abs((dec-deg)*60)-decM)*60)
        else:
            decS = (abs((dec-deg)*60)-decM)*60
        DEC = '{0}{1} {2} {3}'.format(ds, deg, decM, decS)
        
    elif ra:
        if str(ra)[0] == '-':
            rs, ra = '-', abs(ra)
        raH = int(ra/15)
        raM = int(((ra/15)-raH)*60)
        if roundOf:
            raS = int(((((ra/15)-raH)*60)-raM)*60)
        else:
            raS = ((((ra/15)-raH)*60)-raM)*60
        RA = '{0}{1} {2} {3}'.format(rs, raH, raM, raS)
        
    return RA or DEC


def lat_2_R( lat ):
    """Takes a geocentric latitude in radians and puts out the distance from the center of a spheroid Earth to the surface
    
    Arguments:
        lat (float): Latitude angle in radians
        
    Returns:
        (float): Geocentric distance [km]
        
    """
    
    R_polar = 6356.752314245
    R_eq = 6378.137
    
    R = sqrt( ( (R_eq**2*cos(lat))**2 + (R_polar**2*sin(lat))**2 ) / ( (R_eq*cos(lat))**2 + (R_polar*sin(lat))**2 ) )
    
    return R

def scheduler(Occupied_Timeline, date, endDate):
    ''' Function that checks if the scheduled time is available and postpones it otherwise. 
    
    If scheduled time is occupied, it gets postponed with mode_separation*2 seconds (defined in Config_File.Timeline_settings) until available.
    
    Arguments:
        Occupied_Timeline (dict): A dictionary of all planned Modes (except 1-4) containing lists with their scheduled times ([startDate, endDate]) as ephem.Date class.
        date (:obj:`ephem.Date`): The scheduled startdate of the current Mode.
        endDate (:obj:`ephem.Date`): The scheduled end-date of the current Mode.
    
    Returns: 
        date; The scheduled startdate (potentially postponed) of the current Mode as a ephem.Date object.
        
        endDate; The scheduled end-date (potentially postponed) of the current Mode as a ephem.Date object.
        
        iterations; The number of times the scheduled date got postponed. (int)
        
    '''
    
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    iterations = 0
    restart = True
    ## Checks if date is available and postpones starting date of mode until available
    while( restart == True):
        restart = False
        
        "Extract the start and end dates of scheduled mode"
        for busy_dates in Occupied_Timeline.values():
            if( busy_dates == []):
                continue
            else:
                
                "Extract the start and end date of each instance of a scheduled mode"
                for busy_date in busy_dates:
                    
                    "If the planned date collides with any already scheduled ones -> post-pone and restart loop"
                    if( busy_date[0] <= date < busy_date[1] or 
                           busy_date[0] < endDate <= busy_date[1] or
                           (date < busy_date[0] and endDate > busy_date[1])):
                        
                        date = ephem.Date(date + ephem.second*Timeline_settings['mode_separation']*2)
                        endDate = ephem.Date(endDate + ephem.second*Timeline_settings['mode_separation']*2)
                        
                        iterations = iterations + 1
                        restart = True
                        break
                
    return date, endDate, iterations


def FreezeDuration_calculator(pointing_altitude1, pointing_altitude2):
    '''Function that calculates the angle between two tangential altitudes and then calculates
    the time it takes for orbital position angle of a satellite in a circular orbit to change by the same amount.
    
    Arguments:
        pointing_altitude1 (int): First tangential pointing altitude in m
        pointing_altitude2 (int): Second tangential pointing altitude in m
        
    Returns:
        (int): FreezeDuration, Time [s] it takes for the satellites orbital position angle to change 
        by the same amount as the angle between the two tangential pointing altitudes as seen from the satellite.
    '''
    
    TLE2 = OPT_Config_File.getTLE()[1] #Orbits per day
    U = 398600.4418 #Earth gravitational parameter
    MATS_P = 24*3600/float(TLE2[52:63]) #Orbital Period of MATS [s]
    MATS_p = ((MATS_P/2/pi)**2*U)**(1/3) #Semi-major axis of MATS assuming circular orbit [km]
    R_mean = 6371 #Mean Earth radius [km]
    pitch1 = arccos((R_mean+pointing_altitude1/1000)/(MATS_p))/pi*180
    pitch2 = arccos((R_mean+pointing_altitude2/1000 )/(MATS_p))/pi*180
    pitch_angle_difference = abs(pitch1 - pitch2)
    
    #The time it takes for the orbital position angle to change by the same amount as
    #the angle between the pointing axes
    FreezeDuration = round(MATS_P*(pitch_angle_difference)/360,1)
    
    return FreezeDuration



def params_checker(dict1, dict2):
    """Function which compares the keys of two dictionaries and outputs a new dictionary. 
    
    A dict_new will be created containing all the keys and values of dict2. Then for any keys that 
    exist in both dict1 and dict_new, dict_new's keys will have their values replaced by the ones in dict1.
    
    WARNING! All keys in dict1 must also exist in dict2.
    
    Arguments:
        dict1 (dict): 
        dict2 (dict): 
    
    Returns:
        (dict): 
        
    """
    
    
    "Check if optional params were given"
    if( dict1 != dict2):
        dict_new = dict2
        "Loop through parameters given and exchange the settings ones"
        for key in dict1.keys():
            dict_new[key] = dict1[key]
    else:
        dict_new = dict1
        
    return dict_new

def utc_to_onboardTime(utc_date):
    """Function which converts a date in utc into onboard time in seconds.
    
    Arguments:
        utc_date (:obj:`ephem.Date`): The date as a ephem.Date class.
    
    Returns:
        (int): Onboard Time in seconds
        
    """
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    GPS_epoch = ephem.Date(Timeline_settings['GPS_epoch'])
    leapSeconds = ephem.second*Timeline_settings['leap_seconds']
    
    GPS_date = utc_date+leapSeconds-GPS_epoch
    
    onboardTime = around(GPS_date / ephem.second, 1)
    '''
    GPS_week = floor(GPS_date/7)
    
    onboardTime = around( (GPS_date/7 - GPS_week) / ephem.second, 1 )
    '''
    return onboardTime