#!/usr/bin/env python3

import pandas as pd
from pprint import pprint
from jinja2 import Environment, FileSystemLoader
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

environment = Environment(loader=FileSystemLoader(""))
template = environment.get_template("reminder_template.txt")

df = pd.read_csv("responses.csv.zip")

df.EndDate = pd.to_datetime(df.EndDate, errors="coerce", utc=True).dt.tz_convert("Pacific/Auckland")
df["EndDate+1week"] = df.EndDate + pd.Timedelta(weeks=1)

try:
    already_sent = pd.read_csv("sent_emails.csv")
    already_sent["sent_at"] = pd.to_datetime(already_sent["sent_at"], errors="coerce")
except FileNotFoundError:
    already_sent = pd.DataFrame(columns=["email", "sent_at"])

df.drop_duplicates(subset="Q11_4", inplace=True)
df.dropna(subset=["Q11_4"], inplace=True)

# Filter to users that consented to email reminders
df = df[df["Q4"] == "1"]

print(df[["StartDate", "EndDate", "EndDate+1week", "UN", "First", "Last", "Q11_4", "Q4"]].sort_values(by="EndDate"))

def check_sent_email_recently(email):
    already_sent_to_this_person = already_sent[already_sent["email"] == email]
    if len(already_sent_to_this_person) == 0:
        return False
    last_email = already_sent_to_this_person.sent_at.max()
    if (pd.Timestamp.now() - last_email) > pd.Timedelta(days=30):
        return False
    else:
        return True

# Filter to users that haven't touched the survey in 1 week and haven't already had a reminder recently
df = df[(df["EndDate+1week"] < pd.Timestamp.now(tz="Pacific/Auckland")) & (~df["Q11_4"].apply(check_sent_email_recently))]
if len(df) == 0:
    print("No emails need to be sent")
    exit(1)

print(df[["StartDate", "EndDate", "EndDate+1week", "UN", "First", "Last", "Q11_4", "Q4"]])
print(f"Will start sending {len(df)} emails in 10 seconds, CTRL-C now or forever hold your peace")
time.sleep(10)

mailserver = smtplib.SMTP("mailhost.auckland.ac.nz")

for i, row in df.iterrows():
    email = row["Q11_4"]
    print(email)
    message = template.render(row).replace("\n", "<br>")
    print(message)
    fromaddr = "qualtrics@auckland.ac.nz"
    subject = "Long Covid registry survey reminder"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = fromaddr
    msg["To"] = email
    msg["Reply-To"] = "andrew.mccullough@auckland.ac.nz"
    part1 = MIMEText(message, "html", "utf-8")
    msg.attach(part1)
    print(f"Sending mail from {fromaddr} to {email} with subject {subject}")
    mailserver.sendmail(fromaddr, email, msg.as_string())
    pd.DataFrame([{"email": email, "sent_at": pd.Timestamp.now()}]).to_csv("sent_emails.csv", mode="a", index=False)