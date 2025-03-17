"""Module for testsing the main FastAPI application."""

import json
from pathlib import Path
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def get_xml(file_name):
    """Function to read the content of an XML file."""
    valid_xml_file_path = Path(__file__).parent / "resources" / file_name
    with valid_xml_file_path.open("r", encoding="utf-8") as xml_file:
        return xml_file.read()

def test_xml_to_pdf(): 
    print("hello?")
    xml = get_xml("invoice_provided_valid.xml")
    files = {"file": ("test.xml", xml_content, "text/xml")}
    response = client.get("/ubl/invoice/pdf", files=files)

