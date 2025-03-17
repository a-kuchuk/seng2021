"""Module for testsing the main FastAPI application."""

from pathlib import Path

def get_xml(file_name):
    """Function to read the content of an XML file."""
    valid_xml_file_path = Path(__file__).parent / "resources" / file_name
    with valid_xml_file_path.open("r", encoding="utf-8") as xml_file:
        return xml_file.read()
