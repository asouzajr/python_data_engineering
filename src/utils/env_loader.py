import os
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def load_env_file(env_path: str = ".env") -> None:
    """
    Load environment variables from a .env file into os.environ.

    - Uses only Python standard library
    - Does not overwrite existing environment variables
    - Ignores empty lines and comments
    - Handles quoted values
    - Logs loading summary
    """
    path = Path(env_path)

    if not path.exists():
        logger.info(
            "No .env file found at %s. Skipping environment loading.",
            env_path,
        )
        return

    loaded_count = 0

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # Ignore empty lines and comments
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)

                key = key.strip()
                value = value.strip().strip('"').strip("'")

                # Do not overwrite existing environment variables
                if key not in os.environ:
                    os.environ[key] = value
                    loaded_count += 1

    logger.info(
        "Loaded %s environment variables from %s.",
        loaded_count,
        env_path,
    )
