# """Module to test the upload of an order document."""

# import io
# from fastapi.testclient import TestClient

# from src import main
# from src.tests.tests_main import get_xml

# app = main.app

# client = TestClient(app)


# def test_upload_order_doc_valid():
#     """Test the upload of a valid order document."""
#     ubl_xml_content = get_xml("order_provided_valid.xml")
#     files = {"file": ("valid_order_doc.xml", ubl_xml_content, "text/xml")}
#     response = client.post("/ubl/order/upload", files=files)
#     assert response.status_code == 200
#     assert response.json()["order_id"] == "AEG012345"


# def test_upload_order_doc_no_file():
#     """Test the upload of an order document function without a file."""
#     response = client.post("/ubl/order/upload")
#     assert response.status_code == 400
#     assert response.json()["detail"] == "No file provided"


# def test_upload_order_doc_empty_file():
#     """Test the upload of an empty order document."""
#     files = {"file": ("empty_order_doc.xml", "", "text/xml")}
#     response = client.post("/ubl/order/upload", files=files)
#     assert response.status_code == 400


# def test_upload_order_doc_empty_id():
#     """Test the upload of an order document with an empty ID section."""
#     ubl_xml_content = get_xml("order_provided_empty_id.xml")
#     files = {"file": ("no_id_order_doc.xml", ubl_xml_content, "text/xml")}
#     response = client.post("/ubl/order/upload", files=files)
#     assert response.status_code == 400


# def test_upload_order_doc_no_id():
#     """test the upload of an order document with no ID section."""
#     ubl_xml_content = get_xml("order_provided_no_id.xml")
#     files = {"file": ("empty_id_order_doc.xml", ubl_xml_content, "text/xml")}
#     response = client.post("/ubl/order/upload", files=files)
#     assert response.status_code == 400


# def test_upload_order_doc_invalid_xml():
#     """Test the upload of an order document with invalid XML."""
#     ubl_xml_content = get_xml("order_provided_invalid.xml")
#     files = {"file": ("invalid_xml_order_doc.xml", ubl_xml_content, "text/xml")}
#     response = client.post("/ubl/order/upload", files=files)
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Invalid XML format"


# def test_upload_order_doc_non_xml():
#     """Test the upload of a non-XML file."""
#     non_xml_file = io.BytesIO(b"Plain text file")
#     files = {"file": ("non_xml_order_doc.txt", non_xml_file, "text/plain")}
#     response = client.post("/ubl/order/upload", files=files)
#     assert response.status_code == 400
#     assert response.json()["detail"] == "File must be an XML file"
"""
Unit tests for FastAPI UBL Order parsing endpoints.
"""

import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def get_xml(file_name):
    """Function to read the content of an XML file."""
    valid_xml_file_path = Path(__file__).parent / "resources" / file_name
    with valid_xml_file_path.open("r", encoding="utf-8") as xml_file:
        return xml_file.read()

def test_validate_order():
    """Test if a valid UBL order XML is parsed correctly."""
    xml_content = get_xml("order_provided_valid.xml")

    files = {"file": ("test.xml", xml_content, "text/xml")}
    response = client.post("/ubl/order/parse", files=files)

    parsed_order = json.loads(response.json())
    assert parsed_order["Order"]["cbc:ID"] == "AEG012345"

def test_parse_invalid_xml():
    """Test if an invalid XML file returns HTTP 400."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <Order xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
            <cbc:ID>AEG012345</cbc:ID>
            <cbc:IssueDate>2005-06-20</cbc:IssueDate>
    """ # Invalid XML (missing closing tag)

    files = {"file": ("test.xml", xml_content, "text/xml")}
    response = client.post("/ubl/order/parse", files=files)

    assert response.status_code == 400  # Expecting HTTP 400 due to invalid XML
    assert "Invalid XML file" in response.json()["detail"]  # Ensure correct error message

def test_parse_empty_xml():
    """Test if an empty XML file returns HTTP 400."""
    xml_content = ""

    files = {"file": ("test.xml", xml_content, "text/xml")}
    response = client.post("/ubl/order/parse", files=files)

    assert response.status_code == 400  # Expecting HTTP 400 due to invalid XML
    assert "Invalid XML file" in response.json()["detail"]  # Ensure correct error message

def test_valid_invoice():
    """Test valid order document to invoice JSON."""
    xml_content = get_xml("order_provided_valid.xml")
