# src/core/config_manager.py

import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
        self.config_data = {}
        self.load_config()

    def load_config(self):
        """Loads configuration from the JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding config file {self.config_file}: {e}", file=sys.stderr)
                self.config_data = {}
        else:
            print(f"Config file not found: {self.config_file}. Creating default config.")
            self.save_config() # Create an empty one

    def save_config(self):
        """Saves current configuration to the JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=4)
        except IOError as e:
            print(f"Error saving config file {self.config_file}: {e}", file=sys.stderr)

    def get(self, key, default=None):
        """Gets a configuration value."""
        return self.config_data.get(key, default)

    def set(self, key, value):
        """Sets a configuration value."""
        self.config_data[key] = value
        self.save_config() # Save immediately after setting
