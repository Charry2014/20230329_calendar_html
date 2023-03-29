# AppDaemon version testing
FILE_NAME = 'calendar_reader'

if __name__ == FILE_NAME: 
    import appdaemon.plugins.hass.hassapi as hass
else:
    pass

from collections import defaultdict
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import re
from string import Template
from my_secrets import CALENDAR_ID

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Some platform abstraction
# this is on the AppDaemon target
if __name__ == FILE_NAME: 
    TOKEN_JSON = '/config/appdaemon/apps/token.json'
    CREDENTIALS_JSON = '/config/appdaemon/apps/credentials.json'    
    INDEX_HTML = '/config/appdaemon/www/index.html'
    BASE_CLASS = hass.Hass
else:
    # Local debugging
    TOKEN_JSON = 'data/token.json'
    CREDENTIALS_JSON = 'data/credentials.json'    
    INDEX_HTML = 'test/index.html'
    BASE_CLASS = object

HTML_TEMPLATE_START = '''<html>
<head>
<title>Lesmartins Calendar</title>
</head> 
<body>
'''
HTML_TEMPLATE_END = '''
<p>- End -</p> 
</body>
</html>'''

# starts the list of day entries
HTML_TEMPLATE_DAY_TITLE = '<h1>${day} ${date}</h1>'
# Calendar line entry
HTML_TEMPLATE_CALENDAR_ENTRY = '<li>${start} ${end} ${description}</li>'


class HelloWorld(BASE_CLASS):

    if __name__ == FILE_NAME: 
        def initialize(self):
            self.log(f"Hello from AppDaemon {__name__}")
            self.run_hourly(self.run_task, None)
    else:
        def initialize(self):
            # self.log(f"Hello from local {__name__}")
            self.run_task(None)


    def run_task(self, kwargs):
        d = self.read_calendar()
        self.write_html(d)
        # self.log("I wrote some HTML!")


    def read_calendar(self) -> defaultdict:
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(TOKEN_JSON):
            creds = Credentials.from_authorized_user_file(TOKEN_JSON, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_JSON, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_JSON, 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            # Try to read Lesmartins calendar
            events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                                  maxResults=20, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])
        
            # if not events:
            #     print('No upcoming events found.')
            #     return

            # Build a dictionary of lists of events, keyed on start date, sorted by start time
            devents = defaultdict(list)
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date')) # 2022-09-20T16:00:00+02:00 or 2022-09-20
                event['start_date'] = re.match("^(\d+\-\d+\-\d+)", start).groups()[0] # Extract start date
                devents[event['start_date']].append(event)
        except HttpError as error:
            print('An error occurred: %s' % error)

        return devents


    def write_html(self, devents: defaultdict):
        values = {}
        with open(INDEX_HTML, 'w') as f:
            f.write(HTML_TEMPLATE_START)
            for k in devents.keys():
                values['day'] = datetime.datetime.strptime(k, '%Y-%m-%d').strftime('%A')
                values['date'] = k
                t = Template(HTML_TEMPLATE_DAY_TITLE)
                f.write(t.substitute(values))

                f.write('<ul>')
                t = Template(HTML_TEMPLATE_CALENDAR_ENTRY)
                for event in devents[k]:
                    values = {}
                    try:
                        values['start'] = re.search("T(\d\d:\d\d):", event['start'].get('dateTime', event['start'].get('date'))).group(1) # 2022-09-20T16:00:00+02:00
                        values['end']   = re.search("T(\d\d:\d\d):", event['end'].get('dateTime', event['end'].get('date'))).group(1)
                    except AttributeError:
                        values['start'] = ''
                        values['end']   = ''
                    values['description'] = event['summary']
                    f.write(t.substitute(values))
                f.write('</ul>')
            f.write(HTML_TEMPLATE_END)


    # def main():
    #     d = read_calendar()
    #     write_html(d)


if __name__ == '__main__':
    c = HelloWorld()
    c.initialize()
