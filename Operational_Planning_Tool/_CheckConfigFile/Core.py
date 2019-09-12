# -*- coding: utf-8 -*-
"""Created on Tue Jun  4 13:37:48 2019

Checks the values given in the *Configuration File* set by *Set_ConfigFile*.

@author: David
"""

import importlib, logging, sys, ephem

from OPT import _Globals, _Library
OPT_Config_File = importlib.import_module(_Globals.Config_File)

Logger = logging.getLogger(OPT_Config_File.Logger_name())

def CheckConfigFile():
    """ Core function of *CheckConfigFile*.
    
    Checks the values given in the *Configuration File* set by *Set_ConfigFile* and raises an error if any settings are found to be incompatible.
    
    """

    
    _Library.SetupLogger(OPT_Config_File.Logger_name())
    
    Timeline_settings = OPT_Config_File.Timeline_settings()
    Operational_Science_Mode_settings = OPT_Config_File.Operational_Science_Mode_settings()
    #Mode5_settings = OPT_Config_File.Mode5_settings()
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
    Mode134_settings = OPT_Config_File.Mode134_settings()
    
    
    
    if not( Timeline_settings['duration'] > 0 and type(Timeline_settings['duration']) == int ):
        Logger.error('Timeline_settings["duration"]')
        raise ValueError
    if not( 43099.5 < ephem.Date(Timeline_settings['start_date']) < 73049.5 and type(Timeline_settings['start_date']) == str):
        Logger.error('Timeline_settings["start_date"]')
        raise ValueError
    if not( 30 <= Timeline_settings['CMD_duration'] and type(Timeline_settings['CMD_duration']) == int ):
        Logger.error('Timeline_settings["CMD_duration"]')
        raise ValueError
    if not( 15 <= Timeline_settings['mode_separation'] and type(Timeline_settings['mode_separation']) == int ):
        Logger.error('Timeline_settings["mode_separation"]')
        raise ValueError
    if not( 1 <= Timeline_settings['command_separation'] and (type(Timeline_settings['command_separation']) == int or type(Timeline_settings['command_separation']) == float) ):
        Logger.error('Timeline_settings["command_separation"]')
        raise ValueError
    if not( Timeline_settings['command_separation'] * 8 <= Timeline_settings['mode_separation'] ):
        Logger.error("Timeline_settings['command_separation'] * 8 <= Timeline_settings['mode_separation']. Possibility of time separation between CMDs are too large causing CMDs from Science Modes to overlap")
        raise ValueError
    if not( 40 <= Timeline_settings['pointing_stabilization'] and type(Timeline_settings['pointing_stabilization']) == int ):
        Logger.error("Timeline_settings['pointing_stabilization']")
        raise ValueError
    if not( 10000 <= Timeline_settings['LP_pointing_altitude'] <= 300000 and type(Timeline_settings['LP_pointing_altitude']) == int ):
        Logger.error("Timeline_settings['LP_pointing_altitude']")
        raise ValueError
    if not( 0 < Timeline_settings['Mode1_2_5_minDuration'] and type(Timeline_settings['Mode1_2_5_minDuration']) == int ):
        Logger.error("Timeline_settings['Mode1_2_5_minDuration']")
        raise ValueError
    if not( type(Timeline_settings['yaw_correction']) == bool ):
        Logger.error("Timeline_settings['yaw_correction']")
        raise TypeError
    if not( type(Timeline_settings['Schedule_Mode5']) == bool ):
        Logger.error("Timeline_settings['Schedule_Mode5']")
        raise TypeError
    if not( type(Timeline_settings['GPS_epoch']) == str ):
        Logger.error("Timeline_settings['GPS_epoch']")
        raise TypeError
    if not( 0 < Timeline_settings['leapSeconds'] and type(Timeline_settings['leapSeconds']) == int ):
        Logger.error("Timeline_settings['leapSeconds']")
        raise ValueError
    if not( 0 <= abs(Timeline_settings['yaw_amplitude']) < 20 and (type(Timeline_settings['yaw_amplitude']) == int or type(Timeline_settings['yaw_amplitude']) == float) ):
        Logger.error("Timeline_settings['yaw_amplitude']")
        raise ValueError
    if not( 0 <= abs(Timeline_settings['yaw_phase']) and (type(Timeline_settings['yaw_phase']) == int or type(Timeline_settings['yaw_phase']) == float) ):
        Logger.error("Timeline_settings['yaw_phase']")
        raise ValueError
        
    
    for key in Operational_Science_Mode_settings.keys():
        
        if not( Operational_Science_Mode_settings[key] > 0 and type(Operational_Science_Mode_settings[key]) == int ):
            Logger.error('Operational_Science_Mode_settings')
            raise ValueError
        if( key == 'timestep'):
            if not( Operational_Science_Mode_settings[key] < 50):
                Logger.error('Operational_Science_Mode_settings["timestep"]')
                raise ValueError
        if( key == 'lat'):
            if not( 0 <= Operational_Science_Mode_settings[key] <= 90):
                Logger.error('Operational_Science_Mode_settings["lat"]')
                raise ValueError
                
    #if not( 10000 <= Mode5_settings['pointing_altitude'] <= 300000 and type(Mode5_settings['pointing_altitude']) == int ):
    #    Logger.error("Mode5_settings['pointing_altitude']")
    #    raise ValueError
                
    
    
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
    if not( type(Mode100_settings['Exp_Time_IR']) == int and type(Mode100_settings['Exp_Time_UV']) == int):
        Logger.error("Mode100_settings['Exp_Time_IR'] or Mode100_settings['Exp_Time_UV']")
        raise TypeError
    numberOfAltitudes = int( abs(Mode100_settings['pointing_altitude_to'] - Mode100_settings['pointing_altitude_from']) / abs(Mode100_settings['pointing_altitude_interval']) +1  )
    if not( Mode100_settings['Exp_Time_IR'] + numberOfAltitudes * Mode100_settings['ExpTime_step'] < Mode100_settings['pointing_duration']*1000):
        Logger.error("Mode100_settings['pointing_duration']")
        raise ValueError
    if not( Mode100_settings['Exp_Time_UV'] + numberOfAltitudes * Mode100_settings['ExpTime_step'] < Mode100_settings['pointing_duration']*1000):
        Logger.error("Mode100_settings['pointing_duration']")
        raise ValueError
    
    
    
    
    for key in Mode110_settings.keys():
        
        if ( key == 'start_date'):
            if not( type(Mode110_settings[key]) == str ):
                Logger.error('Mode110_settings')
                raise ValueError
        else:
            if not( Mode110_settings[key] > 0 and type(Mode110_settings[key]) == int ):
                Logger.error('Mode110_settings')
                raise ValueError
                
    
    
    if not( 10000 <= Mode120_settings['pointing_altitude'] <= 300000 and type(Mode120_settings['pointing_altitude']) == int ):
        Logger.error("Mode120_settings['pointing_altitude']")
        raise ValueError
    if not( 0 < Mode120_settings['timestep'] <= 10 and type(Mode120_settings['timestep']) == int ):
        Logger.error("Mode120_settings['timestep']")
        raise ValueError
    if not( Mode120_settings['freeze_start'] > Timeline_settings['pointing_stabilization'] and type(Mode120_settings['freeze_start']) == int  ):
        Logger.error("Mode120_settings")
        raise TypeError
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
    if not( 0 < Mode120_settings['SnapshotTime'] and type(Mode120_settings['SnapshotTime']) == int):
        Logger.error("Mode120_settings['SnapshotTime']")
        raise ValueError
    if not( 0 <= Mode120_settings['SnapshotSpacing'] and type(Mode120_settings['SnapshotSpacing']) == int):
        Logger.error("Mode120_settings['SnapshotSpacing']")
        raise ValueError
    if not( Mode120_settings['SnapshotSpacing'] * 5 + Mode120_settings['SnapshotTime'] < Mode120_settings['freeze_duration'] ):
        Logger.error("Mode120_settings['SnapshotSpacing'] * 5 + Mode120_settings['SnapshotTime'] > Mode120_settings['freeze_duration']")
        raise ValueError
    if not( Timeline_settings['LP_pointing_altitude'] < Mode120_settings['pointing_altitude'] and type(Mode120_settings['pointing_altitude']) == int):
        Logger.error("Mode120_settings['pointing_altitude']")
        raise ValueError
        
    
    
    
    if not( 10000 <= Mode121_122_123_settings['pointing_altitude'] <= 300000 and type(Mode121_122_123_settings['pointing_altitude']) == int ):
        Logger.error("Mode121_122_123_settings['pointing_altitude']")
        raise ValueError
    if not( 0 < Mode121_122_123_settings['timestep'] <= 10 and type(Mode121_122_123_settings['timestep']) == int ):
        Logger.error("Mode121_122_123_settings['timestep']")
        raise ValueError
    if not( Mode121_122_123_settings['freeze_start'] > Timeline_settings['pointing_stabilization']*1.1 and type(Mode121_122_123_settings['freeze_start']) == int  ):
        Logger.error("Mode121_122_123_settings")
        raise TypeError
    if not( 0 < abs(Mode121_122_123_settings['V_FOV']) <= 5 and 0 < abs(Mode121_122_123_settings['H_FOV']) <= 10 ):
        Logger.error("Mode121_122_123_settings['V_FOV'] or Mode121_122_123_settings['H_FOV']")
        raise ValueError
    if not( type(Mode121_122_123_settings['automatic']) == bool):
        Logger.error("Mode121_122_123_settings['automatic']")
        raise TypeError
    if not( type(Mode121_122_123_settings['Vmag']) == str):
        Logger.error("Mode121_122_123_settings['Vmag']")
        raise TypeError
    if not( 0 < Mode121_122_123_settings['SnapshotTime'] < Mode121_122_123_settings['freeze_duration']-10 and type(Mode121_122_123_settings['SnapshotTime']) == int):
        Logger.error("Mode121_122_123_settings['SnapshotTime']")
        raise ValueError
    if not( Timeline_settings['LP_pointing_altitude'] < Mode121_122_123_settings['pointing_altitude'] and type(Mode121_122_123_settings['pointing_altitude']) == int):
        Logger.error("Mode121_122_123_settings['pointing_altitude']")
        raise ValueError
    if not( 0 <= Mode121_122_123_settings['TimeSkip'] <= 3 and type(Mode121_122_123_settings['TimeSkip']) == int or type(Mode121_122_123_settings['TimeSkip']) == float ):
        Logger.error("Mode121_122_123_settings['TimeSkip']")
        raise ValueError
    if not( 0 <= Mode121_122_123_settings['SnapshotSpacing'] and type(Mode121_122_123_settings['SnapshotSpacing']) == int):
        Logger.error("Mode121_122_123_settings['SnapshotSpacing']")
        raise ValueError
    if not( Mode121_122_123_settings['SnapshotSpacing'] * 5 + Mode121_122_123_settings['SnapshotTime'] < Mode121_122_123_settings['freeze_duration'] ):
        Logger.error("Mode121_122_123_settings['SnapshotSpacing'] * 5 + Mode121_122_123_settings['SnapshotTime'] > Mode121_122_123_settings['freeze_duration']")
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
        
    if not( 0 <= Mode122_settings['Exp_Time_IR'] and type(Mode122_settings['Exp_Time_IR']) == int):
        Logger.error("Mode122_settings['Exp_Time_IR']")
        raise ValueError
    if not( 0 <= Mode122_settings['Exp_Time_UV'] and type(Mode122_settings['Exp_Time_UV']) == int):
        Logger.error("Mode122_settings['Exp_Time_UV']")
        raise ValueError
    if not( 0 <= Mode123_settings['Exp_Time_IR'] and type(Mode123_settings['Exp_Time_IR']) == int):
        Logger.error("Mode123_settings['Exp_Time_IR']")
        raise ValueError
    if not( 0 <= Mode123_settings['Exp_Time_UV'] and type(Mode123_settings['Exp_Time_UV']) == int):
        Logger.error("Mode123_settings['Exp_Time_UV']")
        raise ValueError
    
    
    
    
    if not( 10000 <= Mode124_settings['pointing_altitude'] <= 300000 and type(Mode124_settings['pointing_altitude']) == int ):
        Logger.error("Mode124_settings['pointing_altitude']")
        raise ValueError
    if not( 0 < Mode124_settings['timestep'] <= 10 and type(Mode124_settings['timestep']) == int ):
        Logger.error("Mode124_settings['timestep']")
        raise ValueError
    if not( Mode124_settings['freeze_start'] > Timeline_settings['pointing_stabilization']*1.2 and type(Mode124_settings['freeze_start']) == int  ):
        Logger.error("Mode124_settings")
        raise TypeError
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
        raise ValueError
    if not( Timeline_settings['LP_pointing_altitude'] < Mode124_settings['pointing_altitude'] and type(Mode124_settings['pointing_altitude']) == int):
        Logger.error("Mode124_settings['pointing_altitude']")
        raise ValueError
    if not( 0 <= Mode124_settings['SnapshotSpacing'] and type(Mode124_settings['SnapshotSpacing']) == int):
        Logger.error("Mode124_settings['SnapshotSpacing']")
        raise ValueError
    if not( Mode124_settings['SnapshotSpacing'] * 5 + Mode124_settings['SnapshotTime'] < Mode124_settings['freeze_duration'] ):
        Logger.error("Mode124_settings['SnapshotSpacing'] * 5 + Mode124_settings['SnapshotTime'] > Mode124_settings['freeze_duration']")
    
        
    
    
    
    
    if not( Timeline_settings['command_separation'] <= Mode130_settings['SnapshotSpacing'] and type(Mode130_settings['SnapshotSpacing']) == int):
        Logger.error("Mode130_settings['mode_duration']")
        raise TypeError
    if not( Timeline_settings['pointing_stabilization'] + Timeline_settings['command_separation'] * 8  < Mode131_settings['mode_duration'] and type(Mode131_settings['mode_duration']) == int):
        Logger.error("Mode131_settings['mode_duration']")
        raise TypeError
    if not( Timeline_settings['pointing_stabilization'] + Timeline_settings['command_separation'] * 8  < Mode134_settings['mode_duration'] and type(Mode134_settings['mode_duration']) == int):
        Logger.error("Mode134_settings['mode_duration']")
        raise TypeError
    
    if not( 10000 <= Mode130_settings['pointing_altitude'] <= 300000 and type(Mode130_settings['pointing_altitude']) == int ):
        Logger.error("Mode130_settings['pointing_altitude']")
        raise ValueError
    if not( 10000 <= Mode131_settings['pointing_altitude'] <= 300000 and type(Mode131_settings['pointing_altitude']) == int ):
        Logger.error("Mode131_settings['pointing_altitude']")
        raise ValueError
    if not( 10000 <= Mode132_settings['pointing_altitude'] <= 300000 and type(Mode132_settings['pointing_altitude']) == int ):
        Logger.error("Mode132_settings['pointing_altitude']")
        raise ValueError
    if not( 10000 <= Mode133_settings['pointing_altitude'] <= 300000 and type(Mode133_settings['pointing_altitude']) == int ):
        Logger.error("Mode133_settings['pointing_altitude']")
        raise ValueError
    if not( 10000 <= Mode134_settings['pointing_altitude'] <= 300000 and type(Mode134_settings['pointing_altitude']) == int ):
        Logger.error("Mode134_settings['pointing_altitude']")
        raise ValueError
    
    if not( type(Mode130_settings['start_date']) == str):
        Logger.error("Mode130_settings['start_date']")
        raise TypeError
    if not( type(Mode131_settings['start_date']) == str):
        Logger.error("Mode131_settings['start_date']")
        raise TypeError
    if not( type(Mode132_settings['start_date']) == str):
        Logger.error("Mode132_settings['start_date']")
        raise TypeError
    if not( type(Mode133_settings['start_date']) == str):
        Logger.error("Mode133_settings['start_date']")
        raise TypeError
    if not( type(Mode134_settings['start_date']) == str):
        Logger.error("Mode134_settings['start_date']")
        raise TypeError
        
    if not( type(Mode132_settings['Exp_Times_IR']) == list and type(Mode132_settings['Exp_Times_UV']) == list):
        Logger.error("Mode132_settings['Exp_Times_IR'] or Mode132_settings['Exp_Times_UV']")
        raise TypeError
    if not( type(Mode133_settings['Exp_Times_IR']) == list and type(Mode133_settings['Exp_Times_UV']) == list):
        Logger.error("Mode133_settings['Exp_Times_IR'] or Mode133_settings['Exp_Times_UV']")
        raise TypeError
        
    if not( len(Mode132_settings['Exp_Times_IR']) == len(Mode132_settings['Exp_Times_UV']) ):
        Logger.error("len(Mode132_settings['Exp_Times_IR']) != len(Mode132_settings['Exp_Times_UV'])")
        raise TypeError
    if not( len(Mode133_settings['Exp_Times_IR']) == len(Mode133_settings['Exp_Times_UV']) ):
        Logger.error("len(Mode133_settings['Exp_Times_IR']) != len(Mode133_settings['Exp_Times_UV'])")
        raise TypeError
    
    
    
    
    
    
    
    