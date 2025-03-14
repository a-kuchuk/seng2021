"""_summary_

contains all routes

Returns:
    _type_: _description_
"""
import os
import json
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/ubl/order/refine/{orderId}")
def refine_data(order_id: str):
    """_summary_

    order refine route

    Returns:
        orderId: string
        message: string
    """
    if not order_id:
        raise HTTPException(status_code=400, detail="Missing or invalid Order Id")

    json_file = "order_data.json"

    if not os.path.exists(json_file):
        raise HTTPException(status_code=400, detail="File doesn't exist")

    with open(json_file, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as decode_error:
            raise HTTPException(status_code=400, detail="Invalid JSON format") from decode_error

    if not data or "orderId" not in data:
        raise HTTPException(status_code=400, detail="Missing or invalid Order Id")

    return {
        "orderId": order_id,
        "message": "Order refined successfully"
    }
