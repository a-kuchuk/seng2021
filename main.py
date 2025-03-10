from fastapi import FastAPI
import xml.etree.ElementTree as ET
import json

app = FastAPI()

@app.post("/ubl/invoice/create/{JSONId}")
def createInvoice():
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
            
        if not data:
            print("File is empty?")
            return
    except FileNotFoundError:
        print("File doesn't exist")
        
    # Create the root element (UBL Invoice)
    invoice = ET.Element("Invoice", xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2")

    # Add invoice ID
    invoice_id = ET.SubElement(invoice, "ID")
    invoice_id.text = f"{data["JSONId"]}"

    # Add issue date
    issue_date = ET.SubElement(invoice, "IssueDate")
    issue_date.text = f"{data["date"]}"
    
    invoice_period = ET.SubElement(invoice, "InvoicePeriod")
    start_date = ET.SubElement(invoice_period, "StartDate")
    start_date.text = f"{data["period"]["start"]}"
    end_date = ET.SubElement(invoice_period, "EndDate")
    end_date.text = f"{data["period"]["end"]}"

    # Supplier details
    supplier = ET.SubElement(invoice, "AccountingSupplierParty")
    supplier_party = ET.SubElement(supplier, "Party")
    supplier_name = ET.SubElement(supplier_party, "Name")
    supplier_name.text = f"{data["supplier"]}"

    # Customer details
    customer = ET.SubElement(invoice, "AccountingCustomerParty")
    customer_party = ET.SubElement(customer, "Party")
    customer_name = ET.SubElement(customer_party, "Name")
    customer_name.text = f"{data["customer"]}"
    
    # Legal Monetary Total
    total_money = ET.SubElement(invoice, "LegalMonetaryTotal")
    payable = ET. SubElement(total_money, "PayableAmount", currencyID=f"{data["total"]["cur"]}")
    payable.text = f"{data["total"]["amt"]}"

    for line in data["lines"]:
        # Invoice Line Item
        invoice_line = ET.SubElement(invoice, "InvoiceLine")
        line_id = ET.SubElement(invoice_line, "ID")
        line_id.text = f"{line["id"]}"
        
        price_amount = ET.SubElement(invoice_line, "LineExtensionAmount", currencyID=f"{line["cur"]}")
        price_amount.text = f"{line["amt"]}"

        item = ET.SubElement(invoice_line, "Item")
        item_name = ET.SubElement(item, "Description")
        item_name.text = f"{line["desc"]}"

    # Convert to XML string and save to file
    tree = ET.ElementTree(invoice)
    
    try:
        tree.write("invoice.xml", encoding="utf-8", xml_declaration=True)
    except Exception as e:
        print(f"Error: Failed to create XML file {e}")
            
    return {"details": "XML file successful?"}
