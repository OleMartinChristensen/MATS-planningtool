# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:56:23 2019

@author: David
"""

import Operational_Planning_Tool as OPT




OPT.Copy_ConfigFile('OPT_Config_File')
#OPT.Set_ConfigFile('OPT_Config_File', '2018/9/3 08:00:40')
OPT.Set_ConfigFile('OPT_Config_File', '2020/6/20 18:32:42')


OPT.CheckConfigFile()

OPT.Data_Plotter()
#OPT.Timeline_Plotter('Output\Science_Mode_Timeline__OPT_Config_File.json', 'MATS_scenario_sim_20190630.h5')
#OPT.Timeline_gen()

#OPT.XML_gen('Output\Science_Mode_Timeline__OPT_Config_File.json')
