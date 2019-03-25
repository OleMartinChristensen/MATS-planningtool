# -*- coding: utf-8 -*-
"""
Contains settings for the Operational Planning Tool
@author: David
"""

import ephem

def Logger_name():
    "Names the shared logger"
    Logger_name = "OPT_logger"
    
    return Logger_name

def Version():
    "Names this version of the Config_File used"
    version_name = 'Original'
    return version_name

def Modes_priority():
    '''
    Creates List of Modes (except 1-4) to be schedueled, the order of which they appear is their priority order.
    The name must be equal to the name of the top function in the OPT_Timeline_Generator_ModeX module, where X is any mode.
    '''
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

def initialConditions():
    '''
    Sets inital conditions for the initialConditions container in the XML-file
    '''
    InitialConditions = { 'spacecraft': {'mode': 'Normal', 'acs': 'Normal'}, 'payload': { 'power': 'On' , 'mode': ''} }
    return InitialConditions

def Timeline_settings():
    '''
    start_time: Sets the starting date of the timeline as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40'))
    duration: Sets the duration in seconds of the timeline
    leap_seconds: Sets the amount of leap seconds for GPS time to be used
    GPS_epoch: Sets the epoch of the GPS time in ephem.Date format (example: ephem.Date('1980/1/6'))
    mode_separation: Sets in seconds the amount of time set at the end of a Mode (still counts to mode run time) where nothing new is ran. 
                    Meaning the minimum amount of time from a command of the current Mode to the start of a new Mode. Meaning that
                    the total schedueled duration of a mode is equal to "mode_duration"+"mode_separation" but no new commands will be given
                    for a duration equal to "mode_separation" at the end of each schedueled mode.
    mode_duration: Sets the amount of time scheduled for modes which do not have their own respective duration settings
    yaw_correction: Decides if Mode1/2 or Mode3/4 are to be scheduled. Set to 1 for Mode3/4, set to 0 for Mode1/2
    command_separation: Minimum ammount of time inbetween scheduled commands [s].
    '''
    timeline_settings = {'start_time': ephem.Date('2018/9/3 08:00:40'), 'duration': 1*4*3600, 
                       'leap_seconds': 18, 'GPS_epoch': ephem.Date('1980/1/6'), 'mode_separation': 300,
                       'mode_duration': 900, 'yaw_correction': 0, 'command_separation': 0.1}
    return timeline_settings

def Mode1_settings():
    '''
    lat: Sets in degrees the latitude (+ and -) that the LP crosses that causes NLC mode to swith on/off
    pointing_altitude: Sets in meters the altitude of the pointing command
    log_timestep: Sets the frequency of data being logged [s]
    '''
    settings = {'lat': 45, 'pointing_altitude': 92000, 'log_timestep': 800}
    return settings

def Mode2_settings():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    log_timestep: Sets the frequency of data being logged [s]
    '''
    settings = {'pointing_altitude': 92000, 'log_timestep': 800}
    return settings

def Mode110_settings():
    '''
    mode_duration: Sets the scheduled duration of the Mode in seconds
    '''
    settings = {'mode_duration': 900}
    return settings

'''
def Mode120_calculator_defaults():
    
        default_pointing_altitude: Sets altitude in meters of LP that will set the pitch angle of the optical axis, 
        H_FOV: Sets Horizontal FOV of optical axis in degrees that will determine if stars are visible
        V_FOV: Sets Vertical FOV of optical axis in degrees that will determine if stars are visible
        Vmag: Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2')
        timestep: sets timestep used in simulation [s]
        log_timestep: Sets the frequency of data being logged [s]
    
    settings = {'default_pointing_altitude': 92000, 'H_FOV': 5, 'V_FOV': 0.8+3*2-0.8, 'Vmag': '<2', 'timestep': 2,'log_timestep': 3600}
    return settings
'''

def Mode120_settings():
    ### Simulation related settings ###
    '''
    default_pointing_altitude: Sets altitude in meters of LP that will set the pitch angle of the optical axis, 
    H_FOV: Sets Horizontal FOV of optical axis in degrees that will determine if stars are visible
    V_FOV: Sets Vertical FOV of optical axis in degrees that will determine if stars are visible
    Vmag: Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2')
    timestep: sets timestep used in simulation [s]
    log_timestep: Sets the frequency of data being logged [s]
    automatic: Sets if the mode date is to be calculated or user provided. 1 for calculated or anything else for user provided.
    date: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40'). Note! only applies if automatic is not set to 1.
    mode_duration: Sets the scheduled duration of the Mode in seconds
    '''
    ### Commands related settings ###
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    freeze_start: Sets in seconds the time from start of the Mode to when the attitude freezes
    freeze_duration: Sets in seconds the duration of the attitude freeze
    '''
    settings = {'default_pointing_altitude': 92000, 'H_FOV': 5, 'V_FOV': 0.8+3*2-0.8, 'Vmag': '<2', 'timestep': 2,'log_timestep': 3600, 
                      'automatic': 1, 'date': ephem.Date('2019'), 'mode_duration': 900, 'pointing_altitude': 227000, 'freeze_start': 300, 
                      'freeze_duration': 300}
    return settings

def Mode130_settings():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    mode_duration: Sets the scheduled duration of the Mode in seconds
    '''
    settings = {'pointing_altitude': 200000, 'mode_duration': 900}
    return settings

'''
def Mode200_calculator_defaults():
    
    default_pointing_altitude: Sets altitude in meters of LP that will set the pitch angle of the optical axis, 
    H_FOV: Sets Horizontal FOV of optical axis in degrees that will determine the Moon is visible
    V_FOV: Sets Vertical FOV of optical axis in degrees that will determine the Moon is visible
    timestep: Sets in seconds the timestep of the simulation when larger timeskips (Moon determined far out of sight) are not made 
    log_timestep: Sets the frequency of data being logged [s]
    
    settings = {'default_pointing_altitude': 92000, 'H_FOV': 5+3*2, 'V_FOV': 0.8+3*2-0.8, 'timestep': 2, 'log_timestep': 1200}
    return settings
'''

def Mode200_settings():
    ### Simulation related settings ###
    '''
    default_pointing_altitude: Sets altitude in meters of LP that will set the pitch angle of the optical axis, 
    H_FOV: Sets Horizontal FOV of optical axis in degrees that will determine the Moon is visible
    V_FOV: Sets Vertical FOV of optical axis in degrees that will determine the Moon is visible
    timestep: Sets in seconds the timestep of the simulation when larger timeskips (Moon determined far out of sight) are not made 
    log_timestep: Sets the frequency of data being logged [s]
    automatic: Sets if the mode date is to be calculated or user provided. 1 for calculated or anything else for user provided.
    date: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40'). Note! only applies if automatic is not set to 1.
    mode_duration: Sets the scheduled duration of the Mode in seconds
    '''
    ### Commands related settings ###
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    freeze_start: Sets in seconds the time from start of the Mode to when the attitude freeze command is scheduled
    freeze_duration: Sets in seconds the duration of the attitude freeze
    '''
    settings = {'default_pointing_altitude': 92000, 'H_FOV': 5+3*2, 'V_FOV': 0.8+3*2-0.8, 'timestep': 2, 'log_timestep': 1200, 
                      'automatic': 1, 'date': ephem.Date('2019'), 'mode_duration': 900, 'pointing_altitude': 227000, 'freeze_start': 300, 'freeze_duration': 300}
    return settings
