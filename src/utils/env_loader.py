import os
from pathlib import Path


def load_env_file(env_path: str = ".env") -> None:
    """
    Load environment variables from a .env file into os.environ.

    Only uses Python standard library.
    """
    path = Path(env_path)

    if not path.exists():
        return

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
