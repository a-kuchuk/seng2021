import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://t6r6w5zni9.execute-api.us-east-1.amazonaws.com/v1/despatchAdvice"

def get_valid_despatch_id():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("despatchId")
    return None

VALID_DESPATCH_ID = get_valid_despatch_id()
if VALID_DESPATCH_ID is None:
    print("Error: No valid despatch ID found. Tests cannot proceed.")

def test_delete_despatch_advice():
    if VALID_DESPATCH_ID is None:
        print("Skipping test: No valid despatch ID found.")
        return
    
    response = requests.delete(f"{BASE_URL}/{VALID_DESPATCH_ID}")
    assert response.status_code == 200, f"Unexpected status: {response.status_code}, Response: {response.json()}"
    assert response.json().get("statusCode") == 200

def test_get_items_of_advice():
    if VALID_DESPATCH_ID is None:
        print("Skipping test: No valid despatch ID found.")
        return
    
    response = requests.get(f"{BASE_URL}/{VALID_DESPATCH_ID}/items")
    assert response.status_code == 200, f"Unexpected status: {response.status_code}, Response: {response.json()}"
    data = response.json()
    assert "Items" in data, f"Expected 'Items' in response, got: {data}"
    items_xml = data.get("Items")
    try:
        root = ET.fromstring(items_xml)
        assert root.tag == "Item"
        assert root.find("cbc:Description", namespaces={"cbc": "cbc"}) is not None
    except ET.ParseError as e:
        assert False, f"XML Parsing Error: {e}, Response: {items_xml}"

def test_get_order_reference():
    if VALID_DESPATCH_ID is None:
        print("Skipping test: No valid despatch ID found.")
        return

    response = requests.get(f"{BASE_URL}/{VALID_DESPATCH_ID}/orderReference")
    assert response.status_code == 200, f"Unexpected status: {response.status_code}, Response: {response.json()}"
    data = response.json()
    assert "Items" in data, f"Expected 'Items' in response, got: {data}"
    order_xml = data.get("Items")
    try:
        root = ET.fromstring(order_xml)
        assert root.tag == "OrderReference"
        assert root.find("cbc:ID", namespaces={"cbc": "cbc"}) is not None
    except ET.ParseError as e:
        assert False, f"XML Parsing Error: {e}, Response: {order_xml}"

def test_get_shipment_details():
    if VALID_DESPATCH_ID is None:
        print("Skipping test: No valid despatch ID found.")
        return

    response = requests.get(f"{BASE_URL}/{VALID_DESPATCH_ID}/shipment")
    assert response.status_code == 200, f"Unexpected status: {response.status_code}, Response: {response.json()}"
    data = response.json()
    assert "Items" in data, f"Expected 'Items' in response, got: {data}"
    shipment_xml = data.get("Items")
    try:
        root = ET.fromstring(shipment_xml)
        assert root.tag == "ShipmentDetails"
    except ET.ParseError as e:
        assert False, f"XML Parsing Error: {e}, Response: {shipment_xml}"

def test_get_shipment_arrival_period():
    if VALID_DESPATCH_ID is None:
        print("Skipping test: No valid despatch ID found.")
        return

    response = requests.get(f"{BASE_URL}/{VALID_DESPATCH_ID}/shipment-arrival")
    assert response.status_code == 200, f"Unexpected status: {response.status_code}, Response: {response.json()}"
    data = response.json()
    assert "requestedDelivery" in data, f"Expected 'requestedDelivery' in response, got: {data}"
    delivery_xml = data.get("requestedDelivery")
    try:
        root = ET.fromstring(delivery_xml)
        assert root.tag == "RequestedDeliveryPeriod"
    except ET.ParseError as e:
        assert False, f"XML Parsing Error: {e}, Response: {delivery_xml}"
