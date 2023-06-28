# qualtrics
Python scripts to call the Qualtrics API, to retrieve unfinished survey responses, and send reminder emails

### Installation

`pip install -r requirements.txt`

### Setup

1. Get an API key & Survey ID from https://auckland.au1.qualtrics.com/Q/QualtricsIdsSection/IdsSection
2. Set these as the environment variables QUALTRICS_API_KEY and SURVEY_ID
3. You should now be able to fetch a CSV of responses from your Qualtrics survey with the `./fetch_from_qualtrics.py`
4. This script writes to `responses.csv.zip`
5. The script `send_emails.py` reads `responses.csv.zip`, filters to users who consented to email reminders and haven't touched the survey in 7 days, and sends them a reminder email if they haven't already received one.

### Automation

I would recommend using cron to do this. Here's an example:

```sh
# minute hour day month day_of_week    command
     0    10   *    *        *         ./fetch_from_qualtrics.py && ./send_emails.py
```