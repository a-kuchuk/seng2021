"""_summary_

contains route tests

Returns:
    _type_: _description_
"""

import json
import os
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

INVOICE_FILE = "./src/tests/resources/invoice_provided_valid.xml"

def setup_invoice_file():
    """_summary_

    invoice file setup
    """

    # Setup sample invoice file
    sample_data = {
        "123": {
            "invoiceId": "123",
            "date": "2011-09-22",
            "period": {"start": "2011-08-01", "end": "2011-08-31"},
            "supplier": "Custom Cotter Pins",
            "customer": "North American Veeblefetzer",
            "total": {"amt": "100.00", "cur": "CAD"},
            "lines": [{"id": "1", "amt": "100.00", "cur": "CAD", "desc": "Cotter pin, MIL-SPEC"}]
        }
    }

    with open(INVOICE_FILE, "w", encoding="utf-8") as file:
        json.dump(sample_data, file)

    yield

    if os.path.exists(INVOICE_FILE):
        os.remove(INVOICE_FILE)

def test_edit_invoice_success():
    """_summary_

    testing successful editing in invoice
    """
    updated_data = {"customer": "Updated Customer", "total": {"amt": "150.00", "cur": "USD"}}

    response = client.put("/ubl/invoice/edit/123", json=updated_data)

    assert response.status_code == 200
    assert response.xml()["invoiceId"] == "123"
    assert response.xml()["customer"] == "Updated Customer"
    assert response.xml()["total"]["amt"] == "150.00"
    assert response.xml()["total"]["cur"] == "USD"

def test_edit_invoice_not_found():
    """_summary_

    Error: invoice not found
    """
    response = client.put("/ubl/invoice/edit/999", json={"customer": "New Customer"})

    assert response.status_code == 400
    assert response.xml() == {"detail": "Invoice not found"}

def test_edit_invoice_missing_input():
    """_summary_

    Error: invoice has missing inputs
    """
    response = client.put("/ubl/invoice/edit/123", json={})

    assert response.status_code == 400
    assert response.xml() == {"detail": "Missing or invalid input data"}

def test_edit_invoice_file_not_found():
    """_summary_

    Error: invoice file is not found
    """
    os.remove(INVOICE_FILE)

    response = client.put("/ubl/invoice/edit/123", xml={"customer": "New Customer"})

    assert response.status_code == 500
    assert response.xml() == {"detail": "Invoice file not found"}
