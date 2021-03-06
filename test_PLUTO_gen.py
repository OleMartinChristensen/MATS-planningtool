import pytest
from OPT import _PLUTOGenerator as pluto

test_folder = "test_data"


def test_read_xml():
    doc = pluto.PLUTOGenerator.read_xml(
        "/home/olemar/Projects/MATS/MATS-planningtool-backup/test_data/XML_TIMELINE__MinimalScience_.xml"
    )
    assert doc["InnoSatTimeline"]["@originator"] == "OHB"


def test_write_header():
    pluto.PLUTOGenerator.write_header("Output/test_header.plp")
    return


def test_write_footer():
    pluto.PLUTOGenerator.write_header("Output/test_footer.plp")
    pluto.PLUTOGenerator.write_footer("Output/test_footer.plp")
    return


def test_write_all():
    pluto.PLUTOGenerator.PLUTO_generator(
        "test_data/XML_TIMELINE__MinimalScience_.xml", "Output/minimal_science.plp"
    )
    return


def test_write_mimnimal_script():
    pluto.PLUTOGenerator.PLUTO_generator(
        "test_data/XML_TIMELINE__MinimalPluto_.xml", "Output/minimal_pluto.plp"
    )
    return


def test_remove_platform_commands():
    XML_Path = "test_data/XML_TIMELINE__Platform_command_.xml"
    PLUTO_Path = "Output/platform_command.plp"
    timeline_xml = pluto.PLUTOGenerator.read_xml(XML_Path)
    with pytest.raises(ValueError):
        pluto.PLUTOGenerator.write_tcArgument(
            timeline_xml["InnoSatTimeline"]["listOfCommands"]["command"], PLUTO_Path
        )


def test_remove_powertoggle_commands():
    XML_Path = "test_data/XML_TIMELINE__Powertoggle_command_.xml"
    PLUTO_Path = "Output/powertoggle_command.plp"
    timeline_xml = pluto.PLUTOGenerator.read_xml(XML_Path)
    with pytest.raises(ValueError):
        pluto.PLUTOGenerator.write_tcArgument(
            timeline_xml["InnoSatTimeline"]["listOfCommands"]["command"], PLUTO_Path
        )
