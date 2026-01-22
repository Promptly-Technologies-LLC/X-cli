# Birdapp: a Twitter/X CLI tool

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
uv tool install -U git+https://github.com/Promptly-Technologies-LLC/birdapp.git
```

After installation, you can use:

```bash
birdapp auth config
birdapp tweet --text "Hello world!"
```

## Configuration

### Getting Twitter API Credentials

Before you can use the CLI, you need to configure your Twitter API credentials. To do this, you need to [sign up for a Twitter/X developer account](https://developer.twitter.com/).

In the dashboard, you will need to create an application. Make sure your application has "Read and Write" permissions. From your application's "Keys and Tokens" section in the developer dashboard, generate:

- API Key
- API Secret  
- Access Token
- Access Token Secret

### Profiles

Birdapp stores credentials by username profile. Each profile is keyed by the X username
(without `@`).

How profiles are created:
- OAuth1: created when you run `birdapp auth config --oauth1` and enter a username.
- OAuth2: created when you run `birdapp auth login` (the username comes from the login).

How profiles are selected:
- The active profile is set by `birdapp profile use <username>`.
- `--profile <username>` overrides the active profile for a single command.

Commands:
```bash
birdapp auth config --oauth1          # creates/updates profile after you enter a username
birdapp auth config --oauth2          # configures shared OAuth2 app credentials
birdapp auth login                    # creates/updates profile after OAuth2 login
birdapp profile list
birdapp profile use yourusername
birdapp profile show yourusername
```

### Setting Up Credentials

Run the configuration command to set up your credentials:

```bash
birdapp auth config --oauth1 # or --oauth2
```

Required:
- OAuth1: run `birdapp auth config --oauth1` per profile.
- OAuth2: run `birdapp auth config --oauth2` once, then `birdapp auth login` per account.
- Choose OAuth1 or OAuth2 based on your app registration and security posture.

Optional:
- Use `--profile <username>` to configure a specific profile without switching.

This will prompt you for your Twitter API credentials and store them securely in
`~/.config/birdapp/config.json`.

To view your current configuration (without showing secrets):

```bash
birdapp auth config --show
```

### Auth Flows

Birdapp supports both OAuth1 and OAuth2. Choose based on your security posture and how
your X app is registered.

OAuth1:
- Required: `birdapp auth config --oauth1`
- Optional: None (no separate login step)
- Stores app key/secret and user access token/secret locally.
- Best when you want direct user tokens and minimal steps.

OAuth2 (Authorization Code with PKCE):
- Required: `birdapp auth config --oauth2` (app config), then `birdapp auth login` (profile creation)
- Optional: `birdapp auth whoami` to verify the token
- Tokens are stored per profile and user id (multiple accounts supported).
- `auth whoami` uses the active profile unless `--profile` or `--user-id` is provided.
- If `X_OAUTH2_CLIENT_SECRET` is set, the client behaves as confidential; otherwise it
  uses public PKCE and avoids storing an app secret. The user experience is the same for both flows, but you may need to use the confidential flow if you registered your app as confidential.

### OAuth2 (User Context)

OAuth2 uses Authorization Code with PKCE. Configure these environment variables:

- `X_OAUTH2_CLIENT_ID`
- `X_OAUTH2_REDIRECT_URI` (must match your app's callback URL)
- `X_OAUTH2_SCOPES` (optional, default: `tweet.read users.read offline.access`)
- `X_OAUTH2_CLIENT_SECRET` (optional, only for confidential clients)

You can set these via the config workflow:

```bash
birdapp auth config --oauth2
```

Required:
- `birdapp auth config --oauth2` (shared app config)
- `birdapp auth login` (creates the profile and stores tokens)

Optional:
- `birdapp auth whoami`

To authenticate and store a token:

```bash
birdapp auth login
```

To verify the token:

```bash
birdapp auth whoami
```

For development fixture capture:

```bash
uv run tests/capture_oauth2_fixtures.py
```

## Usage

### Posting Tweets

To post a tweet:

```bash
birdapp tweet --text "Your tweet content here"
```

To post a tweet with media:

```bash
birdapp tweet --text "Check out this image!" --media /path/to/image.jpg
```

To post a media-only tweet (no text):

```bash
birdapp tweet --media /path/to/image.jpg
```

### Replying to Tweets

To reply to a tweet using its ID:

```bash
birdapp tweet --text "Great point!" --reply-to 1234567890
```

To reply to a tweet using its URL:

```bash
birdapp tweet --text "I agree!" --reply-to "https://x.com/user/status/1234567890"
```

You can also include media in replies:

```bash
birdapp tweet --text "Here's my response" --media /path/to/image.jpg --reply-to 1234567890
```

### Getting Tweets

To retrieve tweets by ID (up to 100 at a time):

```bash
birdapp get 1234567890
birdapp get 1234567890 9876543210 --format detailed
birdapp get 1234567890 --json
```

### Looking Up Users

To look up users by username or ID (up to 100 at a time):

```bash
birdapp user elonmusk
birdapp user @nasa @spacex
birdapp user 44196397 --by-id
birdapp user elonmusk --format detailed --fields public_metrics created_at
```

### Importing your tweets from the Twitter Community Archive

If you have shared your tweets with the public via the Twitter Community Archive, you can download them from the archive and import them into a SQLite database for local search and analysis:

```bash
birdapp import-archive --username yourusername
```

If you've already downloaded your archive.json file, you can import it from a local file:

```bash
birdapp import-archive --path /path/to/archive.json
```

### Help

To see all available commands:

```bash
birdapp --help
```

To see help for a specific command:

```bash
birdapp tweet --help
birdapp auth --help
birdapp get --help
birdapp user --help
```
