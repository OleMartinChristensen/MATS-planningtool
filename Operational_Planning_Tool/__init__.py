# -*- coding: utf-8 -*-
"""Contains the functions that together constitute the Operational_Planning_Tool.

*Operational_Planning_Tool* uses a special .py file as a *Configuration File*. \n
Create a separate copy of the *_ConfigFile* and modify the settings in this copy. \n
A specific copied *Configuration File* and its date must be chosen using *Set_ConfigFile. \n
A timeline can be generated by using *Timeline_gen*. *Timeline_gen* schedules Modes and CMDs and saves it into a .json file. \n
This .json file can be converted with *XML_gen* into an .XML file, as described in the *InnSat Payload Timeline XML Definition* document, which will contain all the relevant commands to be sent to mission control.

*Check_ConfigFile* i used to check if the values stated in the chosen copied *Configuration File* are plausible.

Examples:
    import Operational_Planning_Tool as OPT
    
    OPT.Copy_ConfigFile('OPT_Config_File')
    
    OPT.Set_ConfigFile('OPT_Config_File', '2019/09/05 08:00:00')
    
    OPT.CheckConfigFile()
    
    OPT.Timeline_gen()
    
    OPT.XML_gen('Output/Science_Mode_Timeline__OPT_Config_File.json')
    
    Data_MATS, Data_LP, Time, Time_OHB  = OPT.Timeline_Plotter('Output\Science_Mode_Timeline__OPT_Config_File.json')

Settings for the programs are stated in a .py *Configuration File*, and the *Configuration File* to be used is set 
by calling *Set_ConfigFile*. The *Configuration file* chosen must be visible in *sys.path*. A .py *Configuration File* with default values 
can be created by calling the *Copy_ConfigFile* function. 
It is an copy of the original *_ConfigFile*, located in the *Operational_Planning_Tool* directory. 

All settings in the generated *Configuration File* can be changed to adjust the operation of the Operational Planning Tool. 
All generated output files are saved in a folder called 'Output' in the working directory.
Generated logs are also saved in folders created in the working directory.

"""



def Copy_ConfigFile(Config_File_Name):
    """Makes a copy of the *_ConfigFile* located in *Operational_Planning_Tool*.
    
    The copy is created in the working directory of the user call and can be freely modified.
    Dont forget to also use *Set_ConfigFile* to choose your specific copy.
    
    Arguments:
        Config_File_Name (str): The name of the newly created *.py* copy of the *_ConfigFile* (excluding *.py*).
    Returns:
        None
    """
    import shutil, os
    
    Original_ConfigFile = os.path.join('Operational_Planning_Tool', '_Config_File_Original', 'Config_File_Original.py')
    ConfigFile = os.path.join('Operational_Planning_Tool', '_ConfigFile.py')
    
    Config_File_Name = Config_File_Name+'.py'
    
    #Make copy of the original Config File if no Config File is present.
    if(os.path.isfile(ConfigFile) == False):
        shutil.copyfile(Original_ConfigFile, ConfigFile)
    elif( os.path.isfile(ConfigFile) == True):
        answer = None
        while( answer != 'y' and answer != 'n'):
            answer = input('Overwrite '+ConfigFile+' ? (y/n)\n')
        if(answer == 'y'):
            shutil.copyfile(Original_ConfigFile, ConfigFile)
        elif( answer == 'n'):
            pass
    
    if(os.path.isfile(Config_File_Name) == False):
        shutil.copyfile(ConfigFile, Config_File_Name)
    elif( os.path.isfile(Config_File_Name) == True):
        answer = None
        while( answer != 'y' and answer != 'n'):
            answer = input('Overwrite '+Config_File_Name+' ? (y/n)\n')
        if(answer == 'y'):
            shutil.copyfile(ConfigFile, Config_File_Name)
        elif( answer == 'n'):
            pass
        
    
        
    


