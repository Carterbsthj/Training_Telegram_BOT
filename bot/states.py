"""
This module defines state management classes for user and admin interactions with the Telegram bot.

These classes are used to represent the different states a user or admin can be in during their interactions
with the bot. Each class corresponds to a set of related states and is designed to facilitate a coherent
flow of conversation or administrative actions within the bot.

Classes:
- UserState: Represents user interaction states for managing user conversations.
- AdminState: Represents admin interaction states for administrative tasks and actions.
- AdminProgramState: Manages states related to the administration of programs by admins.
- AdminNewGroup: Manages states for creating new groups associated with programs.

Each class is documented with details about the states it includes and their respective purposes.

Usage:
These state management classes play a crucial role in controlling the conversation flow and user/admin
interactions within the Telegram bot. They ensure that users and admins are guided through the conversation
process step by step and that administrative tasks are performed seamlessly.

Note: Detailed class-level docstrings are provided within each class definition for clarity.
"""


from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """
    Represents the different states a user can be in during interaction with the bot.

    This class is used to manage the state of a user's conversation with the bot,
    ensuring a coherent flow and appropriate handling at each stage of the interaction.

    States:
        greeted: State when the user has been greeted.
        type_of_training: State to capture the type of training the user is doing.
        date: State to capture the date of the training.
        type_of_practice: State to capture the type of practice.
        homework: State to capture if the user did homework.
        total_duration: State to capture the total duration of the training.
        meditation_duration: State to capture the duration of meditation.
        video: State to capture if the user submits a video.
        privacy_state: State to manage user's privacy settings.
        commands_state: State to handle various bot commands.
    """
    greeted = State()
    type_of_training = State()
    date = State()
    type_of_practice = State()
    homework = State()
    total_duration = State()
    meditation_duration = State()
    video = State()
    privacy_state = State()
    commands_state = State()


class AdminState(StatesGroup):
    """
    Represents the different states an admin can be in during interaction with the bot.

    This class is used to manage the state of an admin's conversation with the bot,
    facilitating administrative tasks and actions.

    States:
        main_menu: State representing the main menu for admin actions.
        deleting_user: State for initiating the user deletion process.
        confirm_deleting_user: State for confirming the deletion of a user.
        deleting_program: State for initiating the program deletion process.
        commands_state: State to handle various admin-specific bot commands.
    """
    main_menu = State()
    deleting_user = State()
    confirm_deleting_user = State()
    deleting_program = State()
    commands_state = State()


class AdminProgramState(StatesGroup):
    """
    Represents the states involved in the administration of programs.

    This class is used for handling the creation and configuration of new programs
    by an admin through the bot.

    States:
        new_program_title: State to capture the title of the new program.
        new_program_end_time: State to capture the end time of the new program.
        new_program_group_title: State to capture the group title associated with the new program.
        new_program_spreadsheet: State to capture the spreadsheet details of the new program.
        new_program_confirm: State for confirming the creation of the new program.
    """
    new_program_title = State()
    new_program_end_time = State()
    new_program_group_title = State()
    new_program_spreadsheet = State()
    new_program_confirm = State()


class AdminNewGroup(StatesGroup):
    """
    Represents the states involved in the creation of new groups by an admin.

    This class is used for handling the process of setting up new groups
    associated with different programs.

    States:
        choose_program: State to select the program associated with the new group.
        new_group_title: State to set the title for the new group.
        new_group_spreadsheet_id: State to input the spreadsheet ID linked to the new group.
        new_group_confirm: State for confirming the creation of the new group.
    """
    choose_program = State()
    new_group_title = State()
    new_group_spreadsheet_id = State()
    new_group_confirm = State()
