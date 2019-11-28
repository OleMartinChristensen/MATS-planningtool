# -*- coding: utf-8 -*-
"""Global variables for Operational_Planning_Tool.

**Globals:** \n
Config_File: Contains the name of the used *Configuration File* as set by *Set_ConfigFile*. \n

StartTime = Contains the starting time and date of OPT as set by *Set_ConfigFile*. \n

current_pointing = Only applicable to XML_generator. Contains the pointing altitude of the last scheduled *TC_acfLimbPointingAltitudeOffset* command. Is  \n

TLE = Contains a TLE as a duple of strings which is used by the *Configuration File*. If the strings are empty, the Configuration File will used a default TLE specified in the *Configuration File*. \n

latestRelativeTime = Only applicable to XML_generator. The *relativeTime* of the latest scheduled CMD. Used to make sure that CMDs always are scheduled in a chronological order. \n

LargestSetTEXPMS = The latest largest set TEXPMS on the CCDs whenever CCD_macro is ran. This is the least amount of time that need to pass from going into idle mode and and changing CCD settings. \n

Mode120Iteration = Only applicable to Timeline_gen. Used to keep track of the current iteration of the scheduling process for Mode120. Used to cycle through the V_offsets chosen in the Configuration File. \n

Mode124Iteration = Only applicable to Timeline_gen. Used to keep track of the current iteration of the scheduling process for Mode124. Used to cycle through the V_offsets chosen in the Configuration File. \n
"""

Config_File = 'OPT_Config_File'
current_pointing = None
#science_mode_timeline_path = None
StartTime = None
TLE = ('','')
latestRelativeTime = 0
LargestSetTEXPMS = 0
Mode120Iteration = 0
Mode124Iteration = 0

#TLE = ['1 54321U 19100G   20172.75043981 0.00000000  00000-0  75180-4 0  0014', 
#       '2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010']
    
