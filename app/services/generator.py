import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from app.core.config import settings

class CertificateGenerator:
    """
    Service responsible for rendering the final PDF certificate.
    Encapsulating this allows swapping out the PDF generation logic in the future (e.g. HTML to PDF).
    """
    
    @staticmethod
    def generate_pdf(cert_id: str, recipient_name: str, title: str, issue_date: str, issuer: str) -> str:
        """
        Renders a certificate PDF using ReportLab and returns the saved file path.
        """
        # We use the UUID cert_id to prevent any directory traversal attacks from malicious names.
        filename = f"{cert_id}.pdf"
        filepath = os.path.join(settings.storage_dir, filename)
        
        c = canvas.Canvas(filepath, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Draw a decorative border
        c.setLineWidth(5)
        c.rect(0.5*inch, 0.5*inch, width - 1*inch, height - 1*inch)
        
        # Certificate Header
        c.setFont("Helvetica-Bold", 48)
        c.drawCentredString(width/2.0, height - 2*inch, "CERTIFICATE OF COMPLETION")
        
        c.setFont("Helvetica", 24)
        c.drawCentredString(width/2.0, height - 3*inch, "This is to certify that")
        
        # Safely handle very long recipient names by truncating
        c.setFont("Helvetica-Bold", 36)
        display_name = recipient_name if len(recipient_name) <= 40 else recipient_name[:37] + "..."
        c.drawCentredString(width/2.0, height - 4*inch, display_name)
        
        c.setFont("Helvetica", 24)
        c.drawCentredString(width/2.0, height - 5*inch, "has successfully completed")
        
        # Safely handle very long titles
        c.setFont("Helvetica-Bold", 30)
        display_title = title if len(title) <= 50 else title[:47] + "..."
        c.drawCentredString(width/2.0, height - 6*inch, display_title)
        
        # Footer section for Date and Issuer details
        c.setFont("Helvetica", 18)
        c.drawString(1.5*inch, 1.5*inch, f"Date: {issue_date}")
        c.drawRightString(width - 1.5*inch, 1.5*inch, f"Issuer: {issuer}")
        
        c.save()
        return filepath
