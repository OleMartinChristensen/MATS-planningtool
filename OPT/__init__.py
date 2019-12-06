# -*- coding: utf-8 -*-
"""Make sure to read the "Science Modes for MATS" document (at least Version 3.1). The programs (functions) that together constitute the Operational_Planning_Tool (OPT) are:
    
    - Copy_ConfigFile
    - Set_ConfigFile
    - CheckConfigFile
    - Timeline_gen
    - XML_gen
    - MinimalScienceXML_gen
    - Timeline_analyzer
    - Timeline_Plotter
    - Plot_Timeline_Plotter_Plots

**Abbreviations:**
    CMD = Command \n
    FOV = Field of View \n
    LP = Look point of the instrument \n
    OPT = Operational Planning Tool
    
**Description:**
*Operational_Planning_Tool* uses a hiearchy structure with a procedural programming paradigm. Meaning that only the top level functions (the ones mentioned above) are supposed to be called by a user. \n

*Operational_Planning_Tool* uses a special .py file as a *Configuration File*, meaning that the settings inside the *Configuration File* dictate the operation of the program (unless the same settings are explicitly stated in the input of a function, see *XML_gen* and *Timeline_Plotter*). 
An example of a *Configuration_File* with default values is located in the Operational_Planning_Tool and is called *_ConfigFile.py*.  \n

Create your own *Configuration File* with an appropriate name by running *Copy_ConfigFile* with a chosen name as an input. 
*Copy_ConfigFile* makes a copy of *_ConfigFile.py*. The settings in your copy are modified manually in a text editor. \n

Your *Configuration File* and its date must be chosen by running *Set_ConfigFile*. \n

The objective of *Operational_Planning_Tool* is to create a file consisting of planned Science Modes and Commands with timestamps (specified in "Science Modes for MATS" document). 
A *Science Mode Timeline*, as it is called, is created by running *Timeline_gen*. Remember to edit and choose your *Configuration File* by running *Set_ConfigFile*. \n

The created *Science Mode Timeline* can be converted into a XML-file containing Payload and Platform Commands (formatted as specified in the "Innosat Payload Timeline XML Definition" document) 
by running *XML_gen* with the *Science Mode Timeline* as the input. The *_XMLGenerator* package also contains the definition of Science Modes and Macros on an operational level.

The *Science Mode Timeline* can also be simulated and and plotted by running *Timeline_Plotter* with the *Science Mode Timeline* as the input. 
*Timeline_Plotter* can also optionally plot a special kind of .h5 data-files, created by OHB SWEDEN. \n

**Note:** A *Science Mode Timeline* usually contains settings that are taken from the chosen *Configuration File* when the *Science Mode Timeline* was created. 
Any time a function uses a *Science Mode Timeline* as an input, these settings will be given priority over any similar settings stated in the currently chosen *Configuration File*. \n

*Check_ConfigFile* is used to check if the values stated in the chosen *Configuration File* are plausible. \n

All generated output files are saved in a folder called 'Output' in the working directory.
Generated logs are saved in folders created in the working directory.


Example:
    import OPT
    
    *#Create a new Configuration File named OPT_Config_File.#* \n
    OPT.Copy_ConfigFile('OPT_Config_File')
    
    *#Optionally change any settings in OPT_Config_File by using a text editor.#* \n
    
    *#Choose the newly created Configuration File and set the starting date.#* \n
    OPT.Set_ConfigFile('OPT_Config_File', '2019/09/05 08:00:00')
    
    *#Sanity check for values in the chosen Configuration File.#* \n
    OPT.CheckConfigFile()
    
    *#Creates a Science Mode Timeline specified by settings given in the chosen Configuration File.#* \n
    OPT.Timeline_gen()
    
    *#Converts the created Science Mode Timeline into an XML-file. Settings stated in the Science Mode Timeline overrides settings in the Configuration File#* \n
    OPT.XML_gen('Output/Science_Mode_Timeline__OPT_Config_File.json')
    
    *#Plots the Science Mode Timeline.#* \n
    Data_MATS, Data_LP, Time, Time_OHB  = OPT.Timeline_Plotter('Output/Science_Mode_Timeline__OPT_Config_File.json')
 
**Note:** \n

Science Modes are separated into 2 different areas, *Operational Science Modes* (Mode 1,2,5) and *Calibration Modes*. \n
*Calibration Modes* are scheduled at specific points of time and are usually only scheduled once per *Science Mode Timeline*. 
*Operational Science Modes* (Mode 1,2,5) are scheduled whenever time is available (after the scheduling of *Calibration Modes*) and only 1 *Operational Science Mode* is scheduled per Timeline.

"""



