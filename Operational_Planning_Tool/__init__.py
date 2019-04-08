# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 11:27:05 2019

@author: David

Operational Planning Tool: 
    Contains the functions for Timeline generator, XML generator and Timeline_analyzer, which together constitute
    the Operational_Planning_Tool.\n
    Settings for the program are stated in the OPT_Config_File.py file, which is created in the working directory of the script call
    upon import of the Operational_Planning_Tool package.

"""

import os, shutil

#sys.path.append(os.getcwd()+'/Operational_Planning_Tool')

#if(os.path.isfile('OPT_Config_File.py') == False):
#    shutil.copyfile('Operational_Planning_Tool/OPT_Config_File_Original.py','OPT_Config_File.py')


def Timeline_gen():
    """Invokes the Timeline generator part of Operational Planning Tool.
    
    Predicts and schedueles Science Modes into a list containing dates for each Mode and saves it to a .json file in /Output.
    
    Argument: 
        None
    
    Returns: 
        None
    """
    
    from .OPT_Timeline_generator import Timeline_gen
    
    Timeline_gen()
    
    
def XML_gen(science_mode_timeline_path):
    """Invokes the XML generator part of Operational Planning Tool for MATS.
    
    Converts a .json file containing a list of scheduled Science Modes into commands and saves them to a .xml command file.
    
    Argument: 
        science_mode_timeline_path [str]: Path to the .json file containing the Science Mode Timeline.
    
    Returns: None
    """
    
    from .OPT_XML_generator import XML_generator
    
    "Initialize current_pointing to None"
    import Operational_Planning_Tool.OPT_XML_generator_Commands as commands
    commands.current_pointing = None
    
    XML_generator(science_mode_timeline_path)


def Timeline_analyzer(science_mode_timeline_path, date):
    '''Searches an Science Mode Timeline json file for a given date and returns the scheduled mode and its parameters"
    
    Arg:
        science_mode_timeline_path (str): path to the .json file containing the Science Mode Timeline
        date (str): A given date and time ('2019/09/05 12:09:25')
        
    Output:
        Mode (str): The currently scheduled Mode
        Parameters (dict): The parameters of the Mode
    '''
    
    from .OPT_Timeline_analyzer import Timeline_analyzer
    
    Mode, Parameters = Timeline_analyzer(science_mode_timeline_path, date)
    
    return Mode, Parameters
        
    
    
    