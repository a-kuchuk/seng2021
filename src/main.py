description = """
API that takes an XML order document and provides a XML invoice
with the elements extracted from the order doc and mapped to the invoice.

## Validation

You can validate oder data

## Generation

Generates invoice

"""

import xml.etree.ElementTree as ET
import mimetypes
from fastapi import FastAPI, File, HTTPException, UploadFile

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
    openapi_tags=tags_metadata,
)




@app.get("/", tags=["HEALTH"])
def index():
    """_summary_

    default hello world route

    Returns:
        _type_: _description_
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
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type not in ["text/xml"]:
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
