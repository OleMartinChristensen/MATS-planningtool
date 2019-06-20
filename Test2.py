# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:56:23 2019

@author: David
"""

import Operational_Planning_Tool as OPT
from pylab import sqrt, sin, pi, cos,array

"""
lat = 45
R_polar = 6356.752314245
R_eq = 6378.137

e = sqrt(1-R_polar**2/R_eq**2)

R = R_eq/sqrt(1-e**2*sin(lat/180*pi)**2)
R = sqrt( ( (R_eq**2*cos(lat/180*pi))**2 + (R_polar**2*sin(lat/180*pi))**2 ) / ( (R_eq*cos(lat/180*pi))**2 + (R_polar*sin(lat/180*pi))**2 ) )
"""




OPT.Copy_ConfigFile('OPT_Config_File')
OPT.Set_ConfigFile('OPT_Config_File', '2018/9/3 08:00:40')

OPT.CheckConfigFile()

OPT.Data_Plotter()

#OPT.Timeline_gen()

#OPT.XML_gen('Output\Science_Mode_Timeline__OPT_Config_File.json')
