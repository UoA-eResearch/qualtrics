#!/usr/bin/env python3

import pandas as pd
from pprint import pprint
from jinja2 import Environment, FileSystemLoader
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

environment = Environment(loader=FileSystemLoader(""))
template = environment.get_template("reminder_template.txt")

df = pd.read_csv("responses.csv.zip")
print(df)
print(df["Q4"].value_counts())

# Filter to users that consented to email reminders
df = df[df["Q4"] == "1"]
print(df)

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
