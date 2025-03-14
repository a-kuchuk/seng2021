"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

import json
from fastapi import FastAPI, UploadFile, File, HTTPException
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
