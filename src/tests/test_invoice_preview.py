"""
Unit tests for FastAPI UBL Order parsing endpoints.
"""

import os
from fastapi.testclient import TestClient
from src.main import app

from src.tests.tests_main import get_xml

client = TestClient(app)


def test_email():
    """_summary_

    Tests valid email send
    """
    ubl_xml_content = get_xml("invoice_provided_valid.xml")
    files = {"attachment": ("valid_order_doc.xml", ubl_xml_content, "text/xml")}
    data = {"to_email": "wubenny2@gmail.com"}

    response = client.post("/ubl/order/email/v2", data=data, files=files)
    assert response.status_code == 200
    assert response.json() == {"message": "Invoice sent successfully."}


def test_xml_to_pdf():
    """Tests the creation of a PDF file"""
    xml = get_xml("invoice_provided_valid.xml")
    files = {"file": ("test.xml", xml, "text/xml")}
    response = client.post("/ubl/invoice/pdf", files=files)

    assert response.status_code == 200
    os.remove("invoice.pdf")


def test_invoice_preview_valid():
    """Test preview generation of a valid UBL invoice document."""
    xml = get_xml("invoice_provided_valid.xml")
    files = {"file": ("test_invoice.xml", xml, "text/xml")}
    response = client.post("/ubl/invoice/preview", files=files)

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Invoice ID" in response.text
    assert "<html>" in response.text


def test_invoice_preview_missing_file():
    """Test invoice preview when no file is provided."""
    response = client.post("/ubl/invoice/preview")

    assert (
        response.status_code == 422
    )  # FastAPI will return 422 for missing required file


def test_invoice_preview_invalid_xml():
    """Test invoice preview with invalid XML content."""
    invalid_xml = "<Invoice><ID>Invalid</ID>"  # malformed XML, no closing tag
    files = {"file": ("invalid_invoice.xml", invalid_xml, "text/xml")}
    response = client.post("/ubl/invoice/preview", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid XML format"


def test_invoice_preview_missing_invoice_id():
    """Test preview generation when invoice has no ID (or required fields)."""
    xml = get_xml("invoice_provided_no_id.xml")
    files = {"file": ("no_id_invoice.xml", xml, "text/xml")}
    response = client.post("/ubl/invoice/preview", files=files)

    assert response.status_code == 400
    assert "Invoice ID: None" in response.text


def test_invoice_cancel():
    """Tests the successful cancelation of invoice creation"""
    response = client.post("/ubl/invoice/cancel")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Invoice creation has been canceled successfully."
    }
