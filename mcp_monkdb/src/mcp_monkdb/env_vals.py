"""
Configuration of the environment for the MCP MonkDB server. 
This module manages all environment variable settings with appropriate defaults and type conversions.
"""

from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class MonkDBConfiguration:
    """
    This class manages the configuration of environment variables for MonkDB connection settings, 
    incorporating reasonable defaults and type conversions. It offers typed methods for retrieving each 
    configuration value.

    Required environment variables:
        MONKDB_HOST: The host details (ip address or name) of the MonkDB server
        MONKDB_USER: The username required for authentication
        MONKDB_PASSWORD: The password of the above user required for authentication
        MONKDB_PORT: The port number to connect with MonkDB (default is 4200)

    Optional environment variables (with defaults):
        MONKDB_SCHEMA: Default database schema to use which is monkdb.
    """

    def __init__(self):
        """This initializes the config from environment variables."""
        self._validate_mandatory_vars()

    @property
    def host(self) -> str:
        """Get the MonkDB host."""
        return os.environ["MONKDB_HOST"]

    @property
    def port(self) -> int:
        """Get the MonkDB public API port.

        Defaults to 4200.
        Can be overridden by the MONKDB_API_PORT environment variable.
        """
        return int(os.getenv("MONKDB_API_PORT", 4200))

    @property
    def username(self) -> str:
        """Get the MonkDB username."""
        return os.environ["MONKDB_USER"]

    @property
    def password(self) -> str:
        """Get the MonkDB password."""
        return os.environ["MONKDB_PASSWORD"]

    @property
    def schema(self) -> Optional[str]:
        """Get the default schema name if set."""
        return os.getenv("MONKDB_SCHEMA")

    def get_client_config(self) -> dict:
        """Get the config dictionary for MonkDB py sdk/client.

        Returns:
            dict: Config ready to be passed to client.connect()
        """
        connection_url = f"http://{self.username}:{self.password}@{self.host}:{self.port}"
        config = {
            "url": connection_url,
            "username": self.username,
        }

        if self.schema:
            config["schema"] = self.schema

        return config

    def _validate_mandatory_vars(self) -> None:
        """This method validates whether the environment variables are set or not.

        Raises:
            ValueError: If any required environment variable is missing.
        """
        missing_vars = []
        for var in ["MONKDB_HOST", "MONKDB_USER", "MONKDB_PASSWORD", "MONKDB_API_PORT"]:
            if var not in os.environ:
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(
                f"The required environment variables are missing: {', '.join(missing_vars)}")


# Global instance representation for the singleton design pattern
_CONFIG_INSTANCE = None


def get_config():
    """
    This method gets the singleton instance of MonkDBConfiguration.
    It instantiates the instance in the first call.
    """
    global _CONFIG_INSTANCE
    if _CONFIG_INSTANCE is None:
        # Create the configuration object at this point, confirming that load_dotenv() has probably been executed.
        _CONFIG_INSTANCE = MonkDBConfiguration()
    return _CONFIG_INSTANCE
