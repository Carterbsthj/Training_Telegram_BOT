
# Training Telegram BOT

## Overview
This project involves a Telegram bot with various functionalities, including Flask web application integration, data handling, and interactions with external services like databases and Google Spreadsheets.

## Getting Started
### Prerequisites
- Python 3.x
- Pip (Python package manager)

### Installation
1. Clone the repository to your local machine.
2. Navigate to the project directory and set up a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix or MacOS: `source venv/bin/activate`
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
### Running the Flask Application
To start the Flask application, run:
```
python exe_flask.py
```

### Training the Bot
To train the bot, execute:
```
python exe_training_bot.py
```

## Components
### exe_flask.py
This script is intended for running a Flask application. [Add specific details here.]

### exe_training_bot.py
Contains executable statements for initializing and running the bot. It integrates various functionalities like bot handlers, a welcome bot, and notification functions.

### bot/
A directory containing the core scripts of the bot:
- **main.py**: Manages the main bot operations.
- **texts.py**: Manages text templates and responses.
- **states.py**: Handles different states of the bot.
- **filters.py**: Filters messages or data.
- **handlers.py**: Handles different bot events and actions.
- **settings.py**: Contains configuration settings.
- **functions.py**: Various utility functions.
- **keyboards.py**: For creating custom bot interfaces.

### data_receiver/
- **flaskapp.py**: A Flask application script, likely for handling webhooks or APIs.

### database/
Scripts related to database functionalities.

### go_high_level/
- **api_calls.py**: Functions for making external API calls.

### google_spreadsheets/
- **functions.py**: Integrations with Google Spreadsheets.

### welcome_bot/
A separate module for a bot dedicated to welcoming users, structured similarly to the main bot.

## Contributing
[Instructions for contributing to the project.]

## License
[License information, if any.]

## Contact
For any queries or contributions, please contact [Your Name] at [Your Email].
