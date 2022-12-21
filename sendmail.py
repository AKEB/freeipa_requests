import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test message")

msg['Subject'] = 'Test subject'
msg['From'] = "babadzhanyan@corp.mail.ru"
msg['To'] = "akeb@mail.ru"

s = smtplib.SMTP('localhost')
s.sendmail("babadzhanyan@corp.mail.ru",
           ["akeb@mail.ru"], msg.as_string())
s.quit()
