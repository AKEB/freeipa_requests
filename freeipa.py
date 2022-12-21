import requests
import os
import sys
import json
from urllib3.exceptions import InsecureRequestWarning
import random
import base64


class App:

    def __init__(self) -> None:
        self.settings = {}
        self.settings['host'] = ""
        self.settings['login'] = ""
        self.settings['password'] = ""
        self.settings['username'] = ""
        self.settings['group'] = ""
        self.settings['check'] = False
        self.settings['reset'] = False
        self.settings['otp'] = False

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

    def get_params(self) -> None:
        for k, v in enumerate(sys.argv):
            if v:
                t = v.split("=")
                if len(t) == 2 and t[0] in self.settings and t[1]:
                    self.settings[t[0]] = t[1]

    def collect_result(self, key: str, result: object, error: str = None, exit: bool = False):
        self.result[key] = result
        if error:
            if not self.result[key]:
                self.result[key] = {}
            self.result[key]['error'] = error
        if exit:
            self.show_result()
            quit()

    def show_result(self):
        print(json.dumps(self.result))

    def check_params(self) -> None:
        if not self.settings['host']:
            self.collect_result(
                'result', None, "You need enter host for freeipa", True)
        if not self.settings['login']:
            self.collect_result(
                'result', None, "You need enter admin login for freeipa", True)
        if not self.settings['password']:
            self.collect_result(
                'result', None, "You need enter admin password for freeipa", True)
        if not self.settings['username']:
            self.collect_result(
                'result', None, "You need enter username", True)

    def login(self) -> None:
        url = self.settings['host'] + '/ipa/session/login_password'
        headers = {
            'Accept': 'text/plain',
            'Referer': self.settings['host'] + '/ipa',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        post = {
            'user': self.settings['login'],
            'password': self.settings['password']
        }
        response = self.session.post(
            url, data=post, headers=headers, verify=False)

        if response.status_code != 200:
            self.collect_result(
                'result', None, "Can't login to freeipa", True)

    def __request_freeipa_api(self, payload) -> object:
        url = self.settings['host'] + '/ipa/session/json'
        headers = {
            'Accept': 'application/json',
            'Referer': self.settings['host'] + '/ipa',
            'Content-Type': 'application/json'
        }
        response = self.session.post(
            url, json=payload, headers=headers, verify=False)

        if response.status_code != 200:
            self.collect_result(
                'result', None, "Can't exec query", True)

        response = json.loads(response.text)
        if not response:
            self.collect_result(
                'result', None, "Can't exec query", True)

        if response['error']:
            self.collect_result(
                'result', None, response['error'], True)

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

    def add_user_to_group(self) -> None:
        payload = {
            "method": "group_add_member",
            "params": [
                [
                    self.settings['group']
                ],
                {
                    "all": False,
                    "no_members": False,
                    "raw": False,
                    "user": [
                        self.settings['username']
                    ],
                    "version": "2.246"
                }
            ]
        }
        result = self.__request_freeipa_api(payload)
        if not result or 'failed' in result:
            self.collect_result(
                'group', result, "Failed add user to group")
        else:
            self.collect_result('group', result)

    def _generate_onetime_link(self, text) -> str:
        url = 'https://enigma.dev-my.games/saveSecret'
        headers = {
            'Accept': 'application/json',
            'Referer': 'https://enigma.dev-my.games/',
            'Host': 'enigma.dev-my.games',
            'Origin': 'https://enigma.dev-my.games',
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
                'global', {'status_code': response.status_code}, "Failed to generate one time link", True)
        response = response.text.split('enigma.dev-my.games/view/')
        if not response or len(response) < 2:
            self.collect_result(
                'global', {'status_code': response.status_code}, "Failed to generate one time link", True)
        response = response[1].split('">')
        if not response or len(response) < 2 or not response[0]:
            self.collect_result(
                'global', {'status_code': response.status_code}, "Failed to generate one time link", True)
        return 'https://enigma.dev-my.games/view/' + str(response[0])

    def generate_new_password(self) -> str:
        return self._random_base32(8, chars=b'0123456789ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'.decode("unicode_escape"))

    def _random_base32(self, length=16, random=random.SystemRandom(), chars=base64._b32alphabet.decode("unicode_escape")):
        return ''.join(random.choice(chars) for i in range(length))

    def generate_new_otp(self) -> str:
        secret = self._random_base32(32)
        return secret

    def get_otp_uri(self, secret) -> str:
        return f'otpauth://totp/%(name)s%%40my.games?secret=%(secret)s&issuer=CORP.MY.GAMES' % {'name': self.settings['username'], 'secret': secret}

    def get_otp_qrcode_uri(self, otp) -> str:
        return 'https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl=' + otp

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
                    "setattr": [
                        "userpassword=" + new_password
                    ],
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
            self.collect_result('password', result)

        one_time_link = self._generate_onetime_link(text)
        self.collect_result('password_link', one_time_link)

    def reset_user_otp(self) -> None:
        secret = self.generate_new_otp()
        otpauth = self.get_otp_uri(secret)
        qrcode_uri = self.get_otp_qrcode_uri(otpauth)
        text = "secret: " + secret + "\n"
        text += "otpauth: " + otpauth + "\n"
        text += "URL for qrcode: " + qrcode_uri + "\n"

        text = qrcode_uri
        # TODO: Send New OTP to Freeipa
        one_time_link = self._generate_onetime_link(text)
        self.collect_result('otp', one_time_link)

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

    def main(self):
        self.get_env()
        self.get_params()
        self.check_params()
        self.login()

        self.user = self.get_user_info()
        if not self.user:
            self.collect_result('user', self.user, "User not found!", True)
        self.do_command()
        self.show_result()


if __name__ == "__main__":
    app = App()
    app.main()
    # app.get_params()
    # app.reset_user_password()
    # app.reset_user_otp()
    # app.show_result()
