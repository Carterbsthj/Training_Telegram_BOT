"""
This module sets up the Telegram bot and client using Aiogram and Telethon libraries.

It initializes the bot, dispatcher, and client instances necessary for handling
Telegram bot interactions and user communications.

The Aiogram library is utilized for its asynchronous framework which suits
the real-time nature of a Telegram bot. It facilitates the creation of a bot instance,
a dispatcher for routing incoming messages, and a memory storage for state management.

Telethon, a Python client for Telegram's API, is used alongside Aiogram to provide
additional functionalities and access to Telegram's features that are not available
in the Bot API. This allows for a more comprehensive integration with the Telegram service.

The configuration for the bot and client, such as the API token, app ID, and app hash,
is sourced from the bot.settings module.

Attributes:
    storage (MemoryStorage): An Aiogram storage system to keep track of the bot's state.
    bot (Bot): The Aiogram Bot instance initialized with the token and parse mode.
    dp (Dispatcher): The Aiogram Dispatcher instance for routing and handling updates.
    client (TelegramClient): The Telethon client instance for advanced Telegram API operations.
"""


from aiogram import Bot, Dispatcher
from bot.settings import TOKEN, API_ID, API_HASH
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from telethon import TelegramClient


storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)
client = TelegramClient('', API_ID, API_HASH)  # You need to specify session name
