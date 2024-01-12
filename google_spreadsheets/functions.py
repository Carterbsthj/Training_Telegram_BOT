"""
Google API Module

This module provides functions for interacting with Google APIs, including Google Sheets and Google Drive.
It includes functions for saving videos to Google Drive and saving data to Google Sheets.

Functions:
    - save_video_to_drive(file_name, local_path): Saves a video file to Google Drive and returns the link to the file.
    - save_data_to_sheet(data, spreadsheet, homework=False): Saves data to a Google Sheet, either for training
      or homework records.

Note:
    The module requires valid credentials and scopes to access Google APIs. Ensure that the service account file
    ('teleram-bot-new-5b0d765313b5.json' in this case) and scopes are correctly configured.

Example:
    # Save a video to Google Drive
    file_link = await save_video_to_drive('video_name', 'local_video.mp4')

    # Save data to a Google Sheet
    data = ['John Doe', '2022-01-12', '50%', 'Evening', '60', '10', file_link]
    await save_data_to_sheet(data, 'spreadsheet_id')

    # Homework example:
    await save_data_to_sheet(data, 'spreadsheet_id', homework=True)
"""


from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import asyncio


SERVICE_ACCOUNT_FILE = 'teleram-bot-new-5b0d765313b5.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)
drive_folder_id = '121cYcAJfW_nGlHcfo80Vpa-3NzoTTTBD'


async def save_video_to_drive(file_name, local_path):
    media = MediaFileUpload(local_path, mimetype='video/mp4')
    file_metadata = {
        'name': f'{file_name}.mp4',
        'parents': [drive_folder_id]
    }
    loop = asyncio.get_event_loop()
    file_drive = await loop.run_in_executor(None,
                                            lambda: drive_service.files().create(body=file_metadata,
                                                                                 media_body=media,
                                                                                 fields='id, webViewLink').execute())

    file_link = file_drive.get('webViewLink')

    os.remove(local_path)
    return file_link


async def save_data_to_sheet(data: list, spreadsheet: str, homework: bool = False):
    """Receives list of user name, date of training, process, training type (evening or morning),
    total duration, meditation duration and video url"""
    values = [data]
    if homework:
        range_ = 'HW!A:G'
    else:
        range_ = 'POP!A:G'
    input_option = 'USER_ENTERED'
    body = {'values': values}

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None,
                               lambda: sheets_service.spreadsheets().values().append(spreadsheetId=spreadsheet,
                                                                                     range=range_,
                                                                                     valueInputOption=input_option,
                                                                                     body=body).execute())
