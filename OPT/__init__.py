# -*- coding: utf-8 -*-
"""Contain the functions that together constitute the Operational_Planning_Tool (OPT). These functions are:
    
    - Copy_ConfigFile
    - Set_ConfigFile
    - CheckConfigFile
    - Timeline_gen
    - XML_gen
    - Timeline_analyzer
    - Timeline_Plotter

**Abbreviations:**
    CMD = Command \n
    FOV = Field of View \n
    OPT = Operational Planning Tool
    
**Description:**
*Operational_Planning_Tool* uses a special .py file as a *Configuration File*. An example of a *Configuration_File* is located in the Operational_Planning_Tool and is called *_ConfigFile.py*.  \n

Create your own *Configuration File* with an appropriate name by running *Copy_ConfigFile* with a chosen name as an input. 
*Copy_ConfigFile* makes a copy of *_ConfigFile.py*. You can then modify the settings in your copy. \n

Your *Configuration File* and its date must be chosen by running *Set_ConfigFile*. \n

The objective of *Operational_Planning_Tool* is to create a timeline constituting of planned Science Modes and some available stand-alone Commands (specified in "Science Modes for MATS" document). 
A *Science Mode Timeline*, as it is called, is created by running *Timeline_gen*. Remember to edit and choose your *Configuration File* by running *Set_ConfigFile*. \n

The created *Science Mode Timeline* can be converted into Payload and Platform Commands (as specified in the "Innosat Payload Timeline XML Definition" document) 
by running *XML_gen* with the *Science Mode Timeline* as the input. 

The *Science Mode Timeline* can also be simulated and and plotted by running *Timeline_Plotter* with the *Science Mode Timeline* as the input. 
*Timeline_Plotter* can also optionally plot a special kind of .h5 data-files, created by OHB SWEDEN. \n

Note: A *Science Mode Timeline* usually contains settings that are taken from the chosen *Configuration File* when the *Science Mode Timeline* was created. 
Any time a function uses a *Science Mode Timeline* as an input, these settings will be given priority over any similar settings stated in the currently chosen *Configuration File*. \n

*Check_ConfigFile* is used to check if the values stated in the chosen *Configuration File* are plausible. \n

All generated output files are saved in a folder called 'Output' in the working directory.
Generated logs are saved in folders created in the working directory.


Examples:
    import OPT
    
    OPT.Copy_ConfigFile('OPT_Config_File')
    
    OPT.Set_ConfigFile('OPT_Config_File', '2019/09/05 08:00:00')
    
    OPT.CheckConfigFile()
    
    OPT.Timeline_gen()
    
    OPT.XML_gen('Output/Science_Mode_Timeline__OPT_Config_File.json')
    
    Data_MATS, Data_LP, Time, Time_OHB  = OPT.Timeline_Plotter('Output/Science_Mode_Timeline__OPT_Config_File.json')
 

Science Modes are separated into 2 different areas, *Operational Science Modes* (Mode 1,2,5) and *Calibration Modes*. \n
*Calibration Modes* are scheduled at specific points of time and are usually only scheduled one time per *Science Mode Timeline*. 
*Operational Science Modes* (Mode 1,2,5) are scheduled wherever time is available (after the scheduling of *Calibration Modes*) and only 1 *Operational Science Mode* is scheduled per Timeline.

"""



