"""Service for email registration via Google Form."""
import urllib.parse
import urllib.request
from typing import Optional


class EmailRegistrationService:
    """Service for submitting email registration to Google Form."""
    
    # Google Form endpoint
    GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe03QktsJ50P-LZME7iS4bGhjbFLkHVQUIqFzZvN-jxbmQPfg/formResponse"
    
    # Form field entry ID
    EMAIL_FIELD_ENTRY = "818918261"
    
    def submit_email(self, email: str) -> tuple[bool, Optional[str]]:
        """
        Submit email to Google Form.
        
        Args:
            email: Email address to submit
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Prepare form data
            form_data = {
                f"entry.{self.EMAIL_FIELD_ENTRY}": email
            }
            
            # Encode form data
            data = urllib.parse.urlencode(form_data).encode('utf-8')
            
            # Create request
            req = urllib.request.Request(
                self.GOOGLE_FORM_URL,
                data=data,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            # Submit form
            with urllib.request.urlopen(req, timeout=10) as response:
                # Google Forms returns 200 on success (even if validation fails)
                # We consider it successful if we get a response
                status_code = response.getcode()
                if status_code == 200:
                    print(f"Email registration successful: {email}")
                    return True, None
                else:
                    error_msg = f"Unexpected status code: {status_code}"
                    print(f"Email registration failed: {error_msg}")
                    return False, error_msg
                    
        except urllib.error.URLError as e:
            error_msg = f"Network error: {str(e)}"
            print(f"Email registration failed: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"Email registration failed: {error_msg}")
            return False, error_msg

