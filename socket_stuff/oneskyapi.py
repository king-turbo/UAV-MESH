

import requests
import json
from io import StringIO
from urllib.parse import urlparse
from datetime import datetime, timezone


print(datetime.utcnow())
with open ("mwalton.token", "r") as toke:
    token = toke.read()



dataa = '''{
  "name": "Hello World",
  "description": "This is a description.",
  "aircraftType": "MULTI_ROTOR",
  "altitudeReference": "WGS84",
  "longitude": 89.12345678,
  "latitude": 78.98765432,
  "altitude": 350,
  "radius": 500,
  "maxHeight": 120,
  "startTime": "2019-12-03T10:15:30Z",
  "stopTime": "2019-12-03T10:16:40Z"
}'''

url = 'https://utm.onesky.xyz/api/flights/point'

# session = requests.Session()
# session.headers.update({'Authorization': 'Bearer {}'.format(token),'Content-type': 'application/json'})
# r = session.post(url, data=dataa, stream=True)
# print(r.text)


class OneSkyAPI:
    def __init__(self, token):
        self.token = token
        self.session = self.createSession()

    def createSession(self):
        session = requests.Session()
        session.headers.update({'Authorization': 'Bearer {}'.format(self.token),
            'Content-type': 'application/json'})
        return session

    def currentTime(self):

        return (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def createPointFlight(self, data):
        # self.session.headers.update({'Content-type':"application/json"})
        url = 'https://utm.onesky.xyz/api/flights/point'
        response = self.session.post(url, data=data, stream=True)
        if response.status_code != 201:
            print("Something's wrong")
        else:
            self.GUFI = response.content.decode('utf-8').split('/')[-1]

    def createFlightPlanSimple(self, data):
        url = "https://utm.onesky.xyz/api/flights/pathSimple"
        response = self.session.post(url, data=data)
        if response.status_code != 201:
            print("Something's wrong")
        else:
            self.GUFI = response.content.decode('utf-8').split('/')[-1]

    def update(self):
        orig = 89.12345678

        while True:
            orig = orig + .000001
            url = 'https://utm.onesky.xyz/api/flights/log/telemetry/' + self.GUFI

            data = '''{
              "eventType": "TELEMETRY",
              "timestamp": "''' + self.currentTime()+'''",
              "referenceLocation":
              {
                 "longitude":''' + str(orig)+''',
                 "latitude": 78.98765432,
                 "altitude": 410
              },
              "altitudeReference": "AGL",
              "data": "any extra data"
            }'''
            print(orig)
            response = self.session.post(url, data=data, stream=True)
            print(response.content)



data2 = '''{
  "name": "Hello World",
  "description": "This is a description.",
  "aircraftType": "MULTI_ROTOR",
  "altitudeReference": "WGS84",
  "waypoints": 
  [
    {
        "longitude": 89.12345678,
        "latitude": 78.98765432,
        "altitude": 410
    },
    {
        "longitude": 88.98765432,
        "latitude": 79.12345678,
        "altitude": 430
    }
  ],
  "startTime": "2011-12-03T10:15:30Z",
  "speed": 5
}'''


#
# # headers = {'Authorization': 'Bearer ' + token}
#
# # GUFI = 'test'
# url = 'https://utm.onesky.xyz/api/flights/point'
#
flight = OneSkyAPI(token)
flight.createFlightPlanSimple(data2)
flight.update()
