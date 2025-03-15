"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

import xml.etree.ElementTree as ET
import mimetypes
from fastapi import FastAPI, File, HTTPException, UploadFile
import xml.dom.minidom 
import json

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

@app.post("/ubl/invoice/create/{JSONId}")
async def createInvoice():
    """Route for converting a JSON file containing data into an XML Invoice file"""
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
            
        if not data:
            raise HTTPException(status_code=400, detail="File is Empty")
            
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="File doesn't exist")
        
    # Create the root element (UBL Invoice)
    invoice = ET.Element("Invoice", xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2")
    # Add invoice ID
    invoice_id = ET.SubElement(invoice, "ID")
    invoice_id.text = f"{data['JSONId']}"
    # Add issue date
    issue_date = ET.SubElement(invoice, "IssueDate")
    issue_date.text = f"{data['date']}"
    
    # Add Invoice period (start and end date)
    invoice_period = ET.SubElement(invoice, "InvoicePeriod")
    start_date = ET.SubElement(invoice_period, "StartDate")
    start_date.text = f"{data['period']['start']}"
    end_date = ET.SubElement(invoice_period, "EndDate")
    end_date.text = f"{data['period']['end']}"
    
    # Supplier details
    supplier = ET.SubElement(invoice, "AccountingSupplierParty")
    supplier_party = ET.SubElement(supplier, "Party")
    supplier_name = ET.SubElement(supplier_party, "Name")
    supplier_name.text = f"{data['supplier']}"
    
    # Customer details
    customer = ET.SubElement(invoice, "AccountingCustomerParty")
    customer_party = ET.SubElement(customer, "Party")
    customer_name = ET.SubElement(customer_party, "Name")
    customer_name.text = f"{data['customer']}"
    
    # Legal Monetary Total
    total_money = ET.SubElement(invoice, "LegalMonetaryTotal")
    payable = ET. SubElement(total_money, "PayableAmount", currencyID=f"{data['total']['cur']}")
    payable.text = f"{data['total']['amt']}"
    for line in data['lines']:
        # Invoice Line Item
        invoice_line = ET.SubElement(invoice, "InvoiceLine")
        line_id = ET.SubElement(invoice_line, "ID")
        line_id.text = f"{line['id']}"
        
        price_amount = ET.SubElement(invoice_line, "LineExtensionAmount", currencyID=f"{line['cur']}")
        price_amount.text = f"{line['amt']}"
        item = ET.SubElement(invoice_line, "Item")
        item_name = ET.SubElement(item, "Description")
        item_name.text = f"{line['desc']}"
        
    # Convert to XML string and save to file
    tree = ET.ElementTree(invoice)
    xml_str = ET.tostring(invoice, encoding="utf-8")
    
    # Format the XML file so it's not a single line
    parsed_xml = xml.dom.minidom.parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")
    
    try:
        with open("invoice.xml", "w", encoding="utf-8") as file:
            file.write(pretty_xml)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create XML file {e}")
         
    return {"details": "XML file successful"}
