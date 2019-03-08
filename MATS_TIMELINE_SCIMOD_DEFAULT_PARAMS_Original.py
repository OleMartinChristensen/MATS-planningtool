# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 14:33:11 2019

Contains default values for parameters. This is the original default_params file and not supposed to be ran.
@author: David
"""

import ephem

def Logger_name():
    "Names the shared logger"
    Logger_name = "Timeline-gen_logger"
    return Logger_name

def Version():
    "Names this version of the Default_Params used"
    version_name = 'Original'
    return version_name

def Mode120_calculator_defaults():
    '''default_pointing_altitude: Sets altitude in meters of LP that will set the pitch angle of the optical axis, 
        H_FOV: Sets Horizontal FOV of optical axis in degrees that will determine if stars are visible
        V_FOV: Sets Vertical FOV of optical axis in degrees that will determine if stars are visible
        Vmag: Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2')
        timestep: sets timestep used in simulation [s]
    '''
    params_default = {'default_pointing_altitude': 92000, 'H_FOV': 5, 'V_FOV': 0.8+3*2-0.8, 'Vmag': '<2', 'timestep': 2}
    return params_default

def Mode120_default():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    freeze_start: Sets in seconds the time from start of the Mode to when the attitude freezes
    freeze_duration: Sets in seconds the duration of the attitude freeze
    mode_duration: Sets the duration of the Mode in seconds
    '''
    params_default = {'pointing_altitude': 227000, 'freeze_start': 300, 'freeze_duration': 300, 'mode_duration': 900}
    return params_default

def Mode130_default():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    mode_duration: Sets the duration of the Mode in seconds
    '''
    params_default = {'pointing_altitude': 200000, 'mode_duration': 900}
    return params_default

def Mode1_default():
    '''
    lat: Sets in degrees the latitude (+ and -) that MATS crosses that causes the nadir to swith on/off
    pointing_altitude: Sets in meters the altitude of the pointing command
    '''
    params_default = {'lat': 45, 'pointing_altitude': 92000}
    return params_default

def Mode200_calculator_defaults():
    '''
    default_pointing_altitude: Sets altitude in meters of LP that will set the pitch angle of the optical axis, 
    H_FOV: Sets Horizontal FOV of optical axis in degrees that will determine the Moon is visible
    V_FOV: Sets Vertical FOV of optical axis in degrees that will determine the Moon is visible
    timestep: Sets in seconds the timestep of the simulation when larger timeskips (Moon determined far out of sight) are not made 
    '''
    params_default = {'default_pointing_altitude': 92000, 'H_FOV': 5+3*2, 'V_FOV': 0.8+3*2-0.8, 'timestep': 2}
    return params_default

def Mode200_default():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    freeze_start: Sets in seconds the time from start of the Mode to when the attitude freezes
    freeze_duration: Sets in seconds the duration of the attitude freeze
    mode_duration: Sets the duration of the Mode in seconds
    '''
    params_default = {'pointing_altitude': 227000, 'freeze_start': 300, 'freeze_duration': 300, 'mode_duration': 900}
    return params_default

def Mode2_default():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    '''
    params_default = {'pointing_altitude': 92000}
    return params_default

def Timeline_params():
    '''
    start_time: Sets the starting date of the timeline as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40'))
    duration: Sets the duration in seconds of the timeline
    leap_seconds: Sets the amount of leap seconds for GPS time to be used
    GPS_epoch: Sets the epoch of the GPS time in ephem.Date format (example: ephem.Date('1980/1/6'))
    mode_separation: Sets in seconds the amount of time set at the end of a Mode (still counts to mode run time) where nothing new is ran. 
                    Meaning the minimum amount of time from a command of the current Mode to the start of a new Mode. Meaning that
                    the total schedueled duration of a mode is equal to "mode_duration"+"mode_separation" but no new commands will be given
                    for a duration equal to "mode_separation" at the end of each schedueled mode.
    '''
    timeline_params = {'start_time': ephem.Date('2018/9/3 08:00:40'), 'duration': 1*4*3600, 
                       'leap_seconds': 18, 'GPS_epoch': ephem.Date('1980/1/6'), 'mode_separation': 300}
    return timeline_params

def initialConditions():
    '''
    Sets inital conditions for the initialConditions container in the XML-file
    '''
    InitialConditions = { 'spacecraft': {'mode': 'Normal', 'acs': 'Normal'}, 'payload': { 'power': 'On' , 'mode': ''} }
    return InitialConditions

def Modes_priority():
    "Creates List of Modes (except 1-4) to be schedueled, the order of which they appear is their priority order"
    Modes_priority = [
            'Mode130', 
          'Mode200',
          'Mode120']
    return Modes_priority

def getTLE():
    "Sets values of the two TLE rows that are to be used"
    TLE1 = '1 26702U 01007A   18231.91993126  .00000590  00000-0  00000-0 0  9994'
    TLE2= '2 26702 97.61000 65.95030 0000001 0.000001 359.9590 14.97700580100  4'
    #TLE1 = '1 26702U 01007A   09264.68474097 +.00000336 +00000-0 +35288-4 0  9993'
    #TLE2 = '2 26702 097.7067 283.5904 0004656 126.2204 233.9434 14.95755636467886'
    return [TLE1, TLE2]