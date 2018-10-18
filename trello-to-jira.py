import os
from trello import TrelloClient
from dotenv import load_dotenv

load_dotenv()

twilioApiKey = os.getenv("TWILIO_API_KEY")
twilioApiToken = os.getenv("TWILIO_API_TOKEN")


