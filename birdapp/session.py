import json
import os
from typing import Any, Dict, Mapping, Optional
from requests_oauthlib import OAuth2Session
from .auth import create_oauth2_session
from .config import get_active_profile

def get_sessions_dir() -> str:
    """Get or create the sessions directory."""
    sessions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sessions")
    os.makedirs(sessions_dir, exist_ok=True)
    return sessions_dir

def _resolve_profile(profile: str | None, tokens: Dict[str, Any]) -> Optional[str]:
    if profile:
        return profile
    active = get_active_profile()
    if active:
        return active
    profiles = tokens.get("profiles")
    if isinstance(profiles, dict) and len(profiles) == 1:
        return next(iter(profiles.keys()))
    return None

def _load_tokens(tokens_path: str) -> Dict[str, Any]:
    if not os.path.exists(tokens_path):
        return {}
    try:
        with open(tokens_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_token(user_id: str, token: Mapping[str, Any], profile: str | None = None) -> None:
    """Save a user's token to the tokens file."""
    sessions_dir = get_sessions_dir()
    tokens_path = os.path.join(sessions_dir, "tokens.json")
    
    tokens = _load_tokens(tokens_path)
    profile_name = _resolve_profile(profile, tokens)
    if profile_name:
        profiles = tokens.get("profiles")
        if not isinstance(profiles, dict):
            profiles = {}
            tokens = {"profiles": profiles}
        profile_tokens = profiles.get(profile_name)
        if not isinstance(profile_tokens, dict):
            profile_tokens = {}
            profiles[profile_name] = profile_tokens
        profile_tokens[user_id] = dict(token)
    else:
        tokens[user_id] = dict(token)
    
    # Save updated tokens
    with open(tokens_path, "w") as f:
        json.dump(tokens, f)

def load_token(user_id: str, profile: str | None = None) -> Optional[Dict[str, Any]]:
    """Load a user's token from the tokens file."""
    sessions_dir = get_sessions_dir()
    tokens_path = os.path.join(sessions_dir, "tokens.json")
    
    tokens = _load_tokens(tokens_path)
    profiles = tokens.get("profiles")
    if isinstance(profiles, dict):
        profile_name = _resolve_profile(profile, tokens)
        if not profile_name:
            return None
        profile_tokens = profiles.get(profile_name)
        if isinstance(profile_tokens, dict):
            return profile_tokens.get(user_id)
        return None
    return tokens.get(user_id)

def create_session_from_token(token: Dict[str, Any]) -> OAuth2Session:
    """Create a new OAuth2Session from a token."""
    return create_oauth2_session(token)

def get_user_session(user_id: str, profile: str | None = None) -> tuple[Optional[OAuth2Session], Optional[Dict[str, Any]]]:
    """Get a user's session and token."""
    token = load_token(user_id, profile=profile)
    if token:
        # Add user ID to token for updater closure
        token['user_id'] = user_id
        session = create_session_from_token(token)
        return session, token
    return None, None 