# -*- coding: utf-8 -*-
"""
Contains settings for the Operational Planning Tool
@author: David
"""

import ephem
from Operational_Planning_Tool.OPT_library import FreezeDuration_calculator

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
    The name must be equal to the name of the top function in the OPT_Timeline_generator_ModeX module, where X is any mode.
    '''
    Modes_priority = [
            'Mode130', 
          'Mode200',
          'Mode120',
          'Mode121',
          'Mode110',
          'Mode100',
          'Mode132',
          'Mode122',
          'Mode131']
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
    mode_separation: Separates the scheduling of Modes 1-4 and the start of a new mode by this amount [s].
                        Is also used as an extra term in the calculations of the duration of other modes to act as an prolonged buffer.
                        Meaning that whenever mode_duration is calculated it is equal to an calculated estimation of the modes duration plus "mode_separation"
    mode_duration: Sets the amount of time scheduled for modes which do not have their own respective duration settings
    yaw_correction: Decides if Mode1/2 or Mode3/4 are to be scheduled. Set to 1 for Mode3/4, set to 0 for Mode1/2
    command_separation: Minimum ammount of time inbetween scheduled commands [s].
    pointing_stabilization: Extra time [s] scheduled for fixed pointing commands before new commands are allowed.
    '''
    timeline_settings = {'start_time': ephem.Date('2018/9/3 08:00:40'), 'duration': 1*7*3600, 
                       'leap_seconds': 18, 'GPS_epoch': ephem.Date('1980/1/6'), 'mode_separation': 120,
                       'mode_duration': 900, 'yaw_correction': 0, 'command_separation': 0.1, 'pointing_stabilization': 60}
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

def Mode100_settings():
    '''
    pointing_altitude_from: Sets in meters the starting altitude
    pointing_altitude_to: Sets in meters the ending altitude
    pointing_altitude_interval: Sets in meters the interval size of each succesive pointing
    pointing_duration: Sets the time [s] from attitude stabilization until next pointing command
    
    Args:
        None
    Returns:
        settings (dict)
    '''
    settings = {'pointing_altitude_from': 10000, 'pointing_altitude_to': 150000, 
                'pointing_altitude_interval': 5000, 'pointing_duration': 10}
    return settings

