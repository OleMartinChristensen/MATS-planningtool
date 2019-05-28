# MATS-planningtool
Mission planning tool for the MATS satellite

Operational_Planning_Tool requires at least Python 3.7.3 and these packages:
    
    ephem = Version: >= 3.7.6.0
    matplotlib = Version: >= 3.1.0
    scipy = Version: >= 1.3.0
    lxml = Version: >= 4.3.3
    astroquery, Version: >= 0.3.9, astropy
    pymap3d, Version: >= 1.8.0, pypi
    
It is recommended to install these packages in a conda environment using conda and to use "Spyder" as an editor.

What follows is a basic tutorial for beginners to python3 on how to setup python3 inside a conda environment 
and then install the required packages.

1. Install Anaconda (or Miniconda if prefered) from their website. 

One instance of Python3 is installed together with Anaconda (or Miniconda) inside the conda environment.
Anaconda comes with many preinstalled python packages and some of the ones required by Operational Planning
Tool may already be installed (scipy for example). Miniconda comes with no preinstalled packages and also no graphical interface.

2. After installation open the program "Anaconda Prompt".

3. Run these commands in the "Anaconda Prompt" to install the desired packages.

$ conda install -c anaconda ephem

$ conda install -c conda-forge matplotlib 

$ conda install -c anaconda scipy 

$ conda install -c anaconda lxml

$ conda install -c astropy astroquery

$ conda install pip

$ pip install pymap3d


4. Run the following command to list all currently installed packages and their version number.

$ conda list

5. Then install Spyder by once again using the "Anaconda Prompt".

$ conda install spyder

6. Run Spyder and create a project (found at the toolbar at the top). Place the Operational_Planning_Tool package in the working directory of the project.

The Operational_Planning_Tool package can be put anywhere in *sys.path* but it is easiest to put it in the working directory
of the Spyder project, as that directory is automatically part of the PYTHONPATH which is part of *sys.path*.

7. Finally try to execute these lines in Spyder (either in the IPython console or as part of a script).

import Operational_Planning_Tool as OPT

print(OPT.Create_ConfigFile.__doc__)

OPT.Create_ConfigFile()

print(OPT.Set_ConfigFile.__doc__)

OPT.Set_ConfigFile('OPT_Config_File')

print(OPT.Timeline_gen.__doc__)

OPT.Timeline_gen()

See further documentation found under "Docs" in Operational_Planning_Tool to learn how to use the Operational_Planning_Tool package.
