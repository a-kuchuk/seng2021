"""_summary_

contains route tests

Returns:
    _type_: _description_
"""

import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
from src.main import app
from src.tests.tests_main import write_xml

client = TestClient(app)

def setup_invoice_file():
    """_summary_

    invoice file setup
    """

    # Setup sample invoice file
    # sample_data = {
    #     "123": {
    #         "invoiceId": "123",
    #         "date": "2011-09-22",
    #         "period": {"start": "2011-08-01", "end": "2011-08-31"},
    #         "supplier": "Custom Cotter Pins",
    #         "customer": "North American Veeblefetzer",
    #         "total": {"amt": "100.00", "cur": "CAD"},
    #         "lines": [{"id": "1", "amt": "100.00", "cur": "CAD", "desc": "Cotter pin, MIL-SPEC"}]
    #     }
    # }

    with open(write_xml("invoice_provided_valid.xml"), "w", encoding="utf-8") as file:
        json.dump(write_xml("invoice_provided_valid.xml"), file)

    yield

def test_edit_invoice_success():
    """_summary_

    testing successful editing in invoice
    """
    updated_data = {"AccountingCustomerParty": "Updated Customer", "LegalMonetaryTotal": {"Value": "150.00", "Currency": "USD"}}

    response = client.put("/ubl/invoice/edit/123", json=updated_data)

    assert response.status_code == 200
    assert response.json()["InvoiceId"] == "123"
    assert response.json()["AccountingCustomerParty"] == "Updated Customer"
    assert response.json()["LegalMonetaryTotal"]["Value"] == "150.00"
    assert response.json()["LegalMonetaryTotal"]["Currency"] == "USD"

def test_edit_invoice_not_found():
    """_summary_

    Error: invoice not found
    """
    response = client.put("/ubl/invoice/edit/999", json={"AccountingCustomerParty": "New Customer"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Invoice not found"}

def test_edit_invoice_missing_id():
    """_summary_

    Error: invoice is missing id
    """
    response = client.put("/ubl/invoice/edit/", json={"AccountingCustomerParty": "New Customer"})

    assert response.status_code == 400
    assert response.json()["InvoiceId"] == ""
    assert response.json() == {"detail": "Invoice not found"}

def test_edit_invoice_missing_input():
    """_summary_

    Error: invoice has missing inputs
    """
    response = client.put("/ubl/invoice/edit/123", json={})

    assert response.status_code == 400
    assert response.json() == {"detail": "Missing or invalid input data"}

def test_edit_invoice_file_not_found():
    """_summary_

    Error: invoice file is not found
    """

    response = client.put("/ubl/invoice/edit/123", json={"AccountingCustomerParty": "New Customer"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Invoice file not found"}
