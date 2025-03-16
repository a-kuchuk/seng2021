"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

import json
import random
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
import xmltodict

app = FastAPI()


@app.get("/")
def index():
    """_summary_

    default hello world route

    Returns:
        _type_: _description_
    """
    return {"details": "Hello, World!"}

@app.post("/ubl/order/parse")
async def parse_ubl_order(file: UploadFile = File(...)):
    """
    Parse a UBL order from an uploaded XML file.

    Args:
        file (UploadFile): The uploaded XML.

    Returns:
        str: JSON representation of the parsed XML.
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


@app.post("/ubl/order/validate")
async def validate_order(order_json: str = Body(...)):
    """ 
    Validates an order JSON and ensures required fields are present.

    Args:
        order_json (str): The JSON order data received in the request body.

    Returns:
        Either a validated order or a list of missing field errors.
    """
    try:
        if order_json is None:
            raise HTTPException(status_code=400, detail="No JSON provided")

        order_data = json.loads(order_json)
        order_data = order_data.get("Order", {})
        errors = []
        invoiceId = random.randint(1,1000)
        refined_order = {
            "InvoiceID": invoiceId,
            "IssueDate": order_data.get("cbc:IssueDate"),
            "InvoicePeriod": {
                "StartDate": order_data.get("cac:Delivery", {})
                                    .get("cac:RequestedDeliveryPeriod", {})
                                    .get("cbc:StartDate"),
                "EndDate": order_data.get("cac:Delivery", {})
                                    .get("cac:RequestedDeliveryPeriod", {})
                                    .get("cbc:EndDate")
            },
            "AccountingSupplierParty": order_data.get("cac:SellerSupplierParty", {})
                                .get("cac:Party", {})
                                .get("cac:PartyName", {})
                                .get("cbc:Name")
            ,
            "AccountingCustomerParty": order_data.get("cac:BuyerCustomerParty", {})
                                .get("cac:Party", {})
                                .get("cac:PartyName", {})
                                .get("cbc:Name")
            ,
            "LegalMonetaryTotal": {
                    "Value": order_data.get("cac:AnticipatedMonetaryTotal", {})
                                    .get("cbc:PayableAmount", {})
                                    .get("#text"),
                    "Currency": order_data.get("cac:AnticipatedMonetaryTotal", {})
                                        .get("cbc:PayableAmount", {})
                                        .get("@currencyID")
            },
            "InvoiceLine": {
                "ID": order_data.get("cac:OrderLine", {})
                                .get("cac:LineItem", {})
                                .get("cbc:ID"),
                "Amount": {
                    "Value": order_data.get("cac:OrderLine", {})
                                    .get("cac:LineItem", {})
                                    .get("cbc:LineExtensionAmount", {})
                                    .get("#text"),
                    "Currency": order_data.get("cac:OrderLine", {})
                                        .get("cac:LineItem", {})
                                        .get("cbc:LineExtensionAmount", {})
                                        .get("@currencyID")
                },
                "Item": {
                    "Description": order_data.get("cac:OrderLine", {})
                                            .get("cac:LineItem", {})
                                            .get("cac:Item", {})
                                            .get("cbc:Description")
                }
            }
        }

        required_fields = {
            "Invoice ID": refined_order["InvoiceID"],
            "Issue Date": refined_order["IssueDate"],
            "Invoice Start Date": refined_order["InvoicePeriod"]["StartDate"],
            "Invoice End Date": refined_order["InvoicePeriod"]["EndDate"],
            "Supplier Name": refined_order["AccountingSupplierParty"],
            "Customer Name": refined_order["AccountingCustomerParty"],
            "Total Amount": refined_order["LegalMonetaryTotal"]["Value"],
            "Currency": refined_order["LegalMonetaryTotal"]["Currency"],
            "Item ID": refined_order["InvoiceLine"]["ID"],
            "Item Description": refined_order["InvoiceLine"]["Item"]["Description"],
            "Line Extension Amount": refined_order["InvoiceLine"]["Amount"]["Value"],
            "Line Currency": refined_order["InvoiceLine"]["Amount"]["Currency"]
        }

        for field_name, value in required_fields.items():
            if value is None:
                errors.append(f"Missing field: {field_name}")

        if errors:
            return {"errors": errors}

        return refined_order

    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data") from e

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
    ET.SubElement(invoice, "ID").text = f"{data['JSONId']}"
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