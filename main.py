import os
import argparse
from x_cli.auth import create_oauth1_auth
from x_cli.tweet import post_tweet
from x_cli.config import prompt_for_credentials, show_config

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="X CLI - Post tweets from the command line")
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)
    
    # Config subcommand
    config_parser = subparsers.add_parser('config', help='Configure Twitter API credentials')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    
    # Tweet subcommand
    tweet_parser = subparsers.add_parser('tweet', help='Post a tweet')
    tweet_parser.add_argument('--text', type=str, help='Tweet text to post (optional if media provided)', default="")
    tweet_parser.add_argument('--media', type=str, help='Path to media file (optional)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle config command
    if args.command == 'config':
        if args.show:
            show_config()
        else:
            prompt_for_credentials()
        return
    
    # Handle tweet command
    if args.command == 'tweet':
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