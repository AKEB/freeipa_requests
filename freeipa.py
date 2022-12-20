import requests
import os
import sys


class App:

    def __init__(self) -> None:
        self.settings = {}
        self.settings['host'] = ""
        self.settings['login'] = ""
        self.settings['password'] = ""
        self.settings['group'] = ""
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
        if not self.settings['group'] and not self.settings['reset'] and not self.settings['otp']:
            print("You need choose actions for freeipa")
            quit()

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
        response = self.session.post(url, data=post, headers=headers)
        print(response)
        print(self.session.cookies.get_dict())

    def main(self):
        self._get_env()
        self._get_params()
        self._check_params()
        print(self.settings)
        self._login()
        pass


if __name__ == "__main__":
    app = App()
    app.main()
