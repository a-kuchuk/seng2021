"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

import json
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
async def validate_order(order_JSON: str = Body(...)):
    try:
        if order_JSON is None:
            raise HTTPException(status_code=400, detail="No JSON provided")

        order_data = json.loads(order_JSON)
        order_data = order_data.get("Order", {})
        refined_order = {
            "InvoiceID": {"ID": (id(object()) * 13) % 100 + 1},
            "IssueDate": order_data.get("cbc:IssueDate"),
            "InvoicePeriod": {
                "StartDate": order_data.get("cac:Delivery", {})
                                    .get("cac:RequestedDeliveryPeriod", {})
                                    .get("cbc:StartDate"),
                "EndDate": order_data.get("cac:Delivery", {})
                                    .get("cac:RequestedDeliveryPeriod", {})
                                    .get("cbc:EndDate")
            },
            "AccountingSupplierParty": {
                "Name": order_data.get("cac:SellerSupplierParty", {})
                                .get("cac:Party", {})
                                .get("cac:PartyName", {})
                                .get("cbc:Name")
            },
            "AccountingCustomerParty": {
                "Name": order_data.get("cac:BuyerCustomerParty", {})
                                .get("cac:Party", {})
                                .get("cac:PartyName", {})
                                .get("cbc:Name")
            },
            "LegalMonetaryTotal": {
                "PayableAmount": {
                    "Value": order_data.get("cac:AnticipatedMonetaryTotal", {})
                                    .get("cbc:PayableAmount", {})
                                    .get("#text"),
                    "Currency": order_data.get("cac:AnticipatedMonetaryTotal", {})
                                        .get("cbc:PayableAmount", {})
                                        .get("@currencyID")
                }
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

        return {"validatedOrder": refined_order}

    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data") from e