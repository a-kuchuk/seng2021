import json
import os
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

INVOICE_FILE = "invoice_data.json"

@pytest.fixture(scope="function", autouse=True)
def setup_invoice_file():
    # Setup: Create a sample invoice file
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

    with open(INVOICE_FILE, "w") as file:
        json.dump(sample_data, file)

    yield

    # Teardown: Remove the file after test execution
    if os.path.exists(INVOICE_FILE):
        os.remove(INVOICE_FILE)

def test_edit_invoice_success():
    updated_data = {"customer": "Updated Customer", "total": {"amt": "150.00", "cur": "USD"}}

    response = client.put("/ubl/invoice/edit/123", json=updated_data)

    assert response.status_code == 200
    assert response.json()["invoiceId"] == "123"
    assert response.json()["customer"] == "Updated Customer"
    assert response.json()["total"]["amt"] == "150.00"
    assert response.json()["total"]["cur"] == "USD"

def test_edit_invoice_not_found():
    response = client.put("/ubl/invoice/edit/999", json={"customer": "New Customer"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Invoice not found"}

def test_edit_invoice_missing_input():
    response = client.put("/ubl/invoice/edit/123", json={})

    assert response.status_code == 400
    assert response.json() == {"detail": "Missing or invalid input data"}

def test_edit_invoice_file_not_found():
    os.remove(INVOICE_FILE)

    response = client.put("/ubl/invoice/edit/123", json={"customer": "New Customer"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error: Invoice file not found"}
