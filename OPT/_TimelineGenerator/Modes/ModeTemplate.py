# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 10:35:32 2019

Template for a new Mode where 'X' is exchanged for the number or name of the mode. 
The Mode is here scheduled at the start of the timeline.

For *Timeline_gen* to be able to find and schedule this mode, this function must be imported in the *Modes_Header* module.
Remember to also add the name of this Mode into the *Scheduling_priority* function, in the *Configuration_File*.

@author: David
"""


import ephem, sys, logging, importlib

from OPT._Library import scheduler
from OPT import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def ModeX(Occupied_Timeline):
    
    "Plan to schedule the Mode at the start of the timeline"
    initial_StartDate = ephem.Date(OPT_Config_File.Timeline_settings()['start_date'])
    
    "Set a duration of the Mode in seconds, which in turns sets the endDate"
    duration = 600
    #duration = OPT_Config_File.ModeX_settings()['duration']
    endDate = ephem.Date(initial_StartDate + ephem.second*duration)
    
    "Check if the planned initial_StartDate is available and postpone until available"
    startDate, endDate, iterations = scheduler(Occupied_Timeline, initial_StartDate, endDate)
    
    comment = 'Number of times date postponed: ' + str(iterations)
    
    "Get the name of the function, which is always also the name of the mode"
    Mode_name = sys._getframe(0).f_code.co_name
    
    Occupied_Timeline[Mode_name].append((startDate,endDate))
    
    return Occupied_Timeline, comment
    

