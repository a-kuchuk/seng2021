from fastapi import FastAPI, HTTPException
import os
import json

app = FastAPI()

@app.post("/ubl/order/refine/{orderId}")
def refine_data(orderId: str):
    if not orderId:
        raise HTTPException(status_code=400, detail="Missing or invalid Order Id")

    json_file = "order_data.json"

    if not os.path.exists(json_file):
        raise HTTPException(status_code=400, detail="File doesn't exist")

    with open(json_file, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")

    if not data or "orderId" not in data:
        raise HTTPException(status_code=400, detail="Missing or invalid Order Id")

    return {
        "orderId": orderId,
        "message": "Order refined successfully"
    }
