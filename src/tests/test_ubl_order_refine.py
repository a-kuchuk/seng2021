import json
import sys
import os

# src directory in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_refine_order_success():
    json_data = {
        "orderId": "123",
        "date": "2011-09-22",
        "period": {"start": "2011-08-01", "end": "2011-08-31"},
        "supplier": "Custom Cotter Pins",
        "customer": "North American Veeblefetzer",
        "total": {"amt": "100.00", "cur": "CAD"},
        "lines": [
            {"id": "1", "amt": "100.00", "cur": "CAD", "desc": "Cotter pin, MIL-SPEC"}
        ]
    }

    # filename from main.py
    json_file = "order_data.json"

    with open(json_file, "w") as file:
        json.dump(json_data, file)

    response = client.post("/ubl/order/refine/123")

    print("Response JSON:", response.json())


    assert response.status_code == 200
    assert response.json()["orderId"] == "123"
    assert response.json()["message"] == "Order refined successfully"

    os.remove(json_file)

def test_refine_order_empty_json():
    json_file = "order_data.json"

    with open(json_file, "w") as file:
        file.write("{}")

    response = client.post("/ubl/order/refine/123")

    assert response.status_code == 400
    assert response.json() == {"detail": "Missing or invalid Order Id"}

    os.remove(json_file)

def test_refine_order_file_not_found():
    json_file = "order_data.json"

    if os.path.exists(json_file):
        os.remove(json_file)

    response = client.post("/ubl/order/refine/123")

    assert response.status_code == 400
    assert response.json() == {"detail": "File doesn't exist"}
