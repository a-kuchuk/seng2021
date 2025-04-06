"""invoicve generation api"""

import json
import random
import xml.etree.ElementTree as ET
import xml.dom.minidom
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Form
from fastapi.responses import JSONResponse
import xmltodict
from datetime import datetime
import pycountry
import smtplib
from email.message import EmailMessage
from currency_converter import CurrencyConverter


def valid_date(date_str):
    try:
        datetime.fromisoformat(date_str)
        return True
    except:
        return False


def valid_currency(code):
    try:
        return pycountry.currencies.get(alpha_3=code.upper()) is not None
    except:
        return False


DESCRIPTION = """
API that takes an XML order document and provides a XML invoice
with the elements extracted from the order doc and mapped to the invoice.

## Validation

You can validate oder data

## Generation

Generates invoice

"""


tags_metadata = [
    {
        "name": "DATA VALIDATION",
        "description": "Validates provided files",
    },
    {
        "name": "INVOICE GENERATION",
        "description": "Generates invoivce XML from provided data",
    },
    {
        "name": "INVOICE MANIPULATION",
        "description": "Modifies outputted input based on specifications",
    },
    {
        "name": "HEALTH",
        "description": "Verifies deployment",
    },
]

app = FastAPI(
    title="Invoice Creation API",
    version="0.0.1",
    description=DESCRIPTION,
    openapi_tags=tags_metadata,
)


@app.get("/", tags=["HEALTH"])
def hello_world():
    """_summary_

    default hello world route

    """
    return {"details": "Hello, World!"}


@app.post("/ubl/order/upload", tags=["DATA VALIDATION"])
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


@app.post("/ubl/order/parse", tags=["DATA VALIDATION"])
async def parse_ubl_order(file: UploadFile = File(...)):
    """_summary_

    Parses an uploaded UBL XML order document into JSON format.

    Args:
        file (UploadFile): XML file uploaded by the user.

    Raises:
        HTTPException: If no file is provided.
        HTTPException: If the XML file is invalid.

    Returns:
        dict: Parsed XML data in JSON format.
    """
    if file is None:
        raise HTTPException(status_code=400, detail="No file provided")
    try:
        xml_content = await file.read()

        data_dict = xmltodict.parse(xml_content, process_namespaces=False)

        json_data = json.dumps(data_dict, indent=4)

        # This uncommented code turns the JSON data into a file
        # with open("data.json", "w") as json_file:
        #     json_file.write(json_data)
        # return json.loads(json_data)

        return json_data
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid XML file") from e


@app.post("/ubl/order/validate", tags=["DATA VALIDATION"])
async def validate_order(order_json: str = Body(...)):
    """_summary_

    Validates a parsed UBL order document.

    Args:
        order_json (str): JSON string representation of the order document.

    Raises:
        HTTPException: If no JSON data is provided.
        HTTPException: If the JSON data is invalid.

    Returns:
        dict: Validated order details or errors if missing fields.
    """
    try:
        if order_json is None:
            raise HTTPException(status_code=400, detail="No JSON provided")

        order_data = json.loads(order_json)
        order_data = order_data.get("Order", {})
        errors = []
        refined_order = {
            "InvoiceID": random.randint(1, 1000),
            "IssueDate": order_data.get("cbc:IssueDate"),
            "InvoicePeriod": {
                "StartDate": order_data.get("cac:Delivery", {})
                .get("cac:RequestedDeliveryPeriod", {})
                .get("cbc:StartDate"),
                "EndDate": order_data.get("cac:Delivery", {})
                .get("cac:RequestedDeliveryPeriod", {})
                .get("cbc:EndDate"),
            },
            "AccountingSupplierParty": order_data.get("cac:SellerSupplierParty", {})
            .get("cac:Party", {})
            .get("cac:PartyName", {})
            .get("cbc:Name"),
            "AccountingCustomerParty": order_data.get("cac:BuyerCustomerParty", {})
            .get("cac:Party", {})
            .get("cac:PartyName", {})
            .get("cbc:Name"),
            "LegalMonetaryTotal": {
                "Value": order_data.get("cac:AnticipatedMonetaryTotal", {})
                .get("cbc:PayableAmount", {})
                .get("#text"),
                "Currency": order_data.get("cac:AnticipatedMonetaryTotal", {})
                .get("cbc:PayableAmount", {})
                .get("@currencyID"),
            },
            "InvoiceLine": [
                {
                    "ID": order_data.get("cac:OrderLine", {})
                    .get("cac:LineItem", {})
                    .get("cbc:ID"),
                    "Value": order_data.get("cac:OrderLine", {})
                    .get("cac:LineItem", {})
                    .get("cbc:LineExtensionAmount", {})
                    .get("#text"),
                    "Currency": order_data.get("cac:OrderLine", {})
                    .get("cac:LineItem", {})
                    .get("cbc:LineExtensionAmount", {})
                    .get("@currencyID"),
                    "Description": order_data.get("cac:OrderLine", {})
                    .get("cac:LineItem", {})
                    .get("cac:Item", {})
                    .get("cbc:Description"),
                }
            ],
        }

        required_fields = {
            "Invoice ID": refined_order["InvoiceID"],
            "Issue Date": refined_order["IssueDate"],
            "Invoice Start Date": refined_order["InvoicePeriod"]["StartDate"],
            "Invoice End Date": refined_order["InvoicePeriod"]["EndDate"],
            "Supplier Name": refined_order["AccountingSupplierParty"],
            "Customer Name": refined_order["AccountingCustomerParty"],
            "Total Amount": refined_order["LegalMonetaryTotal"]["Value"],
        }

        for field_name, value in required_fields.items():
            if value is None:
                errors.append(f"Missing field: {field_name}")

        if errors:
            return {"errors": errors}

        refined_order = json.dumps(refined_order)
        return refined_order

    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data") from e


