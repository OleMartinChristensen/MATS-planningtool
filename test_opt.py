# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:56:23 2019

Main test script showcasing how to use the main parts of OPT.

@author: David Skånberg
"""

import OPT



"Make a copy of the defualt Configuration File in OPT and name it 'OPT_Config_File'"
OPT.Copy_ConfigFile('OPT_Config_File')

"Choose you Configuration File ('OPT_Config_File') and set the start date and TLE"
OPT.Set_ConfigFile('OPT_Config_File', '2020/6/20 18:32:42', TLE1 = '1 54321U 19100G   20172.75043981 0.00000000  00000-0  75180-4 0  0014',
        TLE2 = '2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010')

"Check the currently chosen Configuration File and the plausibility of its values. Prints out the currently used start date and TLE"
OPT.CheckConfigFile()

"Create a Science Mode Timeline (.json file) depending on the settings in the Configuration File"
OPT.Timeline_gen()

"Predict state and attitude data from the Science Mode Timeline and plot the results"
Data_MATS, Data_LP, Time, Time_OHB  = OPT.Timeline_Plotter('Output\Science_Mode_Timeline__OPT_Config_File.json', Timestep=25)

"Convert the Science Mode Timeline into payload and platform CMDs as a .xml file)"
OPT.XML_gen('Output\Science_Mode_Timeline__OPT_Config_File.json')
