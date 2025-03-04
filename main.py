from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"details": "Hello, World!"}

# IMPORTANT!!!!  
# body of functions is placeholder bs to get rid of errors
# 

# crete new invoice
@app.post("/invoices/create")
def create_new_invoice(item: int):
    return

# edit invoice
@app.put("/invoices/edit/{invoiceId}")
def edit_invoice(item: int):
    return

# view invoice
@app.get("/invoices/view/{invoiceId}")
def view_invoice(item: int):
    return

# delete invoice
@app.delete("/invoices/delete/{invoiceId}")
def delete_invoice(item: int):
    return

# process UBL
@app.post("/invoices/UBL/")
def process_UBL(item: int):
    return

# process JSON
@app.post("/invoices/{JSONId}")
def process_JSON(item: int):
    return

# validate UBL
@app.get("/invoices/validate/")
def validate_UBL(item: int):
    return

# specify currency
@app.put("/invoices/{invoiceId}/currency")
def specify_currency(item: int):
    return

# specify language
@app.put("/invoices/{invoiceId}/language")
def specify_language(item: int):
    return

# specify template
@app.put("/invoices/{invoiceId}/template")
def specify_template(item: int):
    return