import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase URL and KEY must be set in the environment variables!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def signup(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return response.user, None
    except Exception as e:
        return None, str(e)

def signin(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response.user, None
    except Exception as e:
        return None, str(e)

def signout():
    try:
        supabase.auth.sign_out()
        return True, None
    except Exception as e:
        return False, str(e)

def get_current_user():
    session = supabase.auth.get_session()
    if session and session.user:
        return session.user
    return None

def send_password_reset_email(email):
    try:
        supabase.auth.reset_password_email(email=email)
        return True, None
    except Exception as e:
        return False, str(e)