def Mode110_settings():
    '''
    pointing_altitude_from: Sets in meters the starting altitude of the sweep
    pointing_altitude_to: Sets in meters the ending altitude of the sweep
    sweep_rate: Sets in meters rate of the sweep
    sweep_start: Sets in seconds the time from start of the Mode to when the sweep starts
    
    Args:
        None
    Returns:
        settings (dict)
    '''
    settings = {'pointing_altitude_from': 10000, 'pointing_altitude_to': 150000, 'sweep_rate': 500, 'sweep_start': 120}
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
    pointing_altitude: Sets in meters the altitude of the pointing command
    V_offset: Sets the V-offset of the star (when pointing towards pointing_altitude) for when the attitude freeze command is scheduled
    H_offset: Sets the maximum H-offset angle from the optical axis (angle away from orbital plane) in degrees that determines if stars are available
    Vmag: Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2')
    timestep: sets timestep used in simulation [s].
    log_timestep: Sets the frequency of data being logged [s]
    automatic: Sets if the mode date is to be calculated or user provided. 1 for calculated or anything else for user provided.
    date: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40'). Note! only applies if automatic is not set to 1.
    mode_duration: Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated.
    '''
    ### Commands related settings ###
    '''
    LP_pointing_altitude: Sets altitude of LP in meters
    freeze_start: Sets in seconds the time from start of the Mode to when the attitude freezes
    freeze_duration: Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a value corresponding to the attitude being frozen until realigned with LP_pointing_altitude.
    '''
    settings = {'pointing_altitude': 227000, 'V_offset': 0, 'H_offset': 2.5, 'Vmag': '<2', 'timestep': 2,'log_timestep': 3600, 
                      'automatic': 1, 'date': ephem.Date('2019'), 'mode_duration': 0, 'LP_pointing_altitude': 92000, 'freeze_start': 300, 
                      'freeze_duration': 0}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( settings['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings

def Mode121_settings():
    ### Simulation related settings ###
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    H_FOV: Sets full Horizontal FOV of the Limb instrument in degrees
    V_FOV: Sets full Vertical FOV of the Limb instrument in degrees
    Vmag: Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2')
    timestep: sets timestep used in simulation [s]
    log_timestep: Sets the frequency of data being logged [s]
    automatic: Sets if the mode date is to be calculated or user provided. 1 for calculated or anything else for user provided.
    date: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40'). Note! only applies if automatic is not set to 1.
    mode_duration: Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated.
    '''
    ### Commands related settings ###
    '''
    LP_pointing_altitude: Sets altitude of LP in meters
    freeze_start: Sets in seconds the time from start of the Mode to when the attitude freezes
    freeze_duration: Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a value corresponding to the attitude being frozen until realigned with LP_pointing_altitude.
    '''
    settings = {'pointing_altitude': 227000, 'H_FOV': 5.67, 'V_FOV': 0.91, 'Vmag': '<4', 'timestep': 5,'log_timestep': 3600, 
                      'automatic': 1, 'date': ephem.Date('2019'), 'mode_duration': 0, 'LP_pointing_altitude': 92000, 'freeze_start': 300, 
                      'freeze_duration': 0}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( settings['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings


def Mode122_settings():
    ### Simulation related settings ###
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    H_FOV: Sets full Horizontal FOV of the Limb instrument in degrees
    V_FOV: Sets full Vertical FOV of the Limb instrument in degrees
    Vmag: Sets the Johnson V magnitude of stars to be considered (as a string expression, example '<2')
    timestep: sets timestep used in simulation [s]
    log_timestep: Sets the frequency of data being logged [s]
    automatic: Sets if the mode date is to be calculated or user provided. 1 for calculated or anything else for user provided.
    date: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40'). Note! only applies if automatic is not set to 1.
    mode_duration: Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated.
    ExpTimes: Sets exposure times [s] as a integer list and the exposure intervall (ExpInt = ExpTime + 1).
    '''
    ### Commands related settings ###
    '''
    LP_pointing_altitude: Sets altitude of LP in meters
    freeze_start: Sets in seconds the time from start of the Mode to when the attitude freezes
    freeze_duration: Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a value corresponding to the attitude being frozen until realigned with LP_pointing_altitude.
    '''
    settings = {'pointing_altitude': 227000, 'H_FOV': 5.67, 'V_FOV': 0.91, 'Vmag': '<4', 'timestep': 5,'log_timestep': 3600, 
                      'automatic': 1, 'date': ephem.Date('2019'), 'mode_duration': 0, 'LP_pointing_altitude': 92000, 'freeze_start': 300, 
                      'freeze_duration': 0, 'ExpTimes': [1000, 3000, 5000, 10000, 20000], 'session_duration': 120}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( settings['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings


def Mode130_settings():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    mode_duration: Sets the scheduled duration of the Mode in seconds
    start_time: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40').
    '''
    settings = {'pointing_altitude': 200000, 'mode_duration': 900, 'start_time': ephem.Date('2018/9/3 12:00:40')}
    return settings

def Mode131_settings():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    mode_duration: Sets the scheduled duration of the Mode in seconds
    start_time: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40').
    '''
    settings = {'pointing_altitude': 200000, 'mode_duration': 900, 'start_time': ephem.Date('2018/9/3 12:00:40')}
    return settings

def Mode132_settings():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    start_time: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40').
    ExpTimes: Sets exposure times [s] as a integer list and the exposure intervall (ExpInt = ExpTime + 1).
    session_duration: Sets the duration [s] of each session using the different exposure times in ExpTimes.
    '''
    settings = {'pointing_altitude': 200000, 'start_time': ephem.Date('2018/9/3 12:00:40'), 'ExpTimes': [1000, 3000, 5000, 10000, 20000], 'session_duration': 120}
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
    pointing_altitude: Sets in meters the altitude of the pointing command
    V_offset: Sets the V-offset of the Moon (when pointing towards pointing_altitude) for when the attitude freeze command is scheduled
    H_offset: Sets the maximum H-offset angle from the optical axis in degrees that determines if the Moon is available
    timestep: Sets in seconds the timestep of the simulation when larger timeskips (Moon determined far out of sight) are not made 
    log_timestep: Sets the frequency of data being logged [s]
    automatic: Sets if the mode date is to be calculated or user provided. 1 for calculated or anything else for user provided.
    date: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40'). Note! only applies if automatic is not set to 1.
    mode_duration: Sets the scheduled duration of the Mode in seconds. If set to 0 it is calculated.
    '''
    ### Commands related settings ###
    '''
    LP_pointing_altitude: Sets altitude of LP in meters
    freeze_start: Sets in seconds the time from start of the Mode to when the attitude freeze command is scheduled
    freeze_duration: Sets in seconds the duration of the attitude freeze. If set to 0, it will be estimated to a value corresponding to the attitude being frozen until realigned with LP_pointing_altitude.
    '''
    settings = {'pointing_altitude': 227000, 'V_offset': 0, 'H_offset': 3+2.5, 'timestep': 2, 'log_timestep': 1200, 
                      'automatic': 1, 'date': ephem.Date('2019'), 'mode_duration': 0, 'LP_pointing_altitude': 92000, 'freeze_start': 300, 'freeze_duration': 0}
    
    if( settings['freeze_duration'] == 0):
        settings['freeze_duration'] = FreezeDuration_calculator( settings['LP_pointing_altitude'], settings['pointing_altitude'])
    if( settings['mode_duration'] == 0):
        settings['mode_duration'] = settings['freeze_start'] + settings['freeze_duration'] + Timeline_settings()['mode_separation']
    
    return settings


def Mode201_settings():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    mode_duration: Sets the scheduled duration of the Mode in seconds
    start_time: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40').
    '''
    settings = {'pointing_altitude': 70000}
    return settings


def Mode203_settings():
    '''
    pointing_altitude: Sets in meters the altitude of the pointing command
    mode_duration: Sets the scheduled duration of the Mode in seconds
    start_time: Sets the scheduled date for the mode as a ephem.Date (example: ephem.Date('2018/9/3 08:00:40').
    '''
    settings = {'pitch': 180}
    return settings
