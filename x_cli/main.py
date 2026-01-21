import argparse
import json
from .tweet import post_tweet, get_tweets_by_ids
from .config import prompt_for_credentials, show_config
from .user import (
    get_user_by_id, get_users_by_ids,
    get_user_by_username, get_users_by_usernames,
    AVAILABLE_USER_FIELDS, AVAILABLE_EXPANSIONS, AVAILABLE_TWEET_FIELDS
)

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
    tweet_parser.add_argument('--reply-to', dest='reply_to', type=str, help='Tweet ID or URL to reply to (optional)')
    
    # Get tweets subcommand
    get_parser = subparsers.add_parser('get', help='Get tweets by ID')
    get_parser.add_argument('ids', nargs='+', help='Tweet IDs to retrieve (space separated)')
    get_parser.add_argument('--json', action='store_true', help='Output raw JSON response')
    get_parser.add_argument('--format', choices=['simple', 'detailed'], default='simple', 
                           help='Output format (simple or detailed)')
    
    # User lookup subcommand
    user_parser = subparsers.add_parser('user', help='Look up user information')
    user_parser.add_argument('identifiers', nargs='+', 
                            help='User IDs or usernames to look up (usernames can have @ prefix)')
    user_parser.add_argument('--by-id', action='store_true', 
                            help='Force lookup by ID (default: auto-detect based on format)')
    user_parser.add_argument('--by-username', action='store_true', 
                            help='Force lookup by username (default: auto-detect based on format)')
    user_parser.add_argument('--fields', nargs='+', choices=AVAILABLE_USER_FIELDS,
                            help='User fields to include in response')
    user_parser.add_argument('--expansions', nargs='+', choices=AVAILABLE_EXPANSIONS,
                            help='Data expansions to include')
    user_parser.add_argument('--tweet-fields', nargs='+', choices=AVAILABLE_TWEET_FIELDS,
                            help='Tweet fields to include when expanding tweets')
    user_parser.add_argument('--json', action='store_true', 
                            help='Output raw JSON response')
    user_parser.add_argument('--format', choices=['simple', 'detailed', 'full'], default='simple',
                            help='Output format (simple, detailed, or full)')
    
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
                media_path=args.media,
                reply_to=args.reply_to
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
                    if isinstance(result, dict):
                        format_tweets_output(result, args.format)
                    else:
                        print(f"❌ Failed to get tweets: {result}")
            else:
                print(f"❌ Failed to get tweets: {result}")
                
        except Exception as e:
            print(f"❌ Error getting tweets: {str(e)}")
    
    # Handle user command
    if args.command == 'user':
        try:
            # Determine if we're looking up by ID or username
            identifiers = args.identifiers
            
            # Auto-detect type if not forced
            if not args.by_id and not args.by_username:
                # Check if all identifiers look like IDs (all digits) or usernames
                all_digits = all(ident.isdigit() for ident in identifiers)
                if all_digits:
                    by_id = True
                else:
                    by_id = False
            else:
                by_id = args.by_id
            
            # Perform the lookup
            if len(identifiers) == 1:
                # Single user lookup
                if by_id:
                    success, result = get_user_by_id(
                        identifiers[0],
                        user_fields=args.fields,
                        expansions=args.expansions,
                        tweet_fields=args.tweet_fields
                    )
                else:
                    success, result = get_user_by_username(
                        identifiers[0],
                        user_fields=args.fields,
                        expansions=args.expansions,
                        tweet_fields=args.tweet_fields
                    )
            else:
                # Multiple users lookup
                if by_id:
                    success, result = get_users_by_ids(
                        identifiers,
                        user_fields=args.fields,
                        expansions=args.expansions,
                        tweet_fields=args.tweet_fields
                    )
                else:
                    success, result = get_users_by_usernames(
                        identifiers,
                        user_fields=args.fields,
                        expansions=args.expansions,
                        tweet_fields=args.tweet_fields
                    )
            
            if success:
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    if isinstance(result, dict):
                        format_users_output(result, args.format)
                    else:
                        print(f"❌ Failed to get user(s): {result}")
            else:
                print(f"❌ Failed to get user(s): {result}")
                
        except Exception as e:
            print(f"❌ Error getting user(s): {str(e)}")

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

