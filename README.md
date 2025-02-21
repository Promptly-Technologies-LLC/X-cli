# Twitter/X Bot

Goal: experiment with social media automation to explore business and marketing opportunities for Promptly Technologies in this space.

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

Once uv is installed on your system, clone this repo with:

```bash
git clone https://github.com/Promptly-Technologies-LLC/X_bot
```

Then:

1. Navigate to the cloned directory with `cd X_bot`.
2. Install dependencies with `uv sync`.
3. Copy the `example.env` file to `.env` with `cp example.env .env`.
4. Edit the `.env` file and add your API key, API secret, client token, client secret, access token, and access secret (for instructions on how to get these, see below).

## Configuration

### Getting an API key and secret

Before you can run the app, you need to configure your Twitter API credentials. To do this, you need to [sign up for a Twitter/X developer account](https://developer.twitter.com/). Upon creating your account, you will receive an API key and an API secret. Save these in your `.env` file. 

### Getting a client token and secret

Next, create a new project and application from the developer dashboard. Then, from the application settings, do your user authentication setup. Give your application "Read and Write" permissions, classify it as a "Web App", and set the Callback URI to "http://127.0.0.1:5000/oauth/callback". Enter any URL you like for the required "Website" field; this won't affect our application. Upon saving these settings, you will be provided a client token and secret, which you should save to your `.env` file.

### Getting an access token and secret

You will also need to generate an access token and secret from your application's "Keys and Tokens" section in the developer dashboard. Save these to your `.env` file.

## Usage

Once you have configured your environment and obtained the necessary API credentials, you can use the CLI interface to generate and post tweets. The CLI provides several options to customize your tweet generation and posting process.

### Command Line Interface (CLI) Options

To run the bot, use the following command:

```bash
python main.py [options]
```

#### Options

- `--prompt`: A custom prompt for tweet generation. If not provided, a default prompt will be used.
  
  Example:
  ```bash
  python main.py --prompt "Hello world!"
  ```

- `--n`: The number of tweets to generate and post. The default is 1.

  Example:
  ```bash
  python main.py --n 3
  ```

- `--media`: The path to a media file to include in the tweet. This is optional.

  Example:
  ```bash
  python main.py --media /path/to/image.jpg
  ```

#### Example Usage

To generate and post a single tweet with a custom prompt:

```bash
uv run python main.py --prompt "Exploring the world of AI and automation!"
```

To generate and post three tweets without a custom prompt:

```bash
uv run python main.py --n 3
```

To post a tweet with an image:

```bash
uv run python main.py --prompt "Check out this cool image!" --media /path/to/image.jpg
```

Ensure that your `.env` file is correctly set up with your API credentials before running these commands.
