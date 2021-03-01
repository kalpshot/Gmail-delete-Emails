from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']


def connect():
    creds = None
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

    service = build('gmail', 'v1', credentials=creds)

    return service


def move_to_trash(service):
    result = service.users().messages().list(
        userId='me', labelIds="UNREAD").execute()

    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(
            userId='me', labelIds="UNREAD", pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
            # can delete a maximum of 1000 emails at a a time
            if len(messages) == 1000:
                break

    # check for unread emails
    if messages != []:
        service.users().messages().batchModify(userId='me',
                                               body={
                                                   'ids': [msg['id'] for msg in messages],
                                                   # 'removeLabelIds': ['UNREAD'],
                                                   'addLabelIds': ['TRASH']
                                               }).execute()
    return messages


con = connect()
move_to_trash(con)
