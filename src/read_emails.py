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

        def extract_parts_from_payload(payload):
            text_bits = []
            html_bits = []

            def walk_parts(parts):
                for part in parts:
                    mime_type = part.get("mimeType")
                    body = part.get("body", {})
                    data = body.get("data")

                    if mime_type and mime_type.startswith("multipart/"):
                        nested_parts = part.get("parts", [])
                        walk_parts(nested_parts)

                    elif data:
                        decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        if mime_type == "text/plain":
                            text_bits.append(decoded)
                        elif mime_type == "text/html":
                            html_bits.append(decoded)

            if 'parts' in payload:
                walk_parts(payload['parts'])
            else:
                # Sometimes, emails are not multipart
                mime_type = payload.get('mimeType')
                body = payload.get('body', {})
                data = body.get('data')

                if data:
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    if mime_type == "text/plain":
                        text_bits.append(decoded)
                    elif mime_type == "text/html":
                        html_bits.append(decoded)

            return text_bits, html_bits

        for message in tqdm(messages, desc="Reading emails"):
            full_msg = self.service.users().messages().get(userId='me', id=message['id'], format="full").execute()
            payload = full_msg.get('payload', {})

            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), None)
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), None)

            text_bits, html_bits = extract_parts_from_payload(payload)
            combined_text = "\n".join(text_bits).strip()
            combined_html = "\n".join(html_bits).strip()
            
            
            body = ""

            if combined_text:
                
                body += "\n"+combined_text
            if combined_html:
                soup = BeautifulSoup(combined_html, "html.parser")
                for tag in soup(["style", "script", "link", "img", "svg", "meta", "noscript", "iframe", "head", "a"]):
                    tag.decompose()
                paragraphs = "\n"
                paragraphs = soup.find_all("p")
                paragraphs = ' '.join(p.get_text(strip=True) for p in paragraphs)
                #print(paragraphs)
                body += "\n"+paragraphs
            #print(body)
            body = self.clean_email(body)
            #print("cleaned body - \n")
            #print(body)
            #print("-"*20)
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

        # Remove broken or flattened URLs
        text = re.sub(r'http\S+', '\n', text)
        # Keep only letters, numbers, periods, commas, and spaces
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

        cutoff = int(len(text) * 0.7)
        footer_area = text[cutoff:].lower()
        footer_keywords = [
        "unsubscribe", "privacy policy", "help centre", "terms of service", 
        "replies to this email", "contact customer service", "manage settings",
        "copyright", "©", "capital dock", "grand canal dock"
        ]

        for keyword in footer_keywords:
            idx = footer_area.find(keyword)
            if idx != -1:
                text = text[:cutoff + idx].strip()


        text = re.sub(r'-{2,}', '', text)
        # Collapse multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'-{5,}', '', text)
        text = re.sub(r'\n+', '\n', text)

        # important_keywords = [
        # "position", "application", "hiring", "interview", "selected", 
        # "move forward", "thank you", "role", "opportunity", "applying", "unfortunately"
        # ]

        # text_blocks = text.split("\n")  # break into rough paragraphs
        # good_blocks = [block for block in text_blocks if any(word in block.lower() for word in important_keywords)]

        # text = "\n\n".join(good_blocks)

        
        

        return text.strip()