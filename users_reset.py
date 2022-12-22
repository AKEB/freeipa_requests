import os
import sys
import csv
import json
import freeipa

settings = {}

settings['host'] = os.environ.get('FREEIPA_HOST') or ""
settings['login'] = os.environ.get('FREEIPA_LOGIN') or ""
settings['password'] = os.environ.get('FREEIPA_PASSWORD') or ""
settings['group'] = ""
settings['check'] = False
settings['reset'] = False
settings['otp'] = False

for k, v in enumerate(sys.argv):
    if v:
        t = v.split("=")
        if len(t) == 2 and t[0] in settings and t[1]:
            settings[t[0]] = t[1]

with open('users_ready.csv', 'w', newline="\n") as fp_write:
    writer = csv.writer(fp_write,
                        delimiter=";",
                        quotechar='"',
                        quoting=csv.QUOTE_MINIMAL
                        )
    with open('users_reset.csv', newline="\n") as fp_read:
        reader = csv.reader(fp_read, delimiter=";", quotechar='"')
        for row in reader:
            if len(row) != 2:
                continue
            ipa = freeipa.Freeipa(host=settings['host'],
                                  login=settings['login'],
                                  password=settings['password'],
                                  username=row[0],
                                  group=settings['group'],
                                  check=settings['check'],
                                  reset=settings['reset'],
                                  otp=settings['otp']
                                  )
            results = ipa.run_actions()
            row.append(results['password'])
            row.append(results['otp'])
            writer.writerow(row)
            print(results)
