from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from typing import Any, Mapping, NotRequired, Sequence, TypedDict
from urllib.parse import parse_qs, quote, urlencode, urlparse

import requests

from .config import get_credential

OAUTH2_AUTHORIZE_URL = "https://x.com/i/oauth2/authorize"
OAUTH2_TOKEN_URL = "https://api.x.com/2/oauth2/token"
OAUTH2_ME_URL = "https://api.x.com/2/users/me"
DEFAULT_FIXTURES_DIR = os.path.join("tests", "fixtures")

class Token(TypedDict):
    access_token: str
    token_type: str
    expires_in: NotRequired[int]
    refresh_token: NotRequired[str]
    scope: NotRequired[str]

def create_pkce_pair() -> tuple[str, str]:
    """Create (code_verifier, code_challenge) for PKCE (S256)."""
    code_verifier = secrets.token_urlsafe(64)
    verifier_bytes = code_verifier.encode("ascii")
    challenge_bytes = hashlib.sha256(verifier_bytes).digest()
    code_challenge = base64.urlsafe_b64encode(challenge_bytes).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge

def build_authorize_url(
    state: str,
    code_challenge: str,
    scopes: Sequence[str],
    redirect_uri: str,
    client_id: str,
) -> str:
    """Build the OAuth2 authorization URL."""
    scope = " ".join(scopes)
    query = urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        },
        quote_via=quote,
    )
    return f"{OAUTH2_AUTHORIZE_URL}?{query}"

def exchange_code_for_token(
    code: str,
    code_verifier: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str | None = None,
) -> Token:
    """Exchange authorization code for access (and refresh) token."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }

    if client_secret:
        basic = base64.b64encode(f"{client_id}:{client_secret}".encode("ascii")).decode("ascii")
        headers["Authorization"] = f"Basic {basic}"

    response = requests.post(OAUTH2_TOKEN_URL, headers=headers, data=data, timeout=30)
    if not response.ok:
        raise RuntimeError(f"OAuth2 token exchange failed: {response.status_code} {response.text}")

    token = response.json()
    if "access_token" not in token or "token_type" not in token:
        raise RuntimeError("OAuth2 token response missing required fields")
    return token

def refresh_access_token(
    refresh_token: str,
    client_id: str,
    client_secret: str | None = None,
) -> Token:
    """Refresh an access token using a refresh token."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_id": client_id,
    }

    if client_secret:
        basic = base64.b64encode(f"{client_id}:{client_secret}".encode("ascii")).decode("ascii")
        headers["Authorization"] = f"Basic {basic}"

    response = requests.post(OAUTH2_TOKEN_URL, headers=headers, data=data, timeout=30)
    if not response.ok:
        raise RuntimeError(f"OAuth2 refresh failed: {response.status_code} {response.text}")

    token = response.json()
    if "access_token" not in token or "token_type" not in token:
        raise RuntimeError("OAuth2 refresh response missing required fields")
    return token

