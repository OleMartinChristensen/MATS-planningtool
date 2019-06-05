# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 13:37:48 2019

@author: David
"""

import importlib, logging, sys, ephem

from Operational_Planning_Tool import _Globals, _Library
OPT_Config_File = importlib.import_module(_Globals.Config_File)

Logger = logging.getLogger(OPT_Config_File.Logger_name())

def CheckConfigFile():
    
    _Library.SetupLogger()
    
    Timeline_settings = OPT_Config_File.Timeline_settings()
    Mode_1_2_3_4_settings = OPT_Config_File.Mode_1_2_3_4_settings()
    Mode100_settings = OPT_Config_File.Mode100_settings()
    Mode110_settings = OPT_Config_File.Mode110_settings()
    Mode120_settings = OPT_Config_File.Mode120_settings()
    Mode121_settings = OPT_Config_File.Mode121_settings()
    Mode122_settings = OPT_Config_File.Mode122_settings()
    Mode123_settings = OPT_Config_File.Mode123_settings()
    Mode121_122_123_settings = OPT_Config_File.Mode121_122_123_settings()
    Mode124_settings = OPT_Config_File.Mode124_settings()
    Mode130_settings = OPT_Config_File.Mode130_settings()
    Mode131_settings = OPT_Config_File.Mode131_settings()
    Mode132_settings = OPT_Config_File.Mode132_settings()
    Mode133_settings = OPT_Config_File.Mode133_settings()
    
    if not( Timeline_settings['duration'] > 0 and type(Timeline_settings['duration']) == int ):
        Logger.error('Timeline_settings["duration"]')
        raise ValueError
    if not( 43099.5 < ephem.Date(Timeline_settings['start_date']) < 73049.5 and type(Timeline_settings['start_date']) == str):
        Logger.error('Timeline_settings["start_date"]')
        raise ValueError
    if not( 30 <= Timeline_settings['CMD_duration'] and type(Timeline_settings['CMD_duration']) == int ):
        Logger.error('Timeline_settings["CMD_duration"]')
        raise ValueError
    if not( 30 < Timeline_settings['mode_separation'] and type(Timeline_settings['mode_separation']) == int ):
        Logger.error('Timeline_settings["mode_separation"]')
        raise ValueError
    if not( 1 <= Timeline_settings['command_separation'] and (type(Timeline_settings['command_separation']) == int or type(Timeline_settings['command_separation']) == float) ):
        Logger.error('Timeline_settings["command_separation"]')
        raise ValueError
    if not( 40 <= Timeline_settings['pointing_stabilization'] and type(Timeline_settings['pointing_stabilization']) == int ):
        Logger.error("Timeline_settings['pointing_stabilization']")
        raise ValueError
    if not( Timeline_settings['pointing_stabilization'] <= Timeline_settings['mode_separation'] + Timeline_settings['CMD_duration']):
        Logger.error("Timeline_settings['pointing_stabilization'] <= Timeline_settings['mode_separation'] + Timeline_settings['CMD_duration']")
        raise ValueError
    if not( 0 <= Timeline_settings['LP_pointing_altitude'] <= 300000 and type(Timeline_settings['LP_pointing_altitude']) == int ):
        Logger.error("Timeline_settings['LP_pointing_altitude']")
        raise ValueError
    if not( 0 < Timeline_settings['Mode_1_2_3_4minDuration'] and type(Timeline_settings['Mode_1_2_3_4minDuration']) == int ):
        Logger.error("Timeline_settings['Mode_1_2_3_4minDuration']")
        raise ValueError
    if not( type(Timeline_settings['yaw_correction']) == bool ):
        Logger.error("Timeline_settings['yaw_correction']")
        raise ValueError
    if not( type(Timeline_settings['GPS_epoch']) == str ):
        Logger.error("Timeline_settings['GPS_epoch']")
        raise ValueError
    if not( 0 < Timeline_settings['leap_seconds'] and type(Timeline_settings['leap_seconds']) == int ):
        Logger.error("Timeline_settings['leap_seconds']")
        raise ValueError
        
    
    for key in Mode_1_2_3_4_settings.keys():
        
        if not( Mode_1_2_3_4_settings[key] > 0 and type(Mode_1_2_3_4_settings[key]) == int ):
            Logger.error('Mode_1_2_3_4_settings')
            raise ValueError
        if( key == 'timestep'):
            if not( Mode_1_2_3_4_settings[key] < 100):
                Logger.error('Mode_1_2_3_4_settings["timestep"]')
                raise ValueError
                
    
    
    if not( 5 < Mode100_settings['pointing_duration'] and type(Mode100_settings['pointing_duration']) == int ):
        Logger.error("Mode100_settings['pointing_duration']")
        raise ValueError
    if not( type(Mode100_settings['pointing_altitude_interval']) == int and type(Mode100_settings['pointing_altitude_to']) == int and type(Mode100_settings['pointing_altitude_from']) == int ):
        Logger.error("Mode100_settings")
        raise TypeError
    if not( abs(Mode100_settings['pointing_altitude_interval']) <= abs(Mode100_settings['pointing_altitude_to'] - Mode100_settings['pointing_altitude_from']) ):
        Logger.error("Mode100_settings['pointing_altitude_interval']")
        raise ValueError
    if not( 0 < Mode100_settings['pointing_altitude_interval'] * (Mode100_settings['pointing_altitude_to'] - Mode100_settings['pointing_altitude_from']) ):
        Logger.error("Mode100_settings")
        raise ValueError
    if not( type(Mode100_settings['start_date']) == str):
        Logger.error("Mode100_settings['start_date']")
        raise TypeError
    if not( type(Mode100_settings['Exp_Time_and_Interval_IR']) == tuple and type(Mode100_settings['Exp_Time_and_Interval_UV']) == tuple):
        Logger.error("Mode100_settings['Exp_Time_and_Interval_IR'] or Mode100_settings['Exp_Time_and_Interval_UV']")
        raise TypeError
    
    
    
    
    for key in Mode110_settings.keys():
        
        if ( key == 'start_date'):
            if not( type(Mode110_settings[key]) == str ):
                Logger.error('Mode110_settings')
                raise ValueError
        else:
            if not( Mode110_settings[key] > 0 and type(Mode110_settings[key]) == int ):
                Logger.error('Mode110_settings')
                raise ValueError
                
    
    
    
    if not( 0 < Mode120_settings['timestep'] <= 10 and type(Mode120_settings['timestep']) == int ):
        Logger.error("Mode120_settings['timestep']")
        raise ValueError
    if not( Mode120_settings['freeze_start'] > Timeline_settings['pointing_stabilization'] and type(Mode120_settings['freeze_start']) == int  ):
        Logger.error("Mode120_settings")
        raise TypeError
    if not( Mode120_settings['freeze_start'] + Mode120_settings['freeze_duration']  <= Mode120_settings['mode_duration'] ):
        Logger.error("Mode120_settings['mode_duration']")
        raise ValueError
    if not( abs(Mode120_settings['V_offset']) <= 10 and 0 < abs(Mode120_settings['H_offset']) <= 10 ):
        Logger.error("Mode120_settings['V_offset'] or Mode120_settings['H_offset']")
        raise ValueError
    if not( type(Mode120_settings['start_date']) == str):
        Logger.error("Mode120_settings['date']")
        raise TypeError
    if not( type(Mode120_settings['automatic']) == bool):
        Logger.error("Mode120_settings['automatic']")
        raise TypeError
    if not( type(Mode120_settings['Vmag']) == str):
        Logger.error("Mode120_settings['Vmag']")
    if not( 0 < Mode120_settings['SnapshotTime'] < Mode120_settings['freeze_duration']-10 and type(Mode120_settings['SnapshotTime']) == int):
        Logger.error("Mode120_settings['SnapshotTime']")
    if not( Timeline_settings['LP_pointing_altitude'] < Mode120_settings['pointing_altitude'] and type(Mode120_settings['pointing_altitude']) == int):
        Logger.error("Mode120_settings['pointing_altitude']")
        
    
    
    
    
    if not( 0 < Mode121_122_123_settings['timestep'] <= 10 and type(Mode121_122_123_settings['timestep']) == int ):
        Logger.error("Mode121_122_123_settings['timestep']")
        raise ValueError
    if not( Mode121_122_123_settings['freeze_start'] > Timeline_settings['pointing_stabilization'] and type(Mode121_122_123_settings['freeze_start']) == int  ):
        Logger.error("Mode121_122_123_settings")
        raise TypeError
    if not( Mode121_122_123_settings['freeze_start'] + Mode121_122_123_settings['freeze_duration']  <= Mode121_122_123_settings['mode_duration'] ):
        Logger.error("Mode121_122_123_settings['mode_duration']")
        raise ValueError
    if not( 0 < abs(Mode121_122_123_settings['V_FOV']) <= 5 and 0 < abs(Mode121_122_123_settings['H_FOV']) <= 10 ):
        Logger.error("Mode121_122_123_settings['V_FOV'] or Mode121_122_123_settings['H_FOV']")
        raise ValueError
    if not( type(Mode121_122_123_settings['automatic']) == bool):
        Logger.error("Mode121_122_123_settings['automatic']")
        raise TypeError
    if not( type(Mode121_122_123_settings['Vmag']) == str):
        Logger.error("Mode121_122_123_settings['Vmag']")
    if not( 0 < Mode121_122_123_settings['SnapshotTime'] < Mode121_122_123_settings['freeze_duration']-10 and type(Mode121_122_123_settings['SnapshotTime']) == int):
        Logger.error("Mode121_122_123_settings['SnapshotTime']")
    if not( Timeline_settings['LP_pointing_altitude'] < Mode121_122_123_settings['pointing_altitude'] and type(Mode121_122_123_settings['pointing_altitude']) == int):
        Logger.error("Mode121_122_123_settings['pointing_altitude']")
    if not( 0 <= Mode121_122_123_settings['TimeSkip'] <= 3 and type(Mode121_122_123_settings['TimeSkip']) == int or type(Mode121_122_123_settings['TimeSkip']) == float ):
        Logger.error("Mode121_122_123_settings['TimeSkip']")
        raise ValueError
    
    
    
    if not( type(Mode121_settings['start_date']) == str):
        Logger.error("Mode121_settings['start_date']")
        raise TypeError
    if not( type(Mode122_settings['start_date']) == str):
        Logger.error("Mode122_settings['start_date']")
        raise TypeError
    if not( type(Mode123_settings['start_date']) == str):
        Logger.error("Mode123_settings['start_date']")
        raise TypeError
        
    if not( type(Mode122_settings['Exp_Time_and_Interval_IR']) == tuple and type(Mode122_settings['Exp_Time_and_Interval_UV']) == tuple):
        Logger.error("Mode122_settings['Exp_Time_and_Interval_IR'] or Mode122_settings['Exp_Time_and_Interval_UV']")
        raise TypeError
    if not( type(Mode123_settings['Exp_Time_and_Interval_IR']) == tuple and type(Mode123_settings['Exp_Time_and_Interval_UV']) == tuple):
        Logger.error("Mode123_settings['Exp_Time_and_Interval_IR'] or Mode123_settings['Exp_Time_and_Interval_UV']")
        raise TypeError
    
    
    
    
    
    if not( 0 < Mode124_settings['timestep'] <= 10 and type(Mode124_settings['timestep']) == int ):
        Logger.error("Mode124_settings['timestep']")
        raise ValueError
    if not( Mode124_settings['freeze_start'] > Timeline_settings['pointing_stabilization'] and type(Mode124_settings['freeze_start']) == int  ):
        Logger.error("Mode124_settings")
        raise TypeError
    if not( Mode124_settings['freeze_start'] + Mode124_settings['freeze_duration']  <= Mode124_settings['mode_duration'] ):
        Logger.error("Mode124_settings['mode_duration']")
        raise ValueError
    if not( abs(Mode124_settings['V_offset']) <= 10 and 0 < abs(Mode124_settings['H_offset']) <= 10 ):
        Logger.error("Mode124_settings['V_offset'] or Mode124_settings['H_offset']")
        raise ValueError
    if not( type(Mode124_settings['start_date']) == str):
        Logger.error("Mode124_settings['start_date']")
        raise TypeError
    if not( type(Mode124_settings['automatic']) == bool):
        Logger.error("Mode124_settings['automatic']")
        raise TypeError
    if not( 0 < Mode124_settings['SnapshotTime'] < Mode124_settings['freeze_duration']-10 and type(Mode124_settings['SnapshotTime']) == int):
        Logger.error("Mode124_settings['SnapshotTime']")
    if not( Timeline_settings['LP_pointing_altitude'] < Mode124_settings['pointing_altitude'] and type(Mode124_settings['pointing_altitude']) == int):
        Logger.error("Mode124_settings['pointing_altitude']")
        
    
    
    
    
    
    
    
    
    
    
        
    
    
    
    
    
    
    
    