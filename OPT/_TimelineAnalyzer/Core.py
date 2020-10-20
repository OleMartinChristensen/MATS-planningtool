# -*- coding: utf-8 -*-
"""
Searches a *Science Mode Timeline* .json file for a given date and returns the scheduled mode and its settings.
A part of the Operational Planning Tool.
"""

import ephem
import json
import os


def get_mode(Mode_Timeline, date):

    for x in range(len(Mode_Timeline)):

        "Skip if first element is Timeline_settings"
        if Mode_Timeline[x][0] == "Timeline_settings":
            continue

        start_date = ephem.Date(Mode_Timeline[x][1])
        end_date = ephem.Date(Mode_Timeline[x][2])

        "If not the last element, extract the starting date of the next mode"
        if x != len(Mode_Timeline) - 1:
            next_start_date = ephem.Date(Mode_Timeline[x + 1][1])

        "If the input date is between the starting and end date of a mode or between the starting dates for two different modes"
        if date >= start_date and (date < end_date or date < next_start_date):
            Mode = Mode_Timeline[x][0]
            Settings = Mode_Timeline[x][3]
            break
        elif x == len(Mode_Timeline) - 1:
            raise ValueError("No mode scheduled during that date")

    return Mode, Settings


def Timeline_analyzer(science_mode_timeline_path, date):
    """The core function of the Timeline_analyse program.

    Arguments:
        science_mode_timeline_path (str): path to the .json file containing the Science Mode Timeline.
        date (str): A given date and time ('2019/09/05 12:09:25')

    Returns:
        (tuple): tuple containing:

            **Mode** (*str*): The Mode scheduled at the given date.
            **Settings** (*dict*): The settings of the Mode.

    """

    if os.path.isfile(science_mode_timeline_path) == False:
        raise NameError(science_mode_timeline_path + ", No such file exist...")
    else:

        ################# Read Science Mode Timeline json file ############
        with open(science_mode_timeline_path, "r") as read_file:
            Mode_Timeline = json.load(read_file)
        ################# Read Science Mode Timeline json file ############

        if isinstance(date, list):
            Mode = []
            Settings = []
            for i in range(len(date)):
                date_value = ephem.Date(date[i])

                try:
                    Mode_value, Settings_value = get_mode(
                        Mode_Timeline, date_value)
                except ValueError:
                    Mode_value = []
                    Settings_value = []

                Mode.append(Mode_value)
                Settings.append(Settings_value)

        else:
            date = ephem.Date(date)
            Mode, Settings = get_mode(Mode_Timeline, date)

        return Mode, Settings
