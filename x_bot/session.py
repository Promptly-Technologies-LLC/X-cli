import os
import json
from typing import Optional, Dict, Any
from requests_oauthlib import OAuth2Session
from .auth import create_oauth2_session

def get_sessions_dir() -> str:
    """Get or create the sessions directory."""
    sessions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sessions")
    os.makedirs(sessions_dir, exist_ok=True)
    return sessions_dir

def save_token(user_id: str, token: Dict[str, Any]) -> None:
    """Save a user's token to the tokens file."""
    sessions_dir = get_sessions_dir()
    tokens_path = os.path.join(sessions_dir, "tokens.json")
    
    # Load existing tokens
    tokens = {}
    if os.path.exists(tokens_path):
        try:
            with open(tokens_path, "r") as f:
                tokens = json.load(f)
        except json.JSONDecodeError:
            pass
    
    # Update token for this user
    tokens[user_id] = token
    
    # Save updated tokens
    with open(tokens_path, "w") as f:
        json.dump(tokens, f)

def load_token(user_id: str) -> Optional[Dict[str, Any]]:
    """Load a user's token from the tokens file."""
    sessions_dir = get_sessions_dir()
    tokens_path = os.path.join(sessions_dir, "tokens.json")
    
    if not os.path.exists(tokens_path):
        return None
    
    try:
        with open(tokens_path, "r") as f:
            tokens = json.load(f)
            return tokens.get(user_id)
    except (json.JSONDecodeError, IOError):
        return None

def create_session_from_token(token: Dict[str, Any]) -> OAuth2Session:
    """Create a new OAuth2Session from a token."""
    return create_oauth2_session(token)

def get_user_session(user_id: str) -> tuple[Optional[OAuth2Session], Optional[Dict[str, Any]]]:
    """Get a user's session and token."""
    token = load_token(user_id)
    if token:
        session = create_session_from_token(token)
        return session, token
    return None, None 