def Copy_ConfigFile(Config_File_Name):
    """Makes a copy of the *_ConfigFile* located in *Operational_Planning_Tool*.
    
    The copy is created in the working directory of the user call and can be freely modified.
    Do not forget to also use *Set_ConfigFile* to choose your specific copy.
    
    Arguments:
        Config_File_Name (str): The name of the newly created copy of the *_ConfigFile* (excluding *.py*).
    Returns:
        None
    """
    import shutil, os
    
    Original_ConfigFile = os.path.join('OPT', '_Config_File_Original', 'Config_File_Original.py')
    ConfigFile = os.path.join('OPT', '_ConfigFile.py')
    
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
    """Sets the StartTime for OPT, and the name of the *.py* file that is to be used as a *Configuration file* for OPT.
    
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
    """Checks the values of the settings in the *Configuration File* chosen with *Set_ConfigFile*.
    
    """
    from ._CheckConfigFile.Core import CheckConfigFile
    
    CheckConfigFile()


def Timeline_gen():
    """Invokes the Timeline generator part of Operational Planning Tool.
    
    Creates a *Science Mode Timeline* as a .json file. \n
    Predicts and schedueles Science Modes and separate payload CMDs into a list containing run dates and settings used for each Mode/CMD, and saves it to a .json file in /Output. \n
    The Modes and CMDs to be scheduled are listed in *Modes_priority* in the chosen *Configuration File*.
    
    *Operational Science Modes* (example: Mode 1,2,5) are scheduled separately wherever time is available at the end of the program.
    
    Settings for the operation of the program are stated in the *Configuration File* set by *Set_ConfigFile*.
    
    Returns:
        None
    """
    from ._TimelineGenerator.Core import Timeline_generator
    
    
    Timeline_generator()
    
    
def XML_gen(science_mode_timeline_path):
    """Invokes the XML generator program part of Operational Planning Tool for MATS.
    
    Converts a *Science Mode Timeline*  (.json file) containing a list of scheduled Science Modes/CMDs/Tests into Payload and Plattoform commands and saves them as a .xml command file.  \n
    Settings for the operation of the program are stated in the chosen *Configuration File*, set by *Set_ConfigFile*.
    Settings given in the *Science Mode Timeline* override the settings given in the chosen *Configuration file*.
    
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


def Timeline_analyzer(science_mode_timeline_path, date):
    '''Invokes the Timeline_analyser program part of Operational Planning Tool.
    
    Searches a Science Mode Timeline json file for a given date and returns the scheduled mode and its parameters"
    
    Arguments:
        science_mode_timeline_path (str): path to the .json file containing the Science Mode Timeline
        date (str): A given date and time ('2019/09/05 12:09:25')
        
    Returns:
        (tuple): tuple containing: 
            
            **Mode** (*str*): The currently scheduled Mode. \n
            **Parameters** (*dict*): The parameters of the Mode. \n
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
    
    
def Timeline_Plotter(Science_Mode_Path, OHB_H5_Path = '', Timestep = 16 ):
    '''Invokes the *Timeline_Plotter* program part of *Operational_Planning_Tool*.
    
    Simulates the position and attitude of MATS from a given Science Mode Timeline and also optionally compares it to
    positional and attitude data given in a .h5 data set, located at *OHB_H5_Path*. Plots both the simulated data and given data. \n
    Settings for the operation of the program are stated in the chosen *Configuration File*. 
    Settings stated in the *Science Mode Timeline* override settings given in the chosen *Configuration file*.
    
    Arguments:
        Science_Mode_Path (str): Path to the Science Mode Timeline to be plotted.
        OHB_H5_Path (str): *Optional*. Path to the .h5 file containing position, time, and attitude data.
        Timestep (int): *Optional*. The chosen timestep of the simulation [s].
        
    Returns:
        (tuple): tuple containing:
            
            - **Data_MATS** (*dict*): Dictionary containing lists of simulated data of MATS. \n
            - **Data_LP** (*dict*): Dictionary containing lists of simulated data of LP. \n
            - **Time** (*list*): List containing timestamps of the simulated data in Data_MATS and Data_LP. \n
            - **Time_OHB** (*list*): List containing timestamps of the plotted data in .h5 file. \n
        
        
    '''
    from ._Timeline_Plotter.Core import Timeline_Plotter
    
    
    Data_MATS, Data_LP, Time, Time_OHB  = Timeline_Plotter(Science_Mode_Path = Science_Mode_Path, OHB_H5_Path = OHB_H5_Path, Timestep = Timestep)
    
    return Data_MATS, Data_LP, Time, Time_OHB
    