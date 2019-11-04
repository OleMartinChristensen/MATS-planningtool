"""The *XMLGenerator* part of the *Operational_Planning_Tool* which purpose is to create XML files as defined in the "InnoSat Payload Timeline XML Defintion" document. \n 
*XML_gen* contains the function to convert a *Science Mode Timeline* .json file into an XML file, containing Payload and Platform CMDs. \n

*MinimalScienceXMLGenerator* contains a function for which to create a predefined, time independent XML, used by OHB at unexpected power resets. 
Both parts sses the lmxl package to create a XML file. \n

"""