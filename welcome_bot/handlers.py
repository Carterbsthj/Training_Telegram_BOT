from aiogram.types import Message
from welcome_bot.main import dp, bot
from aiogram.fsm.context import FSMContext
from welcome_bot.states import SubscriberState
from database.main import DatabaseManager
import re
import welcome_bot.texts as texts
from bot.functions import create_small_group
from go_high_level.api_calls import create_user, create_opportunity
from datetime import datetime
import logging


logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@dp.message(SubscriberState.verifying_email)
async def handle_email_verifications(message: Message, state: FSMContext):
    try:
        email_pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(pattern=email_pattern, string=message.text):
            async with DatabaseManager("test.db") as db:
                user_email = message.text.lower()
                parameters = {"column": "email",
                              "value": user_email}
                verified_user = await db.check_existence(table_name="subscribers",
                                                         parameters=parameters)
                if verified_user:
                    user_program_title = verified_user["program_title"]
                    program_query = f"""SELECT * FROM programs 
                                                 WHERE program_name = '{user_program_title}' 
                                     """

                    programs = await db.custom_query(query=program_query)
                    user_program = programs[0]
                    user_program_id = user_program["id"]
                    program_pipeline_id = user_program["ghl_pipeline_id"]
                    default_stage_id = user_program["ghl_students_id"]
                    group_query = f"""SELECT * FROM groups 
                                               WHERE program = {user_program_id} 
                                               AND current_members < 40"""

                    groups = await db.custom_query(query=group_query)
                    user_group = groups[0]
                    main_group_id = user_group["group_id"]
                    flow_60_user_first_name = verified_user["first_name"]
                    flow_60_user_last_name = verified_user["last_name"]
                    group_invite_link = user_group["group_invite_link"]

                    group_title = f"{flow_60_user_first_name} {user_program_title} personal training group"
                    small_group_data = await create_small_group(group_title=group_title)
                    small_group_id = small_group_data["chat_id"]
                    small_group_invite_link = f'<a href="{small_group_data["invite_link"]}">Personal training group</a>'
                    ghl_user_id = await create_user(first_name=flow_60_user_first_name,
                                                    last_name=flow_60_user_last_name,
                                                    email=user_email)
                    username_for_ghl = f"{flow_60_user_first_name} {flow_60_user_last_name}"
                    ghl_opportunity_id = await create_opportunity(username=username_for_ghl,
                                                                  user_id=ghl_user_id,
                                                                  default_stage_id=default_stage_id,
                                                                  pipeline_id=program_pipeline_id)

                    user_data = {"first_name": flow_60_user_first_name,
                                 "last_name": flow_60_user_last_name,
                                 "email": user_email,
                                 "telegram_id": message.from_user.id,
                                 "telegram_username": message.from_user.username,
                                 "main_group_id": main_group_id,
                                 "small_group_id": small_group_id,
                                 "privacy": "Public",
                                 "last_homework": "1",
                                 "last_practice": "1",
                                 "user_program": user_program_id,
                                 "ghl_id": ghl_user_id,
                                 "ghl_opp_id": ghl_opportunity_id,
                                 "first_date": datetime.now().date()}

                    await db.insert_data(table_name="all_users",
                                         data=user_data)
                    main_group_link = f'<a href="{group_invite_link}">Program main group</a>'

                    text = texts.greeting_for_verified_user.format(main_group_link,
                                                                   small_group_invite_link)
                    await message.answer(text=text, disable_web_page_preview=True)
                    await state.clear()

                else:
                    await message.answer(text=texts.answer_to_non_verified_user)
        else:
            await message.answer(text=texts.incorrect_format_of_email)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {message.from_user.id} on state {current_state}.")
        await message.answer(text=texts.error_occurred)


@dp.message()
async def greeting_handler(message: Message, state: FSMContext):
    """Greeting for user and asking about registered email"""
    async with DatabaseManager("test.db") as db:
        parameters = {"column": "telegram_id",
                      "value": message.from_user.id}
        registered_user = await db.check_existence(table_name="all_users",
                                                   parameters=parameters)
        if registered_user:
            query = f"""SELECT * FROM groups WHERE group_id = {registered_user['main_group_id']}"""
            groups = await db.custom_query(query)
            user_group = groups[0]

    if registered_user:
        group_link = f'<a href="{user_group["group_invite_link"]}">training group</a>'

        await message.answer(text=texts.already_registered.format(registered_user["first_name"],
                                                                  group_link),
                             disable_web_page_preview=True)

    else:
        user_name = message.from_user.first_name

        await message.answer(text=texts.initial_greeting_for_subscriber.format(user_name))
        await state.set_state(SubscriberState.verifying_email)


async def exe_welcome_bot():
    """Function to start a bot"""

    logging.info(msg="BOT started")
    print("Welcome BOT started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
