#!/usr/bin/env python3
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import src.conditional_formatting as cf


"""Spreadsheet Editor for Google Sheets and Drive.
This script allows you to create, update, and manage Google Sheets and Drive files. it will have
the following features:
1. Create a new Google Sheet.
2. Update an existing Google Sheet with new data. similar to appending in csv.
apply conditional formatting to the sheet.
list column names and their respective indexes.
search for a specific companies in the sheet."""


class SpreadsheetEditor:
    def __init__(self, creds,workspace_folder_name, spreadsheet_title, column_names=["Sl.no","Job Title", "Company Name", "Location", "Application Status"]):
        """Initialize the SpreadsheetEditor with Google Sheets and Drive API credentials."""
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.sheets_service = build('sheets', 'v4', credentials=creds)
        self.column_names = column_names
        self.create_workspace(folder_name=workspace_folder_name)
        self.create_spreadsheet(spreadsheet_title)
        self.is_column_names_created = False
    def create_workspace(self, folder_name):
        # if workspace folder already exists, return the id else create a new one
        """Create a new folder in Google Drive to store the spreadsheet."""
        self.workspace_folder_id = self.get_folder_id(folder_name)
        print(f"workspace exists with id: {self.workspace_folder_id}")
        if not self.workspace_folder_id:
            print(f"workspace folder {folder_name} not found. Creating a new one.")
            self.workspace_folder_id = self.create_folder_path(folder_name)
        #print(f"Workspace folder ID: {self.workspace_folder_id}")

    def get_folder_id(self, path):
        parent = 'root'
        for name in path.strip('/').split('/'):
            q = f"'{parent}' in parents and name = '{name}' and mimeType = 'application/vnd.google-apps.folder'"
            res = self.drive_service.files().list(q=q, fields="files(id)").execute()
            files = res.get('files')
            if not files:
                return None
            parent = files[0]['id']
        return parent

    def create_folder_path(self, path):
        parent = 'root'
        for name in path.strip('/').split('/'):
            q = f"'{parent}' in parents and name = '{name}' and mimeType = 'application/vnd.google-apps.folder'"
            res = self.drive_service.files().list(q=q, fields="files(id)").execute()
            files = res.get('files')
            if files:
                parent = files[0]['id']
            else:
                file_metadata = {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent]
                }
                file = self.drive_service.files().create(body=file_metadata, fields='id').execute()
                print(file)
                parent = file['id']
        return parent  # ID of the final folder

    def create_spreadsheet(self, title):

        # check if spreadsheet exists in folder id
        q = f"'{self.workspace_folder_id}' in parents and name = '{title}' and trashed = false"
        res = self.drive_service.files().list(q=q, fields="files(id)").execute()
        if res['files']:
            print(f"Spreadsheet {title} already exists.")
            self.spreadsheet_id = res['files'][0]['id']
        else:
            file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [self.workspace_folder_id]
            }
            spreadsheet = self.drive_service.files().create(body=file_metadata, fields="id").execute()
            
            print(f"Spreadsheet {title} created.")
            self.spreadsheet_id = spreadsheet['id']
            self.create_column_names()
            # apply conditional formatting
        sheet_metadata = self.sheets_service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']
        rule = cf.colour_application_status(sheet_id)
        self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=rule
        ).execute()
        print(f"Conditional formatting applied.")

    def append_data(self,emails):
        """Append data to the existing Google Sheet."""
        self.create_column_names()
        data = []
        for email in emails:
            if 'job_info' in email:
                row = email['job_info']
                # print("type of row:",type(row))
                # print(f"row: {row}")
                row = [" ",row['job_title'], row['company_name'], row['location'], row['application_status']]
                data.append(row)
        data = self.update_status(data)
        self.create_index_column(start_row=2, column_index=0, reference_column="B")
        body = {
            "values": data
        }
        self.sheets_service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range="A3",
            valueInputOption="RAW",
            body=body
        ).execute()
        print(f"Data of size {len(data)} appended to the spreadsheet.")
        self.create_index_column(start_row=2, column_index=0, reference_column="B")
        # apply conditional formatting

    def create_column_names(self):
        """Create column names in the first row of the Google Sheet."""
        body = {
            "values": [self.column_names]
        }
        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range="A1",
            valueInputOption="RAW",
            body=body
        ).execute()
        self.is_column_names_created = True
        print(f"Column names {self.column_names} created in the spreadsheet.")

    def create_index_column(self, start_row, column_index, reference_column):
        """Create an index column in the Google Sheet."""
        response = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range="B:B",
            majorDimension="COLUMNS"
        ).execute()

        last_row = len(response.get("values", [[]])[0]) + 3  # offset by row 3

        # 2. Clear A3 downward
        self.sheets_service.spreadsheets().values().clear(
            spreadsheetId=self.spreadsheet_id,
            range="A3:A",
        ).execute()

        # 3. Insert ARRAYFORMULA in A3
        formula = f'=ARRAYFORMULA(IF(ROW(A3:A) <= {last_row}, IF(NOT(ISBLANK(B3:B)), ROW(B3:B)-2, ""), ""))'

        requests = [{
            "updateCells": {
                "rows": [{
                    "values": [{
                        "userEnteredValue": {
                            "formulaValue": formula
                        }
                    }]
                }],
                "fields": "userEnteredValue",
                "start": {
                    "sheetId": 0,
                    "rowIndex": 2,      # A3
                    "columnIndex": 0    # Column A
                }
            }
        }]

        self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={"requests": requests}
        ).execute()
    def update_status(self, data):
        # Update the status of a job application in the Google Sheet.

        #get data from the sheet
        sheets_data = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range="A3:G",
        ).execute().get("values", [])
        to_remove = []
        # check if job title and company name are in the sheet
        for job_row in data:
            flag = False
            for sheet_row in sheets_data:
                #print("sheet_row:",sheet_row)
                if job_row[1].strip().lower() == sheet_row[1].strip().lower() and job_row[2].strip().lower() == sheet_row[2].strip().lower():
                    # update the status
                    flag = True
                    #print(f"Updating status of {job_row[1]} at {job_row[2]}")
                    self.update_row(row_index=int(sheet_row[0])+3, column="A", value=job_row)
            if flag:
                to_remove.append(job_row)
        for job_row in to_remove:
            data.remove(job_row)
        return data

    def update_row(self, row_index, column, value):
        """Update a specific cell in the Google Sheet."""
        print(f"row_index: {row_index}, column_index: {column}, value: {value}")
        body = {
            "values": [value]
        }
        self.sheets_service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f"{column}{row_index}",
            valueInputOption="RAW",
            body=body
        ).execute()
        print(f"Cell {column}{row_index} updated to {value}.")