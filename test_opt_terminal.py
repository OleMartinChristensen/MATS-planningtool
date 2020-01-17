# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 12:18:10 2019

Main script supposed to be ran from the terminal with the inputs given below.

@author: David
"""

import sys

import OPT

if( __name__ == '__main__'):
    
    "Extract arguments given"
    name = sys.argv[1]
    year = sys.argv[2]
    month = sys.argv[3]
    day = sys.argv[4]
    hour = sys.argv[5]
    minute = sys.argv[6]
    second = sys.argv[7]
    tle1 = sys.argv[8]
    tle2 = sys.argv[9]
    
    "Convert into a date string"
    date = year+'/'+month+'/'+day+' '+hour+':'+minute+':'+second
    
    "The created Configuration File will have the data in its name"
    ConfigFileName = name+'_'+year+month+day+'_'+hour+minute+second
    
    #print(ConfigFileName,date,tlefile)
    
    "Copy the default Configuration File with the name ConfigFileName"
    OPT.Copy_ConfigFile(ConfigFileName)
    "Choose the Configuration File to use and set its starting date and TLE"
    OPT.Set_ConfigFile(ConfigFileName, date, tle1, tle2)
    "Check the values in the Configuration File"
    OPT.CheckConfigFile()
    
    
    "Generate the .json Science Mode Timeline file."
    OPT.Timeline_gen()

    "Convert the Science Mode Timeline into platform and payload CMDs and create a .xml CMD file"
    OPT.XML_gen('Output\Science_Mode_Timeline__'+ConfigFileName+'.json')