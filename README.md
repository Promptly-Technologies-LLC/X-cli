# X CLI

A command-line tool for posting tweets to Twitter/X from the command line.

## Setup

This repo uses the `uv` package manager to manage dependencies. If you don't already have `uv` installed, you can install it with the following curl command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

To verify install, use:

```bash
uv --version
```

Consult the [uv installation docs](https://astral.sh/uv/) for more detailed instructions and troubleshooting.

## Installation

You can install the CLI tool globally using uv:

```bash
uv tool install -U git+https://github.com/Promptly-Technologies-LLC/X-cli.git
```

After installation, you can use:

```bash
x-cli config
x-cli tweet --text "Hello world!"
```

## Configuration

### Getting Twitter API Credentials

Before you can use the CLI, you need to configure your Twitter API credentials. To do this, you need to [sign up for a Twitter/X developer account](https://developer.twitter.com/).

In the dashboard, you will need to create an application. Make sure your application has "Read and Write" permissions. From your application's "Keys and Tokens" section in the developer dashboard, generate:

- API Key
- API Secret  
- Access Token
- Access Token Secret

### Setting Up Credentials

Run the configuration command to set up your credentials:

```bash
x-cli config
```

This will prompt you for your Twitter API credentials and store them securely in `~/.config/x-cli/config.json`.

To view your current configuration (without showing secrets):

```bash
x-cli config --show
```

### OAuth2 (User Context)

OAuth2 uses Authorization Code with PKCE. Configure these environment variables:

- `X_OAUTH2_CLIENT_ID`
- `X_OAUTH2_REDIRECT_URI` (must match your app's callback URL)
- `X_OAUTH2_SCOPES` (optional, default: `tweet.read users.read offline.access`)
- `X_OAUTH2_CLIENT_SECRET` (optional, only for confidential clients)

You can set these via the config workflow:

```bash
x-cli config --oauth2
```

To authenticate and store a token:

```bash
x-cli oauth2 login
```

To verify the token:

```bash
x-cli oauth2 whoami
```

For development fixture capture:

```bash
uv run tests/capture_oauth2_fixtures.py
```

## Usage

### Posting Tweets

To post a tweet:

```bash
x-cli tweet --text "Your tweet content here"
```

To post a tweet with media:

```bash
x-cli tweet --text "Check out this image!" --media /path/to/image.jpg
```

To post a media-only tweet (no text):

```bash
x-cli tweet --media /path/to/image.jpg
```

### Replying to Tweets

To reply to a tweet using its ID:

```bash
x-cli tweet --text "Great point!" --reply-to 1234567890
```

To reply to a tweet using its URL:

```bash
x-cli tweet --text "I agree!" --reply-to "https://x.com/user/status/1234567890"
```

You can also include media in replies:

```bash
x-cli tweet --text "Here's my response" --media /path/to/image.jpg --reply-to 1234567890
```

### Getting Tweets

To retrieve tweets by ID (up to 100 at a time):

```bash
x-cli get 1234567890
x-cli get 1234567890 9876543210 --format detailed
x-cli get 1234567890 --json
```

### Looking Up Users

To look up users by username or ID (up to 100 at a time):

```bash
x-cli user elonmusk
x-cli user @nasa @spacex
x-cli user 44196397 --by-id
x-cli user elonmusk --format detailed --fields public_metrics created_at
```

### Importing your tweets from the Twitter Community Archive

If you have shared your tweets with the public via the Twitter Community Archive, you can download them from the archive and import them into a SQLite database for local search and analysis:

```bash
x-cli import-archive --username yourusername
```

If you've already downloaded your archive.json file, you can import it from a local file:

```bash
x-cli import-archive --path /path/to/archive.json
```

### Help

To see all available commands:

```bash
x-cli --help
```

To see help for a specific command:

```bash
x-cli tweet --help
x-cli config --help
x-cli get --help
x-cli user --help
```
