#!/usr/bin/env python3
import os, json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import datetime

class EmailReader:
    def __init__(self, creds,openai_api_key):
        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0)
        self.get_config()
    def get_emails(self,date = None):

        if date is None:
            date = (datetime.date.today()-datetime.timedelta(days=2)).strftime("%Y/%m/%d")
        query = f"after:{date} "
        label_query = self.convert_category_to_query(self.config['gmail_filters'].get('category',[]))
        print(label_query)
        if label_query:
            query += label_query
        print(f"Query: {query}")
        print(f"Categories: {self.config['gmail_filters'].get('categories',[])}")
        results = self.service.users().messages().list(userId='me', q=query).execute()
        # results = self.service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        print(len(messages), "messages found")
        self.get_message_details(messages)
        return messages
    
    def get_config(self):
        #check if config file exists
        config_file = "config/config.json"
        if not os.path.exists(config_file):
            print(f"Config file {config_file} not found.")
            return None
        with open(config_file, "r") as f:
            self.config = json.load(f)
    def convert_category_to_query(self, labels):
        categories = ["social", "promotions", "forums"]
        query = " "
        for category in categories:
            if category not in labels:
                query += f"-category:{category} "
        return query
    def get_message_details(self,messages):
        for message in messages:
            full_msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
            headers = full_msg['payload']['headers']
            subject_list = [h["value"] for h in headers if h["name"].lower() == "subject"]
            subject = subject_list[0] if subject_list else "(No Subject)"  
            print(f"Subject: {subject}") 

        

        
