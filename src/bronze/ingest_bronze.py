import json
import logging
import os
from pathlib import Path
from datetime import datetime, UTC
from src.utils.env_loader import load_env_file


# Configure logging with ISO 8601 format including milliseconds
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)


def read_json_file(file_path: str) -> dict:
    """
    Read a JSON file from a local path and return it as a dictionary.

    :param file_path: Path to the input JSON file
    :return: Parsed JSON content as dictionary
    """
    logger.info("Reading JSON file from %s", file_path)

    if not Path(file_path).exists():
        logger.error("File not found: %s", file_path)
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    logger.info("JSON file loaded successfully.")
    return data


def save_bronze_file(data: dict, output_path: str) -> None:
    """
    Save raw JSON data into the Bronze layer.

    :param data: Dictionary containing raw data
    :param output_path: Path where Bronze file will be saved
    """
    logger.info("Saving Bronze file to %s", output_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    logger.info("Bronze file saved successfully.")


def main():
    """
    Bronze layer ingestion process.

    - Reads raw JSON data
    - Adds ingestion metadata
    - Persists data locally
    """

    # Environment variables with default fallback values
    # Load environment variables from .env
    load_env_file()
    input_path = os.getenv(
        "JIRA_INPUT_PATH",
        "resources/jira_issues_raw.json"
    )

    output_path = os.getenv(
        "JIRA_BRONZE_OUTPUT_PATH",
        "data/bronze/bronze_jira_issues.json"
    )

    logger.info("Starting Bronze ingestion process.")

    data = read_json_file(input_path)

    if "issues" not in data:
        logger.warning("JSON does not contain 'issues' key.")
        return

    bronze_data = {
        "metadata": {
            # ISO 8601 with explicit UTC (Z suffix)
            "ingested_at": datetime.now(UTC).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "source": "local_json_file"
        },
        "raw_data": data
    }

    save_bronze_file(bronze_data, output_path)

    logger.info("Bronze layer created successfully.")


if __name__ == "__main__":
    main()
