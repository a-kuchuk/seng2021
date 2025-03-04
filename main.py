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
def create_item(item: int):
    return

# edit invoice
@app.put("/invoices/edit/{invoiceId}")
def create_item(item: int):
    return

# view invoice
@app.get("/invoices/view/{invoiceId}")
def create_item(item: int):
    return

# delete invoice
@app.delete("/invoices/delete/{invoiceId}")
def create_item(item: int):
    return

# process UBL
@app.post("/invoices/UBL/")
def create_item(item: int):
    return

# process JSON
@app.post("/invoices/{JSONId}")
def create_item(item: int):
    return

# validate UBL
@app.get("/invoices/validate/")
def create_item(item: int):
    return

# specify currency
@app.put("/invoices/{invoiceId}/currency")
def create_item(item: int):
    return

# specify language
@app.put("/invoices/{invoiceId}/language")
def create_item(item: int):
    return

# specify template
@app.put("/invoices/{invoiceId}/template")
def create_item(item: int):
    return