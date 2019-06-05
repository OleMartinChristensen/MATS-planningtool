# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:56:23 2019

@author: David
"""

import Operational_Planning_Tool as OPT


OPT.Copy_ConfigFile('OPT_Config_File')
OPT.Set_ConfigFile('OPT_Config_File', '2018/9/3 08:00:40')

OPT.CheckConfigFile()

OPT.Timeline_gen()

OPT.XML_gen('Output\Science_Mode_Timeline__OPT_Config_File.json')
