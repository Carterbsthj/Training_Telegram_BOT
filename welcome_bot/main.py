"""
Telegram Welcome Bot Module

This module initializes a Telegram bot using the aiogram library. It creates a bot instance and a dispatcher
for handling incoming messages and interactions. The bot token and other settings are loaded from the 'TOKEN'
variable in the 'welcome_bot.settings' module.

Components:
    - bot: An instance of the Telegram bot.
    - dp: The dispatcher for handling incoming messages and interactions.
    - storage: Memory storage used by the dispatcher.

Note:
    Ensure that the 'TOKEN' variable in the 'welcome_bot.settings' module contains a valid Telegram bot token
    for this module to function properly.

Example:
    # Initialize the Telegram bot
    from aiogram import Bot, Dispatcher
    from welcome_bot.settings import TOKEN
    from aiogram.enums import ParseMode
    from aiogram.fsm.storage.memory import MemoryStorage

    storage = MemoryStorage()
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)
"""


from aiogram import Bot, Dispatcher
from welcome_bot.settings import TOKEN
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)
