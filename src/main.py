"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

import os
import json
from fastapi import FastAPI, HTTPException

app = FastAPI()

INVOICE_FILE = "invoice_data.json"

@app.put("/ubl/invoice/edit/{invoiceId}")
def edit_invoice(invoice_id: str, updated_invoice: dict):
    """_summary_

    editing invoice route

    Returns:
        invoiceId: string
    """
    if not invoice_id:
        raise HTTPException(status_code=400, detail="Missing or invalid invoice Id")

    if not updated_invoice or not isinstance(updated_invoice, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid input data")

    if not os.path.exists(INVOICE_FILE):
        raise HTTPException(status_code=500, detail="Invoice file not found")

    try:
        with open(INVOICE_FILE, "r", encoding="utf-8") as file:
            invoices = json.load(file)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Invalid JSON format") from exc

    # Find the invoice and update it
    if invoice_id not in invoices:
        raise HTTPException(status_code=400, detail="Invoice not found")

    invoices[invoice_id].update(updated_invoice)

    with open(INVOICE_FILE, "w", encoding="utf-8") as file:
        json.dump(invoices, file, indent=4)

    return invoices[invoice_id]
