from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
import json

class GoogleSheetsService:
    def __init__(self):
        credentials_dict = st.secrets["gcp_service_account"]["my_project_settings"]
        self.creds = service_account.Credentials.from_service_account_info(
            credentials_dict, 
            scopes=['https://www.googleapis.com/auth/spreadsheets']  # Updated scope
        )
        self.service = build('sheets', 'v4', credentials=self.creds)

    def read_sheet(self, sheet_id, sheet_name):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=sheet_id, 
            range=f'{sheet_name}!A1:Z1000'
        ).execute()
        return result.get('values', [])

    def update_sheet(self, sheet_id, sheet_name, data):
        body = {
            'values': [data]
        }
        result = self.service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f'{sheet_name}!A1',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return result