@app.post("/ubl/invoice/create", tags=["INVOICE GENERATION"])
async def create_invoice(invoice_json: str = Body(...)):
    """_summary_

    Generates an XML invoice from validated order data.

    Args:
        invoice_json (str): JSON string representation of the validated invoice data.

    Raises:
        HTTPException: If the JSON input is empty.
        HTTPException: If the JSON format is invalid.
        HTTPException: If the parsed JSON is empty.
        HTTPException: If the invoice XML file creation fails.

    Returns:
        dict: Confirmation message for XML file creation.
    """
    if not invoice_json.strip():  # Check if the input is empty
        raise HTTPException(status_code=400, detail="JSON string is empty")
    try:
        data = json.loads(invoice_json)  # Parse the JSON into a dictionary
    except json.JSONDecodeError as ex:
        raise HTTPException(status_code=400, detail="Invalid JSON format") from ex

    if not data:  # Ensure the parsed JSON is not an empty dictionary
        raise HTTPException(status_code=400, detail="Parsed JSON is empty")

    # Create the root element (UBL Invoice)
    invoice = ET.Element(
        "Invoice",
        {
            "xmlns": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            "xmlns:cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "xmlns:cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        },
    )

    # Add invoice ID and Issue Date
    ET.SubElement(invoice, "cbc:ID").text = f"{data['InvoiceID']}"
    ET.SubElement(invoice, "cbc:IssueDate").text = f"{data['IssueDate']}"

    # Add Invoice period (start and end date)
    invoice_period = ET.SubElement(invoice, "cac:InvoicePeriod")
    ET.SubElement(invoice_period, "cbc:StartDate").text = (
        f"{data['InvoicePeriod']['StartDate']}"
    )
    ET.SubElement(invoice_period, "cbc:EndDate").text = (
        f"{data['InvoicePeriod']['EndDate']}"
    )

    # Supplier details
    # supplier = ET.SubElement(invoice, "cac:AccountingSupplierParty")
    # supplier_party = ET.SubElement(supplier, "cac:Party")
    # supplier_party_name = ET.SubElement(supplier_party, "cac:PartyName")
    # ET.SubElement(supplier_party_name, "cbc:Name").text = f"{data['AccountingSupplierParty']}"
    ET.SubElement(
        ET.SubElement(
            ET.SubElement(invoice, "cac:AccountingSupplierParty"), "cac:Party"
        ),
        "cac:PartyName",
    )
    ET.SubElement(invoice[-1], "cbc:Name").text = f"{data['AccountingSupplierParty']}"
    # Customer details
    # customer = ET.SubElement(invoice, "cac:AccountingCustomerParty")
    # customer_party = ET.SubElement(customer, "cac:Party")
    # customer_party_name = ET.SubElement(customer_party, "cac:PartyName")
    # ET.SubElement(customer_party_name, "cbc:Name").text = f"{data['AccountingCustomerParty']}"
    ET.SubElement(
        ET.SubElement(
            ET.SubElement(invoice, "cac:AccountingCustomerParty"), "cac:Party"
        ),
        "cac:PartyName",
    )
    ET.SubElement(invoice[-1], "cbc:Name").text = f"{data['AccountingCustomerParty']}"
    # Legal Monetary Total
    total_money = ET.SubElement(invoice, "cac:LegalMonetaryTotal")
    ET.SubElement(
        total_money,
        "cbc:PayableAmount",
        currencyID=f"{data['LegalMonetaryTotal']['Currency']}",
    ).text = f"{data['LegalMonetaryTotal']['Value']}"

    for line in data["InvoiceLine"]:
        # Invoice Line Item
        invoice_line = ET.SubElement(invoice, "cac:InvoiceLine")
        ET.SubElement(invoice_line, "cbc:ID").text = f"{line['ID']}"

        ET.SubElement(
            invoice_line, "cbc:LineExtensionAmount", currencyID=f"{line['Currency']}"
        ).text = f"{line['Value']}"
        ET.SubElement(
            ET.SubElement(invoice_line, "cac:Item"), "cbc:Description"
        ).text = f"{line['Description']}"
    # Convert to XML string and save to file
    xml_str = ET.tostring(invoice, encoding="utf-8")

    # Format the XML file so it's not a single line
    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="\t")
    return pretty_xml

    # try:
    #     with open("invoice.xml", "w", encoding="utf-8") as file:
    #         file.write(pretty_xml)
    # except Exception as ex:
    #     raise HTTPException(status_code=500, detail=f"Failed to create XML file {ex}") from ex

    # return {"details": "XML file successful"}


