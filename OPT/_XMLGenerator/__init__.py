"""The *XMLGenerator* part of the *Operational_Planning_Tool* which purpose is to create XML files as defined in the "InnoSat Payload Timeline XML Defintion" document. \n 
The submodule *XML_gen* contains the function used to convert a *Science Mode Timeline* .json file into an XML file, containing Payload and Platform CMDs. \n

The submodule *MinimalScienceXMLGenerator* contains a function which creates a predefined, time independent XML, used by OHB at unexpected power resets. \n

Both programs uses the lmxl package to create a XML file. \n

"""