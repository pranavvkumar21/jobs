#!/usr/bin/env python3
import os 
from src.authenticate import authenticate_google_api
from src.read_emails import EmailReader
from src.agents import Agent
from dotenv import load_dotenv
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

    if creds:
        print("Google API authentication successful.")
    else:
        print("Google API authentication failed.")
        exit(1)
    # Initialize the EmailReader with the OpenAI API key
    email_reader = EmailReader(creds,openai_api_key)
    # Get the emails
    emails = email_reader.get_emails()
    #run primary classifier agent
    classified_emails = agent.primary_classifier_agent(emails)
    secondary_classified_emails = agent.secondary_classifier_agent(classified_emails)
    #run job info extractor agent
    job_info_extracted_emails = agent.job_info_extractor_agent(secondary_classified_emails)
    # Save the classified emails to a json file
    json_file_path = os.path.join(BASE_DIR, "classified_emails.json")
    with open(json_file_path, "w") as json_file:
        json.dump(job_info_extracted_emails, json_file, indent=4)



    