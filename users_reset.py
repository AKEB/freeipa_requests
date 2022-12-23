import os
import sys
import csv
import json
import freeipa

settings = {}

settings['host'] = os.environ.get('FREEIPA_HOST') or ""
settings['login'] = os.environ.get('FREEIPA_LOGIN') or ""
settings['password'] = os.environ.get('FREEIPA_PASSWORD') or ""
settings['enigma_host'] = os.environ.get('ENIGMA_HOST') or ""
settings['otp_issuer'] = os.environ.get('OTP_ISSUER') or ""
settings['group'] = ""
settings['write_file'] = ""
settings['read_file'] = ""
settings['check'] = False
settings['reset'] = False
settings['otp'] = False

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
    ipa = freeipa.Freeipa(host=settings['host'],
                          login=settings['login'],
                          password=settings['password'],
                          enigma_host=settings['enigma_host'],
                          otp_issuer=settings['otp_issuer'],
                          group=settings['group'],
                          check=settings['check'],
                          reset=settings['reset'],
                          otp=settings['otp']
                          )
    if ipa.login_session() is None:
        with open(settings['read_file'], newline="\n") as fp_read:
            reader = csv.reader(fp_read, delimiter=";", quotechar='"')
            for row in reader:
                if len(row) < 1:
                    continue
                if len(str(row[0])) < 3:
                    continue
                ipa.set_user_name(row[0])
                results = ipa.run_actions()
                row.append(results['password'])
                row.append(results['otp'])
                writer.writerow(row)
                print(results)
print('Done')
