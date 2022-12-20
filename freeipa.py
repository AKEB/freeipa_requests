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
        self.session = requests.Session()

    def _get_env(self) -> None:
        self.settings['host'] = os.environ.get(
            'FREEIPA_HOST') or self.settings['host']
        self.settings['login'] = os.environ.get(
            'FREEIPA_LOGIN') or self.settings['login']
        self.settings['password'] = os.environ.get(
            'FREEIPA_PASSWORD') or self.settings['password']

    def _get_params(self) -> None:
        for k, v in enumerate(sys.argv):
            if v:
                t = v.split("=")
                if len(t) == 2 and t[0] in self.settings and t[1]:
                    self.settings[t[0]] = t[1]

    def _check_params(self) -> None:
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
        # if not self.settings['group'] and not self.settings['reset'] and not self.settings['otp'] and not self.settings['check']:
        #     print("You need choose actions for freeipa")
        #     quit()

    def _login(self) -> None:
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
            url, data=payload, headers=headers, verify=False)

        if response.status_code != 200:
            print("ERROR! Can't exec query")
            quit()

        response = json.loads(response.text)
        return response

    def _get_user_info(self) -> None:
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
        print(user)

    def _add_user_to_group(self) -> None:
        print("Add user " + self.settings['username'] +
              " to group " + self.settings['group'])

    def _generate_onetime_link(self) -> str:
        pass

    def _generate_new_password(self) -> str:
        pass

    def _reset_user_password(self) -> None:
        print("Reset user " + self.settings['username'] + " password")

    def _reset_user_otp(self) -> None:
        print("Reset user " + self.settings['username'] + " otp")

    def _do_command(self) -> None:
        if self.settings['check']:
            return self._get_user_info()

        if self.settings['group'] or self.settings['reset'] or self.settings['otp']:
            if self.settings['group']:
                self._add_user_to_group()
            if self.settings['reset']:
                self._reset_user_password()
            if self.settings['otp']:
                self._reset_user_otp()
        else:
            return self._get_user_info()

    def main(self):
        self._get_env()
        self._get_params()
        self._check_params()
        print(self.settings)
        self._login()
        self._do_command()


if __name__ == "__main__":
    app = App()
    app.main()
