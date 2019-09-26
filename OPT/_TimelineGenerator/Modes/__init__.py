#
"""Contains modules which correspond to the scheduling of each Mode. 

Schedules and calculates duration of modes.

The top or core function of each module is the only one called from higher levels.
The name of the core function in each Mode specific module must be equal to the name 
of the Mode as stated in *Modes_priority* found in the *Configuration File*.  \n

The core function may call two other functions inside the same module, date_calculator() and date_select.
date_calculator returns calculated or chosen dates (1 or many).
date_select chooses the most appropriate date or/and makes sure the date chosen is available.

Core function for the scheduling of a Mode.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes with entries equal to their start and end time as a list.
        
    Returns:
        (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated for the current Mode).\n
        (str): Comment regarding the scheduling result of the active mode.
    
    

"""