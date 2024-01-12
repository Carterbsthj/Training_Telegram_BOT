"""This module contains bot related general functions and telethon client handlers"""

import asyncio
import logging

from bot.main import bot, client
from datetime import datetime
from database.main import DatabaseManager
from bot.texts import (small_group_notification_text, user_notification_for_more_days, user_notification_for_one_day,
                       new_small_group_member_greeting)
from telethon import events
from google_spreadsheets.functions import save_video_to_drive, save_data_to_sheet
from telethon.tl.functions.messages import CreateChatRequest, ExportChatInviteRequest
from go_high_level.api_calls import change_stage
from bot.keyboards import get_submit_training_kb

logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


async def make_notifications():
    """
    Sends daily notifications to all users about their non-submitted Practices of the Day (POPs) at a specific time.

    This function checks each user's last practice date and sends a reminder if they haven't submitted their practice
    for the current day.
    For users who haven't practiced for multiple days, different notifications are sent based on the number of days
    missed.
    Additionally, if a user misses three or more days, their status is updated in an external system via an API call.
    """
    target_hour = 12  # You can specify any desired hour
    while True:
        try:
            current_day = datetime.now().date()
            current_hour = datetime.now().time().hour
            if current_hour == target_hour:
                async with DatabaseManager("test.db") as db:
                    all_users = await db.get_all_table_data(table_name="all_users")

                    for user in all_users:
                        try:
                            query = f"""SELECT * FROM programs WHERE id = {user['user_program']}"""
                            user_program = await db.custom_query(query=query)

                            if user['last_practice'] != str(current_day):
                                if str(user['last_practice']).isdigit():
                                    if int(user['last_practice']) >= 1:
                                        data = {"last_practice": str(int(user['last_practice']) + 1)}
                                        await db.update_data(table_name="all_users",
                                                             data=data,
                                                             telegram_id=user["telegram_id"])

                                    new_last_practice = str(int(user['last_practice']) + 1)
                                    user['last_practice'] = new_last_practice

                                    if user['last_practice'] == 1:
                                        text = user_notification_for_one_day
                                    else:
                                        text = user_notification_for_more_days.format(user['last_practice'])

                                    kb = await get_submit_training_kb()
                                    await bot.send_message(text=text,
                                                           chat_id=user["telegram_id"],
                                                           reply_markup=kb)

                                    if int(user['last_practice']) >= 3:
                                        if int(user['last_practice']) == 3:
                                            pipeline_id = user_program[0]["ghl_pipeline_id"]
                                            next_stage_id = user_program[0]["ghl_no_pop_id"]
                                            opp_id = user["ghl_opp_id"]
                                            await change_stage(opportunity_id=opp_id,
                                                               stage_id=next_stage_id,
                                                               pipeline_id=pipeline_id)

                                        await bot.send_message(text=small_group_notification_text.format(
                                            user["first_name"],
                                            user["last_practice"]
                                        ),
                                            chat_id=user["small_group_id"])
                                else:
                                    data = {"last_practice": "1"}
                                    await db.update_data(table_name="all_users",
                                                         data=data,
                                                         telegram_id=user["telegram_id"])
                                    kb = await get_submit_training_kb()
                                    await bot.send_message(text=user_notification_for_one_day,
                                                           chat_id=user["telegram_id"],
                                                           reply_markup=kb)
                        except Exception as e:
                            logging.error(msg=f"An error occurred during notifications sending: {e}. "
                                              f"User {user['first_name']} ({user['telegram_id']})")

                await asyncio.sleep(3600)

            await asyncio.sleep(600)

        except Exception as e:
            logging.error(msg=f"An error occurred during notifications sending: {e}")


