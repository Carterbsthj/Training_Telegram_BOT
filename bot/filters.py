"""This module contains custom created filters: IsAdminProgramState, NewChatMembersFilter, IsSuperAdmin"""


from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.states import AdminProgramState
from database.main import DatabaseManager


class IsAdminProgramState(Filter):
    """
    A custom filter to check if the current state of a conversation is one of the states defined in AdminProgramState.

    This filter is applied to CallbackQueries to determine whether the callback is occurring within the context of
    an admin program state.
    """

    async def __call__(self, call: CallbackQuery, state: FSMContext) -> bool:
        """
        Asynchronously determines if the current state is an admin program state.

        Args:
            call (CallbackQuery): The callback query from a Telegram user.
            state (FSMContext): The current Finite State Machine context.

        Returns:
            bool: True if the current state is an admin program state, False otherwise.
        """
        current_state = await state.get_state()
        return current_state in AdminProgramState.__all_states__


class NewChatMembersFilter(Filter):
    """
    A custom filter to check if there are new members added to a chat.

    This filter is used to process messages that contain information about new members joining a chat.
    """

    async def __call__(self, message: Message) -> bool:
        """
        Asynchronously checks if the message includes new chat members.

        Args:
            message (Message): The message to be checked.

        Returns:
            bool: True if there are new chat members in the message, False otherwise.
        """
        return bool(message.new_chat_members)


class IsSuperAdmin(Filter):
    """
    A custom filter to verify if a user is a super admin.

    This filter is applied to CallbackQueries to determine whether the user performing the action is a super admin.
    """

    async def __call__(self, call: CallbackQuery) -> bool:
        """
        Asynchronously checks if the user from the CallbackQuery is a super admin.

        Args:
            call (CallbackQuery): The callback query from a Telegram user.

        Returns:
            bool: True if the user is a super admin, False otherwise.
        """
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": call.from_user.id}
            return bool(await db.check_existence(table_name="super_admins", parameters=parameters))
