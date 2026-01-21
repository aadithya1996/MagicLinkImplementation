"""
April Fool's Streamlit App with Magic Link Authentication
"""
import streamlit as st
import time
import uuid
import datetime
from dotenv import load_dotenv
load_dotenv()

# import resend  # In production, use real Resend client

# --- CONFIGURATION ---
SESSION_TIMEOUT_SECONDS = 300  # 5 minutes for demo purposes for session expiry
TOKEN_EXPIRY_SECONDS = 900     # 15 minutes for magic link expiry

# Page configuration
st.set_page_config(
    page_title="🎭 Secret Portal",
    page_icon="🎭",
    layout="centered"
)

# --- DATABASE / AUTH ---
import db
import email_service


# --- SESSION MANAGEMENT ---

def init_session():
    """Initialize session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None

def check_auth_status():
    """
    Check for 'token' in query params and verify it.
    """
    # 1. Check for Query Param
    # st.query_params was added in recent Streamlit, otherwise use experimental_get_query_params
    query_params = st.query_params
    token = query_params.get("token")
    
    if token:
        # Verify the token
        result = db.verify_magic_link(token)
        if result and "user" in result:
            st.session_state.authenticated = True
            st.session_state.user_email = result["email"]
            st.success(f"Successfully logged in as {result['email']}!")
            
            # Clear the token from URL
            st.query_params.clear()
            time.sleep(1)
            st.rerun()
        elif result and "error" in result:
            st.error(f"Login failed: {result['error']}")
            st.query_params.clear()

# --- AUTHENTICATION LOGIC ---

def login_page():
    """Display the login form."""
    st.markdown(
        """
        <h1 style='text-align: center;'>🔐 Secret Portal</h1>
        <p style='text-align: center; color: gray;'>Powered by Supabase</p>
        """,
        unsafe_allow_html=True
    )
    
    if not db.get_supabase_client():
        st.error("⚠️ Supabase Credentials (SUPABASE_URL, SUPABASE_KEY) are missing!")
        st.info("Please set them in your environment variables.")
        return

    with st.form("login_form"):
        email = st.text_input("📧 Email Address", placeholder="you@example.com")
        submitted = st.form_submit_button("✨ Send Magic Link", use_container_width=True)
        
        if submitted and email:
            # Create Custom Magic Link
            result = db.create_magic_link(email)
            
            if result and "error" in result:
                st.error(f"Error: {result['error']}")
            elif result and "token" in result:
                token = result["token"]
                # Get App URL from env/secrets or default to localhost
                app_url = os.environ.get("APP_URL")
                if not app_url and "APP_URL" in st.secrets:
                    app_url = st.secrets["APP_URL"]
                if not app_url:
                    app_url = "http://localhost:8501"

                link = f"{app_url}/?token={token}"
                
                # Send Magic Link via Email
                with st.spinner("Sending magic link..."):
                    email_resp = email_service.send_magic_link(email, link)
                
                if email_resp and "error" not in email_resp:
                    print(f"\n[DEV MODE] MAGIC LINK (Backup): {link}\n") # Still print for backup
                    st.success(f"✨ Magic link sent to {email}!")
                    st.info("Check your inbox (and spam folder) for the login link.")
                else:
                    st.error(f"Failed to send email: {email_resp.get('error')}")
                    # Fallback for dev
                    st.warning("Since email failed, here is the link for testing:")
                    st.code(link, language="text")

def april_fools_dashboard():
    """Display the April Fool's dashboard."""
    
    # 1. Prank effects (Only show once per session)
    if not st.session_state.get("prank_shown", False):
        st.balloons()
        st.toast("🎭 You've been pranked!", icon="🃏")
        st.session_state.prank_shown = True
        time.sleep(1)

    # 2. Header
    st.markdown(
        f"""
        <h1 style='text-align: center;'>🎉 Welcome, {st.session_state.user_email}!</h1>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # 3. The Prank Content
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown(
            """
            <div style='
                background: linear-gradient(135deg, #FF6B6B 0%, #556270 100%);
                padding: 2rem;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                color: white;
            '>
                <h2>🃏 APRIL FOOLS! 🃏</h2>
                <p>Authentication secured by Supabase...<br>But the joke is still on you! 😂</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Prank Button
    if st.button("🎁 Claim Your Prize", use_container_width=True):
        st.snow()
        st.error("Error 404: Prize not found! 🤷‍♂️")

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.prank_shown = False
        st.rerun()

# --- MAIN APP ---

def main():
    init_session()
    
    # Sync with Supabase Auth State
    check_auth_status()

    # Router
    if st.session_state.authenticated:
        april_fools_dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()
