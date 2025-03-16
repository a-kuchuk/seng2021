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
        refined_order = {
            "InvoiceID": {"ID": random.randint(1,1000)},
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

        required_fields = {
            "Invoice ID": refined_order["InvoiceID"]["ID"],
            "Issue Date": refined_order["IssueDate"],
            "Invoice Start Date": refined_order["InvoicePeriod"]["StartDate"],
            "Invoice End Date": refined_order["InvoicePeriod"]["EndDate"],
            "Supplier Name": refined_order["AccountingSupplierParty"]["Name"],
            "Customer Name": refined_order["AccountingCustomerParty"]["Name"],
            "Total Amount": refined_order["LegalMonetaryTotal"]["PayableAmount"]["Value"],
            "Currency": refined_order["LegalMonetaryTotal"]["PayableAmount"]["Currency"],
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
