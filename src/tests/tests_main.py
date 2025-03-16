"""Module for testsing the main FastAPI application."""

from fastapi.testclient import TestClient
from src import main

def test_xml_to_pdf(): 
    response = client.get("/ubl/invoice/pdf/invoice_provided_valid.xml")

