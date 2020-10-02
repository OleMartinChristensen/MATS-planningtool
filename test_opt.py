# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:56:23 2019

Main test script showcasing how to use the main parts of OPT.

@author: David Skånberg
"""

import OPT


# "Make a copy of the defualt Configuration File in OPT and name it 'OPT_Config_File'"
OPT.Copy_ConfigFile("OPT_Config_File")

# "Choose your Configuration File ('OPT_Config_File') and set the start date and TLE"
OPT.Set_ConfigFile(
    "OPT_Config_File",
    "2020/9/25 16:45:00",
    TLE1="1 54321U 19100G   20172.75043981 0.00000000  00000-0  75180-4 0  0014",
    TLE2="2 54321  97.7044   6.9210 0014595 313.2372  91.8750 14.93194142000010",
)

# "Choose your Configuration File ('OPT_Config_File') but optionally use the TLE and start date values given directly in the Configuration File"
OPT.Set_ConfigFile("OPT_Config_File")

# "Check the currently chosen Configuration File and the plausibility of its values. Prints out the currently used start date and TLE"
OPT.CheckConfigFile()

# "Create a Science Mode Timeline (.json file) depending on the settings in the Configuration File"
OPT.Timeline_gen()

# "Predict state and attitude data from the Science Mode Timeline and plot the results"
# Data_MATS, Data_LP, Time, Time_OHB = OPT.Timeline_Plotter(
#     "Output/Science_Mode_Timeline__OPT_Config_File.json", Timestep=20
# )

# "Convert the Science Mode Timeline into payload and platform CMDs as a .xml file)"
OPT.XML_gen("Output/Science_Mode_Timeline__OPT_Config_File.json")

# "Plot the example Science Mode Timeline together with the example h5 file and the example STK generated .csv file"
# Data_MATS, Data_LP, Time, Time_OHB = OPT.Timeline_Plotter(
#     "OPT/Example_Science_Mode_Timeline__OPT_Config_File.json",
#     STK_CSV_PATH="OPT/ExampleCSVfile.csv",
#     OHB_H5_Path="OPT/ExampleH5file_LEVEL_1A_PLATF_20200120-094217_20200120-102136.hdf5",
#     Timestep=20,
# )

# "Open plots previously created with Timeline_Plotter"
# OPT.Plot_Timeline_Plotter_Plots(
#     "Output/Science_Mode_Timeline__OPT_Config_File/Timeline_Plotter_PlotsAndData"
# )

# # "Return the active science mode and its settings at a specfic date from a Science Mode Timeline"
# Mode, Parameters = OPT.Timeline_analyzer(
#     "Output/Science_Mode_Timeline__OPT_Config_File.json", "2020-06-20 19:30:00"
# )

# "Create a Minimal Science XML which is defined directly in the Source Code under _XMLGenerator.MinimalScienceXML_gen.py"
# OPT.MinimalScienceXML_gen()

# "Schedule StartUpCMDs and all defined commisioning phase Tests with default settings"
# OPT.XML_gen("OPT/Example_Science_Mode_Timeline__Commisioning_Phase_Tests.json")

OPT.PLUTOGenerator(
    "Output/XML_TIMELINE__FROM__Output_Science_Mode_Timeline__OPT_Config_File.xml",
    "Output/optest_pluto.plp",
)

# OPT.PLUTOGenerator(
#     "Output/XML_TIMELINE__MinimalScience_.xml", "Output/minimal_science_pluto.plp",
# )

