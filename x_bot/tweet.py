import logging
import requests
from .media import create_media_payload

logger = logging.getLogger("uvicorn.error")

def create_text_payload(text: str) -> dict[str, str]:
    return {"text": text}

def create_tweet_payload(text: str, media_path: str | None = None) -> dict:
    text_payload = create_text_payload(text=text)
    if media_path is None:
        return text_payload
    media_payload = create_media_payload(path=media_path)
    return {**text_payload, **media_payload}

def post_tweet(text: str, media_path: str | None = None, new_token: dict | None = None) -> requests.Response:
    if not new_token:
        raise ValueError("Token is required")
        
    tweet_payload = create_tweet_payload(text=text, media_path=media_path)
    logger.info(f"Posting tweet with payload: {tweet_payload}")
    
    return requests.request(
        method="POST",
        url="https://api.x.com/2/tweets",
        json=tweet_payload,
        headers={
            "Authorization": f"Bearer {new_token['access_token']}",
            "Content-Type": "application/json",
        },
    )
