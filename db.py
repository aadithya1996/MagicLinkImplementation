"""
Supabase client initialization and helper functions.
"""
import os
import uuid
import datetime
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
def get_secret(key):
    """Safely get secret from os.environ or st.secrets"""
    # 1. Try os.environ (loaded via dotenv)
    value = os.environ.get(key)
    if value:
        return value
    
    # 2. Try st.secrets
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass 
    return None

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

# Initialize Client
@st.cache_resource
def get_supabase_client() -> Client:
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            # Return None instead of raising to allow UI to show helpful message
            return None
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase Init Error: {e}")
        return None

# --- CUSTOM MAGIC LINK AUTH ---

def create_magic_link(email: str):
    """
    1. Upsert user in public.users
    2. Create a magic link token in public.magic_links
    3. Return the token (so app.py can display/email it)
    """
    client = get_supabase_client()
    if not client:
        return {"error": "Supabase not configured"}

    try:
        # 1. Upsert User
        # We use the email as the key.
        user_data = {"email": email}
        # Assuming 'email' is unique in schema
        user_res = client.table("users").upsert(user_data, on_conflict="email").execute()
        
        if not user_res.data:
            return {"error": "Failed to create/fetch user"}
            
        user_id = user_res.data[0]['id']

        # 2. Generate Token
        token = str(uuid.uuid4())
        # Expires in 15 minutes
        expires_at = (datetime.datetime.utcnow() + datetime.timedelta(minutes=15)).isoformat()
        
        link_data = {
            "token": token,
            "user_id": user_id,
            "expires_at": expires_at
        }
        
        client.table("magic_links").insert(link_data).execute()
        
        return {"token": token}
        
    except Exception as e:
        return {"error": str(e)}

def verify_magic_link(token: str):
    """
    Verify the token and return the user info if valid.
    """
    client = get_supabase_client()
    if not client:
        return None
        
    try:
        # 1. Fetch token
        res = client.table("magic_links").select("*, users(*)").eq("token", token).execute()
        
        if not res.data:
            return {"error": "Invalid token"}
            
        link_record = res.data[0]
        expires_at = datetime.datetime.fromisoformat(link_record['expires_at'])
        
        # 2. Check Expiry
        if datetime.datetime.utcnow() > expires_at:
            return {"error": "Token expired"}
            
        if link_record.get('used_at'):
            return {"error": "Token already used"}
            
        # 3. Mark as used
        client.table("magic_links").update({
            "used_at": datetime.datetime.utcnow().isoformat()
        }).eq("token", token).execute()
        
        return {"user": link_record['users'], "email": link_record['users']['email']}
        
    except Exception as e:
        return {"error": str(e)}

def sign_out():
    """Clear local session only since we are using custom auth."""
    pass
