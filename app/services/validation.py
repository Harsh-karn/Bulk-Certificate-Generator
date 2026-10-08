from email_validator import validate_email, EmailNotValidError
from typing import Optional

class ValidationService:
    """
    Service responsible for semantic validation rules of business entities.
    """

    @staticmethod
    def validate_recipient(name: Optional[str], email: Optional[str]) -> Optional[str]:
        """
        Validates recipient data.
        Returns a string containing the error message if invalid, or None if perfectly valid.
        """
        # Ensure a name was provided and is not just empty whitespace
        if not name or not name.strip():
            return "Name is required."
        
        # If an email is provided, validate its formatting
        if email:
            try:
                # check_deliverability=False because we don't want to make DNS network calls during generation
                validate_email(email, check_deliverability=False)
            except EmailNotValidError as e:
                return f"Invalid email format: {str(e)}"
                
        return None