@app.post("/ubl/order/upload/v2", tags=["DATA VALIDATION"])
async def parse_ubl_order(file: UploadFile = File(...)):
    """_summary_

    Parses an uploaded UBL XML order document into JSON format.

    Args:
        file (UploadFile): XML file uploaded by the user.

    Raises:
        HTTPException: If no file is provided.
        HTTPException: If the XML file is invalid.

    Returns:
        dict: Parsed XML data in JSON format.
    """
    if file is None:
        raise HTTPException(status_code=400, detail="No file provided")
    try:
        xml_content = await file.read()

        data_dict = xmltodict.parse(xml_content, process_namespaces=False)

        json_data = json.dumps(data_dict, indent=4)

        return json_data
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid XML file") from e


@app.post("/ubl/order/validate/v2", tags=["DATA VALIDATION"])
async def validate_order(order_json: str = Body(...)):
    """_summary_

    Validates a parsed UBL order document.

    Args:
        order_json (str): JSON string representation of the order document.

    Raises:
        HTTPException: If no JSON data is provided.
        HTTPException: If the JSON data is invalid.

    Returns:
        dict: Validated order details or errors if missing fields.
    """
    try:
        if order_json is None:
            raise HTTPException(status_code=400, detail="No JSON provided")

        order_data = json.loads(order_json)
        order_data = order_data.get("Order", {})
        errors = []
        refined_order = {
            "InvoiceID": random.randint(1, 1000),
            "IssueDate": order_data.get("cbc:IssueDate"),
            "InvoicePeriod": {
                "StartDate": order_data.get("cac:Delivery", {})
                .get("cac:RequestedDeliveryPeriod", {})
                .get("cbc:StartDate"),
                "EndDate": order_data.get("cac:Delivery", {})
                .get("cac:RequestedDeliveryPeriod", {})
                .get("cbc:EndDate"),
            },
            "AccountingSupplierParty": order_data.get("cac:SellerSupplierParty", {})
            .get("cac:Party", {})
            .get("cac:PartyName", {})
            .get("cbc:Name"),
            "AccountingCustomerParty": order_data.get("cac:BuyerCustomerParty", {})
            .get("cac:Party", {})
            .get("cac:PartyName", {})
            .get("cbc:Name"),
            "LegalMonetaryTotal": {
                "Value": order_data.get("cac:AnticipatedMonetaryTotal", {})
                .get("cbc:PayableAmount", {})
                .get("#text"),
                "Currency": order_data.get("cac:AnticipatedMonetaryTotal", {})
                .get("cbc:PayableAmount", {})
                .get("@currencyID"),
            },
            "InvoiceLine": [],
        }
        all_items = order_data.get("cac:OrderLine", [])
        if isinstance(all_items, dict):
            all_items = [all_items]

        for items in all_items:
            item = items.get("cac:LineItem", {})
            refined_order["InvoiceLine"].append(
                {
                    "ID": item.get("cbc:ID"),
                    "Value": item.get("cbc:LineExtensionAmount", {}).get("#text"),
                    "Currency": item.get("cbc:LineExtensionAmount", {}).get(
                        "@currencyID"
                    ),
                    "Description": item.get("cac:Item", {}).get("cbc:Description"),
                }
            )

        required_fields = {
            "Invoice ID": refined_order["InvoiceID"],
            "Issue Date": refined_order["IssueDate"],
            "Invoice Start Date": refined_order["InvoicePeriod"]["StartDate"],
            "Invoice End Date": refined_order["InvoicePeriod"]["EndDate"],
            "Supplier Name": refined_order["AccountingSupplierParty"],
            "Customer Name": refined_order["AccountingCustomerParty"],
            "Total Amount": refined_order["LegalMonetaryTotal"]["Value"],
        }

        for field_name, value in required_fields.items():
            if value is None:
                errors.append(f"Missing field: {field_name}")

        if errors:
            raise HTTPException(status_code=400, detail=errors)

        errors = []

        issue_date = refined_order["IssueDate"]
        start_date = refined_order["InvoicePeriod"]["StartDate"]
        end_date = refined_order["InvoicePeriod"]["EndDate"]

        if not valid_date(issue_date):
            errors.append("Invalid IssueDate format. Must be in format (YYYY-MM-DD).")
        if not valid_date(start_date):
            errors.append("Invalid StartDate format. Must be in format (YYYY-MM-DD).")
        if not valid_date(end_date):
            errors.append("Invalid EndDate format. Must be in format (YYYY-MM-DD).")
        if valid_date(start_date) and valid_date(end_date):
            if datetime.fromisoformat(end_date) < datetime.fromisoformat(start_date):
                errors.append("EndDate must be after StartDate.")

        if not isinstance(refined_order["AccountingSupplierParty"], str):
            errors.append("Supplier Name must be a string.")

        if not isinstance(refined_order["AccountingCustomerParty"], str):
            errors.append("Customer Name must be a string.")

        currency = refined_order["LegalMonetaryTotal"]["Currency"]
        if not valid_currency(currency):
            errors.append(f"Invalid currency: {currency}. Must be valid currency code.")

        try:
            float(refined_order["LegalMonetaryTotal"]["Value"])
        except:
            errors.append("Total Amount must be a number.")

        for i, line in enumerate(refined_order["InvoiceLine"]):
            try:
                if line["ID"] is None or not str(line["ID"]).isdigit():
                    errors.append(f"Item {i+1}: ID must be a number.")
                float(line["Value"])
                if not valid_currency(line["Currency"]):
                    errors.append(
                        f"Item {i+1}: Invalid currency: {currency}. Must be valid currency code."
                    )
                if not isinstance(line["Description"], str):
                    errors.append(f"Item {i+1}: Description must be a string.")
            except:
                errors.append(f"Item {i+1}: Invalid item data.")

        if errors:
            raise HTTPException(status_code=400, detail=errors)

        refined_order = json.dumps(refined_order)
        return refined_order

    except HTTPException as http_exc:
        raise http_exc

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON data")


