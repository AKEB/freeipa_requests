import requests
import os
import sys
import csv
import json
import freeipa

settings = {}

settings['enigma_host'] = os.environ.get('ENIGMA_HOST') or ""
settings['write_file'] = ""
settings['read_file'] = ""
settings['mail_password'] = False


def generate_onetime_link(settings, text) -> str:
    url = 'https://' + settings['enigma_host'] + '/saveSecret'
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://' + settings['enigma_host'] + '/',
        'Host': settings['enigma_host'],
        'Origin': 'https://' + settings['enigma_host'],
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'secretMessage': text,
        'secretKey': '',
        'duration': 691200,
    }
    response = requests.post(
        url, data=data, headers=headers, verify=False)
    if not response or response.status_code != 200:
        print("Failed to generate one time link")
        return None
    response = response.text.split(settings['enigma_host'] + '/view/')
    if not response or len(response) < 2:
        print("Failed to generate one time link")
        return None
    response = response[1].split('">')
    if not response or len(response) < 2 or not response[0]:
        print("Failed to generate one time link")
        return None
    return 'https://' + settings['enigma_host'] + '/view/' + str(response[0])


for k, v in enumerate(sys.argv):
    if v:
        t = v.split("=")
        if len(t) == 2 and t[0] in settings and t[1]:
            settings[t[0]] = t[1]

with open(settings['write_file'], 'w', newline="\n") as fp_write:
    writer = csv.writer(fp_write,
                        delimiter=";",
                        quotechar='"',
                        quoting=csv.QUOTE_MINIMAL
                        )
    with open(settings['read_file'], newline="\n") as fp_read:
        reader = csv.reader(fp_read, delimiter=";", quotechar='"')
        for row in reader:
            if len(row) < 6:
                continue
            if len(str(row[2])) < 3:
                continue
            email = row[2]
            password = row[5]
            (username, domain) = email.split('@')
            text = "email: " + email + "\n"
            text += "password: " + password + "\n"
            url = generate_onetime_link(settings, text)
            new_row = list()
            new_row.append(row[0])
            new_row.append(row[1])
            new_row.append(row[2])
            new_row.append(row[3])
            new_row.append(row[4])
            new_row.append(url if url else '')
            writer.writerow(new_row)
print('Done')
