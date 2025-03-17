"""Module to test the upload of an order document."""

import os
import io
from fastapi.testclient import TestClient

from src.main import app

from src.tests.tests_main import get_xml


client = TestClient(app)


def test_upload_order_doc_valid():
    """Test the upload of a valid order document."""
    ubl_xml_content = get_xml("order_provided_valid.xml")
    files = {"file": ("valid_order_doc.xml", ubl_xml_content, "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 200
    assert response.json()["order_id"] == "AEG012345"


def test_upload_order_doc_no_file():
    """Test the upload of an order document function without a file."""
    response = client.post("/ubl/order/upload")
    assert response.status_code == 400
    assert response.json()["detail"] == "No file provided"


def test_upload_order_doc_empty_file():
    """Test the upload of an empty order document."""
    files = {"file": ("empty_order_doc.xml", "", "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400


def test_upload_order_doc_empty_id():
    """Test the upload of an order document with an empty ID section."""
    ubl_xml_content = get_xml("order_provided_empty_id.xml")
    files = {"file": ("no_id_order_doc.xml", ubl_xml_content, "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400


def test_upload_order_doc_no_id():
    """test the upload of an order document with no ID section."""
    ubl_xml_content = get_xml("order_provided_no_id.xml")
    files = {"file": ("empty_id_order_doc.xml", ubl_xml_content, "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400


def test_upload_order_doc_invalid_xml():
    """Test the upload of an order document with invalid XML."""
    ubl_xml_content = get_xml("order_provided_invalid.xml")
    files = {"file": ("invalid_xml_order_doc.xml", ubl_xml_content, "text/xml")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid XML format"


def test_upload_order_doc_non_xml():
    """Test the upload of a non-XML file."""
    non_xml_file = io.BytesIO(b"Plain text file")
    files = {"file": ("non_xml_order_doc.txt", non_xml_file, "text/plain")}
    response = client.post("/ubl/order/upload", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "File must be an XML file"

def test_xml_to_pdf():
    """Tests the creation of a PDF file"""
    xml = get_xml("invoice_provided_valid.xml")
    files = {"file": ("test.xml", xml, "text/xml")}
    response = client.post("/ubl/invoice/pdf", files=files)

    assert response.status_code == 200
    os.remove("invoice.pdf")
