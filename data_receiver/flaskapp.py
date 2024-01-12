"""
This module defines a Flask web application that serves as a webhook endpoint for Kajabi.

The application receives webhook data from Kajabi, extracts relevant information, and inserts it into a database.

Routes:
- `/`: Displays a simple "Hello, World!" message.
- `/kajabi-webhook` (POST): Receives Kajabi webhook data, processes it, and inserts it into a database.

Functions:
- `exe_flask()`: Runs the Flask application, listening on host '0.0.0.0' and port 5000.

This application is designed to handle Kajabi webhook events and store subscriber information in a database.
"""


from flask import Flask, request, jsonify
from database.main import DatabaseManager

app = Flask(__name__)


@app.route('/')
def hello():
    """
    A simple route that returns a greeting message.

    Returns:
        str: A greeting message.
    """
    return 'Hello, World!'


@app.route('/kajabi-webhook', methods=['POST'])
async def kajabi_webhook():
    """
    Handle incoming webhook data from Kajabi.

    This function processes JSON data received from a Kajabi webhook, extracts relevant information, and inserts it into
    a database table named "subscribers".

    Returns:
        dict: A JSON response indicating the status of the webhook processing.
    """
    try:
        data = request.get_json()
        member_email = data["payload"]["member_email"].lower()
        member_first_name = data["payload"]["member_first_name"]
        member_last_name = data["payload"]["member_last_name"]
        offer_title = data["payload"]["offer_title"]

        member_data = {"email": member_email,
                       "first_name": member_first_name,
                       "last_name": member_last_name,
                       "program_title": offer_title}

        async with DatabaseManager("test.db") as db:
            await db.insert_data(table_name="subscribers", data=member_data)

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"{e} exception has raised.")


def exe_flask():
    """
    Run the Flask web application to listen for incoming requests.

    This function starts the Flask application and listens on host '0.0.0.0' and port 5000. It serves as the entry
    point for running the application.

    Returns:
        None
    """
    app.run(host='0.0.0.0', port=5000)
