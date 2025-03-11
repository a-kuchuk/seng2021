import json
import os
from fastapi.testclient import TestClient
from main import app  

client = TestClient(app)

def test_create_invoice_success():
    json_data = {
        "invoiceId": "123",
        "date": "2011-09-22",
        "period": {"start": "2011-08-01", "end": "2011-08-31"},
        "supplier": "Custom Cotter Pins",
        "customer": "North American Veeblefetzer",
        "total": {"amt": "100.00", "cur": "CAD"},
        "lines": [
            {"id": "1", "amt": "100.00", "cur": "CAD", "desc": "Cotter pin, MIL-SPEC"}
        ]
    }

    with open("data.json", "w") as file:
        json.dump(json_data, file)

    response = client.post("/ubl/invoice/create/123")

    assert response.status_code == 200
    assert response.json() == {"invoiceId": "123"}
    assert os.path.exists("invoice.xml")

    os.remove("data.json")
    os.remove("invoice.xml")

def test_create_invoice_empty_json():
    with open("data.json", "w") as file:
        file.write("{}")

    response = client.post("/ubl/invoice/create/123")

    assert response.status_code == 400
    assert response.json() == {"error": "Missing or invalid JSON Id"}

    os.remove("data.json")

def test_create_invoice_file_not_found():
    if os.path.exists("data.json"):
        os.remove("data.json")

    response = client.post("/ubl/invoice/create/123")

    assert response.status_code == 400
    assert response.json() == {"error": "File doesn't exist"}
