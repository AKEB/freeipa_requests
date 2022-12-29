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
settings['fix'] = False
settings['verbose'] = False

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
                          otp=settings['otp'],
                          verbose=settings['verbose'],
                          fix=settings['fix']
                          )
    if ipa.login_session() is None:
        with open(settings['read_file'], newline="\n") as fp_read:
            reader = csv.reader(fp_read, delimiter=";", quotechar='"')
            for row in reader:
                if len(row) < 4:
                    continue
                if len(str(row[2])) < 3:
                    continue
                email = row[2]
                (username, domain) = email.split('@')
                ipa.user_add_to_freeipa(row[0], row[1], email, "")
                ipa.set_user_name(username)
                results = ipa.run_actions()

                new_row = list()
                new_row.append(username)
                new_row.append(row[3].lower())
                new_row.append(results['password'] if 'password' in results else '')
                new_row.append(results['otp'] if 'otp' in results else '')
                writer.writerow(new_row)
                print(results)
print('Done')
