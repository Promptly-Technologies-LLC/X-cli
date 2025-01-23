import base64
import hashlib
import os
import secrets
import time
from typing import Dict, Any, Optional
from requests_oauthlib import OAuth1, OAuth2Session
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

# Define the scopes needed for the OAuth2 flow
SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access", "media.write"]

def generate_code_verifier() -> str:
    """Generates a random code verifier string."""
    return secrets.token_urlsafe(100)

def generate_code_challenge(code_verifier: str) -> str:
    """Generates the code challenge from the code verifier."""
    code_challenge: bytes = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge_b64: str = base64.urlsafe_b64encode(code_challenge).decode()
    return code_challenge_b64.rstrip("=")

def create_oauth1_auth() -> OAuth1:
    """Create OAuth1 authentication object for media uploads."""
    return OAuth1(
        os.environ.get("X_API_KEY"),
        os.environ.get("X_API_SECRET"),
        os.environ.get("X_ACCESS_TOKEN"),
        os.environ.get("X_ACCESS_TOKEN_SECRET")
    )

def is_token_expired(token: Dict[str, Any]) -> bool:
    """Check if the token is expired or about to expire (within 5 minutes)."""
    if not token or 'expires_at' not in token:
        return True
    
    # Add 5 minute buffer
    return token['expires_at'] <= time.time() + 300

def create_oauth2_session(token: Optional[Dict[str, Any]] = None) -> OAuth2Session:
    """
    Create an OAuth2 session for tweet posting. 
    If 'token' is provided, the session can manage refresh automatically.
    """
    client_id = os.environ.get("X_CLIENT_ID")
    client_secret = os.environ.get("X_CLIENT_SECRET")
    redirect_uri = os.environ.get("X_REDIRECT_URI")

    def token_updater(token: Dict[str, Any]) -> None:
        """Callback to save refreshed token."""
        from x_twitter_api_v2_demo.session import save_session
        # Note: We need to get the current session from the app context
        # This is a bit of a hack, but it works for our simple case
        save_session(session, token)  # type: ignore # session is defined after this function

    session = OAuth2Session(
        client_id=client_id,
        token=token,
        scope=SCOPES,
        redirect_uri=redirect_uri,
        auto_refresh_url="https://api.x.com/2/oauth2/token",
        auto_refresh_kwargs={
            "client_id": client_id,
            "client_secret": client_secret,
        },
        token_updater=token_updater if token else None
    )

    return session