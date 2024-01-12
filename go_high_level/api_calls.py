"""
This module contains integration functionality with GoHighLevel.
Due to the constraints of a Non-Disclosure Agreement (NDA),
specific details of this section cannot be disclosed or shared publicly.
"""

import requests
from database.main import DatabaseManager


location_id = ''


async def update_token_from_ghl():
    pass


async def make_api_request(url, method, payload=None):
    pass


async def create_user(first_name: str, last_name: str, email: str):
    pass


async def create_opportunity(username: str, user_id: str, default_stage_id: str, pipeline_id: str):
    pass


async def change_stage(opportunity_id: str, stage_id: str, pipeline_id):
    pass


async def delete_user(user_id: str):
    pass


async def get_pipeline(program_title: str):
    pass