@app.put("/ubl/order/edit/v2", tags=["DATA VALIDATION"])
async def edit_invoice(payload: dict = Body(...)):
    """
    Edits fields in an invoice and re-validates it using the existing validation logic.
    """
    refined_order = json.loads(payload["invoice_json"])
    updates = payload["updates"]
    try:
        if refined_order is None:
            raise HTTPException(status_code=400, detail="No invoice data provided")

        if updates is None:
            raise HTTPException(status_code=400, detail="No edits provided")

        if "IssueDate" in updates:
            refined_order["IssueDate"] = updates["IssueDate"]

        if "StartDate" in updates:
            refined_order["InvoicePeriod"]["StartDate"] = updates["StartDate"]

        if "EndDate" in updates:
            refined_order["InvoicePeriod"]["EndDate"] = updates["EndDate"]

        if "AccountingSupplierParty" in updates:
            refined_order["AccountingSupplierParty"] = updates[
                "AccountingSupplierParty"
            ]

        if "AccountingCustomerParty" in updates:
            refined_order["AccountingCustomerParty"] = updates[
                "AccountingCustomerParty"
            ]

        if "TotalAmount" in updates:
            raise HTTPException(
                status_code=400,
                detail="Cannot Change CurrTotal Amount. Use currency api",
            )

        if "Currency" in updates:
            raise HTTPException(
                status_code=400, detail="Cannot Change Currency. Use currency api"
            )

        if "InvoiceID" in updates:
            raise HTTPException(status_code=400, detail="Cannot Change InvoiceId.")

        if "InvoiceLine" in updates:
            raise HTTPException(status_code=400, detail="Cannot Change Items.")

        errors = []

        issue_date = refined_order["IssueDate"]
        start_date = refined_order["InvoicePeriod"]["StartDate"]
        end_date = refined_order["InvoicePeriod"]["EndDate"]

        if not valid_date(issue_date):
            errors.append("Invalid IssueDate format. Must be in format (YYYY-MM-DD).")
        if not valid_date(start_date):
            errors.append("Invalid StartDate format. Must be in format (YYYY-MM-DD).")
        if not valid_date(end_date):
            errors.append("Invalid EndDate format. Must be in format (YYYY-MM-DD).")
        if valid_date(start_date) and valid_date(end_date):
            if datetime.fromisoformat(end_date) < datetime.fromisoformat(start_date):
                errors.append("EndDate must be after StartDate.")

        if not isinstance(refined_order["AccountingSupplierParty"], str):
            errors.append("Supplier Name must be a string.")

        if not isinstance(refined_order["AccountingCustomerParty"], str):
            errors.append("Customer Name must be a string.")

        if errors:
            raise HTTPException(status_code=400, detail=errors)

        refined_order = json.dumps(refined_order)
        return refined_order

    except HTTPException as http_exc:
        raise http_exc

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON data")