def Set_ConfigFile(Config_File_Name, Date):
    """Sets the StartTime for OPT, and the name of the *.py* file that is to be used as a Config File for OPT.
    
    The *Configuration file* chosen must be visible in sys.path.
    
    Arguments:
        Config_File_Name (str): The name of the Config File to be used (excluding .py).
        Date (str): The start time and date for the Operational Planning Tool (yyyy/mm/dd hh:mm:ss).
        
    Returns:
        None
    """
    
    from . import _Globals as Globals
    
    Globals.Config_File = Config_File_Name
    Globals.StartTime = Date
    

def CheckConfigFile():
    """Checks the values of the settings in the *Configuration File* set by *Set_ConfigFile*.
    
    """
    from ._CheckConfigFile.Core import CheckConfigFile
    
    CheckConfigFile()


def Timeline_gen():
    """Invokes the Timeline generator part of Operational Planning Tool.
    
    Predicts and schedueles Science Modes and some separate payload CMDs into a list containing dates for each Mode and saves it to a .json file in /Output. \n
    The Modes and CMDs to be scheduled are listed in *Modes_priority* in the chosen *Configuration File*.
    
    Settings for the operation of the program are stated in the *Configuration File* set by *Set_ConfigFile*.
    
    Returns:
        None
    """
    from ._TimelineGenerator.Core import Timeline_generator
    
    
    Timeline_generator()
    
    
def XML_gen(science_mode_timeline_path):
    """Invokes the XML generator program part of Operational Planning Tool for MATS.
    
    Converts a .json file containing a list of scheduled Science Modes/CMDs/Tests into commands and saves them as a .xml command file. 
    Each Mode/CMD/Test in the Science Mode Timeline may contain or be given specific settings to override the Mode/CMD/Test specific settings given in the chosen Config file. \n
    
    Settings for the operation of the program stated in the *Configuration File* set by *Set_ConfigFile*.
    
    Arguments: 
        science_mode_timeline_path (str): Path to the .json file containing the Science Mode Timeline.
    
    Returns: 
        None
    """
    
    from ._XMLGenerator.Core import XML_generator
    from . import _Globals as Globals
    
    
    "Initialize current_pointing to None"
    Globals.current_pointing = None
    #Globals.science_mode_timeline_path = science_mode_timeline_path
    
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
    '''Invokes the *Data_Plotter* program part of *Operational_Planning_Tool*.
    
    Simulates the position and attitude of MATS during normal operation and compares it to 
    the actual positional and attitude data given in a data set. Plots both the simulated data and given data. \n
    Settings for the operation of the program are stated in the chosen *Configuration File*, set by *Set_ConfigFile*.
    
    Arguments:
        
            
    Returns:
        None
    '''
    from ._DataPlotter.Core import Data_Plotter
    
    
    Data_Plotter()
    
    
def Timeline_Plotter(Science_Mode_Path, OHB_H5_Path = False, Timestep = 16 ):
    '''Invokes the *Timeline_Plotter* program part of *Operational_Planning_Tool*.
    
    Simulates the position and attitude of MATS from a given Science Mode Timeline and also optionally compares it to
    positional and attitude data given in a data set, OHB_H5_Path. Plots both the simulated data and given data. \n
    Settings for the operation of the program are provided by the chosen *Science Mode Timeline*.
    
    Arguments:
        Science_Mode_Path (str): Path to the Science Mode Timeline to be plotted.
        OHB_H5_Path (str): *Optional*. Path to the .h5 file containing position, time, and attitude data.
        Timestep (int): *Optional*. The chosen timestep of the simulation [s].
        
    Returns:
        
    '''
    from ._Timeline_Plotter.Core import Timeline_Plotter
    
    
    Data_MATS, Data_LP, Time, Time_OHB  = Timeline_Plotter(Science_Mode_Path, OHB_H5_Path, Timestep)
    
    return Data_MATS, Data_LP, Time, Time_OHB
    