"""This Module is for testing the creation of an XML Invoice file"""

import json
import os
from fastapi.testclient import TestClient
from src import main

app = main.app
 
client = TestClient(app)
def test_create_invoice_success():
    """Tests if an invoice can be created successfully from a JSON file"""
    json_data = {
        "JSONId": "123",
        "date": "2011-09-22",
        "period": {"start": "2011-08-01", "end": "2011-08-31"},
        "supplier": "Custom Cotter Pins",
        "customer": "North American Veeblefetzer",
        "total": {"amt": "150.00", "cur": "CAD"},
        "lines": [
            {"id": "1", "amt": "100.00", "cur": "CAD", "desc": "Cotter pin, MIL-SPEC"},
            {"id": "2", "amt": "50.00", "cur": "CAD", "desc": "Cotter thread, MIL-SPEC"}
        ]
    }
    
    with open("data.json", "w") as file:
        json.dump(json_data, file)
    
    response = client.post("/ubl/invoice/create/123")
    
    assert response.status_code == 200
    assert response.json() == {"details": "XML file successful?"}
    assert os.path.exists("invoice.xml")
    
    os.remove("data.json")
    os.remove("invoice.xml")
    print("invoice creation success!")
    
def test_create_invoice_empty_json():
    """Tests the creation of Invoice from Empty JSON file"""
    with open("data.json", "w") as file:
        file.write("{}")
    
    response = client.post("/ubl/invoice/create/123")
    assert response.status_code == 400 
    assert "File is Empty" in response.json()["detail"] 
    
    os.remove("data.json")
    print("invoice empty success!")
    
def test_create_invoice_file_not_found():
    """Tests the creation of Invoice file from non-existing JSON file"""
    if os.path.exists("data.json"):
        os.remove("data.json")
    
    response = client.post("/ubl/invoice/create/123")
    
    assert response.status_code == 400 
    assert "File doesn't exist" in response.json()["detail"]
    print("success not found!")
if __name__ == "__main__":
    test_create_invoice_success()
    test_create_invoice_empty_json()
    test_create_invoice_file_not_found()
