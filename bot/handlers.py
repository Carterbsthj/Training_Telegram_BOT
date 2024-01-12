"""This module contains all bot handlers"""


import re
import bot.texts as texts
import logging

from aiogram.types import Message, CallbackQuery, FSInputFile
from bot.main import dp, bot, client
from aiogram.fsm.context import FSMContext
from bot.states import UserState, AdminState, AdminProgramState, AdminNewGroup
from bot.keyboards import (get_submit_training_kb, get_training_day_calendar, get_types_of_training_kb, get_back_kb,
                           get_types_of_practice_kb, get_settings_keyboard, get_admin_main_menu_kb, get_confirm_kb,
                           get_confirm_admin_kb, get_programs_kb, get_commands_kb)
from database.main import DatabaseManager
from google_spreadsheets.functions import save_data_to_sheet
from aiogram.filters import Command
from bot.filters import IsAdminProgramState, NewChatMembersFilter, IsSuperAdmin
from bot.settings import TELETHON_ID
from bot.functions import create_main_group
from go_high_level.api_calls import get_pipeline, delete_user, change_stage


logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@dp.callback_query(UserState.greeted)
async def handle_submit(call: CallbackQuery, state: FSMContext):
    """Handles submit button and starts process of training input"""
    try:
        await state.set_state(UserState.type_of_training)
        kb = await get_types_of_training_kb()
        await call.message.edit_text(text=texts.choose_homework_or_practice,
                                     reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.callback_query(UserState.type_of_training)
async def handle_type_of_training(call: CallbackQuery, state: FSMContext):
    """Handles type of training - homework or proof of practice"""
    try:
        if call.data == "main_menu":
            data = await state.get_data()
            kb = await get_submit_training_kb()
            user_name = data["user_name"]
            await state.set_state(UserState.greeted)
            await state.update_data(user_name=user_name)
            await call.message.edit_text(text=texts.greeting_for_user.format(user_name),
                                         reply_markup=kb)
        else:
            await state.set_state(UserState.date)
            await state.update_data(process=call.data)
            kb = await get_training_day_calendar()
            await call.message.edit_text(text=texts.choose_day_of_training,
                                         reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.callback_query(UserState.date)
async def handle_date_of_training(call: CallbackQuery, state: FSMContext):
    """Handles date of training"""
    month_counter = 1
    try:
        if "next" in call.data:
            data = call.data.split("_")
            current_month = int(data[1])
            current_year = int(data[2])
            kb = await get_training_day_calendar(month_number=current_month + month_counter,
                                                 year_number=current_year)
            await call.message.edit_reply_markup(reply_markup=kb)

        elif "back" in call.data:
            data = call.data.split("_")
            current_month = int(data[1])
            current_year = int(data[2])
            kb = await get_training_day_calendar(month_number=current_month - month_counter,
                                                 year_number=current_year)
            await call.message.edit_reply_markup(reply_markup=kb)

        elif "previous_menu" in call.data:
            kb = await get_types_of_training_kb()
            await state.set_state(UserState.type_of_training)
            await call.message.edit_text(text=texts.choose_homework_or_practice,
                                         reply_markup=kb)

        elif call.data != "None":
            await state.update_data(date=call.data)
            data = await state.get_data()
            process = data["process"]
            if process == "homework":
                text = texts.input_homework
                kb = await get_back_kb()
                await state.set_state(UserState.homework)
            else:
                text = texts.choose_type_of_training
                kb = await get_types_of_practice_kb()
                await state.set_state(UserState.type_of_practice)

            await call.message.edit_text(text=text,
                                         reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.callback_query(UserState.type_of_practice)
async def type_of_practice(call: CallbackQuery, state: FSMContext):
    """Handles types of practice - evening or morning"""
    try:
        if call.data == "previous_menu":
            await state.set_state(UserState.date)
            kb = await get_training_day_calendar()
            await call.message.edit_text(text=texts.choose_day_of_training,
                                         reply_markup=kb)

        else:
            await state.update_data(type_of_practice=call.data)
            await state.set_state(UserState.total_duration)
            kb = await get_back_kb()
            await call.message.edit_text(text=texts.input_duration,
                                         reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.message(UserState.homework)
async def handle_homework(message: Message, state: FSMContext):
    """Receives user homework in text"""
    try:
        async with DatabaseManager("test.db") as db:
            user_data = await db.get_all_user_data(table_name="all_users", telegram_id=message.from_user.id)

        small_user_group = user_data["small_group_id"]
        main_user_group = user_data["main_group_id"]

        data = await state.get_data()
        user_name = data["user_name"]
        homework_date = data["date"]

        await bot.forward_message(chat_id=small_user_group,
                                  from_chat_id=message.from_user.id,
                                  message_id=message.message_id)

        if user_data["privacy"] == "Public":
            await bot.forward_message(chat_id=main_user_group,
                                      from_chat_id=message.from_user.id,
                                      message_id=message.message_id)

        if data["process"] == "homework":
            thanks_text = texts.thanks_for_submitting_homework
        else:
            thanks_text = texts.thanks_for_submitting_training

        await message.answer(text=thanks_text)

        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": int(message.from_user.id)}
            user_data = await db.check_existence(table_name="all_users", parameters=parameters)
            query = f"""SELECT group_spreadsheet_id 
                                    FROM groups 
                                    WHERE group_id = {user_data['main_group_id']}"""
            spreadsheet_data = await db.custom_query(query)
            spreadsheet_id = spreadsheet_data[0]["group_spreadsheet_id"]

        data_to_sheets = [user_name, message.from_user.id, data["process"], homework_date, message.text]

        await save_data_to_sheet(data=data_to_sheets, spreadsheet=spreadsheet_id, homework=True)

        kb = await get_submit_training_kb()
        await bot.send_message(chat_id=message.from_user.id,
                               text=texts.greeting_for_user.format(user_name),
                               reply_markup=kb)

        async with DatabaseManager("test.db") as db:
            data = {"last_homework": homework_date}
            await db.update_data(table_name="all_users", data=data, telegram_id=message.from_user.id)

        await state.clear()
        await state.set_state(UserState.greeted)
        await state.update_data(user_name=user_name)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {message.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await message.answer(text=texts.error_occurred,
                             reply_markup=kb)


@dp.callback_query(UserState.homework)
async def handle_back_homework(call: CallbackQuery, state: FSMContext):
    """Handles back to previous menu button"""
    try:
        await state.set_state(UserState.date)
        kb = await get_training_day_calendar()
        await call.message.edit_text(text=texts.choose_day_of_training,
                                     reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.message(UserState.total_duration)
async def handle_duration(message: Message, state: FSMContext):
    """Receives total duration of training"""
    try:
        kb = await get_back_kb()
        if message.text.isdigit():
            await state.update_data(duration=message.text)
            await state.set_state(UserState.meditation_duration)
            await message.answer(text=texts.input_meditation_duration,
                                 reply_markup=kb)

        else:
            await message.answer(text=texts.incorrect_duration,
                                 reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {message.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await message.answer(text=texts.error_occurred,
                             reply_markup=kb)


@dp.callback_query(UserState.total_duration)
async def handle_back_duration(call: CallbackQuery, state: FSMContext):
    """Handles back to previous menu button"""
    try:
        await state.set_state(UserState.type_of_practice)
        kb = await get_types_of_practice_kb()
        await call.message.edit_text(text=texts.choose_type_of_training,
                                     reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.message(UserState.meditation_duration)
async def handle_meditation(message: Message, state: FSMContext):
    """Receives duration of meditation"""
    try:
        kb = await get_back_kb()
        if message.text.isdigit():
            await state.update_data(meditation=message.text)
            await state.set_state(UserState.video)
            tutorial = FSInputFile("video_tutorial.gif")

            await message.answer_animation(animation=tutorial,
                                           caption=texts.upload_video,
                                           reply_markup=kb)

        else:
            await message.answer(text=texts.incorrect_duration,
                                 reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {message.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await message.answer(text=texts.error_occurred,
                             reply_markup=kb)


@dp.callback_query(UserState.meditation_duration)
async def handle_back_meditation(call: CallbackQuery, state: FSMContext):
    """Handles back to previous menu button"""
    try:
        await state.set_state(UserState.total_duration)
        kb = await get_back_kb()
        await call.message.edit_text(text=texts.input_duration,
                                     reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.message(UserState.video)
async def handle_video(message: Message, state: FSMContext):
    """Receives video from user and saves it into gdrive"""
    try:
        if message.video:
            async with DatabaseManager("test.db") as db:
                user_data = await db.get_all_user_data(table_name="all_users", telegram_id=message.from_user.id)

                query = f"""SELECT * FROM programs WHERE id = {user_data['user_program']}"""
                user_program = await db.custom_query(query=query)

            small_user_group = user_data["small_group_id"]
            main_user_group = user_data["main_group_id"]

            data = await state.get_data()
            user_last_name = user_data["last_name"]

            if user_last_name is not None:
                user_name = data["user_name"] + user_last_name
            else:
                user_name = data["user_name"]

            training_date = data["date"]

            data_to_telethon = (f"{user_name};{message.from_user.id};{data['process']};{training_date};"
                                f"{data['type_of_practice']};{data['duration']};{data['meditation']};"
                                f"{user_data['first_date']}")

            caption_for_video = texts.video_from_user.format(user_name,
                                                             data["type_of_practice"],
                                                             training_date,
                                                             data["duration"],
                                                             data["meditation"])

            video_file = message.video.file_id
            await bot.send_video(chat_id=int(TELETHON_ID), video=video_file, caption=data_to_telethon)
            await bot.send_video(chat_id=small_user_group, video=video_file, caption=caption_for_video)

            if user_data["privacy"] == "Public":
                await bot.send_video(chat_id=main_user_group, video=video_file, caption=caption_for_video)

            if data["process"] == "homework":
                thanks_text = texts.thanks_for_submitting_homework
            else:
                thanks_text = texts.thanks_for_submitting_training

            await message.answer(text=thanks_text)

            if str(user_data['last_practice']).isdigit() and user_data['last_practice'] >= 3:
                pipeline_id = user_program[0]["ghl_pipeline_id"]
                next_stage_id = user_program[0]["ghl_students_id"]
                opp_id = user_data["ghl_opp_id"]
                await change_stage(opportunity_id=opp_id, stage_id=next_stage_id, pipeline_id=pipeline_id)

            async with DatabaseManager("test.db") as db:
                data = {"last_practice": training_date}
                await db.update_data(table_name="all_users", data=data, telegram_id=message.from_user.id)

            kb = await get_submit_training_kb()
            await bot.send_message(chat_id=message.from_user.id,
                                   text=texts.greeting_for_user.format(user_name),
                                   reply_markup=kb)

            await state.clear()
            await state.set_state(UserState.greeted)
            await state.update_data(user_name=user_name)
        else:
            await message.answer(text=texts.please_send_video)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {message.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await message.answer(text=texts.error_occurred,
                             reply_markup=kb)


@dp.callback_query(UserState.video)
async def handle_back_video(call: CallbackQuery, state: FSMContext):
    """Handles back to previous menu button"""
    try:
        kb = await get_back_kb()
        await call.message.edit_text(text=texts.input_meditation_duration,
                                     reply_markup=kb)
        await state.set_state(UserState.meditation_duration)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.message(Command("commands"))
async def handle_settings_command(message: Message, state: FSMContext):
    """Handles settings command for users"""
    try:
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": message.from_user.id}
            admin = await db.check_existence(table_name="admins", parameters=parameters)
            authorized_user = await db.check_existence(table_name="all_users", parameters=parameters)

        if admin:
            text = texts.create_new_group
            kb = await get_commands_kb(admin=True)
            await state.set_state(AdminState.commands_state)

        elif authorized_user:
            text = texts.change_privacy
            kb = await get_commands_kb()
            await state.set_state(UserState.commands_state)

        else:
            text = texts.request_admin
            kb = await get_commands_kb(non_authorized=True)

        await message.answer(text=text, reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {message.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await message.answer(text=texts.error_occurred,
                             reply_markup=kb)


@dp.callback_query(AdminState.commands_state)
async def handle_commands_admin(call: CallbackQuery, state: FSMContext):
    try:
        if call.data == "create_group":
            async with DatabaseManager("test.db") as db:
                all_programs = await db.get_all_table_data(table_name="programs")

            if not all_programs:
                await call.message.edit_text(text=texts.no_programs)

            else:
                kb = await get_programs_kb()
                await call.message.edit_text(text=texts.choose_program,
                                             reply_markup=kb)

                await state.set_state(AdminNewGroup.choose_program)

        else:
            await call.message.delete()
            await state.set_state(AdminState.main_menu)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.callback_query(UserState.commands_state)
async def handle_command_user(call: CallbackQuery, state: FSMContext):
    try:
        if call.data == "privacy":
            async with DatabaseManager("test.db") as db:
                user_data = await db.get_all_user_data(table_name="all_users", telegram_id=call.from_user.id)

                current_privacy = user_data["privacy"]

                kb = await get_settings_keyboard(call.from_user.id)
                await call.message.edit_text(text=texts.settings_text.format(current_privacy),
                                             reply_markup=kb)

                await state.set_state(UserState.privacy_state)

        else:
            await call.message.delete()
            await state.set_state(UserState.greeted)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.callback_query(AdminNewGroup.choose_program)
async def handle_program_choice(call: CallbackQuery, state: FSMContext):
    """Handles program choice while creating new group"""
    try:
        if call.data == "previous_menu":
            kb = await get_admin_main_menu_kb()
            await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                         reply_markup=kb)

            await state.clear()
            await state.set_state(AdminState.main_menu)

        else:
            program_id = int(call.data)
            async with DatabaseManager("test.db") as db:
                parameters = {"column": "id",
                              "value": program_id}
                program_data = await db.check_existence(table_name="programs", parameters=parameters)

            await state.update_data(program=program_id,
                                    program_title=program_data["program_name"])

            kb = await get_back_kb()
            await call.message.edit_text(text=texts.provide_new_group_spreadsheet_id
                                         .format(program_data["program_name"]),
                                         reply_markup=kb)

            await state.set_state(AdminNewGroup.new_group_spreadsheet_id)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(AdminState.main_menu)
        kb = await get_admin_main_menu_kb()
        await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                     reply_markup=kb)


@dp.message(AdminNewGroup.new_group_spreadsheet_id)
async def handle_new_group_spreadsheet_id(message: Message, state: FSMContext):
    """Handles new group spreadsheet for a program"""
    await state.update_data(group_spreadsheet_id=message.text)
    new_group_data = await state.get_data()

    kb = await get_back_kb()
    await message.answer(text=texts.choose_new_group_title.format(new_group_data["program_title"]),
                         reply_markup=kb)

    await state.set_state(AdminNewGroup.new_group_title)


@dp.callback_query(AdminNewGroup.new_group_spreadsheet_id)
async def handle_back_spreadsheet(call: CallbackQuery, state: FSMContext):
    """Handles back to previous menu button"""
    try:
        kb = await get_programs_kb()
        await call.message.edit_text(text=texts.choose_program,
                                     reply_markup=kb)

        await state.set_state(AdminNewGroup.choose_program)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(AdminState.main_menu)
        kb = await get_admin_main_menu_kb()
        await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                     reply_markup=kb)


@dp.message(AdminNewGroup.new_group_title)
async def handle_new_group_title(message: Message, state: FSMContext):
    """Handles new group title for a program"""
    data = await state.get_data()

    group_title = message.text
    new_group_data = await create_main_group(group_title=group_title)
    group_id = new_group_data["chat_id"]
    new_group_invite_link = new_group_data["invite_link"]
    program_title = data["program_title"]

    data.update({"group_title": group_title,
                 "group_id": group_id,
                 "current_members": 0,
                 "group_invite_link": new_group_invite_link})

    del data["program_title"]

    async with DatabaseManager("test.db") as db:
        await db.insert_data(table_name="groups", data=data)

    text = texts.group_created.format(program_title) + texts.admin_menu.format(message.from_user.first_name)
    kb = await get_admin_main_menu_kb()
    await message.answer(text=text,
                         reply_markup=kb)

    await state.clear()
    await state.set_state(AdminState.main_menu)


@dp.callback_query(AdminNewGroup.new_group_title)
async def handle_back_title(call: CallbackQuery, state: FSMContext):
    """Handles back to previous menu button"""
    try:
        group_data = await state.get_data()
        kb = await get_back_kb()
        await call.message.edit_text(text=texts.provide_new_group_spreadsheet_id.format(group_data["program_title"]),
                                     reply_markup=kb)

        await state.set_state(AdminNewGroup.new_group_spreadsheet_id)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(AdminState.main_menu)
        kb = await get_admin_main_menu_kb()
        await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                     reply_markup=kb)


@dp.callback_query(UserState.privacy_state)
async def handle_privacy_settings(call: CallbackQuery, state: FSMContext):
    """Handles actions in settings menu for authorized user"""
    try:
        async with DatabaseManager("test.db") as db:
            user_data = await db.get_all_user_data(table_name="all_users", telegram_id=call.from_user.id)

        user_name = user_data["first_name"]

        if call.data == "previous_menu":
            kb = await get_submit_training_kb()
            await state.set_state(UserState.greeted)
            await state.update_data(user_name=user_name)
            await call.message.edit_text(text=texts.greeting_for_user.format(user_name),
                                         reply_markup=kb)

        elif call.data == "public" or call.data == "private":
            async with DatabaseManager("test.db") as db:
                if call.data == "public":
                    data = {"privacy": "Public"}
                else:
                    data = {"privacy": "Private"}

                await db.update_data(table_name="all_users", data=data, telegram_id=call.from_user.id)
                user_data = await db.get_all_user_data(table_name="all_users", telegram_id=call.from_user.id)

            current_privacy = user_data["privacy"]

            kb = await get_settings_keyboard(call.from_user.id)
            await call.message.edit_text(text=texts.settings_text.format(current_privacy),
                                         reply_markup=kb)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(UserState.greeted)
        kb = await get_submit_training_kb()
        await call.message.edit_text(text=texts.error_occurred,
                                     reply_markup=kb)


@dp.callback_query(AdminState.main_menu)
async def handle_admin_main_menu(call: CallbackQuery, state: FSMContext):
    """Handles actions in main menu"""
    try:
        if call.data == "delete_user":
            kb = await get_back_kb()
            await call.message.edit_text(text=texts.enter_user_id_to_delete,
                                         reply_markup=kb)
            await state.set_state(AdminState.deleting_user)

        elif call.data == "delete_program":
            kb = await get_programs_kb()
            await call.message.edit_text(text=texts.choose_program_to_delete,
                                         reply_markup=kb)

            await state.set_state(AdminState.deleting_program)

        else:
            kb = await get_back_kb()
            await call.message.edit_text(text=texts.program_name,
                                         reply_markup=kb)
            await state.set_state(AdminProgramState.new_program_title)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(AdminState.main_menu)
        kb = await get_admin_main_menu_kb()
        await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                     reply_markup=kb)


@dp.message(AdminProgramState.new_program_title)
async def handle_program_title(message: Message, state: FSMContext):
    """Handles new program title"""
    await state.update_data(program_title=message.text)
    kb = await get_back_kb()
    await message.answer(text=texts.program_end_date,
                         reply_markup=kb)

    await state.set_state(AdminProgramState.new_program_end_time)


@dp.message(AdminProgramState.new_program_end_time)
async def handle_program_end_time(message: Message, state: FSMContext):
    """Handles new program end time"""
    end_date_pattern = "^\d{4}-\d{2}-\d{2}$"
    if re.match(end_date_pattern, message.text):
        await state.update_data(program_end_date=message.text)
        kb = await get_back_kb()
        await message.answer(text=texts.provide_spreadsheet_id,
                             reply_markup=kb)

        await state.set_state(AdminProgramState.new_program_spreadsheet)

    else:
        kb = await get_back_kb()
        await message.answer(text=texts.incorrect_format_of_end_date,
                             reply_markup=kb)


@dp.message(AdminProgramState.new_program_spreadsheet)
async def handle_program_spreadsheet(message: Message, state: FSMContext):
    """Handles new program spreadsheet"""
    await state.update_data(program_spreadsheet_id=message.text)
    kb = await get_back_kb()
    await message.answer(text=texts.provide_title_of_group,
                         reply_markup=kb)

    await state.set_state(AdminProgramState.new_program_group_title)


@dp.message(AdminProgramState.new_program_group_title)
async def handle_program_group_title(message: Message, state: FSMContext):
    """Handles new program group title"""
    await state.update_data(program_group_title=message.text)

    program_data = await state.get_data()

    kb = await get_confirm_kb()

    await message.answer(text=texts.confirmation_program.format(program_data["program_title"],
                                                                program_data["program_end_date"],
                                                                program_data["program_group_title"],
                                                                program_data["program_spreadsheet_id"]),
                         reply_markup=kb)

    await state.set_state(AdminProgramState.new_program_confirm)


@dp.callback_query(IsAdminProgramState())
async def handle_admin_program_back(call: CallbackQuery, state: FSMContext):
    """Handles callback query in program creation flow"""
    try:
        current_state = await state.get_state()
        if current_state == AdminProgramState.new_program_title:
            kb = await get_admin_main_menu_kb()
            await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                         reply_markup=kb)

            await state.clear()
            await state.set_state(AdminState.main_menu)

        elif current_state == AdminProgramState.new_program_end_time:
            kb = await get_back_kb()
            await call.message.edit_text(text=texts.program_name,
                                         reply_markup=kb)

            await state.set_state(AdminProgramState.new_program_title)

        elif current_state == AdminProgramState.new_program_spreadsheet:
            kb = await get_back_kb()
            await call.message.edit_text(text=texts.program_end_date,
                                         reply_markup=kb)

            await state.set_state(AdminProgramState.new_program_end_time)

        elif current_state == AdminProgramState.new_program_group_title:
            kb = await get_back_kb()
            await call.message.edit_text(text=texts.provide_spreadsheet_id,
                                         reply_markup=kb)

            await state.set_state(AdminProgramState.new_program_spreadsheet)

        elif current_state == AdminProgramState.new_program_confirm:
            if call.data == "yes":
                program_data = await state.get_data()

                group_data = await create_main_group(group_title=program_data["program_group_title"])
                invite_link = group_data["invite_link"]
                group_id = group_data["chat_id"]
                pipeline = await get_pipeline(program_data["program_title"])
                pipeline_id = pipeline["id"]
                students_stage = pipeline["stages"]["Students"]
                no_pops_stage = pipeline["stages"]["No POP's submitted"]

                async with DatabaseManager("test.db") as db:
                    program_data_to_db = {"program_name": program_data["program_title"],
                                          "program_end": program_data["program_end_date"],
                                          "ghl_pipeline_id": pipeline_id,
                                          "ghl_students_id": students_stage,
                                          "ghl_no_pop_id": no_pops_stage}

                    program_id = await db.insert_data(table_name="programs", data=program_data_to_db)

                    group_data_to_db = {"group_title": program_data["program_group_title"],
                                        "group_id": group_id,
                                        "group_spreadsheet_id": program_data["program_spreadsheet_id"],
                                        "group_invite_link": invite_link,
                                        "current_members": 0,
                                        "program": program_id}

                    await db.insert_data(table_name="groups", data=group_data_to_db)

                kb = await get_admin_main_menu_kb()
                text = texts.program_created + texts.admin_menu.format(call.from_user.first_name)
                await call.message.edit_text(text=text,
                                             reply_markup=kb)

                await state.set_state(AdminState.main_menu)

            else:
                kb = await get_back_kb()
                await call.message.edit_text(text=texts.provide_title_of_group,
                                             reply_markup=kb)

                await state.set_state(AdminProgramState.new_program_group_title)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(AdminState.main_menu)
        kb = await get_admin_main_menu_kb()
        await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                     reply_markup=kb)


@dp.callback_query(AdminState.deleting_user)
async def handle_back_from_deleting(call: CallbackQuery, state: FSMContext):
    """Handles back from delete stage"""
    try:
        kb = await get_admin_main_menu_kb()
        await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                     reply_markup=kb)
        await state.set_state(AdminState.main_menu)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(AdminState.main_menu)
        kb = await get_admin_main_menu_kb()
        await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                     reply_markup=kb)


@dp.message(AdminState.deleting_user)
async def handle_user_deleting(message: Message, state: FSMContext):
    """Handles deleting user with his Telegram id"""
    if message.text.isdigit():
        async with DatabaseManager("test.db") as db:
            user_data = await db.get_all_user_data(table_name="all_users", telegram_id=int(message.text))

        if user_data:

            user_to_delete_name = f"{user_data['first_name']} {user_data['last_name']}"
            await state.update_data(user_to_delete_id=int(message.text),
                                    user_to_delete_name=user_to_delete_name)
            kb = await get_confirm_kb()
            await message.answer(text=texts.confirm_deleting_user.format(user_to_delete_name),
                                 reply_markup=kb)
            await state.set_state(AdminState.confirm_deleting_user)

        else:
            kb = await get_back_kb()
            await message.answer(text=texts.user_not_found.format(message.text),
                                 reply_markup=kb)
    else:
        kb = await get_back_kb()
        await message.answer(text=texts.non_valid_user_id,
                             reply_markup=kb)


@dp.callback_query(AdminState.confirm_deleting_user)
async def handle_confirm_user_deleting(call: CallbackQuery, state: FSMContext):
    """Confirming user deletion"""
    try:
        if call.data == "yes":
            state_data = await state.get_data()
            async with DatabaseManager("test.db") as db:
                parameters = {"column": "telegram_id",
                              "value": state_data["user_to_delete_id"]}

                user = await db.check_existence(table_name="all_users", parameters=parameters)
                ghl_id = user["ghl_id"]
                user_chats = [user["main_group_id"], user["small_group_id"]]
                await delete_user(user_id=ghl_id)
                await db.delete_user_from_db(table_name="all_users", telegram_id=state_data["user_to_delete_id"])

            for chat in user_chats:
                await bot.ban_chat_member(chat_id=chat, user_id=user["telegram_id"])

            kb = await get_admin_main_menu_kb()
            text = (texts.user_deleted.format(state_data["user_to_delete_name"]) +
                    texts.admin_menu.format(call.from_user.first_name))
            await call.message.edit_text(text=text,
                                         reply_markup=kb)

            await state.clear()
            await state.set_state(AdminState.main_menu)

        else:
            kb = await get_admin_main_menu_kb()
            await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                         reply_markup=kb)

            await state.clear()
            await state.set_state(AdminState.main_menu)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(AdminState.main_menu)
        kb = await get_admin_main_menu_kb()
        await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                     reply_markup=kb)


@dp.callback_query(AdminState.deleting_program)
async def handle_program_deletion(call: CallbackQuery, state: FSMContext):
    try:
        if call.data == "previous_menu":
            await state.set_state(AdminState.main_menu)
            kb = await get_admin_main_menu_kb()
            await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                         reply_markup=kb)

        else:
            program_id = int(call.data)
            async with DatabaseManager("test.db") as db:
                program_parameters = {"column": "id",
                                      "value": program_id}

                program_data = await db.check_existence(table_name="programs", parameters=program_parameters)
                program_name = program_data["program_name"]
                query = f"""SELECT * FROM all_users 
                                                     WHERE user_program = {program_id}"""

                program_all_users = await db.custom_query(query=query)

                await db.delete_program(program_id=program_id)

            for user in program_all_users:
                user_chats = [user["main_group_id"], user["small_group_id"]]
                for chat in user_chats:
                    await bot.ban_chat_member(chat_id=chat, user_id=user["telegram_id"])

            text = texts.program_deleted.format(program_name) + texts.admin_menu.format(call.from_user.first_name)

            kb = await get_admin_main_menu_kb()
            await call.message.edit_text(text=text, reply_markup=kb)
            await state.set_state(AdminState.main_menu)

    except Exception as e:
        current_state = await state.get_state()
        logging.error(msg=f"An error occurred: {e}. User {call.from_user.id} on state {current_state}.")
        await state.clear()
        await state.set_state(AdminState.main_menu)
        kb = await get_admin_main_menu_kb()
        await call.message.edit_text(text=texts.admin_menu.format(call.from_user.first_name),
                                     reply_markup=kb)


@dp.message(NewChatMembersFilter())
async def handle_new_members(message: Message):
    """Handles new user adding and sending notification about group members amount"""
    members_count = await bot.get_chat_member_count(chat_id=message.chat.id)
    chat_id = message.chat.id

    async with DatabaseManager("test.db") as db:
        all_admins = await db.get_all_table_data(table_name="admins")
        group_parameters = {"column": "group_id",
                            "value": chat_id}
        group_data = await db.check_existence(table_name="groups",
                                              parameters=group_parameters)

        if group_data:
            program_id = group_data["program"]

            program_parameters = {"column": "id",
                                  "value": program_id}

            program_data = await db.check_existence(table_name="programs",
                                                    parameters=program_parameters)
            admins_id = [admin["telegram_id"] for admin in all_admins]

            if members_count >= 37:
                if 37 < members_count < 40:
                    text = texts.group_is_almost_full.format(program_data["program_name"], members_count)

                else:
                    text = texts.group_is_almost_full.format(program_data["program_name"], members_count)

                for admin_id in admins_id:
                    await bot.send_message(text=text, chat_id=admin_id)


@dp.callback_query(IsSuperAdmin())
async def handle_admin_adding(call: CallbackQuery):
    """Handle super admin action with adding new admin"""
    potential_admin_id = int(call.data.split("_")[1])

    if "yes" in call.data:
        async with DatabaseManager("test.db") as db:
            potential_admin_data = await db.get_all_user_data(table_name="pending_admins",
                                                              telegram_id=potential_admin_id)
            await db.insert_data(table_name="admins", data=potential_admin_data)
            await db.delete_user_from_db(table_name="pending_admins", telegram_id=potential_admin_id)

        await call.message.edit_text(text=texts.admin_added.format(potential_admin_data["first_name"]))
        await bot.send_message(text=texts.message_for_added_admin, chat_id=potential_admin_id)

    else:
        async with DatabaseManager("test.db") as db:
            potential_admin_data = await db.get_all_user_data(table_name="pending_admins",
                                                              telegram_id=potential_admin_id)
            await db.delete_user_from_db(table_name="pending_admins", telegram_id=potential_admin_id)

        await call.message.edit_text(text=texts.admin_rejected.format(potential_admin_data["first_name"]))
        await bot.send_message(text=texts.message_for_rejected_admin, chat_id=potential_admin_id)


@dp.callback_query()
async def handle_non_authorized_callback(call: CallbackQuery):
    """Handles callback from others users"""
    if call.data == "request_admin":
        await call.message.edit_text(text=texts.waiting_for_approve)

        potential_admin_data = {"first_name": call.from_user.first_name,
                                "last_name": call.from_user.last_name,
                                "telegram_id": call.from_user.id}

        async with DatabaseManager("test.db") as db:
            await db.insert_data(table_name="pending_admins", data=potential_admin_data)
            super_admins = await db.get_all_table_data(table_name="super_admins")

        kb = await get_confirm_admin_kb(telegram_id=call.from_user.id)
        for admin in super_admins:
            await bot.send_message(chat_id=admin["telegram_id"],
                                   text=texts.confirm_admin.format(call.from_user.first_name, call.from_user.id),
                                   reply_markup=kb)

    else:
        await call.message.delete()


@dp.message()
async def greeting_handler(message: Message, state: FSMContext):
    """Handles first time message from user in private chat and updates user record
    in all_users with small group id if it is not updated"""
    user_id = message.from_user.id

    if message.chat.type == "private":
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": user_id}
            admin = await db.check_existence(table_name="admins", parameters=parameters)
            verified_user = await db.check_existence(table_name="all_users", parameters=parameters)

        if admin:
            kb = await get_admin_main_menu_kb()
            await message.answer(text=texts.admin_menu.format(message.from_user.first_name),
                                 reply_markup=kb)
            await state.set_state(AdminState.main_menu)

        elif verified_user:
            kb = await get_submit_training_kb()
            user_name = verified_user["first_name"]
            await state.set_state(UserState.greeted)
            await state.update_data(user_name=user_name)
            await message.answer(text=texts.greeting_for_user.format(user_name),
                                 reply_markup=kb)

        else:
            await message.answer(text=texts.answer_to_unauthorized_user)


async def exe_bot():
    """Function to start a bot"""
    async with DatabaseManager("test.db") as db:
        await db.create_tables()

    logging.info(msg="BOT started")
    await client.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
