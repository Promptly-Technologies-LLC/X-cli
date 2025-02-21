import os
import logging
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Tuple
from .media import create_media_payload

load_dotenv()

logger = logging.getLogger(__name__)

def create_text_payload(text: str) -> dict[str, str]:
    return {"text": text}

def create_tweet_payload(text: str, media_path: str | None = None) -> dict:
    text_payload = create_text_payload(text=text)
    if media_path is None:
        return text_payload
    media_payload = create_media_payload(path=media_path)
    return {**text_payload, **media_payload}

def construct_tweet_link(tweet_id: str) -> str:
    """Construct the tweet link from the username and tweet ID."""
    return f"https://x.com/{os.getenv("X_USERNAME")}/status/{tweet_id}"


def handle_tweet_response(response: requests.Response) -> tuple[bool, str]:
    """
    Handle the response from posting a tweet.
    Returns (success, message) tuple where:
    - success: Boolean indicating if the tweet was posted successfully
    - message: A user-friendly message describing the result
    """
    if response.ok:
        tweet_id = response.json().get("data", {}).get("id", "")
        tweet_link = construct_tweet_link(tweet_id=tweet_id)
        logger.info("Successfully posted tweet: %s", tweet_link)
        return True, f"Tweet posted successfully! View it at: {tweet_link}"

    try:
        error_details = response.json()
        if 'errors' in error_details:
            error_messages = [error['message'] for error in error_details['errors']]
            error_msg = '; '.join(error_messages)
            logger.error("Twitter API errors: %s", error_messages)
        else:
            status_code = response.status_code
            if status_code == 429:
                error_msg = "Rate limit exceeded. Please wait a few minutes and try again."
            else:
                detail = error_details.get('detail') or error_details.get('title') or response.reason
                error_msg = f"Error ({status_code}): {detail}"
                logger.error("API error %d: %s", status_code, detail)
    except ValueError:
        error_msg = f"Error ({response.status_code}): {response.reason}"
        logger.error("Failed to parse error response: %s", response.text)
    
    logger.error("Failed to post tweet: %s", error_msg)
    return False, f"Failed to post tweet: {error_msg}"

def submit_tweet(text: str, media_path: str | None = None, new_token: Dict[str, Any] | None = None) -> requests.Response:
    """
    Post a tweet with optional media.
    Returns the raw response object.
    """
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

def post_tweet(text: str, media_path: str | None = None, new_token: Dict[str, Any] | None = None) -> tuple[bool, str]:
    """
    Post a tweet with optional media.
    Returns (success, message) tuple.
    """
    try:
        response = submit_tweet(text=text, media_path=media_path, new_token=new_token)
        return handle_tweet_response(response)
    except Exception as e:
        logger.error("Error posting tweet: %s", str(e))
        return False, f"Error posting tweet: {str(e)}"
