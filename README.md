# MATS-planningtool
Mission planning tool for the MATS satellite

OPT (Operational_Planning_Tool) requires at least Python 3.7.3 and these packages (newer versions might work):
    
    	ephem = Version: = 3.7.6.0
    	matplotlib = Version: = 3.1.1
    	scipy = Version: = 1.2.1
    	lxml = Version: >= 4.3.3
    	astroquery, Version: >= 0.3.9, astropy
    	skyfield, Version: = 1.13
		astropy, Version >= 3.2.3, astropy
		h5py, Version = 2.9.0
    
It is recommended to install these packages in a conda environment using conda and to use "Spyder" as an scientific environment.

What follows is a basic tutorial for beginners to python3 on how to setup python3 inside a conda environment 
and then install the required packages.

1. Install Anaconda (or Miniconda if prefered) from their website. 

One instance of Python3 is installed together with Anaconda (or Miniconda) inside the conda environment.
Anaconda comes with many preinstalled python packages, and some of the ones required by Operational Planning
Tool may already be installed (scipy for example). Miniconda comes with no preinstalled packages and also no graphical interface.

2. After installation open the program "Anaconda Prompt".

3. Run these commands in the "Anaconda Prompt" to install the desired packages. Alternatively run the CMD_file.bat in the "Anaconda Prompt".

$ conda install -c anaconda ephem=3.7.6.0

$ conda install -c conda-forge matplotlib=3.1.1 

$ conda install -c anaconda scipy=1.2.1

$ conda install -c anaconda lxml=4.3.3

$ conda install astropy=3.2.3

$ conda install -c astropy astroquery=0.3.9

$ conda install pip

$ conda install -c anaconda h5py=2.9.0

$ conda install -c conda-forge skyfield=1.13


4. Run the following command to list all currently installed packages and their version number.

$ conda list

5. Then install Spyder by once again using the "Anaconda Prompt".

$ conda install spyder

6. Run Spyder and create a project (found at the toolbar at the top). Place the OPT (Operational_Planning_Tool) package in the working directory of the project.

The OPT (Operational_Planning_Tool) package can be put anywhere in *sys.path* but it is easiest to put it in the working directory
of the Spyder project, as that directory is automatically part of the PYTHONPATH which is part of *sys.path*.

7. Allow plots created with python to be printed in separate windows. Go to tools/preferences in Spyder. Then in the preferences window, select "IPython Console". Go to Graphics. In the dropdown menu of "Graphics backend" select automatic.

8. Finally try to execute these lines in Spyder (either in the IPython console or as part of a script).

    import OPT
    
    OPT.Copy_ConfigFile('OPT_Config_File')
    
    OPT.Set_ConfigFile('OPT_Config_File', '2020/09/05 08:00:00')
    
    OPT.CheckConfigFile()
    
    OPT.Timeline_gen()
    
    OPT.XML_gen('Output/Science_Mode_Timeline__OPT_Config_File.json')
	
	Data_MATS, Data_LP, Time, Time_OHB  = OPT.Timeline_Plotter('Output/Science_Mode_Timeline__OPT_Config_File.json')

See further documentation found under "Docs" in OPT (Operational_Planning_Tool) to learn how to use the OPT package. The docs are automatically generated from the source code 
by using the python package Sphinx. The documentation is saved in *OPT_Build_Extensive* and *OPT_Build_Simplified*, where the extensive one contains documentation about every part of OPT, 
including private modules and packages, while the simplified one only contains information about the public functions which are meant to be used by the user. To rebuild the documentation, simply 
run the Sphinx_CMD_File.bat in the anaconda prompt (requires installation of sphinx package).
