from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import calendar
from database.main import DatabaseManager


async def get_submit_training_kb():
    """
    Generates an inline keyboard with a button for submitting new training.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    submit_button = [InlineKeyboardButton(text="Submit new training",
                                          callback_data="submit")]

    kb = InlineKeyboardMarkup(inline_keyboard=[submit_button])

    return kb


async def get_types_of_training_kb():
    """
    Generates an inline keyboard with buttons for selecting types of training such as 'Homework' or 'Proof of practice'.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    buttons = []

    types_buttons = [InlineKeyboardButton(text="Homework",
                                          callback_data="homework"),
                     InlineKeyboardButton(text="Proof of practice",
                                          callback_data="practice")]

    back_button = [InlineKeyboardButton(text="Back",
                                        callback_data="main_menu")]

    buttons.append(types_buttons)
    buttons.append(back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_training_day_calendar(month_number=None, year_number=None):
    """
    Generates an inline keyboard that acts as a calendar for selecting a training day.

    Args:
        month_number (int, optional): The month number for the calendar. Defaults to the current month.
        year_number (int, optional): The year number for the calendar. Defaults to the current year.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup representing a calendar for Telegram bot.
    """
    current_date = datetime.now()
    year = current_date.year

    if year_number and year_number != year:
        year = year_number

    if month_number and month_number > 12:
        month_number = 1
        year += 1
    elif month_number == 0:
        month_number = 12
        year -= 1

    if month_number:
        current_month = month_number
    else:
        current_month = current_date.month

    months_titles = {1: "January",
                     2: "February",
                     3: "March",
                     4: "April",
                     5: "May",
                     6: "June",
                     7: "July",
                     8: "August",
                     9: "September",
                     10: "October",
                     11: "November",
                     12: "December"}

    month_title = months_titles[current_month]

    cal = calendar.Calendar()
    initial_month = cal.monthdatescalendar(year, current_month)

    formatted_month = {month_title: []}

    for week in initial_month:
        formatted_week = []
        for day in week:
            if day.month == current_month:
                formatted_week.append([day, int(day.strftime("%d"))])
            else:
                formatted_week.append([day, " "])
        formatted_month[month_title].append(formatted_week)

    buttons = []

    month = [InlineKeyboardButton(text=f"{month_title}, {year}",
                                  callback_data="None")]

    days_row = [InlineKeyboardButton(text="Mon",
                                     callback_data="None"),
                InlineKeyboardButton(text="Tue",
                                     callback_data="None"),
                InlineKeyboardButton(text="Wed",
                                     callback_data="None"),
                InlineKeyboardButton(text="Thu",
                                     callback_data="None"),
                InlineKeyboardButton(text="Fri",
                                     callback_data="None"),
                InlineKeyboardButton(text="Sat",
                                     callback_data="None"),
                InlineKeyboardButton(text="Sun",
                                     callback_data="None")
                ]

    today_mark = "\u2714\ufe0f"
    next_arrow = "\u27A1\ufe0f"
    back_arrow = "\u2B05\ufe0f"

    dates_rows = []

    for week in formatted_month[month_title]:
        dates_row = []
        for date in week:
            if str(current_month) in str(date[0]):
                if date[0] == current_date.date():
                    dates_row.append(InlineKeyboardButton(text=today_mark,
                                                          callback_data=str(date[0])))
                else:
                    dates_row.append(InlineKeyboardButton(text=str(date[1]),
                                                          callback_data=str(date[0])))
            else:
                dates_row.append(InlineKeyboardButton(text=str(date[1]),
                                                      callback_data='None'))
        dates_rows.append(dates_row)

    next_back_row = [InlineKeyboardButton(text=back_arrow,
                                          callback_data=f"back_{current_month}_{year}"),
                     InlineKeyboardButton(text=next_arrow,
                                          callback_data=f"next_{current_month}_{year}")]

    back_button = [InlineKeyboardButton(text="Back",
                                        callback_data="previous_menu")]

    buttons.append(month)
    buttons.append(days_row)
    for date_row in dates_rows:
        buttons.append(date_row)
    buttons.append(next_back_row)
    buttons.append(back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_types_of_practice_kb():
    """
    Generates an inline keyboard with buttons for selecting the type of practice, such as 'Morning training'
    or 'Evening training'.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    buttons = []

    types_buttons = [InlineKeyboardButton(text="Morning training",
                                          callback_data="morning"),
                     InlineKeyboardButton(text="Evening training",
                                          callback_data="evening")]

    back_button = [InlineKeyboardButton(text="Back",
                                        callback_data="previous_menu")]

    buttons.append(types_buttons)
    buttons.append(back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_back_kb():
    """
    Generates an inline keyboard with a 'Back' button for navigation.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    back_button = [InlineKeyboardButton(text="Back",
                                        callback_data="previous_menu")]

    kb = InlineKeyboardMarkup(inline_keyboard=[back_button])

    return kb


async def get_settings_keyboard(user_id: int):
    """
    Generates an inline keyboard for user settings, allowing a user to toggle between 'Public'
    and 'Private' privacy settings.

    Args:
        user_id (int): The user ID for whom the settings are being adjusted.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    buttons = []

    async with DatabaseManager("test.db") as db:
        user_data = await db.get_all_user_data(table_name="all_users", telegram_id=user_id)

    current_privacy = user_data["privacy"]

    check_mark = "\u2714"

    if current_privacy == "Public":
        on_off_buttons = [InlineKeyboardButton(text=f"Public {check_mark}",
                                               callback_data="public"),
                          InlineKeyboardButton(text="Private",
                                               callback_data="private")]
    else:
        on_off_buttons = [InlineKeyboardButton(text="Public",
                                               callback_data="public"),
                          InlineKeyboardButton(text=f"Private {check_mark}",
                                               callback_data="private")]

    back_button = [InlineKeyboardButton(text="Back",
                                        callback_data="previous_menu")]

    buttons.append(on_off_buttons)
    buttons.append(back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_admin_main_menu_kb():
    """
    Generates an inline keyboard for the admin main menu, with options like 'Create a new program' or 'Delete user'.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    buttons = []

    first_row_buttons = [InlineKeyboardButton(text="Create a new program",
                                              callback_data="create_program")]

    second_row_buttons = [InlineKeyboardButton(text="Delete user",
                                               callback_data="delete_user"),
                          InlineKeyboardButton(text="Delete program",
                                               callback_data="delete_program")]

    buttons.append(first_row_buttons)
    buttons.append(second_row_buttons)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_confirm_kb():
    """
    Generates an inline keyboard with 'Yes' and 'No' buttons for general confirmation purposes.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    buttons = []

    yes_no_buttons = [InlineKeyboardButton(text="Yes",
                                           callback_data="yes"),
                      InlineKeyboardButton(text="No",
                                           callback_data="no")]

    buttons.append(yes_no_buttons)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_confirm_admin_kb(telegram_id: int):
    """
    Generates an inline keyboard for confirming admin rights for a specific user.

    Args:
        telegram_id (int): The Telegram ID of the user in question.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    buttons = []

    yes_no_buttons = [InlineKeyboardButton(text="Yes",
                                           callback_data=f"yes_{telegram_id}"),
                      InlineKeyboardButton(text="No",
                                           callback_data=f"no_{telegram_id}")]

    buttons.append(yes_no_buttons)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_programs_kb():
    """
    Generates an inline keyboard with buttons representing different programs available in the system.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    buttons = []

    async with DatabaseManager("test.db") as db:
        all_programs = await db.get_all_table_data(table_name="programs")

    for program in all_programs:
        buttons.append([InlineKeyboardButton(text=program["program_name"],
                                             callback_data=str(program["id"]))])

    back_button = [InlineKeyboardButton(text="Back",
                                        callback_data="previous_menu")]

    buttons.append(back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb


async def get_commands_kb(admin: bool = False, non_authorized: bool = False):
    """
    Generates an inline keyboard with different command options based on the user's role (admin or non-authorized).

    Args:
        admin (bool, optional): Indicates if the user is an admin. Defaults to False.
        non_authorized (bool, optional): Indicates if the user is non-authorized. Defaults to False.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for Telegram bot.
    """
    buttons = []

    if admin:
        create_group_button = [InlineKeyboardButton(text="Create new group",
                                                    callback_data="create_group")]

        buttons.append(create_group_button)

    elif non_authorized:
        request_admin_button = [InlineKeyboardButton(text="Request admin rights 👑",
                                                     callback_data="request_admin")]

        buttons.append(request_admin_button)

    else:
        privacy_settings_button = [InlineKeyboardButton(text="Privacy settings 🥷",
                                                        callback_data="privacy")]
        buttons.append(privacy_settings_button)

    back_button = [InlineKeyboardButton(text="Back",
                                        callback_data="previous_menu")]

    buttons.append(back_button)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb
