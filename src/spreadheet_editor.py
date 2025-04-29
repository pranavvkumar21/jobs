#!/usr/bin/env python3
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


"""Spreadsheet Editor for Google Sheets and Drive.
This script allows you to create, update, and manage Google Sheets and Drive files. it will have
the following features:
1. Create a new Google Sheet.
2. Update an existing Google Sheet with new data. similar to appending in csv.
apply conditional formatting to the sheet.
list column names and their respective indexes.
search for a specific companies in the sheet."""


class SpreadsheetEditor:
    def __init__(self, creds,workspace_folder_name, spreadsheet_title):
        """Initialize the SpreadsheetEditor with Google Sheets and Drive API credentials."""
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.sheets_service = build('sheets', 'v4', credentials=creds)
        self.create_workspace(folder_name=workspace_folder_name)
        self.create_spreadsheet()
        self.is_column_names_created = False
    def create_workspace(self, folder_name):
        # if workspace folder already exists, return the id else create a new one
        """Create a new folder in Google Drive to store the spreadsheet."""
        folder_id = self.get_folder_id(self.drive_service, folder_name)
        if not folder_id:
            self.workspace_folder_id = self.create_folder(self.drive_service, folder_name)
        self.workspace_folder_id = folder_id

    def get_folder_id(service, path):
        parent = 'root'
        for name in path.strip('/').split('/'):
            q = f"'{parent}' in parents and name = '{name}' and mimeType = 'application/vnd.google-apps.folder'"
            res = service.files().list(q=q, fields="files(id)").execute()
            files = res.get('files')
            if not files:
                return None
            parent = files[0]['id']
        return parent

    def create_folder_path(service, path):
        parent = 'root'
        for name in path.strip('/').split('/'):
            q = f"'{parent}' in parents and name = '{name}' and mimeType = 'application/vnd.google-apps.folder'"
            res = service.files().list(q=q, fields="files(id)").execute()
            files = res.get('files')
            if files:
                parent = files[0]['id']
            else:
                file_metadata = {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent]
                }
                file = service.files().create(body=file_metadata, fields='id').execute()
                parent = file['id']
        return parent  # ID of the final folder


    def create_spreadsheet(self, title, folder_id=None):
        """Create a new Google Sheet with the given title."""
        spreadsheet = {
            "properties": {"title": title },
            "parents": [folder_id] if folder_id else [],
        }
        spreadsheet = self.sheets_service.spreadsheets().create(body=spreadsheet, fields="spreadsheetId").execute()
        return spreadsheet.get("spreadsheetId")
    def append_data(self,data: list):
        """Append data to the existing Google Sheet."""
        body = {
            "values": data
        }
        self.sheets_service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range="A1",
            valueInputOption="RAW",
            body=body
        ).execute()
    def create_column_names(self, column_names: list):
        """Create column names in the first row of the Google Sheet."""
        body = {
            "values": [column_names]
        }
        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range="A1",
            valueInputOption="RAW",
            body=body
        ).execute()
        self.is_column_names_created = True
    def create_index_column(self, start_row, column_name, reference_column):
        """Create an index column in the Google Sheet."""
        requests = [
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": 0,
                            "startRowIndex": start_row - 1,
                            "startColumnIndex": column_name,
                            "endColumnIndex": column_name + 1
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": [{"userEnteredValue": f"=ISBLANK({reference_column}{start_row})"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 1, "green": 0.9, "blue": 0.9}
                            }
                        }
                    },
                    "index": 0
                }
            }
        ]

        self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={"requests": requests}
        ).execute()