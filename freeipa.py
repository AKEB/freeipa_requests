import requests
import os
import re
import sys
import json
import time
import urllib.parse
from urllib3.exceptions import InsecureRequestWarning
import random
import base64


class Freeipa:

    def __init__(self,
                 host: str = "",
                 login: str = "",
                 password: str = "",
                 username: str = "",
                 group: str = "",
                 enigma_host: str = "",
                 otp_issuer: str = "",
                 check: bool = False,
                 reset: bool = False,
                 otp: bool = False,
                 verbose: bool = False
                 ) -> None:
        self.settings = {}
        self.settings['enigma_host'] = enigma_host
        self.settings['otp_issuer'] = otp_issuer
        self.settings['host'] = host
        self.settings['login'] = login
        self.settings['password'] = password
        self.settings['username'] = username
        self.settings['group'] = group.split(',')
        self.settings['check'] = check
        self.settings['reset'] = reset
        self.settings['otp'] = otp
        self.settings['verbose'] = verbose

        self.user = None
        self.result = {}
        requests.packages.urllib3.disable_warnings(
            category=InsecureRequestWarning)

        self.session = requests.Session()

    def get_env(self) -> None:
        self.settings['host'] = os.environ.get(
            'FREEIPA_HOST') or self.settings['host']
        self.settings['login'] = os.environ.get(
            'FREEIPA_LOGIN') or self.settings['login']
        self.settings['password'] = os.environ.get(
            'FREEIPA_PASSWORD') or self.settings['password']
        self.settings['enigma_host'] = os.environ.get(
            'ENIGMA_HOST') or self.settings['enigma_host']
        self.settings['otp_issuer'] = os.environ.get(
            'OTP_ISSUER') or self.settings['otp_issuer']

    def get_params(self) -> None:
        for k, v in enumerate(sys.argv):
            if v:
                t = v.split("=")
                if len(t) == 2 and t[0] in self.settings and t[1]:
                    if t[0] == 'group':
                        t[1] = t[1].split(',')
                    self.settings[t[0]] = t[1]


    def collect_result(self, key: str, result: object, error: str = None):
        self.result[key] = result
        if error:
            if not self.result[key]:
                self.result[key] = {}
            self.result[key]['error'] = error

    def show_result(self):
        print(json.dumps(self.result))

    def check_params(self) -> bool:
        if not self.settings['host']:
            self.collect_result(
                'global', None, "You need enter host for freeipa")
            return False
        if not self.settings['login']:
            self.collect_result(
                'global', None, "You need enter admin login for freeipa")
            return False
        if not self.settings['password']:
            self.collect_result(
                'global', None, "You need enter admin password for freeipa")
            return False
        return True

    def login(self) -> bool:
        url = self.settings['host'] + '/ipa/session/login_password'
        headers = {
            'Accept': 'text/plain',
            'Referer': self.settings['host'] + '/ipa',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        }
        post = {
            'user': self.settings['login'],
            'password': self.settings['password']
        }
        try:
            response = self.session.post(
                url, data=post, headers=headers, verify=False, timeout=10)
            # print(response.request.headers)
            if response.status_code != 200:
                self.collect_result(
                    'global', {'response': response.text}, "Can't login to freeipa")
                return False
        except Exception as e:
            print("Can't login to freeipa: " + str(e))
            return False
        return True

    def __request_freeipa_api(self, payload) -> object:
        url = self.settings['host'] + '/ipa/session/json'
        headers = {
            'Accept': 'application/json',
            'Referer': self.settings['host'] + '/ipa',
            'Content-Type': 'application/json'
        }
        response = self.session.post(
            url, json=payload, headers=headers, verify=False, timeout=10)

        if response.status_code != 200:
            self.collect_result(
                payload['method'], {'response': response.text}, "Can't exec query")
            return None

        response = json.loads(response.text)
        if not response:
            self.collect_result(
                payload['method'], {'response': response}, "Can't exec query")
            return None

        if response['error']:
            self.collect_result(
                payload['method'], {'response': response}, response['error'])
            return None

        return response['result']

    def get_user_info(self) -> None:
        payload = {
            "method": "user_show",
            "params": [
                [
                ],
                {
                    "uid": self.settings['username'],
                    "all": True,
                    "version": "2.246"
                }
            ],
            "id": 0
        }
        user = self.__request_freeipa_api(payload)
        if user and 'result' in user:
            return user['result']
        return None

    def add_user_to_group(self, groups: list = []) -> None:
        if (self.settings['group'] and len(self.settings['group']) > 0):
            for group in self.settings['group']:
                groups.append(group)

        # payload = {
        #     "method": "group_add_member",
        #     "params": [
        #         groups,
        #         {
        #             "all": False,
        #             "no_members": False,
        #             "raw": False,
        #             "user": [
        #                 self.settings['username']
        #             ],
        #             "version": "2.246"
        #         }
        #     ]
        # }
        payload = {
            "method": "group_find",
            "params": [
                [],
                {
                    "version": "2.246"
                }
            ]
        }
        result = self.__request_freeipa_api(payload)
        print(result)
        # for group in groups:
        #     payload = {
        #         "method": "group_add_member",
        #         "params": [
        #             [],
        #             {
        #                 "cn": group,
        #                 "group": group,
        #                 "user": self.settings['username'],
        #                 "version": "2.246"
        #             }
        #         ]
        #     }
        #     result = self.__request_freeipa_api(payload)
        # if not result or ('failed' in result and 'completed' in result and int(result['completed']) < 1):
        #     self.collect_result(
        #         'group', None, "Failed add user to group")
        # else:
        #     self.collect_result('group', "ok")

    def _generate_onetime_link(self, text) -> str:
        url = 'https://' + self.settings['enigma_host'] + '/saveSecret'
        headers = {
            'Accept': 'application/json',
            'Referer': 'https://' + self.settings['enigma_host'] + '/',
            'Host': self.settings['enigma_host'],
            'Origin': 'https://' + self.settings['enigma_host'],
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'secretMessage': text,
            'secretKey': '',
            'duration': 604800,
        }
        response = requests.post(
            url, data=data, headers=headers, verify=False)
        if not response or response.status_code != 200:
            self.collect_result(
                'global', {'status_code': response.status_code}, "Failed to generate one time link")
            return None
        response = response.text.split(self.settings['enigma_host'] + '/view/')
        if not response or len(response) < 2:
            self.collect_result(
                'global', None, "Failed to generate one time link")
            return None
        response = response[1].split('">')
        if not response or len(response) < 2 or not response[0]:
            self.collect_result(
                'global', None, "Failed to generate one time link")
            return None
        return 'https://' + self.settings['enigma_host'] + '/view/' + str(response[0])

    def _create_onetime_link_for_picture(self, qrcode_uri, try_count: int = 1) -> str:
        if try_count > 10:
            return ''
        try:
            response = requests.get(qrcode_uri)
            headers = {
                'Max-Downloads': '1',
                'Max-Days': '7',
            }
            resp = requests.put("https://tpic.dev-my.com/" + self.settings['username'] + ".png",
                                data=response.content,
                                headers=headers
                                )
            if resp.status_code != 200:
                time.sleep(1)
                try_count += 1
                return self._create_onetime_link_for_picture(qrcode_uri, try_count)
            return resp.text.replace("\n", "")
        except Exception as e:
            print("ERROR send QR code")
            return ''

    def generate_new_password(self) -> str:
        while True:
            password = self._random_base32(
                8,
                chars=b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'.decode(
                    "unicode_escape"
                )
            )
            if re.search('[0-9]{2}', password) is None:
                continue
            if re.search('[A-Z]{2}', password) is None:
                continue
            if re.search('[a-z]{2}', password) is None:
                continue
            break
        return password

    def _random_base32(self, length=16, random=random.SystemRandom(), chars=base64._b32alphabet.decode("unicode_escape")):
        return ''.join(random.choice(chars) for i in range(length))

    def generate_new_otp(self) -> str:
        secret = self._random_base32(32)
        return secret

    def get_otp_uri(self, secret) -> str:
        return f'otpauth://totp/%(name)s?secret=%(secret)s&issuer=%(issuer)s' % {'name': self.settings['username'], 'secret': secret, 'issuer': self.settings['otp_issuer']}

    def get_otp_qrcode_uri(self, otp) -> str:
        return 'https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl=' + urllib.parse.quote_plus(otp)

    def _otp_token_find(self):
        payload = {
            "method": "otptoken_find",
            "params": [
                [
                ],
                {
                    "ipatokenowner": self.settings['username'],
                    # "ipatokenuniqueid": self.settings['username'] + "-hmg",
                    "version": "2.246",
                    "all": True
                }
            ],
            "id": 0
        }
        result = self.__request_freeipa_api(payload)

    def _otp_token_delete(self):
        payload = {
            "method": "otptoken_del",
            "params": [
                [
                ],
                {
                    "ipatokenuniqueid": self.settings['username'] + "-hmg",
                    "version": "2.246",
                }
            ],
            "id": 0
        }
        result = self.__request_freeipa_api(payload)

    def _otp_token_add(self, secret):
        payload = {
            "method": "otptoken_add",
            "params": [
                [
                ],
                {
                    "ipatokenuniqueid": self.settings['username'] + "-hmg",
                    "ipatokenowner": self.settings['username'],
                    "ipatokenotpkey": secret,
                    "version": "2.246",
                    "type": 'totp',
                    "ipatokenotpalgorithm": 'sha1',
                    "ipatokenotpdigits": 6,
                    "ipatokentotptimestep": 30,
                    "ipatokentotpclockoffset": 0,
                    "all": True,
                    "raw": True,
                    "no_qrcode": False,
                    "no_members": False
                }
            ],
            "id": 0
        }
        result = self.__request_freeipa_api(payload)

    def reset_user_password(self) -> None:
        new_password = self.generate_new_password()
        text = "username: " + self.settings['username'] + "\n"
        text += "password: " + new_password + "\n"
        payload = {
            "method": "user_mod",
            "params": [
                [
                ],
                {
                    "ipauserauthtype": 'otp',
                    "userpassword": new_password,
                    "uid": self.settings['username'],
                    "version": "2.246"
                }
            ],
            "id": 0
        }
        result = self.__request_freeipa_api(payload)
        if not result or 'failed' in result:
            self.collect_result(
                'password', result, "Failed to reset user password")
        else:
            if self.settings['verbose']:
                self.collect_result('password_verbose', new_password)
            one_time_link = self._generate_onetime_link(text)
            self.collect_result('password', one_time_link)

    def reset_user_otp(self) -> None:
        secret = self.generate_new_otp()
        otpauth = self.get_otp_uri(secret)
        qrcode_uri = self.get_otp_qrcode_uri(otpauth)

        text = qrcode_uri

        # self._otp_token_find()
        self._otp_token_delete()
        self._otp_token_add(secret)

        one_time_link = self._create_onetime_link_for_picture(text)
        self.collect_result('otp', one_time_link)
        if self.settings['verbose']:
            self.collect_result('otp_verbose', qrcode_uri)

    def do_command(self) -> None:
        if self.settings['check']:
            self.collect_result('user', self.user)
            return

        if self.settings['group'] or self.settings['reset'] or self.settings['otp']:
            if self.settings['group']:
                self.add_user_to_group()
            if self.settings['reset']:
                self.reset_user_password()
            if self.settings['otp']:
                self.reset_user_otp()
        else:
            self.collect_result('user', self.user)
            return

    def login_session(self):
        if not self.check_params():
            return self.result

        if not self.login():
            return self.result
        return None

    def user_add_to_freeipa(self, name: str, surname: str, email: str, telephonenumber: str = ""):
        (username, domain) = email.split('@')
        self.settings[username] = username
        initials = ('-'.join([x[0] for x in name.split(' ') if x[0] == x[0].upper()])) + ('-'.join([x[0] for x in surname.split(' ') if x[0] == x[0].upper()]))
        payload = {
            "method": "user_add",
            "params": [
                [
                ],
                {
                    "givenname": name,
                    "sn": surname,
                    "cn": ' '.join([name, surname]),
                    "displayname": ' '.join([name, surname]),
                    "mail": email,
                    "uid": username,
                    "initials": initials,
                    "telephonenumber": telephonenumber,
                    "ipauserauthtype": 'otp',
                    "version": "2.246"
                }
            ],
            "id": 0
        }
        print(payload)
        result = self.__request_freeipa_api(payload)
        print(result)
        if not result or ('failed' in result and 'completed' in result and int(result['completed']) < 1):
            self.collect_result(
                'useradd', None, "Failed add user")
        else:
            self.collect_result('useradd', "ok")
            self.add_user_to_group(["ipausers"])

    def set_user_name(self, username):
        self.settings['username'] = username

    def run_actions(self) -> object:
        if not self.settings['username']:
            self.collect_result(
                'global', None, "You need enter username")
            return self.result

        self.user = self.get_user_info()
        if not self.user:
            self.collect_result('user', self.user, "User not found!")
            return self.result

        self.collect_result(
            'user_name', self.settings['username'])

        self.do_command()

        return self.result


if __name__ == "__main__":
    app = Freeipa()
    app.get_env()
    app.get_params()
    if app.login_session() is None:
        results = app.run_actions()
    print(json.dumps(results))
