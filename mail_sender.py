import os
import sys
import csv
from os.path import basename
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

settings = {}
settings['smtp_server'] = os.environ.get('SMTP_SERVER') or ""
settings['smtp_username'] = os.environ.get('SMTP_USERNAME') or ""
settings['smtp_password'] = os.environ.get('SMTP_PASSWORD') or ""
settings['sender_email'] = os.environ.get('MAIL_SENDER') or ""
settings['subject'] = os.environ.get('MAIL_SUBJECT') or ""
settings['attach_file'] = os.environ.get('MAIL_ATTACH') or ""
settings['csv_file_name'] = ""
settings['template_file_name'] = ""

for k, v in enumerate(sys.argv):
    if v:
        t = v.split("=")
        if len(t) == 2 and t[0] in settings and t[1]:
            settings[t[0]] = t[1]

template = ""
with open(settings['template_file_name'], newline="") as fp_read:
    template = fp_read.read()

if not template or len(template) < 10:
    print("ERROR: Incorrect template file!")
    quit()

part = None
if settings['attach_file']:
    with open(settings['attach_file'], "rb") as fil:
        part = MIMEApplication(
            fil.read(),
            Name=basename(settings['attach_file'])
        )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(
            settings['attach_file'])

with open(settings['csv_file_name'], newline="\n") as fp_read:
    reader = csv.reader(fp_read, delimiter=";", quotechar='"')
    for row in reader:
        if len(row) < 4:
            continue
        if len(row[1]) < 5:
            continue
        if len(row[2]) < 5:
            continue
        if len(row[3]) < 5:
            continue
        destination = row[1]
        link1 = row[2]
        link2 = row[3]

        text = template.format(link2, link1)

        try:
            msg = MIMEMultipart()
            msg['Subject'] = settings['subject']
            msg['To'] = destination
            msg['From'] = settings['sender_email']

            msg.attach(MIMEText(text, 'html'))

            if part:
                msg.attach(part)

            conn = SMTP(settings['smtp_server'])
            conn.set_debuglevel(False)
            conn.login(settings['smtp_username'], settings['smtp_password'])
            try:
                conn.sendmail(settings['sender_email'], [
                              destination], msg.as_string())
            finally:
                conn.quit()
                print("mail send; " + destination)
        except Exception as e:
            print("mail failed; " + destination)
            continue
print('Done')
