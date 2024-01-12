"""
This module is responsible for initializing the environment for a Telegram bot application.

It sets up logging, loads environment variables, and retrieves critical configuration
parameters necessary for the bot's operation. These configurations include the bot token
for Aiogram, API ID, API Hash for Telethon, and an identifier for the Telethon session.

The module uses the `python-dotenv` package to load environment variables from a `.env` file,
making it easier to manage sensitive information such as API keys and tokens.

The logging configuration is set to display warnings and more severe messages to aid in debugging.

Attributes:
    TOKEN (str): The Telegram bot token retrieved from the environment variables.
    API_ID (str): The API ID for Telegram API access, retrieved from the environment variables.
    API_HASH (str): The API Hash for Telegram API access, retrieved from the environment variables.
    TELETHON_ID (str): The session identifier for Telethon, retrieved from the environment variables.

Raises:
    KeyError: If any required environment variables are missing, a KeyError is raised with a critical log message.

Make sure to create .env file!
"""


import logging
import os
from dotenv import load_dotenv

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
load_dotenv()

try:
    TOKEN = os.environ['TRAINING_BOT_TOKEN']
    API_ID = os.environ['API_ID']
    API_HASH = os.environ['API_HASH']
    TELETHON_ID = os.environ['TELETHON_ID']
except KeyError as err:
    logging.critical(f"Can't read token from environment variable. Message: {err}")
    raise KeyError(err)
