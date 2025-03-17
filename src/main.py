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

def extract_text_with_titles(element, indent=0):
    """ Recursively extract tag names and their text content """
    content = []
    tag_name = element.tag.split('}')[-1] 

    if element.text and element.text.strip():
        content.append(f"{'  ' * indent}{tag_name}: {element.text.strip()}")

    for child in element:
        content.extend(extract_text_with_titles(child, indent=indent + 1))
    
    return content

@app.get("/ubl/invoice/pdf")
async def xml_to_pdf(invoicePath: str):
    tree = ET.parse(invoicePath)
    root = tree.getroot()
    
    print("made it in")
    
    content = extract_text_with_titles(root)
    
    print("finished extracting")
        
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