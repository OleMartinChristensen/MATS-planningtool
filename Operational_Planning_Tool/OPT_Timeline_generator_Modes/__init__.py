# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 11:27:05 2019

@author: David

Operational Planning Tool: 
    Contains functions for both Timeline generator and XML generator

"""

import os, shutil
#sys.path.append(os.getcwd()+'/Operational_Planning_Tool')

if(os.path.isfile('OPT_Config_File.py') == False):
    shutil.copyfile('Operational_Planning_Tool/OPT_Config_File_Original.py','OPT_Config_File.py')


def Timeline_gen():
    """Timeline generator part of Operational Planning Tool for MATS.
    Predicts and schedueles Science Modes into a list containing dates for each Mode and saves it to a .json file
    Settings for the program can be changed in the generated OPT_Config_File.py file.
    Input: None
    Output: None
    """
    from Operational_Planning_Tool.OPT_Timeline_generator import Timeline_gen
    
    Timeline_gen()
    
def XML_gen(science_mode_timeline_path):
    """XML generator part of Operational Planning Tool for MATS.
    Converts a .json file containing a list of scheduled Science Modes into commands and saves them to a .xml file.
    Settings for the program can be changed in the generated OPT_Config_File.py file.
    Input: path to the .json file containing the Science Mode Timeline as a string
    Output: None
    """
    from Operational_Planning_Tool.OPT_XML_generator import XML_generator
    
    "Initialize current_pointing to None"
    import Operational_Planning_Tool.OPT_XML_generator_Commands as commands
    commands.current_pointing = None
    
    XML_generator(science_mode_timeline_path)

