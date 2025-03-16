"""This Module is for testing the creation of an XML Invoice file"""

import json
import os
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)
def test_create_invoice_success():
    """Tests if an invoice can be created successfully from a JSON file"""
    json_data = {
        "InvoiceID": "123",
        "IssueDate": "2011-09-22",
        "InvoicePeriod": {"StartDate": "2011-08-01", "EndDate": "2011-08-31"},
        "AccountingSupplierParty": "Custom Cotter Pins",
        "AccountingCustomerParty": "North American Veeblefetzer",
        "LegalMonetaryTotal": {"Value": "150.00", "Currency": "CAD"},
        "InvoiceLine": [
            {"ID": "1", "Value": "100.00", "Currency": "CAD", "Description": "Cotter pin, MIL-SPEC"},
            {"ID": "2", "Value": "50.00", "Currency": "CAD", "Description": "Cotter thread, MIL-SPEC"}
        ]
    }

    json_string = json.dumps(json_data)  # Convert dictionary to JSON string

    response = client.post(
        "/ubl/invoice/create/123",
        json=json_string
    )
    
    print(response)

    assert response.status_code == 200
    assert response.json() == {"InvoiceID": "123"}
    assert os.path.exists("invoice.xml")

    os.remove("invoice.xml")

def test_create_invoice_empty_json():
    """Tests the creation of an Invoice from an empty JSON string"""

    json_string = ""  # Empty JSON object

    response = client.post(
        "/ubl/invoice/create/123",
        json=json_string  # Send empty JSON string as request body
    )

    assert response.status_code == 400
    assert "JSON string is empty" in response.json()["detail"]
    print("Invoice empty success!")

def test_create_invoice_invalid_json():
    """Tests the creation of an Invoice from an invalid JSON string"""

    json_string = "{invalid json}"  # invalid JSON

    response = client.post(
        "/ubl/invoice/create/123",
        json=json_string  # Send empty JSON string as request body
    )

    assert response.status_code == 400
    assert "Invalid JSON format" in response.json()["detail"]
    print("Invoice invalid success!")

def test_create_invoice_empty_json_object():
    """Tests the creation of an Invoice from an empty JSON object"""

    json_string = "{}"  # Empty JSON object

    response = client.post(
        "/ubl/invoice/create/123",
        json=json_string  # Send empty JSON string as request body
    )

    assert response.status_code == 400
    assert "Parsed JSON is empty" in response.json()["detail"]
    print("Parsed JSON empty success!")

if __name__ == "__main__":
    test_create_invoice_success()
    test_create_invoice_empty_json()
    test_create_invoice_invalid_json()
    test_create_invoice_empty_json_object()
