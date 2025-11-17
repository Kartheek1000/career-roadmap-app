import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
if not FIREBASE_API_KEY:
    raise RuntimeError("Firebase API KEY must be set in the environment variables!")

FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

def signup(email, password):
    try:
        url = f"{FIREBASE_AUTH_URL}:signUp?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        data = response.json()
        if "error" in data:
            return None, data['error']['message']
        return data, None
    except Exception as e:
        return None, str(e)

def signin(email, password):
    try:
        url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        data = response.json()
        if "error" in data:
            return None, data['error']['message']
        return data, None
    except Exception as e:
        return None, str(e)

def send_password_reset_email(email):
    try:
        url = f"{FIREBASE_AUTH_URL}:sendOobCode?key={FIREBASE_API_KEY}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        response = requests.post(url, json=payload)
        data = response.json()
        if "error" in data:
            return False, data['error']['message']
        return True, None
    except Exception as e:
        return False, str(e)

# Firebase does not provide a true 'sign out' endpoint because sign out is client-side:
def signout():
    # In a web or mobile app, delete tokens/local storage to sign out.
    # Here, return True to indicate this action must be handled by the client.
    return True, None

# To get the current user, you need to keep/store the idToken from signin.
# For serverless or stateless apps, this is typically handled by the frontend.
def get_current_user(id_token):
    # Verify ID token with Firebase Admin SDK or Google endpoint if needed (not shown here).
    # In practice, you verify tokens when needed for protected endpoints.
    # You'd need to implement this verification.
    pass
