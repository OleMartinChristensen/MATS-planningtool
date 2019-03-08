# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 15:43:21 2018

Creates the base of the XML-tree and calculates initial values such as the 
start and end time and also duration of the timeline.



@author: David
"""

from lxml import etree
from MATS_TIMELINE_XML_generator_select import XML_generator_select
from MATS_TIMELINE_SCIMOD_DEFAULT_PARAMS import Timeline_params, initialConditions

import ephem


def MATS_TIMELINE_XML_generator(SCIMOD):
    
    
    
    timeline_duration = Timeline_params()['duration']
    
    timeline_start = Timeline_params()['start_time']
    
    #earliestStartingDate = str(ephem.Date(timeline_start-ephem.second)).replace(' ','T')
    #latestStartingDate = str(timeline_start).replace(' ','T')
    
    earliestStartingDate = ephem.Date(timeline_start-ephem.second).datetime().strftime("%Y-%m-%dT%H:%M:%S")
    latestStartingDate = ephem.Date(timeline_start).datetime().strftime("%Y-%m-%dT%H:%M:%S")
    
    #earliestStartingDate = earliestStartingDate.replace('/','-')
    #latestStartingDate = latestStartingDate.replace('/','-')
    
    
    ########    Call function to create XML-tree basis ##########################
    root = XML_Initial_Basis_Creator(earliestStartingDate,latestStartingDate,timeline_duration)
    
    ######## Loop through SCIMOD TIMELINE lIST, selecting one mode at a time #####
    for x in range(len(SCIMOD)):
        
        mode_duration = int((ephem.Date(SCIMOD[x][2]) - ephem.Date(SCIMOD[x][1]) ) *24*3600)
        relativeTime = int((ephem.Date(SCIMOD[x][1])-ephem.Date(timeline_start))*24*3600)
        
        XML_generator_select(root, mode_duration, relativeTime, mode=SCIMOD[x][0], date=ephem.Date(SCIMOD[x][1]), params=SCIMOD[x][3])
        
    #print(etree.tostring(root, pretty_print=True, encoding = 'unicode'))
    
    ### Write finished XML-tree to a file ###
    f = open('MATS_COMMANDS.xml', 'w')
    f.write(etree.tostring(root, pretty_print=True, encoding = 'unicode'))
    f.close()



################### XML-tree basis creator ####################################

def XML_Initial_Basis_Creator(earliestStartingDate,latestStartingDate,timeline_duration):
    "Construct Basis of XML document and adds the description container"
    
    
    
    root = etree.Element('InnoSatTimeline', originator='OHB', sdbVersion='9.5.99.2')
    
    
    root.append(etree.Element('description'))
    
    
    etree.SubElement(root[0], 'timelineID', procedureIdentifier = "", descriptiveName = "", version = "1.0")
    
    etree.SubElement(root[0], 'changeLog')
    etree.SubElement(root[0][1], 'changeLogItem', version = "1.1", date = "2019-01-17", author = "David Skånberg")
    root[0][1][0].text = "Created Document"
    
    
    etree.SubElement(root[0], 'initialConditions')
    etree.SubElement(root[0][2], 'spacecraft', mode = initialConditions()['spacecraft']['mode'], acs = initialConditions()['spacecraft']['acs'])
    etree.SubElement(root[0][2], 'payload', power = initialConditions()['payload']['power'], mode = initialConditions()['payload']['mode'])
    
    
    etree.SubElement(root[0], 'validity')
    etree.SubElement(root[0][3], 'earliestStartingDate')
    root[0][3][0].text = earliestStartingDate
    etree.SubElement(root[0][3], 'latestStartingDate')
    root[0][3][1].text = latestStartingDate
    etree.SubElement(root[0][3], 'scenarioDuration')
    root[0][3][2].text = str(timeline_duration)
    
    etree.SubElement(root[0], 'comment')
    root[0][4].text = "This command sequence is an Innosat timeline"
    
    
    root.append(etree.Element('listOfCommands'))
    
    return root
    
####################### End of XML-tree basis creator #############################
    