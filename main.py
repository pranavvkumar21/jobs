#!/usr/bin/env python3
import os 
from src.authenticate import authenticate_google_api
from src.read_emails import EmailReader
from dotenv import load_dotenv
load_dotenv()
scopes = ['https://www.googleapis.com/auth/gmail.readonly',
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
creds_file = os.path.join(BASE_DIR, "credentials/credentials.json")
token_file = os.path.join(BASE_DIR, "credentials/token.json")
openai_api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    # Define the paths to your credentials and token files
    creds = authenticate_google_api(creds_file, token_file, scopes)

    if creds:
        print("Google API authentication successful.")
    else:
        print("Google API authentication failed.")
        exit(1)
    # Initialize the EmailReader with the OpenAI API key
    email_reader = EmailReader(creds,openai_api_key)
    # Get the emails
    emails = email_reader.get_emails()

    