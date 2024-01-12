"""
Telegram Bot State Module

This module defines the states for the Telegram bot using the 'aiogram' library. It includes a single state group,
'SubscriberState', which represents the different states a subscriber can be in, such as 'verifying_email'.

Components:
    - State Group: 'SubscriberState': Represents the states for subscriber interactions, including email verification.

Example:
    # Define a state group for subscriber states
    from aiogram.fsm.state import State, StatesGroup

    class SubscriberState(StatesGroup):
        verifying_email = State()
"""


from aiogram.fsm.state import State, StatesGroup


class SubscriberState(StatesGroup):
    verifying_email = State()
