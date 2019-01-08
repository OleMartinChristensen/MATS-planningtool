# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 16:08:16 2018

Represents how a user would create an XML file by calling one function with a read-in Sciencemode list

@author: David
"""


from MATS_TIMELINE_XML_generator import MATS_TIMELINE_XML_generator
import json

SCIMOD_TIMELINE = []

with open("MATS_AUTOMATIC_SCIMOD_generator\MATS_SCIMOD_TIMELINE.json", "r") as read_file:
    SCIMOD_TIMELINE = json.load(read_file)
    

MATS_TIMELINE_XML_generator(SCIMOD=SCIMOD_TIMELINE)


