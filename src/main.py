"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

import xml.etree.ElementTree as ET
import xml.dom.minidom
import mimetypes
import json
from fastapi import FastAPI, File, HTTPException, UploadFile, Body

app = FastAPI()


@app.get("/")
def index():
    """_summary_

    default hello world route

    Returns:
        _type_: _description_
    """
    return {"details": "Hello, World!"}


@app.post("/ubl/order/upload")
# use None here to allow empty file, which we then respond with detailed error msg below
async def upload_order_document(file: UploadFile = File(None)):
    """Route to upload an order document and extract order ID"""
    # Check if file is provided
    if file is None:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check if file is XML (not sure if it should be text or app yet)
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type not in ["application/xml", "text/xml"]:
        raise HTTPException(status_code=400, detail="File must be an XML file")

    try:
        contents = await file.read()
        # optional extra check for empty file to return error message on it -
        # currently empty file gives invalid XML format error:
        # if not contents:
        #    raise HTTPException(status_code=400, detail="Empty file")
        tree = ET.ElementTree(ET.fromstring(contents))
        root = tree.getroot()

        # Extract order ID - ensuring it's directly inside <Order>
        cbc_ns = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        order_id = root.find(f"{{{cbc_ns}}}ID")

        # Check order id exists in file and is not empty
        if order_id is not None and order_id.text and order_id.text.strip():
            return {"order_id": order_id.text}
        # this line is not being reached,
        # but taking out the if else block allows the empty id to be valid so I've kept it
        raise HTTPException(status_code=400, detail="Order ID not found")

    except ET.ParseError as exc:
        raise HTTPException(status_code=400, detail="Invalid XML format") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid XML format") from exc

@app.post("/ubl/invoice/create/{JSON_Id}")
async def create_invoice(invoice_json: str = Body(...)):
    """Route for converting a JSON file containing data into an XML Invoice file"""
    if not invoice_json.strip():  # Check if the input string is empty
        raise HTTPException(status_code=400, detail="JSON string is empty")
    try:
        data = json.loads(invoice_json)  # Parse the JSON string into a dictionary
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="Invalid JSON format") from ex

    if not data:  # Ensure the parsed JSON is not an empty dictionary
        raise HTTPException(status_code=400, detail="Parsed JSON is empty")

    print("made it past the checks?")
    # Create the root element (UBL Invoice)
    invoice = ET.Element("Invoice", xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2")

    # Add invoice ID and Issue Date
    ET.SubElement(invoice, "ID").text = f"{data['InvoiceID']}"
    ET.SubElement(invoice, "IssueDate").text = f"{data['date']}"

    # Add Invoice period (start and end date)
    invoice_period = ET.SubElement(invoice, "InvoicePeriod")
    ET.SubElement(invoice_period, "StartDate").text = f"{data['period']['start']}"
    ET.SubElement(invoice_period, "EndDate").text = f"{data['period']['end']}"

    # Supplier details
    supplier = ET.SubElement(invoice, "AccountingSupplierParty")
    supplier_party = ET.SubElement(supplier, "Party")
    ET.SubElement(supplier_party, "Name").text = f"{data['supplier']}"

    # Customer details
    customer = ET.SubElement(invoice, "AccountingCustomerParty")
    customer_party = ET.SubElement(customer, "Party")
    ET.SubElement(customer_party, "Name").text = f"{data['customer']}"

    # Legal Monetary Total
    total_money = ET.SubElement(invoice, "LegalMonetaryTotal")
    ET.SubElement(
        total_money, "PayableAmount", currencyID=f"{data['total']['cur']}"
    ).text = f"{data['total']['amt']}"

    for line in data['lines']:
        # Invoice Line Item
        invoice_line = ET.SubElement(invoice, "InvoiceLine")
        ET.SubElement(invoice_line, "ID").text = f"{line['id']}"

        ET.SubElement(
            invoice_line, "LineExtensionAmount", currencyID=f"{line['cur']}"
        ).text = f"{line['amt']}"
        ET.SubElement(ET.SubElement(invoice_line, "Item"), "Description").text = f"{line['desc']}"

    # Convert to XML string and save to file
    xml_str = ET.tostring(invoice, encoding="utf-8")

    # Format the XML file so it's not a single line
    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="\t")

    try:
        with open("invoice.xml", "w", encoding="utf-8") as file:
            file.write(pretty_xml)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to create XML file {ex}") from ex

    return {"details": "XML file successful"}
