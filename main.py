from fastapi import FastAPI, File, HTTPException, UploadFile
import xml.etree.ElementTree as ET
import mimetypes

app = FastAPI()

@app.get("/")
def index():
    return {"details": "Hello, World!"}

@app.post("/ubl/order/upload")
#use None here to allow empty file, which we then respond with detailed error msg below
async def upload_order_document(file: UploadFile = File(None)): 
    if file is None:
        raise HTTPException(status_code=400, detail="No file provided")
    
     # Check if file is XML (not sure if it should be text or app yet)
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type not in ["application/xml", "text/xml"]:   
        raise HTTPException(status_code=400, detail="File must be an XML file")
    
    try:
        contents = await file.read()
        #optional extra check for empty file to return error message on it - currently empty file gives invalid XML format error:
        #if not contents:
        #    raise HTTPException(status_code=400, detail="Empty file")
        tree = ET.ElementTree(ET.fromstring(contents))
        root = tree.getroot()
        
        # Extract order ID - ensuring it's directly inside <Order>
        cbc_ns = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        order_id = root.find(f"{{{cbc_ns}}}ID")
        
        # Check order id exists in file and is not empty
        if order_id is not None and order_id.text and order_id.text.strip():  
            return {"order_id": order_id.text}
        else:
           # this line is not being reached, but taking out the if else block allows the empty id to be valid so I've kept it
           raise HTTPException(status_code=400, detail="Order ID not found")

    except ET.ParseError:
        raise HTTPException(status_code=400, detail="Invalid XML format")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid XML format")