def Copy_ConfigFile(Config_File_Name):
    """Makes a copy of the *_ConfigFile* located in *Operational_Planning_Tool*.
    
    The copy is created in the working directory of the user call and can be freely modified.
    Do not forget to also use *Set_ConfigFile* to choose your specific copy.
    *_ConfigFile* is imagined to contain the default settings of the program, while each copy contains week specific settings.
    If the default *_ConfigFile* is ever changed it is recommended to change the Version Name of it to keep track of changes.
    
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
        
    
        
    


def Set_ConfigFile(Config_File_Name, Date, TLE1='1 54321U 19100G   20172.75043981 0.00000000  00000-0  75180-4 0  0014', 
                   TLE2='2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010'):
    """Sets the StartTime and TLE for OPT, and the name of the *.py* file that shall be used as a *Configuration file* for OPT.
    
    The *Configuration file* chosen must be visible in sys.path.
    
    Arguments:
        Config_File_Name (str): The name of the Config File to be used (excluding .py).
        Date (str): The start time and date for the Operational Planning Tool (yyyy/mm/dd hh:mm:ss).
        TLE1 (str): The first row of the TLE.
        TLE2 (str): The second row of the TLE.
        
    Returns:
        None
    """
    
    from . import _Globals as Globals
    
    Globals.Config_File = Config_File_Name
    Globals.StartTime = Date
    Globals.TLE = (TLE1,TLE2)
    


def CheckConfigFile():
    """Checks the values of the settings in the *Configuration File* chosen with *Set_ConfigFile*.
    
    Also prints out the currently selected *Configuration File* and which starting date and TLE it currently uses.
    
    """
    from ._CheckConfigFile.Core import CheckConfigFile
    
    CheckConfigFile()


def Timeline_gen():
    """Invokes the Timeline generator part of Operational Planning Tool.
    
    Creates a *Science Mode Timeline* as a .json file. \n
    Predicts and schedueles Science Modes that depend on certain events such as position of stars and the moon (Mode120-Mode124). 
    Other Science Modes and StartUpCMDs are just scheduled at the start of the Timeline or at a given date. 
    The Science Modes and StartUpCMDs to be scheduled are listed in *Modes_priority* in the chosen *Configuration File*.
    
    *Operational Science Modes* (example: Mode 1,2,5) are scheduled separately wherever time is available at the end of the program.
    
    Settings for the operation of the program are stated in the *Configuration File* chosen with *Set_ConfigFile*.
    
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
    
    from ._XMLGenerator.XML_gen import XML_generator
    from . import _Globals as Globals
    
    
    "Initialize current_pointing to None"
    Globals.current_pointing = None
    #Globals.science_mode_timeline_path = science_mode_timeline_path
    
    XML_generator(science_mode_timeline_path)


