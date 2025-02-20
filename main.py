import os
import requests
from dotenv import load_dotenv
import base64
from urllib.parse import urlencode, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from typing import Dict, Optional, Tuple
from x_bot.auth import (
    create_oauth1_auth,
    initialize_oauth_flow,
    exchange_code_for_token,
    refresh_token_if_needed,
    create_oauth2_session
)
from x_bot.tweet import post_tweet
from x_bot.session import save_token

load_dotenv()

# --- Configuration ---
# Twitter API credentials (replace with your own keys and tokens)
CONSUMER_KEY = os.environ.get("X_API_KEY")
CONSUMER_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")
CLIENT_ID = os.environ.get("X_CLIENT_ID")
CLIENT_SECRET = os.environ.get("X_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:5000/oauth/callback"  # Replace with your actual redirect URI
SCOPES = "tweet.read tweet.write users.read offline.access media.write" # Add other scopes as needed
AUTHORIZATION_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.x.com/2/oauth2/token"
TWEET_URL = "https://api.x.com/2/tweets"
MEDIA_URL = "https://api.twitter.com/2/media/upload"

# Initialize OAuth1 authentication
auth = create_oauth1_auth()  # Replaces manual OAuth1 initialization

# --- New Helper to reduce repetitive code when applying auth ---
def _apply_auth_if_confidential(headers: Dict[str, str], data: Dict[str, str]) -> None:
    """
    Applies Basic Auth headers and removes 'client_id' from the data if 
    CLIENT_SECRET is present (confidential client).
    """
    if CLIENT_SECRET:
        auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        headers["Authorization"] = f"Basic {auth_str}"
        # 'client_id' is not needed in the POST body for confidential clients
        data.pop("client_id", None)

# --- Helper Functions ---
def create_authorization_url(code_challenge: str, state: str) -> str:
    """Constructs the authorization URL."""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{AUTHORIZATION_URL}?{urlencode(params)}"

def get_access_token(auth_code: str, code_verifier: str) -> Dict[str, str]:
    """
    Exchanges the authorization code for an access token.
    Returns a dict containing the new token data.
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "code": auth_code,
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID or "",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    }
    # Use the helper to apply Basic Auth if needed
    _apply_auth_if_confidential(headers, data)
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()

def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    """
    Refreshes the access token using the refresh token.
    Returns a dict containing the refreshed token data.
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID or "",
    }
    # Use the helper to apply Basic Auth if needed
    _apply_auth_if_confidential(headers, data)
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()

# --- HTTP Server Handler ---
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/oauth/callback'):
            query_params = parse_qs(self.path[self.path.find('?') + 1:])
            auth_code = query_params.get('code', [None])[0]
            returned_state = query_params.get('state', [None])[0]
            
            if auth_code and returned_state:
                self.server.auth_code = auth_code # type: ignore
                self.server.returned_state = returned_state # type: ignore
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><head><title>Authorization Successful</title></head><body><h1>Authorization Successful</h1><p>You can close this window.</p></body></html>")
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><head><title>Authorization Failed</title></head><body><h1>Authorization Failed</h1><p>Invalid parameters.</p></body></html>")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><head><title>Not Found</title></head><body><h1>Not Found</h1></body></html>")

class MyHTTPServer(HTTPServer):
    def __init__(self, server_address: tuple[str, int], RequestHandlerClass: type[BaseHTTPRequestHandler]):
        super().__init__(server_address, RequestHandlerClass)
        self.auth_code: Optional[str] = None
        self.returned_state: Optional[str] = None

def start_oauth_server() -> Tuple[str, Optional[str]]:
    """
    Creates and starts the OAuth HTTP server in a separate thread.
    Returns (auth_code, returned_state) once it's available.
    """
    server_address = ('127.0.0.1', 5000)
    httpd = MyHTTPServer(server_address, OAuthCallbackHandler)

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Wait for the authorization code
    while httpd.auth_code is None:
        pass

    auth_code = httpd.auth_code # type: ignore
    returned_state = httpd.returned_state # type: ignore
    httpd.shutdown()
    return auth_code, returned_state

# --- Updated Main Flow ---
if __name__ == "__main__":
    # 1. Initialize OAuth flow using auth.py helper
    twitter_session, code_verifier, auth_url, state = initialize_oauth_flow()
    print(f"Please visit this URL to authorize the app:\n{auth_url}")

    # 2. Start the HTTP server in a separate thread
    auth_code, returned_state = start_oauth_server()
    print("Authorization code received.")

    # 3. Validate state
    if returned_state != state:
        raise Exception("State does not match")

    # 4. Exchange authorization code for token using auth.py helper
    try:
        token_response = exchange_code_for_token(twitter_session, auth_code, code_verifier)
        if not token_response:
            raise Exception("Failed to obtain access token")
            
        # Create a proper session with the new token
        session = create_oauth2_session(token_response)
        
        # Check and refresh token if needed using auth.py helper
        new_token = refresh_token_if_needed(session, token_response)
        if new_token:
            token_response = new_token
            
        print("Successfully obtained access token.")
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining access token: {e}")
        exit()

    # After obtaining the token_response
    user_id = "default_user"  # In real app, get from user system
    save_token(user_id, token_response)
    
    # When loading token (for subsequent runs)
    # token_response = load_token(user_id)

    # 6. Prompt user for tweet text and media path
    tweet_text = input("Enter your tweet message: ")
    media_path = input("Enter the path to your media file (or leave empty for no media): ").strip() or None

    # 7. Post the tweet using the unified function
    try:
        # Use media.py helper instead of direct media upload
        success, message = post_tweet(
            text=tweet_text,
            media_path=media_path,
            new_token=token_response
        )
        
        if success:
            print(f"✅ Success: {message}")
        else:
            print(f"❌ Error: {message}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")