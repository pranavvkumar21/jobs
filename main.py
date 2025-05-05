#!/usr/bin/env python3
import os 
from src.authenticate import authenticate_google_api
from src.read_emails import EmailReader
from src.spreadheet_editor import SpreadsheetEditor
from src.agents import Agent
from dotenv import load_dotenv
import datetime
import json
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
    agent = Agent(openai_api_key)
    classify = True
    if creds:
        print("Google API authentication successful.")
    else:
        print("Google API authentication failed.")
        exit(1)
    todays_date = datetime.date.today().strftime("%Y_%m_%d")
    json_file_path = os.path.join(BASE_DIR, f"data/emails_{todays_date}.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as json_file:
            emails = json.load(json_file)
        classify = False
    if classify:
        # Initialize the EmailReader with the OpenAI API key
        email_reader = EmailReader(creds,openai_api_key)
        # Get the emails
        emails = email_reader.get_emails()
        print(f"Found {len(emails)} emails")
        print("Classifying emails...")
        #run primary classifier agent
        emails = agent.run(emails)
        # Save the classified emails to a json file

        with open(json_file_path, "w") as json_file:
            json.dump(emails, json_file, indent=4)
    
    spreadsheet_editor = SpreadsheetEditor(creds, "JOBS Application Tracker", "Job Applications")
    spreadsheet_editor.append_data(emails)
    # for email in emails:
    #     #print(email)
    #     if email['secondary_classification'] == "YES":
    #         #print(email)
    #         spreadsheet_editor.append_data(email)




    