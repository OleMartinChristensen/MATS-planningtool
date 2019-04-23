#
"""Contains modules which correspond to the scheduling of each Mode.

The top or core function of each module is the only one called from higher levels.
The name of the core function in each Mode specific module must be equal to the name 
of the Mode as stated in OPT_Config_File.Modes_priority(). The core function calls
two other functions inside the same module, date_calculator() and date_select.
date_calculator returns calculated or chosen dates (1 or many).
date_select filters chooses the most appropriate date or/and makes sure the date chosen is available.

"""