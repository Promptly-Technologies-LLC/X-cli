import os
from requests_oauthlib import OAuth1

def create_oauth1_auth() -> OAuth1:
    """Create OAuth1 authentication object for Twitter API requests."""
    required_vars = [
        ("X_API_KEY", os.environ.get("X_API_KEY")),
        ("X_API_SECRET", os.environ.get("X_API_SECRET")),
        ("X_ACCESS_TOKEN", os.environ.get("X_ACCESS_TOKEN")),
        ("X_ACCESS_TOKEN_SECRET", os.environ.get("X_ACCESS_TOKEN_SECRET"))
    ]
    
    missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            "Please check your .env file and ensure all Twitter API credentials are set."
        )
    
    return OAuth1(
        required_vars[0][1],  # X_API_KEY
        required_vars[1][1],  # X_API_SECRET
        required_vars[2][1],  # X_ACCESS_TOKEN
        required_vars[3][1]   # X_ACCESS_TOKEN_SECRET
    )