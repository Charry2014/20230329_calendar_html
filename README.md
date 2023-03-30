# Read Google Calendar from HomeAssistant AppDaemon

## Introduction

The aim of this project is to provide a simpler view of the upcoming entries in a Google Calendar and have these display in HomeAssistant dashboard, or whereever you want them.

## Credits

The code to read the calendar is taken from Google's sample code, modified a bit.

##
Open items
* A lot of clean up and error handling


# Configuration & Installation

## Google Calendar Authentication

Follow [Google's developer documentation](https://developers.google.com/calendar/api/quickstart/python) to get set up. You need to enable the API and get access to your calendar. This will create the `credentials.json` and a `token.json` files. I have not found a way to create these in HA so I did this on the desktop and copied them over.

## AppDaemon Installation

The docs for AppDaemon in HomeAssistant contain a lot of words, but not much detail how to actually get a script set up and running. Here we go.
* Install AppDaemon following the [instructions](https://community.home-assistant.io/t/home-assistant-community-add-on-appdaemon-4/163259)
* Add Visual Studio Code Server extension to HA. This makes editing a lot easier.
* Edit the file `/config/appdaemon/apps/apps.yaml` and add the following section:
```
calendar_reader:
  module: calendar_reader
  class: CalendarReader
```
* Move the files `calendar_reader.py`, `my_secrets.py`, `credentials.json`, `token.json` into the `/config/appdaemon/apps/apps.yaml` folder.
* Edit `my_secrets.py` to contain the correct CALENDAR_ID. See `fake_secrets.py` for a template what this should look like.
* Create a folder `/config/www/calendar`
* At this point the AppDaeomon script should run - monitor this in [AppDaemon's console](http://localhost:5050/aui/index.html#/state?tab=apps)

## HomeAssistant Configuration
* In HomeAssistant dashboard add a Web Page card and add the following code
````
type: iframe
url: /local/my_location/index6.html
aspect_ratio: 100%
```
* At this point everything should work. It might take a minute or two for everything to sync, but sync it should.


