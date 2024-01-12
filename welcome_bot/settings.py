"""
Telegram Bot Settings Module

This module contains settings and configurations for the Telegram bot. It initializes logging and loads the bot token
from environment variables using the 'dotenv' library.

Components:
    - Logging Configuration: Initializes logging with a specified format and level.
    - Loading Bot Token: Attempts to load the bot token from the 'WELCOME_BOT_TOKEN' environment variable.

Note:
    Ensure that the 'WELCOME_BOT_TOKEN' environment variable is set with a valid Telegram bot token for this module
    to function properly.

Example:
    # Initialize bot settings
    import logging
    import os
    from dotenv import load_dotenv

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
    load_dotenv()

    try:
        TOKEN = os.environ['WELCOME_BOT_TOKEN']
    except KeyError as err:
        logging.critical(f"Can't read token from environment variable. Message: {err}")
        raise KeyError(err)
"""


import logging
import os
from dotenv import load_dotenv

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
load_dotenv()

try:
    TOKEN = os.environ['WELCOME_BOT_TOKEN']
except KeyError as err:
    logging.critical(f"Can't read token from environment variable. Message: {err}")
    raise KeyError(err)
