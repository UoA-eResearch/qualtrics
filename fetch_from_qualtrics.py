#!/usr/bin/env python3

import requests
import os
import time
from pprint import pprint

# API key from https://auckland.au1.qualtrics.com/Q/QualtricsIdsSection/IdsSection
QUALTRICS_API_KEY = os.getenv("QUALTRICS_API_KEY")
# Also on the same URL as above
SURVEY_ID = os.getenv("SURVEY_ID")
URL = f"https://syd1.qualtrics.com/API/v3/surveys/{SURVEY_ID}/export-responses"

headers = {"X-API-TOKEN": QUALTRICS_API_KEY}

r = requests.post(
    URL, json={"exportResponsesInProgress": True, "format": "csv"}, headers=headers
).json()
pprint(r)

exportProgressId = r["result"]["progressId"]

# Wait for the export to finish, checking every 2s
while r["result"]["status"] == "inProgress":
    time.sleep(2)
    r = requests.get(URL + f"/{exportProgressId}", headers=headers).json()
    pprint(r)

fileId = r["result"]["fileId"]
r = requests.get(URL + f"/{fileId}/file", headers=headers)
pprint(r)
print(len(r.content))

# Save the resulting file
with open("responses.csv.zip", "wb") as f:
    f.write(r.content)