@app.put("/ubl/order/currency/v2", tags=["DATA VALIDATION"])
async def edit_invoice(payload: dict = Body(...)):
    """
    Edits fields in an invoice and re-validates it using the existing validation logic.
    """
    refined_order = json.loads(payload["invoice_json"])
    updates = payload["updates"]

    try:
        if refined_order is None:
            raise HTTPException(status_code=400, detail="No invoice data provided")

        if updates is None:
            raise HTTPException(status_code=400, detail="No edits provided")

        currency = refined_order["LegalMonetaryTotal"]["Currency"]

        errors = []

        c = CurrencyConverter()

        if not valid_currency(updates["Currency"]):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid currency: {updates["Currency"]}. Must be valid currency code.",
            )

        updates["Currency"] = updates["Currency"].upper()

        refined_order["LegalMonetaryTotal"]["Currency"] = updates["Currency"]
        for i, line in enumerate(refined_order["InvoiceLine"]):
            try:
                line["Currency"] = updates["Currency"]
                amount = float(line["Value"])
                line["Value"] = round(
                    c.convert(amount, currency, updates["Currency"]), 2
                )
            except Exception:
                errors.append(f"Item {i+1}: Invalid value or conversion failed.")
        total = 0
        for i, line in enumerate(refined_order["InvoiceLine"]):
            try:
                amount = float(line["Value"])
                total += amount
            except Exception:
                errors.append(f"Item {i+1}: Invalid value or conversion failed.")
        refined_order["LegalMonetaryTotal"]["Value"] = round(total, 2)

        if errors:
            raise HTTPException(status_code=400, detail=errors)

        refined_order = json.dumps(refined_order)
        return refined_order

    except HTTPException as http_exc:
        raise http_exc

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON data")


@app.post("/ubl/order/email/v2", tags=["DATA VALIDATION"])
async def edit_invoice(to_email: str = Form(...), attachment: UploadFile = Form(...)):
    smtp_port = 587
    smtp_server = "smtp.gmail.com"

    email_from = "wubenny2@gmail.com"
    pswd = "rhtp imjq hoch enpv "

    subject = "Invoice"
    body = "Hello,\nThank you for using our service. Attached below is your invoice."
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = to_email
    msg.set_content(body)

    file_content = await attachment.read()
    msg.add_attachment(
        file_content,
        maintype="application",
        subtype="octet-stream",
        filename=attachment.filename,
    )

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(email_from, pswd)
            smtp.send_message(msg)
        return {"message": "Invoice sent successfully."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
