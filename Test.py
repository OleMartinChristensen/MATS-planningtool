# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 12:18:10 2019

@author: David
"""

import sys

import Operational_Planning_Tool as OPT

if( __name__ == '__main__'):
    #a = sys.argv(3)
    
    name = sys.argv[1]
    year = sys.argv[2]
    month = sys.argv[3]
    day = sys.argv[4]
    hour = sys.argv[5]
    minute = sys.argv[6]
    second = sys.argv[7]
    #tlefile = sys.argv[3]
    
    date = year+'/'+month+'/'+day+' '+hour+':'+minute+':'+second
    
    ConfigFileName = name+'_'+year+month+day+'_'+hour+minute+second
    
    #print(ConfigFileName,date,tlefile)
    
    OPT.Copy_ConfigFile(ConfigFileName)
    OPT.Set_ConfigFile(ConfigFileName, date)
    OPT.CheckConfigFile()
    
    #OPT.Create_ConfigFile(date,tlefile,configname)
    #OPT.Set_ConfigFile(configname)
    
    OPT.Timeline_gen()

    OPT.XML_gen('Output\Science_Mode_Timeline__'+ConfigFileName+'.json')