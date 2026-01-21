import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
if not SENDGRID_API_KEY and "SENDGRID_API_KEY" in st.secrets:
    SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]

SENDGRID_FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL")
if not SENDGRID_FROM_EMAIL and "SENDGRID_FROM_EMAIL" in st.secrets:
    SENDGRID_FROM_EMAIL = st.secrets["SENDGRID_FROM_EMAIL"]

def send_magic_link(email: str, link: str):
    """
    Send a magic link email using SendGrid.
    """
    if not SENDGRID_API_KEY or not SENDGRID_FROM_EMAIL:
        return {"error": "SendGrid Configuration Missing (API Key or From Email)"}

    print(f"Sending email to {email} with link: {link}")
    
    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=email)
    
    # Use the Dynamic Transactional Template
    message.template_id = 'd-0c62429286df4c0e919fc2a4a4110ab0'
    message.dynamic_template_data = {
        'login_link': link,
        'subject': '🔑 Login to Secret Portal'  # Optional, if your template uses verification
    }
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        # SendGrid returns 202 Accepted for success
        if response.status_code >= 200 and response.status_code < 300:
            return {"status": "sent", "code": response.status_code}
        else:
            return {"error": f"SendGrid Error: {response.status_code}"}
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"error": str(e)}
