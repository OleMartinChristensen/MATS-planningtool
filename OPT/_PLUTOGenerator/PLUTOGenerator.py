# -*- coding: utf-8 -*-
"""This module contains the core function of the *PLUTO_gen* program and the first subfunction of *PLUTO_gen*.
"""

import xmltodict


def read_xml(filename):
    """Reads in the XML to be converted
    
    Reads a *XML-Timeline*  file. And returns a dictionary
    
    Arguments:
        filename (str): A string containing the path to the Timeline-XML file.
    Returns:
        doc (dictionary)     
    """

    with open(filename) as fd:
        doc = xmltodict.parse(fd.read())
    return doc


def check_payload_command(pafCommand):
    return pafCommand["@mnemonic"][0:6] == "TC_paf"


def write_header(plutopath="tmp.plp"):
    f = open(plutopath, "w")
    f.write("procedure\n")
    f.write("\tinitiate and confirm step myStep\n")
    f.write("\t\tmain\n")
    f.write(
        '\t\t\tlog "------------------------------------------------------------------------------------------------------------------";\n'
    )
    f.write('\t\t\tlog "Starting tests";\n')
    f.write("\t\t\tlog to string (current time());\n")
    f.write("\n")
    f.write("\t\t\tinitiate TC_pafPWRTOGGLE with arguments\n")
    f.write("\t\t\t\tCONST:=165\n")
    f.write("\t\t\tend with;\n")
    f.write("\n")
    f.write("\t\t\twait for 10s;\n")
    f.write("\n")
    f.write("\t\t\tinitiate TC_pafPLTMCONTROL with arguments\n")
    f.write("\t\t\t\tTMMODE:=1\n")
    f.write("\t\t\tend with;\n")
    f.write("\n")
    f.close()


def write_footer(plutopath="tmp.plp"):
    f = open(plutopath, "a+")
    f.write("\t\tend main\n")
    f.write("\tend step;\n")
    f.write("end procedure\n")
    f.close()


def write_tcArgument(pafCommand, plutopath="tmp.plp"):
    if not check_payload_command(pafCommand):
        raise ValueError(
            "Command "
            + pafCommand["@mnemonic"]
            + " PLUTO generator only supports Platform commands"
        )
    elif pafCommand["@mnemonic"] == "TC_pafPWRTOGGLE":
        raise ValueError(
            "Command "
            + pafCommand["@mnemonic"]
            + " PLUTO generator will remove powertoggles"
        )
    else:
        f = open(plutopath, "a+")
        f.write("\t\t\tinitiate " + str(pafCommand["@mnemonic"]) + " with arguments\n")
        if isinstance(pafCommand["tcArguments"]["tcArgument"], list):
            for i in range(len(pafCommand["tcArguments"]["tcArgument"])):
                # print(str(pafCommand["tcArguments"]["tcArgument"][i]))
                f.write(
                    "\t\t\t\t"
                    + str(pafCommand["tcArguments"]["tcArgument"][i]["@mnemonic"])
                    + ":="
                    + str(pafCommand["tcArguments"]["tcArgument"][i]["#text"])
                )
                if i < len(pafCommand["tcArguments"]["tcArgument"]) - 1:
                    f.write(",\n")
                else:
                    f.write("\n")
        else:
            # print(str(pafCommand["tcArguments"]["tcArgument"]))
            f.write(
                "\t\t\t\t"
                + str(pafCommand["tcArguments"]["tcArgument"]["@mnemonic"])
                + ":="
                + str(pafCommand["tcArguments"]["tcArgument"]["#text"])
            )
            f.write("\n")

        f.write("\t\t\tend with;\n\n")
    f.close()


def write_wait(wait_time, plutopath="tmp.plp"):
    if wait_time > 0:
        f = open(plutopath, "a+")
        f.write("\t\t\twait for " + str(wait_time) + "s;\n\n")
        f.close()


def PLUTO_generator(XML_Path, PLUTO_Path="pluto_script.plp"):
    """The core function of the PLUTO_gen program.
    
    Reads a *XML-Timeline*  file. And output a PLUTO script for running on the MATS standalone instrument.
    
    Arguments:
        SCIMXML_Path (str): A string containing the path to the Timeline-XML file.
        PLUTO_Path (str): A string containing the path where outputfile should be written (default "pluto_script.plp")
    Returns:
        None     
    """
    timeline_xml = read_xml(XML_Path)
    write_header(PLUTO_Path)
    command_ignored_flag = 0
    for i in range(len(timeline_xml["InnoSatTimeline"]["listOfCommands"]["command"])):
        if command_ignored_flag == 0:
            if i > 0:
                wait_time = int(
                    timeline_xml["InnoSatTimeline"]["listOfCommands"]["command"][i][
                        "relativeTime"
                    ]
                ) - int(
                    timeline_xml["InnoSatTimeline"]["listOfCommands"]["command"][i - 1][
                        "relativeTime"
                    ]
                )
            else:
                wait_time = 0
        try:
            write_tcArgument(
                timeline_xml["InnoSatTimeline"]["listOfCommands"]["command"][i],
                PLUTO_Path,
            )
            write_wait(wait_time, PLUTO_Path)

        except ValueError:
            print("WARNING: XML contains a ivalid command, the command will be ignored")
            command_ignored_flag += 1

    write_footer(PLUTO_Path)

    return
