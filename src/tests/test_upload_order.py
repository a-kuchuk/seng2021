import io
import os
from fastapi.testclient import TestClient
from pathlib import Path

from src import main
app = main.app

client = TestClient(app)

def get_order_doc_xml(file_name):
	valid_xml_file_path = Path(__file__).parent / "resources" / file_name
	with valid_xml_file_path.open("r", encoding="utf-8") as xml_file:
		return xml_file.read()
     
def test_upload_order_doc_valid():
    ubl_xml_content = get_order_doc_xml("order_provided_valid.xml")
    files = {"file": ("valid_order_doc.xml", ubl_xml_content, "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 200
    assert response.json()["order_id"] == "AEG012345"

def test_upload_order_doc_no_file():
    response = client.post("/ubl/order/upload")
    assert response.status_code == 400 
    assert response.json()["detail"] == "No file provided"

def test_upload_order_doc_empty_file():
    files = {"file": ("empty_order_doc.xml", "", "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400 
    #assert response.json()["detail"] == "Empty file"

def test_upload_order_doc_empty_id():
    ubl_xml_content = get_order_doc_xml("order_provided_empty_id.xml")
    files = {"file": ("no_id_order_doc.xml", ubl_xml_content, "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400
    #assert response.json()["detail"] == "Order ID not found"

def test_upload_order_doc_no_id():
    ubl_xml_content = get_order_doc_xml("order_provided_no_id.xml")
    files = {"file": ("empty_id_order_doc.xml", ubl_xml_content, "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400
    #assert response.json()["detail"] == "Order ID not found"

def test_upload_order_doc_invalid_xml():
    ubl_xml_content = get_order_doc_xml("order_provided_invalid.xml")
    files = {"file": ("invalid_xml_order_doc.xml", ubl_xml_content, "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400 
    assert response.json()["detail"] == "Invalid XML format"

def test_upload_order_doc_non_xml():
    non_xml_file = io.BytesIO(b"Plain text file")
    files = {"file": ("non_xml_order_doc.txt", non_xml_file, "text/plain")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400 
    assert response.json()["detail"] == "File must be an XML file"

