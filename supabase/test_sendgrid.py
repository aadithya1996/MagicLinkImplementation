import os
import sys
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load .env
load_dotenv()

API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL")

print("--- SendGrid Connectivity Test ---")

if not API_KEY:
    print("❌ Error: SENDGRID_API_KEY is missing from .env")
    sys.exit(1)

if not FROM_EMAIL:
    print("❌ Error: SENDGRID_FROM_EMAIL is missing from .env")
    sys.exit(1)

# Masked Key Check
masked_key = f"{API_KEY[:4]}...{API_KEY[-4:]}" if len(API_KEY) > 8 else "INVALID"
print(f"API Key Loaded: {masked_key}")
print(f"From Email: {FROM_EMAIL}")

# Construct Email
message = Mail(
    from_email=FROM_EMAIL,
    to_emails=FROM_EMAIL,  # Send to self for testing
    subject='Test Email from Script',
    html_content='<strong>Hello! SendGrid is working.</strong>')

try:
    print("\nAttempting to send email...")
    sg = SendGridAPIClient(API_KEY)
    response = sg.send(message)
    
    print(f"\n✅ Success!")
    print(f"Status Code: {response.status_code}")
    print(f"Body: {response.body}")
    print(f"Headers: {response.headers}")

except Exception as e:
    print(f"\n❌ Failed to send email.")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    
    # If it's a python_http_client error, it might have more details
    if hasattr(e, 'body'):
        print(f"Response Body: {e.body}")
