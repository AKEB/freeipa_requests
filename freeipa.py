import requests
import os
import sys
import json


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

    def check_params(self) -> None:
        if not self.settings['host']:
            print("You need enter host for freeipa")
            quit()
        if not self.settings['login']:
            print("You need enter admin login for freeipa")
            quit()
        if not self.settings['password']:
            print("You need enter admin password for freeipa")
            quit()
        if not self.settings['username']:
            print("You need enter username")
            quit()

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
            print("ERROR! Can't login to freeipa")
            quit()

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
            print("ERROR! Can't exec query")
            quit()

        response = json.loads(response.text)
        if not response:
            print("ERROR! Can't exec query")
            quit()

        if response['error']:
            print("ERROR! " + response['error'])
            quit()

        return response['result']

    def get_user_info(self) -> None:
        print("Get user (" + self.settings['username'] + ") info")
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

    def _add_user_to_group(self) -> None:
        print("Add user " + self.settings['username'] +
              " to group " + self.settings['group'])
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
        print(result)

    def _generate_onetime_link(self) -> str:
        pass

    def _generate_new_password(self) -> str:
        pass

    def _reset_user_password(self) -> None:
        print("Reset user " + self.settings['username'] + " password")

    def _reset_user_otp(self) -> None:
        print("Reset user " + self.settings['username'] + " otp")

    def do_command(self) -> None:
        if self.settings['check']:
            print(self.user)
            return

        if self.settings['group'] or self.settings['reset'] or self.settings['otp']:
            if self.settings['group']:
                self._add_user_to_group()
            if self.settings['reset']:
                self._reset_user_password()
            if self.settings['otp']:
                self._reset_user_otp()
        else:
            print(self.user)
            return

    def main(self):
        self.get_env()
        self.get_params()
        self.check_params()
        print(self.settings)
        self.login()

        self.user = self.get_user_info()
        if not self.user:
            print("ERROR! User not found!")
            quit()
        self.do_command()


if __name__ == "__main__":
    app = App()
    app.main()
