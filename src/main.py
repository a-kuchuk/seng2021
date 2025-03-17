"""API that takes an XML order document and provides a XML invoice
with the elements extracted from the order doc and mapped to the invoice.

Contains all routes

Returns:
    _type_: _description_
"""

import os
import json
import xml.etree.ElementTree as ET
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI()

INVOICE_FILE = "./src/tests/resources/invoice_provided_valid.xml"

@app.put("/ubl/invoice/edit/{invoiceId}")
def edit_invoice(invoice_id: str, updated_invoice: dict):
    """_summary_

    editing invoice route

    Returns:
        invoiceId: string
    """
    if not invoice_id:
        raise HTTPException(status_code=400, detail="Missing or invalid invoice Id")

    if not updated_invoice or not isinstance(updated_invoice, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid input data")

    if not os.path.exists(INVOICE_FILE):
        raise HTTPException(status_code=500, detail="Invoice file not found")

    try:
        with open(INVOICE_FILE, "r", encoding="utf-8") as file:
            invoices = json.load(file)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Invalid JSON format") from exc

    if invoice_id not in invoices:
        raise HTTPException(status_code=400, detail="Invoice not found")

    invoices[invoice_id].update(updated_invoice)

    with open(INVOICE_FILE, "w", encoding="utf-8") as file:
        json.dump(invoices, file, indent=4)

    return invoices[invoice_id]


@app.post("/ubl/order/upload")
async def upload_order_document(file: UploadFile = File(None)):
    """Upload an XML order document and extract the order ID

    Args:
        file (UploadFile, optional): the UBL XML order document. Defaults to File(None).

    Raises:
        HTTPException: No file provided
        HTTPException: File must be an XML file
        HTTPException: Order ID not found
        HTTPException: Invalid XML format

    Returns:
        text: the order ID extracted from the XML document
    """

    # Check if file is provided
    if file is None:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check if file is XML text
    filename = file.filename
    if not filename.lower().endswith(".xml"):
        raise HTTPException(status_code=400, detail="File must be an XML file")

    try:
        contents = await file.read()
        tree = ET.ElementTree(ET.fromstring(contents))
        root = tree.getroot()

        # Extract order ID - ensuring it's directly inside <Order>
        cbc_ns = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        order_id = root.find(f"{{{cbc_ns}}}ID")

        # Check order id exists in file and is not empty
        if order_id is not None and order_id.text and order_id.text.strip():
            return {"order_id": order_id.text}

        # Raise error if order id not found
        raise HTTPException(status_code=400, detail="Order ID not found")

    except ET.ParseError as exc:
        # Invalid XML format includes empty file, missing root element
        raise HTTPException(status_code=400, detail="Invalid XML format") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid XML format") from exc
