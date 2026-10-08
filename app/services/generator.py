import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from app.config import settings

def generate_certificate_pdf(cert_id: str, recipient_name: str, title: str, issue_date: str, issuer: str) -> str:
    """
    Generates a certificate PDF and returns the file path.
    """
    filename = f"{cert_id}.pdf"
    filepath = os.path.join(settings.storage_dir, filename)
    
    # Create the PDF
    c = canvas.Canvas(filepath, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Border
    c.setLineWidth(5)
    c.rect(0.5*inch, 0.5*inch, width - 1*inch, height - 1*inch)
    
    # Title
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(width/2.0, height - 2*inch, "CERTIFICATE OF COMPLETION")
    
    # Subtitle
    c.setFont("Helvetica", 24)
    c.drawCentredString(width/2.0, height - 3*inch, "This is to certify that")
    
    # Recipient Name (Handling long names by using a smaller font if needed, here just basic truncation/shrink)
    c.setFont("Helvetica-Bold", 36)
    # Simple truncate if too long
    display_name = recipient_name if len(recipient_name) <= 40 else recipient_name[:37] + "..."
    c.drawCentredString(width/2.0, height - 4*inch, display_name)
    
    # Text
    c.setFont("Helvetica", 24)
    c.drawCentredString(width/2.0, height - 5*inch, "has successfully completed")
    
    # Course/Event Title
    c.setFont("Helvetica-Bold", 30)
    display_title = title if len(title) <= 50 else title[:47] + "..."
    c.drawCentredString(width/2.0, height - 6*inch, display_title)
    
    # Footer - Date and Issuer
    c.setFont("Helvetica", 18)
    c.drawString(1.5*inch, 1.5*inch, f"Date: {issue_date}")
    c.drawRightString(width - 1.5*inch, 1.5*inch, f"Issuer: {issuer}")
    
    c.save()
    return filepath
