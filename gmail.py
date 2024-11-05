from google.auth import exceptions
from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.auth.transport.requests
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Path to your downloaded service account key file (JSON)
SERVICE_ACCOUNT_FILE = 'credentials/service_creds.json'

# Scopes for Calendar and Gmail API
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/gmail.send']

def create_service(api_name, api_version, scopes):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes)
    try:
        service = build(api_name, api_version, credentials=credentials)
        return service
    except exceptions.GoogleAuthError as error:
        print(f'An error occurred while creating the service: {error}')
        return None

def create_calendar_event(service):
    # Create a new event on Google Calendar
    event = {
        'summary': 'Sample Event',
        'location': 'Some Location',
        'description': 'This is a sample event.',
        'start': {
            'dateTime': '2024-10-09T09:00:00',
            'timeZone': 'Europe/London',
        },
        'end': {
            'dateTime': '2024-10-09T10:00:00',
            'timeZone': 'Europe/London',
        },
    }

    calendar_service = create_service('calendar', 'v3', SCOPES)
    if calendar_service:
        event_result = calendar_service.events().insert(
            calendarId='primary', body=event).execute()
        print(f'Event created: {event_result.get("htmlLink")}')



def create_message(sender, to, subject, body):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(body)
    message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return raw_message

def authenticate_service_account():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    # Impersonate the user (replace with your Gmail address)
    delegated_credentials = credentials.with_subject('adam.urquhart96@gmail.com')
    return delegated_credentials


def send_email(service):
    # Send an email using Gmail API
    message = {
        'raw': create_message('adam.urquhart96@gmail.com',
                              'adam.urquhart96@gmail.com',
                              'Tennis (auto)',
                              'Tennis has been booked for ___')
    }

    credentials = authenticate_service_account()
    gmail_service = build('gmail', 'v1', credentials=credentials)
    if gmail_service:
        try:
            message_sent = gmail_service.users().messages().send(userId='me', body=message).execute()
            print(f'Message sent successfully! Message Id: {message_sent["id"]}')
        except Exception as error:
            print(f'An error occurred while sending email: {error}')

if __name__ == '__main__':
    # create_calendar_event(None)  # To create an event
    send_email(None)  # To send an email
