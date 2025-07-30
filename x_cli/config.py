import os
import json
import getpass
from pathlib import Path
from typing import Dict, Optional

def get_config_path() -> Path:
    """Get the path to the user-level config file."""
    config_dir = Path.home() / ".config" / "x-cli"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"

def load_config() -> Dict[str, str]:
    """Load configuration from the user-level config file."""
    config_path = get_config_path()
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_config(config: Dict[str, str]) -> None:
    """Save configuration to the user-level config file."""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure permissions (read/write for owner only)
        os.chmod(config_path, 0o600)
    except IOError as e:
        raise RuntimeError(f"Failed to save config: {e}")

def get_credential(key: str) -> Optional[str]:
    """Get a credential from the config file."""
    config = load_config()
    return config.get(key)

def prompt_for_credentials() -> None:
    """Prompt user for Twitter API credentials and save them."""
    print("X CLI Configuration")
    print("==================")
    print("Please enter your Twitter API credentials.")
    print("You can get these from https://developer.twitter.com/")
    print("(Sensitive fields will be hidden as you type)")
    print()
    
    credentials = {}
    
    # Prompt for each credential (hide sensitive fields)
    credentials['X_API_KEY'] = getpass.getpass("API Key: ").strip()
    credentials['X_API_SECRET'] = getpass.getpass("API Secret: ").strip()
    credentials['X_ACCESS_TOKEN'] = getpass.getpass("Access Token: ").strip()
    credentials['X_ACCESS_TOKEN_SECRET'] = getpass.getpass("Access Token Secret: ").strip()
    credentials['X_USERNAME'] = input("Username (without @): ").strip()
    
    # Validate that all fields are filled
    missing = [key for key, value in credentials.items() if not value]
    if missing:
        print(f"\nError: Missing required fields: {', '.join(missing)}")
        return
    
    # Save the configuration
    try:
        save_config(credentials)
        config_path = get_config_path()
        print(f"\n✅ Configuration saved to {config_path}")
        print("You can now use the CLI to post tweets!")
    except RuntimeError as e:
        print(f"\n❌ {e}")

def show_config() -> None:
    """Show current configuration (without secrets)."""
    config = load_config()
    if not config:
        print("No configuration found. Run 'x-cli config' to set up credentials.")
        return
    
    print("Current configuration:")
    print(f"  Username: {config.get('X_USERNAME', 'Not set')}")
    print(f"  API Key: {'*' * len(config.get('X_API_KEY', '')) if config.get('X_API_KEY') else 'Not set'}")
    print(f"  API Secret: {'*' * len(config.get('X_API_SECRET', '')) if config.get('X_API_SECRET') else 'Not set'}")
    print(f"  Access Token: {'*' * len(config.get('X_ACCESS_TOKEN', '')) if config.get('X_ACCESS_TOKEN') else 'Not set'}")
    print(f"  Access Token Secret: {'*' * len(config.get('X_ACCESS_TOKEN_SECRET', '')) if config.get('X_ACCESS_TOKEN_SECRET') else 'Not set'}")