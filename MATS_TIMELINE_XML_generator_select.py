# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 11:01:47 2018
Selects corresponding functions from received science mode

@author: David
"""


from MATS_TIMELINE_XML_generator_MODES import XML_generator_Mode1, XML_generator_Mode2, XML_generator_Mode120, XML_generator_Mode130, XML_generator_Mode200


def XML_generator_select(root,duration,relativeTime,mode,date,params):
    
    Mode_dict = {'Mode1': XML_generator_Mode1, 'Mode2': XML_generator_Mode2, 'Mode120': XML_generator_Mode120, 
             'Mode130': XML_generator_Mode130, 'Mode200': XML_generator_Mode200}

    
    #If no optional paramters are given
    if(len(params.keys()) == 0):
        
        Mode_dict[mode](root, date, duration, relativeTime)
        
    else:
        
        Mode_dict[mode](root, date, duration, relativeTime, params = params)
    
    
