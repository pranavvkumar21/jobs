#!/usr/bin/env python3
import os, json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from tqdm import tqdm
import datetime
from bs4 import BeautifulSoup
import base64
from email import message_from_bytes
import csv, re, unicodedata

class EmailReader:
    def __init__(self, creds,openai_api_key):
        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)
        self.get_config()
    def get_emails(self,date = None):

        if date is None:
            date = (datetime.date.today()-datetime.timedelta(days=0)).strftime("%Y/%m/%d")
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
        emails = self.get_message_details(messages)
        return emails
    
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
        all_emails = []
        for message in tqdm(messages, desc="Reading emails"):
            full_msg = self.service.users().messages().get(userId='me', id=message['id'], format="raw").execute()
            msg_bytes = base64.urlsafe_b64decode(full_msg["raw"])
            email_msg = message_from_bytes(msg_bytes)
            subject = email_msg["subject"]
            sender = email_msg["from"]
            body = None
            parts = []

            if email_msg.is_multipart():
                for part in email_msg.walk():
                    if part.get_content_type().startswith("text/"):
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                decoded = payload.decode(errors="replace")
                                parts.append(decoded)
                        except Exception:
                            continue
            else:
                payload = email_msg.get_payload(decode=True)
                if payload:
                    parts.append(payload.decode(errors="replace"))

            combined = "\n".join(parts)
            soup = BeautifulSoup(combined, "html.parser")
            body = soup.get_text()
            #body = clean_based_on_sender(sender)
            body = self.clean_email(body)
            all_emails.append({
                "subject": subject,
                "sender": sender,
                "body": body
            })
        return all_emails
    def clean_email(self, text):
        # Remove unwanted characters and clean the email content
        if not text:
            return ""

        # Optional: fix broken UTF-8 bytes
        try:
            text = text.encode('latin1', errors='ignore').decode('utf-8', errors='ignore')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        # Remove broken or flattened URLs
        text = re.sub(r'\b(?:http|https|www)[^\s,\.]*', '', text)
        # Keep only letters, numbers, periods, commas, and spaces
        text = re.sub(r'[^A-Za-z0-9., ]+', ' ', text)

        

        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()