# Pass in the order document in XML format to the /ubl/order/parse endpoint
# and then pass into the /ubl/order/validate endpoint

    files = {"file": ("test.xml", xml_content, "text/xml")}
    response = client.post("/ubl/order/parse", files=files)

    parsed_order = response.json()
    response2 = client.post("/ubl/order/validate", json=parsed_order)
    parsed_invoice = response2.json()
    assert isinstance(parsed_invoice["InvoiceID"], int)

def test_empty_field():
    """Test if API returns error when necessary field is empty."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Order xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2">
	<cbc:UBLVersionID>2.0</cbc:UBLVersionID>
	<cbc:CustomizationID>urn:oasis:names:specification:ubl:xpath:Order-2.0:sbs-1.0-draft</cbc:CustomizationID>
	<cbc:ProfileID>bpid:urn:oasis:names:draft:bpss:ubl-2-sbs-order-with-simple-response-draft</cbc:ProfileID>
	<cbc:ID>AEG012345</cbc:ID>
	<cbc:SalesOrderID>CON0095678</cbc:SalesOrderID>
	<cbc:CopyIndicator>false</cbc:CopyIndicator>
	<cbc:UUID>6E09886B-DC6E-439F-82D1-7CCAC7F4E3B1</cbc:UUID>
	<cbc:IssueDate></cbc:IssueDate>
	<cbc:Note>sample</cbc:Note>
	<cac:BuyerCustomerParty>
		<cbc:CustomerAssignedAccountID>XFB01</cbc:CustomerAssignedAccountID>
		<cbc:SupplierAssignedAccountID>GT00978567</cbc:SupplierAssignedAccountID>
		<cac:Party>
			<cac:PartyName>
				<cbc:Name>IYT Corporation</cbc:Name>
			</cac:PartyName>
			<cac:PostalAddress>
				<cbc:StreetName>Avon Way</cbc:StreetName>
				<cbc:BuildingName>Thereabouts</cbc:BuildingName>
				<cbc:BuildingNumber>56A</cbc:BuildingNumber>
				<cbc:CityName>Bridgtow</cbc:CityName>
				<cbc:PostalZone>ZZ99 1ZZ</cbc:PostalZone>
				<cbc:CountrySubentity>Avon</cbc:CountrySubentity>
				<cac:AddressLine>
					<cbc:Line>3rd Floor, Room 5</cbc:Line>
				</cac:AddressLine>
				<cac:Country>
					<cbc:IdentificationCode>GB</cbc:IdentificationCode>
				</cac:Country>
			</cac:PostalAddress>
			<cac:PartyTaxScheme>
				<cbc:RegistrationName>Bridgtow District Council</cbc:RegistrationName>
				<cbc:CompanyID>12356478</cbc:CompanyID>
				<cbc:ExemptionReason>Local Authority</cbc:ExemptionReason>
				<cac:TaxScheme>
					<cbc:ID>UK VAT</cbc:ID>
					<cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
				</cac:TaxScheme>
			</cac:PartyTaxScheme>
			<cac:Contact>
				<cbc:Name>Mr Fred Churchill</cbc:Name>
				<cbc:Telephone>0127 2653214</cbc:Telephone>
				<cbc:Telefax>0127 2653215</cbc:Telefax>
				<cbc:ElectronicMail>fred@iytcorporation.gov.uk</cbc:ElectronicMail>
			</cac:Contact>
		</cac:Party>
	</cac:BuyerCustomerParty>
	<cac:SellerSupplierParty>
		<cbc:CustomerAssignedAccountID>CO001</cbc:CustomerAssignedAccountID>
		<cac:Party>
			<cac:PartyName>
				<cbc:Name>Consortial</cbc:Name>
			</cac:PartyName>
			<cac:PostalAddress>
				<cbc:StreetName>Busy Street</cbc:StreetName>
				<cbc:BuildingName>Thereabouts</cbc:BuildingName>
				<cbc:BuildingNumber>56A</cbc:BuildingNumber>
				<cbc:CityName>Farthing</cbc:CityName>
				<cbc:PostalZone>AA99 1BB</cbc:PostalZone>
				<cbc:CountrySubentity>Heremouthshire</cbc:CountrySubentity>
				<cac:AddressLine>
					<cbc:Line>The Roundabout</cbc:Line>
				</cac:AddressLine>
				<cac:Country>
					<cbc:IdentificationCode>GB</cbc:IdentificationCode>
				</cac:Country>
			</cac:PostalAddress>
			<cac:PartyTaxScheme>
				<cbc:RegistrationName>Farthing Purchasing Consortium</cbc:RegistrationName>
				<cbc:CompanyID>175 269 2355</cbc:CompanyID>
				<cbc:ExemptionReason>N/A</cbc:ExemptionReason>
				<cac:TaxScheme>
					<cbc:ID>VAT</cbc:ID>
					<cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
				</cac:TaxScheme>
			</cac:PartyTaxScheme>
			<cac:Contact>
				<cbc:Name>Mrs Bouquet</cbc:Name>
				<cbc:Telephone>0158 1233714</cbc:Telephone>
				<cbc:Telefax>0158 1233856</cbc:Telefax>
				<cbc:ElectronicMail>bouquet@fpconsortial.co.uk</cbc:ElectronicMail>
			</cac:Contact>
		</cac:Party>
	</cac:SellerSupplierParty>
	<cac:OriginatorCustomerParty>
		<cac:Party>
			<cac:PartyName>
				<cbc:Name>The Terminus</cbc:Name>
			</cac:PartyName>
			<cac:PostalAddress>
				<cbc:StreetName>Avon Way</cbc:StreetName>
				<cbc:BuildingName>Thereabouts</cbc:BuildingName>
				<cbc:BuildingNumber>56A</cbc:BuildingNumber>
				<cbc:CityName>Bridgtow</cbc:CityName>
				<cbc:PostalZone>ZZ99 1ZZ</cbc:PostalZone>
				<cbc:CountrySubentity>Avon</cbc:CountrySubentity>
				<cac:AddressLine>
					<cbc:Line>3rd Floor, Room 5</cbc:Line>
				</cac:AddressLine>
				<cac:Country>
					<cbc:IdentificationCode>GB</cbc:IdentificationCode>
				</cac:Country>
			</cac:PostalAddress>
			<cac:PartyTaxScheme>
				<cbc:RegistrationName>Bridgtow District Council</cbc:RegistrationName>
				<cbc:CompanyID>12356478</cbc:CompanyID>
				<cbc:ExemptionReason>Local Authority</cbc:ExemptionReason>
				<cac:TaxScheme>
					<cbc:ID>UK VAT</cbc:ID>
					<cbc:TaxTypeCode>VAT</cbc:TaxTypeCode>
				</cac:TaxScheme>
			</cac:PartyTaxScheme>
			<cac:Contact>
				<cbc:Name>S Massiah</cbc:Name>
				<cbc:Telephone>0127 98876545</cbc:Telephone>
				<cbc:Telefax>0127 98876546</cbc:Telefax>
				<cbc:ElectronicMail>smassiah@the-email.co.uk</cbc:ElectronicMail>
			</cac:Contact>
		</cac:Party>
	</cac:OriginatorCustomerParty>
	<cac:Delivery>
		<cac:DeliveryAddress>
			<cbc:StreetName>Avon Way</cbc:StreetName>
			<cbc:BuildingName>Thereabouts</cbc:BuildingName>
			<cbc:BuildingNumber>56A</cbc:BuildingNumber>
			<cbc:CityName>Bridgtow</cbc:CityName>
			<cbc:PostalZone>ZZ99 1ZZ</cbc:PostalZone>
			<cbc:CountrySubentity>Avon</cbc:CountrySubentity>
			<cac:AddressLine>
				<cbc:Line>3rd Floor, Room 5</cbc:Line>
			</cac:AddressLine>
			<cac:Country>
				<cbc:IdentificationCode>GB</cbc:IdentificationCode>
			</cac:Country>
		</cac:DeliveryAddress>
		<cac:RequestedDeliveryPeriod>
			<cbc:StartDate>2005-06-29</cbc:StartDate>
			<cbc:StartTime>09:30:47.0Z</cbc:StartTime>
			<cbc:EndDate>2005-06-29</cbc:EndDate>
			<cbc:EndTime>09:30:47.0Z</cbc:EndTime>
		</cac:RequestedDeliveryPeriod>
	</cac:Delivery>
	<cac:DeliveryTerms>
		<cbc:SpecialTerms>1% deduction for late delivery as per contract</cbc:SpecialTerms>
	</cac:DeliveryTerms>
	<cac:TransactionConditions>
		<cbc:Description>order response required; payment is by BACS or by cheque</cbc:Description>
	</cac:TransactionConditions>
	<cac:AnticipatedMonetaryTotal>
		<cbc:LineExtensionAmount currencyID="GBP">100.00</cbc:LineExtensionAmount>
		<cbc:PayableAmount currencyID="GBP">100.00</cbc:PayableAmount>
	</cac:AnticipatedMonetaryTotal>
	<cac:OrderLine>
		<cbc:Note>this is an illustrative order line</cbc:Note>
		<cac:LineItem>
			<cbc:ID>1</cbc:ID>
			<cbc:SalesOrderID>A</cbc:SalesOrderID>
			<cbc:LineStatusCode>NoStatus</cbc:LineStatusCode>
			<cbc:Quantity unitCode="KGM">100</cbc:Quantity>
			<cbc:LineExtensionAmount currencyID="GBP">100.00</cbc:LineExtensionAmount>
			<cbc:TotalTaxAmount currencyID="GBP">17.50</cbc:TotalTaxAmount>
			<cac:Price>
				<cbc:PriceAmount currencyID="GBP">100.00</cbc:PriceAmount>
				<cbc:BaseQuantity unitCode="KGM">1</cbc:BaseQuantity>
			</cac:Price>
			<cac:Item>
				<cbc:Description>Acme beeswax</cbc:Description>
				<cbc:Name>beeswax</cbc:Name>
				<cac:BuyersItemIdentification>
					<cbc:ID>6578489</cbc:ID>
				</cac:BuyersItemIdentification>
				<cac:SellersItemIdentification>
					<cbc:ID>17589683</cbc:ID>
				</cac:SellersItemIdentification>
			</cac:Item>
		</cac:LineItem>
	</cac:OrderLine>
</Order>"""
# Pass in the order document in XML format to the /ubl/order/parse endpoint
# and then pass into the /ubl/order/validate endpoint

    files = {"file": ("test.xml", xml_content, "text/xml")}
    response = client.post("/ubl/order/parse", files=files)

    parsed_order = response.json()
    response2 = client.post("/ubl/order/validate", json=parsed_order)
    parsed_invoice = response2.json()
    assert "Missing field: Issue Date" in parsed_invoice["errors"], (
		"Expected 'Missing field: Issue Date' error"
		)

