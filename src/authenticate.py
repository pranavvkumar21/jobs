#!/usr/bin/env python3
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
"""
Authenticate with Google API and OpenAI API.
This script handles the authentication process for both Google and OpenAI APIs."""


def authenticate_google_api(creds_file, token_file,scopes):
    """
    Authenticate with Google API using OAuth 2.0.
    Args:
        creds_file (str): Path to the client secrets file.
        token_file (str): Path to the token file.
        scopes (list): List of scopes for the API access.
    Returns:
        service: Authenticated Google API service instance.
    """
    creds = None
    if os.path.exists(token_file):
        print(f"Token file {token_file} found. Loading credentials.")
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    else:
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, scopes)
        creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    return creds
