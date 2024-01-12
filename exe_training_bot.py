"""Module contains exe statements for a bot"""


import asyncio

from bot.handlers import exe_bot
from welcome_bot.handlers import exe_welcome_bot
from bot.functions import make_notifications


async def start_program():
    """Starts whole program"""
    await asyncio.gather(exe_bot(), make_notifications(), exe_welcome_bot())


if __name__ == "__main__":
    asyncio.run(start_program())
