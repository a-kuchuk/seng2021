"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

from http.client import HTTPException
import os
import json
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    """_summary_

    default hello world route

    Returns:
        _type_: _description_
    """
    return {"details": "Hello, World!"}

@app.post("/ubl/order/refine/{order_id}")
def refine_data(order_id: str):
    """refines data

    Args:
        order_id (str): _description_

    Raises:
        HTTPException: Missing or invalid Order Id"
        HTTPException: File doesn't exist
        HTTPException: Invalid JSON format
        HTTPException: Missing or invalid Order Id

    Returns:
        _type_: _description_
    """
    if not order_id:
        raise HTTPException(status_code=400, detail="Missing or invalid Order Id")

    json_file = "order_data.json"

    if not os.path.exists(json_file):
        raise HTTPException(status_code=400, detail="File doesn't exist")

    with open(json_file, "r", encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as decode_err:
            raise HTTPException(status_code=400, detail="Invalid JSON format") from decode_err

    if not data or "order_id" not in data:
        raise HTTPException(status_code=400, detail="Missing or invalid Order Id")

    # Simulate data refinement
    refined_data = {
        "JSONId": order_id,
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