@client.on(events.ChatAction)
async def handler(event: events.chataction.ChatAction.Event):
    """
    Handles new user join events in small groups.

    When a new user joins a small group, this function checks if the user is registered in the system.
    If registered, it sends a greeting message to the group, introducing the user and the training tracker bot.
    """
    if event.user_joined:
        chat_id = event.chat_id
        user_id = event.user_id

        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": user_id}
            user_data = await db.check_existence(table_name="all_users", parameters=parameters)

            bot_link = f'<a href="@MiaFlow60Bot">training tracker</a>'

            if user_data and user_data["small_group_id"] == chat_id:
                await client.send_message(entity=chat_id,
                                          message=new_small_group_member_greeting.format(user_data["first_name"],
                                                                                         bot_link),
                                          link_preview=False,
                                          parse_mode="HTML")


@client.on(events.NewMessage(chats=bot.id))
async def video_receiver(event):
    """
    Handles receiving and processing video messages sent to the bot.

    This function is triggered when a video message is received. It extracts necessary information from the message,
    downloads the video, and uploads it to Google Drive. It then stores the relevant data, including the video URL,
    in a Google Sheets spreadsheet.
    """
    if event.message.video:
        data = event.raw_text.split(";")
        user_id = data[1]
        async with DatabaseManager("test.db") as db:
            parameters = {"column": "telegram_id",
                          "value": int(user_id)}
            user_data = await db.check_existence(table_name="all_users", parameters=parameters)
            query = f"""SELECT group_spreadsheet_id 
                            FROM groups 
                            WHERE group_id = {user_data['main_group_id']}"""
            spreadsheet_data = await db.custom_query(query)
            spreadsheet_id = spreadsheet_data[0]["group_spreadsheet_id"]

        file_name = f"{data[0]}_{data[3]}"
        local_path = f"{file_name}.mp4"
        await client.download_media(event.message, local_path)
        try:
            url = await save_video_to_drive(file_name=file_name, local_path=local_path)
        except Exception as e:
            print("Video upload failed!")
            logging.error(msg=f"An error occurred during video upload: {e}. "
                              f"Video upload from {data[0]}")
            try:
                url = await save_video_to_drive(file_name=file_name, local_path=local_path)
            except Exception as e:
                print("Video upload failed again!")
                logging.error(msg=f"An error occurred during video upload: {e}. "
                                  f"Video upload from {data[0]} failed second time in a row")
                url = "Failed download."

        data.append(url)
        await save_data_to_sheet(data=data, spreadsheet=spreadsheet_id)
        print("Video saved, data stored!")


async def create_main_group(group_title: str):
    """
    Creates a main group chat with the training bot and all admins.

    Args:
        group_title (str): The title of the main group to be created.

    Returns:
        dict: A dictionary containing the chat ID and invite link of the newly created main group.
    """
    users = [bot.id]

    async with DatabaseManager("test.db") as db:
        all_admins = await db.get_all_table_data(table_name="admins")

    for admin in all_admins:
        user_entity = await client.get_entity(admin["telegram_id"])
        users.append(user_entity)

    result = await client(CreateChatRequest(users=users, title=group_title))

    chat_id = -result.chats[0].id

    invite_link = await client(ExportChatInviteRequest(
        peer=chat_id,
        legacy_revoke_permanent=True
    ))

    link = invite_link.link

    chat_data = {"chat_id": chat_id,
                 "invite_link": link}

    return chat_data


async def create_small_group(group_title: str):
    """
    Creates a small group chat with the training bot and a predefined set of users.

    Args:
        group_title (str): The title of the small group to be created.

    Returns:
        dict: A dictionary containing the chat ID and invite link of the newly created small group.
    """
    users = [bot.id]  # You can add any desired amount of Telegram user's id's.
    # Make sure they have a chat with you service account!

    result = await client(CreateChatRequest(users=users, title=group_title))

    chat_id = -result.chats[0].id

    invite_link = await client(ExportChatInviteRequest(
        peer=chat_id,
        legacy_revoke_permanent=True
    ))

    link = invite_link.link

    chat_data = {"chat_id": chat_id,
                 "invite_link": link}

    return chat_data
