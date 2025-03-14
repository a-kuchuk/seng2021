"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

from fastapi import FastAPI, HTTPException
import os
import json

app = FastAPI()

INVOICE_FILE = "invoice_data.json"

@app.put("/ubl/invoice/edit/{invoiceId}")
def edit_invoice(invoiceId: str, updated_invoice: dict):
    if not invoiceId:
        raise HTTPException(status_code=400, detail="Missing or invalid invoice Id")

    if not updated_invoice or not isinstance(updated_invoice, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid input data")

    if not os.path.exists(INVOICE_FILE):
        raise HTTPException(status_code=500, detail="Internal server error: Invoice file not found")

    try:
        with open(INVOICE_FILE, "r", encoding="utf-8") as file:
            invoices = json.load(file)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Internal server error: Invalid JSON format") from exc

    # Find the invoice and update it
    if invoiceId not in invoices:
        raise HTTPException(status_code=400, detail="Invoice not found")

    invoices[invoiceId].update(updated_invoice)

    with open(INVOICE_FILE, "w", encoding="utf-8") as file:
        json.dump(invoices, file, indent=4)

    return invoices[invoiceId]
