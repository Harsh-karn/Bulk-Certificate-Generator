from email_validator import validate_email, EmailNotValidError
from typing import Optional

def validate_recipient(name: Optional[str], email: Optional[str]) -> Optional[str]:
    """
    Validates a recipient.
    Returns an error message string if invalid, or None if valid.
    """
    if not name or not name.strip():
        return "Name is required."
    
    if email:
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError as e:
            return f"Invalid email: {str(e)}"
            
    return None
