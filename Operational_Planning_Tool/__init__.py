# -*- coding: utf-8 -*-
"""Contains the functions that can be called to invoke Timeline generator, XML generator and Timeline_analyse, which together constitute the Operational_Planning_Tool.

Example:
    import Operational_Planning_Tool as OPT
    OPT.Timeline_gen()
    OPT.XML_gen('Output/Science_Mode_Timeline_Version_Original.json.json')

Settings for the program are stated in the OPT_Config_File.py file, which is created in the working directory of the user call
upon import of the Operational_Planning_Tool package. It is an copy of the original Config_File_Original, located in the Operational_Planning_Tool directory. 
All settings in the generated OPT_Config_File can be changed to adjust the Operational Planning Tool. 
All generated output files are saved in a folder called 'Output' in the working directory.
Generated logs are also saved in folders created in the working directory.

"""

import os, shutil

if(os.path.isfile('OPT_Config_File.py') == False):
    shutil.copyfile('Operational_Planning_Tool/Config_File_Original.py','OPT_Config_File.py')


from .XML_generator.Core import XML_generator
from .Timeline_generator.Core import Timeline_generator
from .Timeline_analyzer.Core import Timeline_analyzer
from .Data_Plotter.Core import Data_Plotter
from . import Globals



#sys.path.append(os.getcwd()+'/Operational_Planning_Tool')



def Timeline_gen():
    """Invokes the Timeline generator part of Operational Planning Tool.
    
    Predicts and schedueles Science Modes into a list containing dates for each Mode and saves it to a .json file in /Output.
    
    Returns:
        None
    """
    
    Timeline_generator()
    
    
def XML_gen(science_mode_timeline_path):
    """Invokes the XML generator program part of Operational Planning Tool for MATS.
    
    Converts a .json file containing a list of scheduled Science Modes into commands and saves them to a .xml command file.
    
    Arguments: 
        science_mode_timeline_path (str): Path to the .json file containing the Science Mode Timeline.
    
    Returns: 
        None
    """
    
    "Initialize current_pointing to None"
    Globals.current_pointing = None
    Globals.science_mode_timeline_path = science_mode_timeline_path
    
    XML_generator(science_mode_timeline_path)


def Timeline_analyse(science_mode_timeline_path, date):
    '''Invokes the Timeline analyzer program part of Operational Planning Tool.
    
    Searches a Science Mode Timeline json file for a given date and returns the scheduled mode and its parameters"
    
    Arguments:
        science_mode_timeline_path (str): path to the .json file containing the Science Mode Timeline
        date (str): A given date and time ('2019/09/05 12:09:25')
        
    Returns:
        (str): The currently scheduled Mode.
        (dict): The parameters of the Mode.
    '''
    
    
    Mode, Parameters = Timeline_analyzer(science_mode_timeline_path, date)
    
    return Mode, Parameters

def Data_Plot(science_mode_timeline_path, date):
    '''Invokes the Timeline analyzer program part of Operational Planning Tool.
    
    Searches a Science Mode Timeline json file for a given date and returns the scheduled mode and its parameters"
    
    Arguments:
        science_mode_timeline_path (str): path to the .json file containing the Science Mode Timeline
        date (str): A given date and time ('2019/09/05 12:09:25')
        
    Returns:
        (str): The currently scheduled Mode.
        (dict): The parameters of the Mode.
    '''
    
    
    Data_Plotter(data)
    
    