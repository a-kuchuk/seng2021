"""API that takes an XML order document and provides a XML invoice
with the elements extracted from the order doc and mapped to the invoice.

Contains all routes

Returns:
    _type_: _description_
"""

import xml.etree.ElementTree as ET
from fastapi import FastAPI, File, HTTPException, UploadFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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


@app.post("/ubl/invoice/pdf")
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
