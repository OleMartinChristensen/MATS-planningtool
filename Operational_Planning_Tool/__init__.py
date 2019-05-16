# -*- coding: utf-8 -*-
"""Contains the functions that can be called to invoke Timeline generator, XML generator, Data_Plotter and Timeline_analyse, which together constitute the Operational_Planning_Tool.

Examples:
    import Operational_Planning_Tool as OPT
    
    OPT.Create_ConfigFile()
    
    OPT.Timeline_gen()
    
    OPT.XML_gen('Output/Science_Mode_Timeline_Version_Original.json')

Settings for the programs are stated in the *OPT_Config_File.py* file located in the working directory of the user call. This file can be created by
by calling the *OPT.Create_ConfigFile* function (unless there already is an *OPT_Config_File.py* file inte working directory of the user call). 
It is an copy of the original *Config_File_Original*, located in the Operational_Planning_Tool directory. 
All settings in the generated *OPT_Config_File.py* can be changed to adjust the operation of the Operational Planning Tool. 
All generated output files are saved in a folder called 'Output' in the working directory.
Generated logs are also saved in folders created in the working directory.

"""



def Create_ConfigFile():
    """Makes a copy of the original Config file (Config_File_Original, located in Operational_Planning_Tool).
    
    The copy is created in the working directory of the user call and can be freely modified. Operational_Planning_Tool will
    use whatever file named "OPT_Config_File" that is also located in the working directory of the user call.
    
    Returns:
        None
    """
    import os, shutil
    
    if(os.path.isfile('OPT_Config_File.py') == False):
        shutil.copyfile('Operational_Planning_Tool/_Config_File_Original.py','OPT_Config_File.py')



def Timeline_gen():
    """Invokes the Timeline generator part of Operational Planning Tool.
    
    Predicts and schedueles Science Modes into a list containing dates for each Mode and saves it to a .json file in /Output. \n
    
    Settings for the operation of the program are stated in *OPT_Config_File.py*, which is created by running Operational_Planning_Tool.Create_ConfigFile.
    
    Returns:
        None
    """
    from ._TimelineGenerator.Core import Timeline_generator
    
    Timeline_generator()
    
    
def XML_gen(science_mode_timeline_path):
    """Invokes the XML generator program part of Operational Planning Tool for MATS.
    
    Converts a .json file containing a list of scheduled Science Modes/CMDs into commands and saves them to a .xml command file. 
    Each Mode/CMD in the Science Mode Timeline may contain or be given specific settings to override the Mode/CMD specific settings given in OPT_Config_File.py file. \n
    
    Settings for the operation of the program is stated in *OPT_Config_File.py*, which is created by running Operational_Planning_Tool.Create_ConfigFile.
    
    Arguments: 
        science_mode_timeline_path (str): Path to the .json file containing the Science Mode Timeline.
    
    Returns: 
        None
    """
    
    from ._XMLGenerator.Core import XML_generator
    from . import _Globals as Globals
    
    "Initialize current_pointing to None"
    Globals.current_pointing = None
    Globals.science_mode_timeline_path = science_mode_timeline_path
    
    XML_generator(science_mode_timeline_path)


def Timeline_analyser(science_mode_timeline_path, date):
    '''Invokes the Timeline analyzer program part of Operational Planning Tool.
    
    Searches a Science Mode Timeline json file for a given date and returns the scheduled mode and its parameters"
    
    Arguments:
        science_mode_timeline_path (str): path to the .json file containing the Science Mode Timeline
        date (str): A given date and time ('2019/09/05 12:09:25')
        
    Returns:
        (tuple): tuple containing: 
            (str): The currently scheduled Mode. \n
            (dict): The parameters of the Mode.
    '''
    from ._TimelineAnalyzer.Core import Timeline_analyzer
    
    Mode, Parameters = Timeline_analyzer(science_mode_timeline_path, date)
    
    return Mode, Parameters

def Data_Plotter():
    '''Invokes the Data_Plotter program part of Operational Planning Tool.
    
    Simulates the position and attitude of MATS during normal operation and compares it to 
    the actual positional and attitude data given in a data set. Plots both the simulated data and given data. \n
    Settings for the operation of the program is stated in *OPT_Config_File.py*, which is created by running Operational_Planning_Tool.Create_ConfigFile.
    
    Arguments:
        DataSet_path (str): Path to the .csv file containing the relevant data of analysis.
        
    Returns:
        None
    '''
    from ._DataPlotter.Core import Data_Plotter
    
    Data_Plotter()
    
    