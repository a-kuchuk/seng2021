"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

from fastapi import FastAPI
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = FastAPI()

@app.get("/")
def index():
    """_summary_

    default hello world route

    Returns:
        _type_: _description_
    """
    return {"details": "Hello, World!"}


@app.get("/ubl/invoice/pdf/{invoicePath}")
async def xml_to_pdf(invoicePath: str):
    tree = ET.parse(invoicePath)
    root = tree.getroot()
    content = []
    
    for elem in root.iter():
        if elem.text and elem.text.strip():
            content.append(elem.text.strip())
        
    c = canvas.Canvas("invoice.pdf", pagesize=letter)
    width, height = letter
    y_position = height - 40  # Start position from the top
    
    for line in content:
        c.drawString(40, y_position, line)
        y_position -= 20  # Move down for next line
        if y_position < 40:  # Start a new page if needed
            c.showPage()
            y_position = height - 40
    
    c.save()