def format_users_output(data: dict, format_type: str):
    """Format and display user data"""
    if 'data' not in data:
        print("No users found")
        return
    
    # Handle both single user and multiple users response
    users = data['data']
    if isinstance(users, dict):
        users = [users]  # Convert single user to list for uniform handling
    
    # Get expanded tweet data if available
    tweets = {}
    if 'includes' in data and 'tweets' in data['includes']:
        for tweet in data['includes']['tweets']:
            tweets[tweet['id']] = tweet
    
    for user in users:
        if format_type == 'simple':
            print(f"User ID: {user['id']}")
            print(f"Username: @{user['username']}")
            print(f"Name: {user['name']}")
            if 'description' in user:
                print(f"Bio: {user.get('description', '')[:100]}...")
            print("-" * 50)
            
        elif format_type == 'detailed':
            print(f"User ID: {user['id']}")
            print(f"Username: @{user['username']}")
            print(f"Name: {user['name']}")
            
            if 'description' in user:
                print(f"Bio: {user['description']}")
            
            if 'created_at' in user:
                print(f"Joined: {user['created_at']}")
            
            if 'location' in user:
                print(f"Location: {user['location']}")
            
            if 'url' in user:
                print(f"Website: {user['url']}")
            
            if 'public_metrics' in user:
                metrics = user['public_metrics']
                print(f"Followers: {metrics.get('followers_count', 0):,}")
                print(f"Following: {metrics.get('following_count', 0):,}")
                print(f"Tweets: {metrics.get('tweet_count', 0):,}")
                print(f"Listed: {metrics.get('listed_count', 0):,}")
            
            if 'verified' in user and user['verified']:
                print("✓ Verified account")
            
            if 'protected' in user and user['protected']:
                print("🔒 Protected account")
            
            print("-" * 50)
            
        else:  # full
            print("=== User Profile ===")
            print(f"User ID: {user['id']}")
            print(f"Username: @{user['username']}")
            print(f"Name: {user['name']}")
            
            if 'description' in user:
                print(f"\nBio: {user['description']}")
            
            if 'created_at' in user:
                print(f"\nAccount created: {user['created_at']}")
            
            if 'location' in user:
                print(f"Location: {user['location']}")
            
            if 'url' in user:
                print(f"Website: {user['url']}")
            
            if 'profile_image_url' in user:
                print(f"Profile image: {user['profile_image_url']}")
            
            if 'profile_banner_url' in user:
                print(f"Banner image: {user['profile_banner_url']}")
            
            if 'public_metrics' in user:
                print("\n=== Metrics ===")
                metrics = user['public_metrics']
                print(f"Followers: {metrics.get('followers_count', 0):,}")
                print(f"Following: {metrics.get('following_count', 0):,}")
                print(f"Tweets: {metrics.get('tweet_count', 0):,}")
                print(f"Listed: {metrics.get('listed_count', 0):,}")
            
            # Account status
            status_items = []
            if user.get('verified'):
                status_items.append("✓ Verified")
            if user.get('protected'):
                status_items.append("🔒 Protected")
            if user.get('is_identity_verified'):
                status_items.append("🆔 Identity Verified")
            
            if status_items:
                print("\n=== Account Status ===")
                print(" | ".join(status_items))
            
            # Show pinned tweet if expanded
            if 'pinned_tweet_id' in user and user['pinned_tweet_id'] in tweets:
                pinned = tweets[user['pinned_tweet_id']]
                print("\n=== Pinned Tweet ===")
                print(f"ID: {pinned['id']}")
                print(f"Text: {pinned['text']}")
                if 'created_at' in pinned:
                    print(f"Posted: {pinned['created_at']}")
            
            # Show most recent tweet if expanded
            if 'most_recent_tweet_id' in user and user['most_recent_tweet_id'] in tweets:
                recent = tweets[user['most_recent_tweet_id']]
                print("\n=== Most Recent Tweet ===")
                print(f"ID: {recent['id']}")
                print(f"Text: {recent['text']}")
                if 'created_at' in recent:
                    print(f"Posted: {recent['created_at']}")
            
            print("=" * 50)

if __name__ == "__main__":
    main()