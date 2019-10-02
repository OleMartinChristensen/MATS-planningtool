# -*- coding: utf-8 -*-
"""Globals for Operational_Planning_Tool.

**Globals:** \n
Config_File: Contains the name of the used *Configuration File* as set by *Set_ConfigFile*. \n

StartTime = Contains the starting time and date of OPT as set by *Set_ConfigFile*. \n

current_pointing: Only applicable to XML_generator. Contains the pointing altitude of the last scheduled *TC_acfLimbPointingAltitudeOffset* command. \n

Timeline_settings = Only applicable to XML_generator. Contains the Timeline_settings used, set by the *Science Mode Timeline* or *Configuration File*.

latestRelativeTime = Only applicable to XML_generator. The *relativeTime* of the latest scheduled CMD. Used to make sure that CMDs always are scheduled in a chronological order.

"""

Config_File = 'OPT_Config_File'
current_pointing = None
#science_mode_timeline_path = None
StartTime = None
Timeline_settings = None
latestRelativeTime = 0
#TLE = ['1 54321U 19100G   20172.75043981 0.00000000  00000-0  75180-4 0  0014', 
#       '2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010']
    
