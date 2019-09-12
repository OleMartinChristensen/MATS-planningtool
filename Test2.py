# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:56:23 2019

@author: David
"""

import OPT




OPT.Copy_ConfigFile('OPT_Config_File')
#OPT.Set_ConfigFile('OPT_Config_File', '2018/9/3 08:00:40')
OPT.Set_ConfigFile('OPT_Config_File', '2020/6/20 18:32:42')


OPT.CheckConfigFile()
OPT.Timeline_gen()

Data_MATS, Data_LP, Time, Time_OHB  = OPT.Timeline_Plotter('Output\Science_Mode_Timeline__OPT_Config_File.json')

OPT.XML_gen('Output\Science_Mode_Timeline__OPT_Config_File.json')
