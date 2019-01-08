# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 15:05:39 2018
Contains default values for parameters
@author: David
"""'2018/8/22 22:00:00'

import ephem

def Mode120_calculator_defaults():
    params_default = {'default_pointing_altitude': 92000, 'H_FOV': 5, 'V_FOV': 0.8+3*2-0.8, 'Vmag': '<2'}
    return params_default

def Mode120_default():
    params_default = {'pointing_altitude': 227000, 'freeze_start': 300, 'freeze_duration': 300, 'mode_duration': 900}
    return params_default

def Mode130_default():
    params_default = {'pointing_altitude': 200000, 'mode_duration': 900}
    return params_default

def Mode1_default():
    params_default = {'lat': 45, 'pointing_altitude': 92000}
    return params_default

def Mode200_calculator_defaults():
    params_default = {'default_pointing_altitude': 92000, 'H_FOV': 5+3*2, 'V_FOV': 0.8+3*2-0.8, 'timestep': 2}
    return params_default

def Mode200_default():
    params_default = {'pointing_altitude': 227000, 'freeze_start': 300, 'freeze_duration': 300, 'mode_duration': 900}
    return params_default

def Mode2_default():
    params_default = {'pointing_altitude': 92000}
    return params_default

def Timeline_params():
    timeline_params = {'start_time': ephem.Date('2018/9/3 08:00:40'), 'duration': 1*12*3600, 
                       'leap_seconds': 18, 'GPS_epoch': ephem.Date('1980/1/6'), 'mode_separation': 300}
    return timeline_params

def initialConditions():
    InitialConditions = { 'spacecraft': {'mode': 'Normal', 'acs': 'Normal'}, 'payload': { 'power': 'On' , 'mode': ''} }
    return InitialConditions

def Modes_priority():
    "Creates List of Modes (except 1-4) to be ran, the order of which they appear is their priority order"
    Modes_priority = [
            'Mode130', 
          'Mode200',
          'Mode120']
    return Modes_priority

def getTLE():
    TLE1 = '1 26702U 01007A   18231.91993126  .00000590  00000-0  00000-0 0  9994'
    TLE2= '2 26702 97.61000 65.95030 0000001 0.000001 359.9590 14.97700580100  4'
    #TLE1 = '1 26702U 01007A   09264.68474097 +.00000336 +00000-0 +35288-4 0  9993'
    #TLE2 = '2 26702 097.7067 283.5904 0004656 126.2204 233.9434 14.95755636467886'
    return [TLE1, TLE2]