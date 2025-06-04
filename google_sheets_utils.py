import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_google_sheets_service():
    """Get or create Google Sheets service."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service

def read_qa_data_from_sheet(spreadsheet_id, range_name):
    """
    Read QA data from Google Sheet.
    
    Args:
        spreadsheet_id (str): The ID of the spreadsheet to read from
        range_name (str): The A1 notation of the values to retrieve
    
    Returns:
        pandas.DataFrame: The QA data as a DataFrame
    """
    try:
        service = get_google_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('No data found.')
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        
        # Convert numeric columns
        numeric_columns = [
            'P0 issues Open', 'P0 issues closed',
            'P1 Issues Open', 'P1 Issues Closed',
            'Rest Issues Open', 'Rest Issues Closed'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Convert list columns
        list_columns = ['Test Type', 'Bug Titles', 'Test Cases']
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.split(',') if isinstance(x, str) else [])
        
        return df
        
    except Exception as e:
        print(f"Error reading from Google Sheet: {str(e)}")
        return None 