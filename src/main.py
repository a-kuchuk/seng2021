from http.client import HTTPException
import os
from fastapi import FastAPI
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

    # Simulate data refinement
    refined_data = {
        "JSONId": orderId,
        "date": data.get("date", "2011-09-22"),
        "period": data.get("period", {"start": "2011-08-01", "end": "2011-08-31"}),
        "supplier": data.get("supplier", "Custom Cotter Pins"),
        "customer": data.get("customer", "North American Veeblefetzer"),
        "total": data.get("total", {"amt": "100.00", "cur": "CAD"}),
        "lines": data.get(
            "lines",
            [
                {
                    "id": "1",
                    "amt": "100.00",
                    "cur": "CAD",
                    "desc": "Cotter pin, MIL-SPEC",
                }
            ],
        ),
    }

    return refined_data
