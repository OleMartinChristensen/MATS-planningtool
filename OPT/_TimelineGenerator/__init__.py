"""**Description:** \n

The *Timeline_gen* part of the *Operational_Planning_Tool* which purpose is to automatically generate a
*Science Mode Timeline* from settings defined in the set *Configuration File*. The generated timeline consists of
Science Modes and separate CMDs together with their planned start/end dates, settings, and comments, 
expressed as a list in that order. \n

*Timeline_gen* has a setable priority for the scheduling of modes and CMDs, 
which can be seen in the order of the modes in the list fetched from the 
function *Scheduling_priority* in the *Configuration File*. \n

For each mode/CMD, one at a time, an appropriate date is calculated, or
a predetermined date is already set in the *Configuration File* (or could also be at the start of the timeline if no specific date was given). A dictionary (Occupied_Timeline) 
keeps track of the planned runtime of all Modes/CMDs, this to prevent colliding scheduling. \n

Mode1,2,5 are known as *Operational Science Modes*.
These modes will fill out time left available after the rest of the Modes, set in *Scheduling_priority*, have been scheduled. 

If calculated starting dates for modes are occupied, they will be changed  
depending on a specialized filtering process (mode 120-124...), or postponed until time is available (CMDs and mode 130, 131...) using *_Library.scheduler*.

**Adding your own Science Modes:** \n

To add your own Mode to be scheduled using *Timeline_gen* you need to follow these steps: \n

 - Copy the *ModesTemplate* module in the subpackage *Modes* and name the new copy whatever you want (like the name of the new mode).
 - Change the name of the already defined function (inside the module you just copied from *ModeX*) into the exact name of the new Mode.
 - Lastly import your new function inside the *Modes_Header* module, which is also located in the *Modes* package, and also add your new Mode into the *Scheduling_priority* function inside the *Configuration File*.
 - It is recommended (but not necessary) to also give the new Mode its own "Configuration function" inside the *_ConfigFile*. This function will hold tuneable settings for the Mode, such as the duration.
 
 The function, inside your new module, has as input the *Occupied_Timeline* variable, which is a dictionary with keys equal to the names of scheduled modes. 
 Each key then contain a list of duples. Each element in each duple is a *ephem.Date* object, representing the scheduled starting date and end date respectively. \n
 
 The output of the function is a tuple where the first element is the *Occupied_Timeline* dictionary again. You can see in the code of your new module that the *Occupied_Timeline* variable is updated with a newly scheduled start date and end date.
 
 The second element of the output tuple is a string containing any comment you want. Currently it is by default just saying how many times the Mode got postponed and rescheduled.
 
 Your new mode should now be scheduled at the start of the timeline, or as soon as time is available, with a duration of 600 seconds when running *Timeline_gen*.

 Feel free to redesign the scheduling process of your new Mode any way you want, as long as the input and output stays the same and that the *Occupied_Timeline* dictionary is still updated with the newly scheduled start date and end date. 

"""