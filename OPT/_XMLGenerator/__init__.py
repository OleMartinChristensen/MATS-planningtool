"""The *XML_gen* part of the *Operational_Planning_Tool* which purpose is to convert a
*Science Mode Timeline* .json file into a XML file, containing Payload and Platform CMDs. \n

Any settings given in the *Science Mode Timeline* file will overide the use of the same settings stated in the set *Configuration File*.

All CMDs are stated in the "InnoSat Payload Timeline XML Defintion" document. 

*XML_gen* goes through the *Science Mode Timeline* chronologically and calls for functions from the modules inside the *Modes_and_Tests* package.

These functions then uses the settings given in the *Science Mode Timeline* or in the set *Configuration File* to calculate parameters to be used by their CMDs.

Then they either call directly for a Command function, located in the *Commands* module, inside the *Macros_Commands* package, or call for a Macro function located in the *Macros* module, inside the *Macros_Commands* package.

A Macro is a combination of commonly used CMDs. For more information seee the *Macros* module inside the *Macros_Commands* package.

**Adding your own Mode:** \n

To add your own Mode to be converted into CMDs using *XML_gen* you need to follow these steps: \n

 - Go into the *Modes* module, inside the *Modes_and_Tests* package. At the bottom you should find a Mode template function called "XML_generator_X". Copy this function. Replace the X for the name of your Mode.
 - Calculate or define any appropriate parameters for your Mode's CMDs/Macros.
 - Now use these parameters to add any calls for Macros/Command functions located in the modules inside the *Macros_Commands* package. By default there is a call for the *TC_acfLimbPointingAltitudeOffset* CMD as an example, you can remove this.
 - It is recommended (but not necessary) to also give the new Mode its own "Configuration function" inside the *_ConfigFile*. This function will hold tuneable settings for the Mode, such as pointing altitude for the *TC_acfLimbPointingAltitudeOffset* CMD.

You should now have working Mode in XML_gen. Feel free to check the other Modes defined in the *MODES* module to understand how they are implemented. There are also some outcommented lines of code which you might find useful when defining your Mode. 
These outcommented rows of code calls for Mode and CCD settings from the *Configuration File*, and by using *params_checker* it compares the Mode settings to the Mode settings given in the *Science Mode Timeline*. Lastly there is a outcommented call for a Macro called *Operational_Limb_Pointing_macro*.

"""