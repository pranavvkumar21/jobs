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
    def __init__(self,spreadsheet_id=None):
        self.spreadsheet_id = spreadsheet_id
        self.is_column_names_created = False
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