def test_invoice_creation():
    """Test if API returns valid invoice when all data is present"""
    xml_content = get_xml("order_provided_valid.xml")
# Pass in the order document in XML format to the /ubl/order/parse endpoint
# and then pass into the /ubl/order/validate endpoint
    files = {"file": ("test.xml", xml_content, "text/xml")}
    response = client.post("/ubl/order/parse", files=files)

    parsed_order = response.json()
    response2 = client.post("/ubl/order/validate", json=parsed_order)
    parsed_invoice = response2.json()
    parsed_invoice=json.dumps(parsed_invoice)
    response3 = client.post("/ubl/invoice/create", json=parsed_invoice)
    assert response3.status_code == 200
    os.remove("invoice.xml")

def test_create_invoice_empty_json():
    """Tests the creation of an Invoice from an empty JSON string"""

    json_string = ""  # Empty JSON object

    response = client.post(
        "/ubl/invoice/create",
        json=json_string  # Send empty JSON string as request body
    )

    assert response.status_code == 400
    assert "JSON string is empty" in response.json()["detail"]
    print("Invoice empty success!")

def test_create_invoice_invalid_json():
    """Tests the creation of an Invoice from an invalid JSON string"""

    json_string = "{invalid json}"  # invalid JSON

    response = client.post(
        "/ubl/invoice/create",
        json=json_string  # Send empty JSON string as request body
    )

    assert response.status_code == 400
    assert "Invalid JSON format" in response.json()["detail"]
    print("Invoice invalid success!")

def test_create_invoice_empty_json_object():
    """Tests the creation of an Invoice from an empty JSON object"""

    json_string = "{}"  # Empty JSON object

    response = client.post(
        "/ubl/invoice/create",
        json=json_string  # Send empty JSON string as request body
    )

    assert response.status_code == 400
    assert "Parsed JSON is empty" in response.json()["detail"]
    print("Parsed JSON empty success!")
