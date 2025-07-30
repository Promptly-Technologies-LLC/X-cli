import os
import argparse
from dotenv import load_dotenv
from x_cli.auth import create_oauth1_auth
from x_cli.tweet import post_tweet

load_dotenv()

# Initialize OAuth1 authentication
auth = create_oauth1_auth()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="X CLI - Post tweets from the command line")
    parser.add_argument('--text', type=str, help='Tweet text to post', required=True)
    parser.add_argument('--media', type=str, help='Path to media file (optional)')
    args = parser.parse_args()

    # Validate arguments
    if not args.text.strip() and not args.media:
        print("Error: Cannot post empty tweet without media")
        exit(1)

    # Post the tweet
    try:
        success, message = post_tweet(
            text=args.text,
            media_path=args.media
        )
        
        if success:
            print(f"✅ Successfully posted tweet: {message}")
        else:
            print(f"❌ Failed to post tweet: {message}")
            
    except Exception as e:
        print(f"❌ Error posting tweet: {str(e)}")

if __name__ == "__main__":
    main()