def get_user_me(access_token: str) -> dict[str, Any]:
    """Fetch the authenticated user's profile via /2/users/me."""
    response = requests.get(
        OAUTH2_ME_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(f"OAuth2 /2/users/me failed: {response.status_code} {response.text}")
    return response.json()

def _redact_secret(value: str) -> str:
    if len(value) <= 10:
        return "REDACTED"
    return f"{value[:4]}REDACTED{value[-4:]}"

def redact_token_for_fixture(token: Mapping[str, Any]) -> dict[str, Any]:
    """Return a redacted token suitable for fixtures."""
    redacted: dict[str, Any] = dict(token)
    if "access_token" in redacted and isinstance(redacted["access_token"], str):
        redacted["access_token"] = _redact_secret(redacted["access_token"])
    if "refresh_token" in redacted and isinstance(redacted["refresh_token"], str):
        redacted["refresh_token"] = _redact_secret(redacted["refresh_token"])
    return redacted

def write_oauth2_fixtures(
    token: Mapping[str, Any],
    user_payload: Mapping[str, Any],
    fixtures_dir: str = DEFAULT_FIXTURES_DIR,
) -> None:
    os.makedirs(fixtures_dir, exist_ok=True)
    token_path = os.path.join(fixtures_dir, "oauth2_token.json")
    user_path = os.path.join(fixtures_dir, "oauth2_user.json")
    with open(token_path, "w") as f:
        json.dump(redact_token_for_fixture(token), f, indent=2)
    with open(user_path, "w") as f:
        json.dump(user_payload, f, indent=2)

def oauth2_login_flow(record_fixtures: bool = False) -> dict[str, Any]:
    """Run the OAuth2 login flow and return the /2/users/me payload."""
    from .session import save_token

    client_id = os.getenv("X_OAUTH2_CLIENT_ID") or get_credential("X_OAUTH2_CLIENT_ID")
    redirect_uri = os.getenv("X_OAUTH2_REDIRECT_URI") or get_credential("X_OAUTH2_REDIRECT_URI")
    raw_scopes = os.getenv("X_OAUTH2_SCOPES") or get_credential("X_OAUTH2_SCOPES")
    client_secret = os.getenv("X_OAUTH2_CLIENT_SECRET") or get_credential("X_OAUTH2_CLIENT_SECRET")

    if not client_id or not redirect_uri:
        raise RuntimeError("Missing X_OAUTH2_CLIENT_ID or X_OAUTH2_REDIRECT_URI")

    scopes = (raw_scopes or "tweet.read users.read offline.access").split()
    state = secrets.token_urlsafe(16)
    code_verifier, code_challenge = create_pkce_pair()

    authorize_url = build_authorize_url(
        state=state,
        code_challenge=code_challenge,
        scopes=scopes,
        redirect_uri=redirect_uri,
        client_id=client_id,
    )
    print("Open this URL in your browser and authorize the app:")
    print(authorize_url)

    redirect_response = input("Paste the full redirect URL here: ").strip()
    parsed = urlparse(redirect_response)
    params = parse_qs(parsed.query)
    returned_state = params.get("state", [None])[0]
    code = params.get("code", [None])[0]

    if not code or returned_state != state:
        raise RuntimeError("Invalid OAuth2 redirect URL (missing code or state mismatch)")

    token = exchange_code_for_token(
        code=code,
        code_verifier=code_verifier,
        redirect_uri=redirect_uri,
        client_id=client_id,
        client_secret=client_secret,
    )

    user_payload = get_user_me(token["access_token"])
    user_id = user_payload.get("data", {}).get("id")
    if not user_id:
        raise RuntimeError("OAuth2 /2/users/me response missing user id")

    save_token(user_id=str(user_id), token=token)
    if record_fixtures:
        write_oauth2_fixtures(token=token, user_payload=user_payload)
    return user_payload

def oauth2_whoami(user_id: str | None = None) -> dict[str, Any]:
    """Return /2/users/me payload using stored token."""
    from .session import get_sessions_dir, load_token

    if user_id:
        token = load_token(user_id)
        if not token:
            raise RuntimeError(f"No OAuth2 token stored for user id {user_id}")
    else:
        sessions_dir = get_sessions_dir()
        tokens_path = os.path.join(sessions_dir, "tokens.json")
        if not os.path.exists(tokens_path):
            raise RuntimeError("No OAuth2 tokens stored. Run `x-cli oauth2 login` first.")

        with open(tokens_path, "r") as f:
            tokens = f.read().strip()
        if not tokens:
            raise RuntimeError("No OAuth2 tokens stored. Run `x-cli oauth2 login` first.")

        tokens_data = json.loads(tokens)
        if not tokens_data:
            raise RuntimeError("No OAuth2 tokens stored. Run `x-cli oauth2 login` first.")

        first_user_id = next(iter(tokens_data.keys()))
        token = tokens_data[first_user_id]

    access_token = token.get("access_token")
    if not access_token:
        raise RuntimeError("Stored OAuth2 token missing access_token")
    return get_user_me(access_token=access_token)
