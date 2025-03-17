"""Tests for invoice editing API"""

import xml.etree.ElementTree as ET
from pathlib import Path
from fastapi.testclient import TestClient
from src.main import app
from src.tests.tests_main import write_xml

client = TestClient(app)

INVOICE_FILE = "./src/tests/resources/invoice_provided_valid.xml"

def setup_invoice_file():
    invoice_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <Invoice>
        <InvoiceId>123</InvoiceId>
        <AccountingCustomerParty>Original Customer</AccountingCustomerParty>
        <LegalMonetaryTotal>
            <Value>100.00</Value>
            <Currency>CAD</Currency>
        </LegalMonetaryTotal>
    </Invoice>"""

    file_path = Path(INVOICE_FILE)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(invoice_xml_content, encoding="utf-8")

def test_edit_invoice_success():
    """Test successful editing of an invoice."""
    write_xml(
        "invoice_provided_valid.xml",
        """<Invoice>
            <InvoiceId>123</InvoiceId>
            <AccountingCustomerParty>Original Customer</AccountingCustomerParty>
            <LegalMonetaryTotal>
                <Value>100.00</Value>
                <Currency>CAD</Currency>
            </LegalMonetaryTotal>
        </Invoice>"""
    )

    updated_data = {
        "AccountingCustomerParty": "Updated Customer",
        "LegalMonetaryTotal": {"Value": "150.00", "Currency": "USD"}
    }

    response = client.put("/ubl/invoice/edit/123", json=updated_data)

    # # Debugging: Print response to check format
    # print("Response Status Code:", response.status_code)
    # print("Raw Response Text:", repr(response.text))

    assert response.status_code == 200

    # Sanitize the response text before parsing
    response_text = response.text.strip().replace("\ufeff", "")

    try:
        root = ET.fromstring(response_text)
    except ET.ParseError as e:
        print("XML Parsing Error:", e)
        print("Raw Response:", response_text)
        raise  # Re-raise to see full error in pytest

    # Extract values from XML
    assert root.find("InvoiceId").text == "123"
    assert root.find("AccountingCustomerParty").text == "Updated Customer"
    assert root.find("LegalMonetaryTotal/Value").text == "150.00"
    assert root.find("LegalMonetaryTotal/Currency").text == "USD"

def test_edit_invoice_not_found():
    """Test error when editing a non-existent invoice."""
    setup_invoice_file()

    response = client.put("/ubl/invoice/edit/999", json={"AccountingCustomerParty": "New Customer"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Invoice not found"}

def test_edit_invoice_missing_id():
    """Test error when invoice ID is missing in the request."""
    setup_invoice_file()

    response = client.put("/ubl/invoice/edit/", json={"AccountingCustomerParty": "New Customer"})

    assert response.status_code == 404  # FastAPI returns 404 for missing path params

def test_edit_invoice_missing_input():
    """Test error when input data is missing."""
    setup_invoice_file()

    response = client.put("/ubl/invoice/edit/123", json={})

    assert response.status_code == 400
    assert response.json() == {"detail": "Missing or invalid input data"}

def test_edit_invoice_file_not_found():
    """Test error when the invoice file is not found."""
    
    response = client.put("/ubl/invoice/edit/123", json={"AccountingCustomerParty": "New Customer"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Invoice file not found"}
