import os
import logging
import requests
from typing import Optional, Dict, Any, Tuple
from .media import create_media_payload
from .auth import create_oauth1_auth
from .config import get_credential

logger = logging.getLogger(__name__)

def create_text_payload(text: str) -> dict[str, str]:
    return {"text": text}

def create_tweet_payload(text: str, media_path: str | None = None) -> dict:
    payload = {}
    
    # Add text if provided and not empty
    if text and text.strip():
        payload.update(create_text_payload(text=text))
    
    # Add media if provided
    if media_path:
        media_payload = create_media_payload(path=media_path)
        payload.update(media_payload)
    
    return payload

def construct_tweet_link(tweet_id: str) -> str:
    """Construct the tweet link from the username and tweet ID."""
    username = get_credential("X_USERNAME")
    if not username:
        return f"https://x.com/status/{tweet_id}"
    return f"https://x.com/{username}/status/{tweet_id}"


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

def submit_tweet(text: str, media_path: str | None = None) -> requests.Response:
    """
    Post a tweet with optional media using OAuth1 authentication.
    Returns the raw response object.
    """
    tweet_payload = create_tweet_payload(text=text, media_path=media_path)
    logger.info(f"Posting tweet with payload: {tweet_payload}")
    
    auth = create_oauth1_auth()
    return requests.request(
        method="POST",
        url="https://api.x.com/2/tweets",
        json=tweet_payload,
        auth=auth,
        headers={
            "Content-Type": "application/json",
        },
    )

def post_tweet(text: str, media_path: str | None = None) -> tuple[bool, str]:
    """
    Post a tweet with optional media using OAuth1 authentication.
    Returns (success, message) tuple.
    """
    try:
        response = submit_tweet(text=text, media_path=media_path)
        return handle_tweet_response(response)
    except Exception as e:
        logger.error("Error posting tweet: %s", str(e))
        return False, f"Error posting tweet: {str(e)}"

def get_tweets_by_ids(tweet_ids: list[str]) -> tuple[bool, str | dict]:
    """
    Retrieve tweets by their IDs using the X API.
    Returns (success, result) tuple where result is either error message or tweet data.
    """
    if not tweet_ids:
        return False, "No tweet IDs provided"
    
    if len(tweet_ids) > 100:
        return False, "Too many tweet IDs provided (maximum 100)"
    
    try:
        auth = create_oauth1_auth()
        ids_param = ",".join(tweet_ids)
        
        response = requests.get(
            url="https://api.x.com/2/tweets",
            params={
                "ids": ids_param,
                "tweet.fields": "created_at,author_id,public_metrics,context_annotations,lang,possibly_sensitive",
                "expansions": "author_id",
                "user.fields": "name,username,verified,public_metrics"
            },
            auth=auth
        )
        
        if response.ok:
            data = response.json()
            logger.info("Successfully retrieved tweets")
            return True, data
        else:
            try:
                error_details = response.json()
                if 'errors' in error_details:
                    error_messages = [error['detail'] for error in error_details['errors']]
                    error_msg = '; '.join(error_messages)
                else:
                    error_msg = f"Error ({response.status_code}): {response.reason}"
                logger.error("Failed to retrieve tweets: %s", error_msg)
                return False, error_msg
            except ValueError:
                error_msg = f"Error ({response.status_code}): {response.reason}"
                logger.error("Failed to parse error response: %s", response.text)
                return False, error_msg
                
    except Exception as e:
        logger.error("Error retrieving tweets: %s", str(e))
        return False, f"Error retrieving tweets: {str(e)}"