def Timeline_analyzer(science_mode_timeline_path, date):
    '''Invokes the Timeline_analyser program part of Operational Planning Tool.
    
    Searches a Science Mode Timeline json file for a given date and returns the scheduled mode and its parameters.
    
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
    
    
def Timeline_Plotter(Science_Mode_Path, OHB_H5_Path = '', STK_CSV_PATH = '', Timestep = 16 ):
    '''Invokes the *Timeline_Plotter* program part of *Operational_Planning_Tool*.
    
    Simulates the position and attitude of MATS from a given Science Mode Timeline and also optionally compares it to
    positional and attitude data given in a .h5 data set, located at *OHB_H5_Path*. Plots both the simulated data and given data. 
    The attitude data shows only the target orientation and does not mimic MATS's actual control system. The timesteps of both the .h5 data and the Science Mode is synchronized to allow direct comparison if possible. \n
    A .csv file, generated in STK, may also be included to plot the predicted positional error of the satellite compared to STK data.
    Saves generated plots as binary files. \n
    Settings for the operation of the program are stated in the chosen *Configuration File*. 
    Settings stated in the *Science Mode Timeline* override settings given in the chosen *Configuration file*.
    
    Arguments:
        Science_Mode_Path (str): Path to the Science Mode Timeline to be plotted.
        OHB_H5_Path (str): *Optional*. Path to the .h5 file containing position, time, and attitude data. The .h5 file is defined in the "Ground Segment ICD" document.
        STK_CSV_PATH (str): *Optional*. Path to the .csv file containing position (column 1-3), velocity (column 4-6), and time (column 7), generated in STK. Position and velocity data is assumed to be in km and in ICRF.
        Timestep (int): *Optional*. The chosen timestep of the simulation [s].
        
    Returns:
        (tuple): tuple containing:
            
            - **Data_MATS** (*dict*): Dictionary containing lists of simulated data of MATS. \n
            - **Data_LP** (*dict*): Dictionary containing lists of simulated data of LP. \n
            - **Time** (*list*): List containing timestamps (utc) of the simulated data in Data_MATS and Data_LP. \n
            - **Time_OHB** (*list*): List containing timestamps (utc) of the plotted data in the .h5 file. \n
        
        
    '''
    from ._Timeline_Plotter.Core import Timeline_Plotter
    
    
    Data_MATS, Data_LP, Time, Time_OHB  = Timeline_Plotter(Science_Mode_Path = Science_Mode_Path, OHB_H5_Path = OHB_H5_Path, STK_CSV_FILE = STK_CSV_PATH, Timestep = Timestep)
    
    return Data_MATS, Data_LP, Time, Time_OHB
    

def Plot_Timeline_Plotter_Plots(FigureDirectory, FilesToPlot = ['ActiveScienceMode', 'Yaw', 
                                               'Pitch', 'Roll','Lat', 'Long', 'Alt', 'PosError', 
                                               'PosErrorRCI', 'MagPosError', 'Lat_LP', 'Long_LP', 
                                               'Alt_LP', 'AltError_LP', 'PosError_LP', 'PosErrorRCI_LP',
                                               'MagPosError_LP', 'RA_OpticalAxis', 'RA_OpticalAxisError', 
                                               'Dec_OpticalAxis', 'Dec_OpticalAxisError', 
                                               'PosErrorMATS_STK']):
    """Plots binary files created with *Timeline_Plotter*.
    
    Tries to plot all files which are generated by default by *Timeline_Plotter* unless a second input is given.
    
    Arguments:
        FigureDirectory (str): Path to the directory where the binary files are located.
        FilesToPlot (list of str): Optional. List of strings containing the names of the binary files (excluding "fig.pickle") to be plotted.
    
    """
    
    from ._Plot_Timeline_Plotter_Plots.Core import Plot_Timeline_Plotter_Plots
    
    Plot_Timeline_Plotter_Plots(FigureDirectory, FilesToPlot)
    
    

def MinimalScienceXML_gen():
    """Invokes the *MinimalScienceXML_gen* part of the *OPT*.
    
    Creates an .xml file with fixed CMDs which purpose is to define a flight procedure which is ran on the satellite 
    following unscheduled power termination of the payload.
    Runs startup CMDs and sets the payload in operational mode with the CCD macro *HighResIR*.
    The CMD staggering is fixed. No date is given in the generated XML and will need to be added manually.
    Uses settings for the CMDs from the currently set *Configuration File*.
    
    """
    
    from ._XMLGenerator.MinimalScienceXML_gen import MinimalScienceXMLGenerator
    
    MinimalScienceXMLGenerator()