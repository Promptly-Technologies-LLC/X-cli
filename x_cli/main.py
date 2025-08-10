import os
import argparse
import json
from .auth import create_oauth1_auth
from .tweet import post_tweet, get_tweets_by_ids
from .config import prompt_for_credentials, show_config

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
    
    # Get tweets subcommand
    get_parser = subparsers.add_parser('get', help='Get tweets by ID')
    get_parser.add_argument('ids', nargs='+', help='Tweet IDs to retrieve (space separated)')
    get_parser.add_argument('--json', action='store_true', help='Output raw JSON response')
    get_parser.add_argument('--format', choices=['simple', 'detailed'], default='simple', 
                           help='Output format (simple or detailed)')
    
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
    
    # Handle get command
    if args.command == 'get':
        try:
            success, result = get_tweets_by_ids(args.ids)
            
            if success:
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    format_tweets_output(result, args.format)
            else:
                print(f"❌ Failed to get tweets: {result}")
                
        except Exception as e:
            print(f"❌ Error getting tweets: {str(e)}")

def format_tweets_output(data: dict, format_type: str):
    """Format and display tweet data"""
    if 'data' not in data:
        print("No tweets found")
        return
    
    tweets = data['data']
    users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
    
    for tweet in tweets:
        author_id = tweet.get('author_id')
        author = users.get(author_id, {})
        
        if format_type == 'simple':
            print(f"Tweet ID: {tweet['id']}")
            print(f"Author: @{author.get('username', 'unknown')} ({author.get('name', 'Unknown')})")
            print(f"Text: {tweet['text']}")
            print(f"Created: {tweet.get('created_at', 'unknown')}")
            print("-" * 50)
        else:  # detailed
            print(f"Tweet ID: {tweet['id']}")
            print(f"Author: @{author.get('username', 'unknown')} ({author.get('name', 'Unknown')})")
            print(f"Text: {tweet['text']}")
            print(f"Created: {tweet.get('created_at', 'unknown')}")
            print(f"Language: {tweet.get('lang', 'unknown')}")
            
            if 'public_metrics' in tweet:
                metrics = tweet['public_metrics']
                print(f"Likes: {metrics.get('like_count', 0)}")
                print(f"Retweets: {metrics.get('retweet_count', 0)}")
                print(f"Replies: {metrics.get('reply_count', 0)}")
                print(f"Quotes: {metrics.get('quote_count', 0)}")
            
            if author.get('verified'):
                print("✓ Verified account")
            
            print("-" * 50)

if __name__ == "__main__":
    main()