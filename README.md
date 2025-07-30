# X CLI

A command-line tool for generating and posting tweets using LLMs and the Twitter/X API.

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

## Configuration

### Getting an API key and secret

Before you can run the app, you need to configure your Twitter API credentials. To do this, you need to [sign up for a Twitter/X developer account](https://developer.twitter.com/).

In the dashboard, you will need to create an application. Make sure your application has "Read and Write" permissions. From your application's "Keys and Tokens" section in the developer dashboard, generate an api key, api secret, access token, and access token secret. Save these credentials to your `.env` file.

## Usage

Once you have configured your environment and obtained the necessary API credentials, you can use the CLI to post or generate tweets.

### Installation

After setting up dependencies, you can install the CLI tool:

```bash
uv tool install git+https://github.com/Promptly-Technologies-LLC/X_cli.git
```

This will install the `x-cli` command globally.

### Command Line Options

To run the CLI, use:

```bash
x-cli [options]
```

#### Options

- `--text`: The text of the tweet to post.
  
  Example:
  ```bash
  x-cli --text "Hello world!"
  ```

- `--media`: The path to a media file to include in the tweet. This is optional.

  Example:
  ```bash
  x-cli --media /path/to/image.jpg
  ```

#### Example Usage

To post a single tweet:

```bash
x-cli --text "I'm tweeiting this from the command-line!"
```

To post a tweet with an image:

```bash
x-cli --text "Check out this cool image!" --media /path/to/image.jpg
```

Ensure that your `.env` file is correctly set up with your API credentials before running these commands.
