"""invoicve generation api"""

import json
import random
import xml.etree.ElementTree as ET
import xml.dom.minidom
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.openapi.utils import get_openapi
import xmltodict
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

DESCRIPTION= """
API that takes an XML order document and provides a XML invoice
with the elements extracted from the order doc and mapped to the invoice.
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
    title="The Real Guy Chilcott",
    version="2.0.1",
    description=DESCRIPTION,
    openapi_tags=tags_metadata,
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="The Real Guy Chilcott",
        version="2.0.1",
        summary="Invoice Generation OpenAPI schema",
        description="Our updated and up to standard OpenAPI schema, available on web and for download",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi




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
    except Exception as ex:
        raise HTTPException(status_code=400, detail="Invalid XML file") from ex


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
            "InvoiceID": random.randint(1,1000),
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
            "InvoiceLine": [ {
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
                                        .get("cbc:Description")
            }
            ]
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

    except Exception as ex:
        raise HTTPException(status_code=400, detail="Invalid JSON data") from ex

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
    invoice = ET.Element("Invoice", {
        "xmlns": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        "xmlns:cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "xmlns:cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    })

    # Add invoice ID and Issue Date
    ET.SubElement(invoice, "cbc:ID").text = f"{data['InvoiceID']}"
    ET.SubElement(invoice, "cbc:IssueDate").text = f"{data['IssueDate']}"

    # Add Invoice period (start and end date)
    invoice_period = ET.SubElement(invoice, "cac:InvoicePeriod")
    ET.SubElement(invoice_period, "cbc:StartDate").text = f"{data['InvoicePeriod']['StartDate']}"
    ET.SubElement(invoice_period, "cbc:EndDate").text = f"{data['InvoicePeriod']['EndDate']}"

    # Supplier details
    # supplier = ET.SubElement(invoice, "cac:AccountingSupplierParty")
    # supplier_party = ET.SubElement(supplier, "cac:Party")
    # supplier_party_name = ET.SubElement(supplier_party, "cac:PartyName")
    # ET.SubElement(supplier_party_name, "cbc:Name").text = f"{data['AccountingSupplierParty']}"
    ET.SubElement(
        ET.SubElement(
            ET.SubElement(
                invoice, "cac:AccountingSupplierParty"), "cac:Party"),
                "cac:PartyName")
    ET.SubElement(invoice[-1], "cbc:Name").text = f"{data['AccountingSupplierParty']}"
    # Customer details
    # customer = ET.SubElement(invoice, "cac:AccountingCustomerParty")
    # customer_party = ET.SubElement(customer, "cac:Party")
    # customer_party_name = ET.SubElement(customer_party, "cac:PartyName")
    # ET.SubElement(customer_party_name, "cbc:Name").text = f"{data['AccountingCustomerParty']}"
    ET.SubElement(
        ET.SubElement(
            ET.SubElement(
                invoice, "cac:AccountingCustomerParty"), "cac:Party"),
                "cac:PartyName")
    ET.SubElement(invoice[-1], "cbc:Name").text = f"{data['AccountingCustomerParty']}"
    # Legal Monetary Total
    total_money = ET.SubElement(invoice, "cac:LegalMonetaryTotal")
    ET.SubElement(
        total_money, "cbc:PayableAmount", currencyID=f"{data['LegalMonetaryTotal']['Currency']}"
    ).text = f"{data['LegalMonetaryTotal']['Value']}"

    for line in data['InvoiceLine']:
        # Invoice Line Item
        invoice_line = ET.SubElement(invoice, "cac:InvoiceLine")
        ET.SubElement(invoice_line, "cbc:ID").text = f"{line['ID']}"

        ET.SubElement(
            invoice_line, "cbc:LineExtensionAmount", currencyID=f"{line['Currency']}"
        ).text = f"{line['Value']}"
        ET.SubElement(ET.SubElement(invoice_line, "cac:Item"),
        "cbc:Description").text = f"{line['Description']}"
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


@app.post("/ubl/invoice/pdf", tags=["INVOICE MANIPULATION"])
async def xml_to_pdf(file: UploadFile = File(...)):
    """Upload an XML invoice document and converts in into a PDF

    Args:
        file (UploadFile, optional): the UBL XML invoice document. Defaults to File(None).

    Returns:
        none
    """
    contents = await file.read()
    tree = ET.ElementTree(ET.fromstring(contents))
    root = tree.getroot()

    def extract_text_with_titles(element, indent=0):
        """ Recursively extract tag names and their text content """
        content = []
        tag_name = element.tag.split('}')[-1]  # Remove namespace if present
        if element.text and element.text.strip():
            content.append(f"{'  ' * indent}{tag_name}: {element.text.strip()}")
        for child in element:
            content.extend(extract_text_with_titles(child, indent=indent + 1))
        return content

    content = extract_text_with_titles(root)

    can = canvas.Canvas("invoice.pdf", pagesize=letter)
    height = letter[1]
    y_position = height - 40  # Start position from the top

    for line in content:
        can.drawString(40, y_position, line)
        y_position -= 20  # Move down for the next line
        if y_position < 40:  # Start a new page if needed
            can.showPage()
            y_position = height - 40

    can.save()
