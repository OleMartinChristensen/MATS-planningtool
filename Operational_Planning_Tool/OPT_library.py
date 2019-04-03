# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 15:10:41 2018

@author: David
"""

from pylab import cos, sin, sqrt, array

def rot_arbit(angle, u_v):
    "Takes an angle in radians and a unit vector and outputs a rotation matrix around that vector"
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

def deg2HMS(ra='', dec='', round=False):
  "Takes an declination or RAAN angle and converts it to DMS or HMS format respectively"
  RA, DEC, rs, ds = '', '', '', ''
  if dec:
    if str(dec)[0] == '-':
      ds, dec = '-', abs(dec)
    deg = int(dec)
    decM = abs(int((dec-deg)*60))
    if round:
      decS = int((abs((dec-deg)*60)-decM)*60)
    else:
      decS = (abs((dec-deg)*60)-decM)*60
    DEC = '{0}{1} {2} {3}'.format(ds, deg, decM, decS)
  
  if ra:
    if str(ra)[0] == '-':
      rs, ra = '-', abs(ra)
    raH = int(ra/15)
    raM = int(((ra/15)-raH)*60)
    if round:
      raS = int(((((ra/15)-raH)*60)-raM)*60)
    else:
      raS = ((((ra/15)-raH)*60)-raM)*60
    RA = '{0}{1} {2} {3}'.format(rs, raH, raM, raS)
  
  if ra and dec:
    return (RA, DEC)
  else:
    return RA or DEC

def lat_2_R( lat ):
    "Takes a latitude in radians and puts out the distance from the center of Earth"
    R_polar = 6356.752314245
    R_eq = 6378.137
    
    R = sqrt( ( (R_eq**2*cos(lat))**2 + (R_polar**2*sin(lat))**2 ) / ( (R_eq*cos(lat))**2 + (R_polar*sin(lat))**2 ) )
    
    return R

def scheduler(Occupied_Timeline, date, endDate):
    ''' 
    Function that checks if the scheduled time is available and postpones
    it otherwise with mode_separation (defined in OPT_Config_File.Timeline_settings) times 2.
    
    Input:
        Occupied_Timeline: A dictionary of all planned Modes (except 1-4) containing lists with their scheduled times ([startDate, endDate]) as ephem.Date class.
        date: The scheduled startdate of the current Mode as a ephem.Date class.
        endDate: The scheduled end-date of the current Mode as a ephem.Date class.
    Output: 
        date: The scheduled startdate (potentially postponed) of the current Mode as a ephem.Date class.
        endDate: The scheduled end-date (potentially postponed) of the current Mode as a ephem.Date class.
        iterations: The number of times the scheduled date got postponed as a integer class-
    '''
    
    import ephem
    from OPT_Config_File import Timeline_settings
    
    iterations = 0
    restart = True
    ## Checks if date is available and postpones starting date of mode until available
    while( restart == True):
        restart = False
        
        "Extract the start and end date of each scheduled mode"
        for busy_dates in Occupied_Timeline.values():
            if( busy_dates == []):
                continue
            else:
                "If the planned date collides with any already scheduled ones -> post-pone and restart loop"
                if( busy_dates[0] <= date < busy_dates[1] or 
                       busy_dates[0] < endDate <= busy_dates[1] or
                       (date < busy_dates[0] and endDate > busy_dates[1])):
                    
                    date = ephem.Date(date + ephem.second*Timeline_settings()['mode_separation']*2)
                    endDate = ephem.Date(endDate + ephem.second*Timeline_settings()['mode_separation']*2)
                    
                    iterations = iterations + 1
                    restart = True
                    break
                
    return date, endDate, iterations


def FreezeDuration_calculator(pointing_altitude1, pointing_altitude2):
    '''Function that calculates the angle between two tangential altitudes and then calculates
    the time it takes for orbital position angle of a satellite in a circular orbit to change by the same amount.
    
    Args:
        pointing_altitude1 (int): First tangential pointing altitude in m
        pointing_altitude2 (int): Second tangential pointing altitude in m
        
    Returns:
        FreezeDuration (int): Time [s] it takes for the satellites orbital position angle to change 
            by the amount as the angle between the two tangential pointing altitudes as seen from the satellite
    '''
    
    from OPT_Config_File import getTLE
    from pylab import arccos, pi
    
    TLE2 = getTLE()[1] #Orbits per day
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
