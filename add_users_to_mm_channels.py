import mattermost
import json
import csv


class MMApi(mattermost.MMApi):

    def get_user_by_email(self, user_email, **kwargs):
        return self._get("/v4/users/email/" + user_email, **kwargs)

    def search_users(self, term, **kwargs):
        dataParams = {
            **({"term": term} if term else {}),
        }
        return self._post("/v4/users/search", data=dataParams, **kwargs)

    def find_user_by_email(self, user_email: str):
        try:
            user = self.get_user_by_email(user_email)
            if user and type(user) == dict and 'id' in user and len(user['id']) > 0:
                return user
            user_email_name = user_email.split('@')
            user = self.get_user_by_username(user_email_name[0])
            if user and type(user) == dict and 'id' in user and len(user['id']) > 0:
                return user
            user = self.search_users(user_email)
            if user and type(user) == dict and 'id' in user and len(user['id']) > 0:
                return user
            user = self.search_users(user_email_name[0])
            if user and type(user) == dict and 'id' in user and len(user['id']) > 0:
                return user
        except Exception:
            return False
        return False


def user_add_to_channel(channel_id: str, user_email: str):
    user = MM.find_user_by_email(user_email)
    if not user:
        return False
    try:
        MM.add_user_to_channel(channel_id, user['id'])
    except Exception:
        return False
    return True


MM = MMApi('https://mm.corp.my.games/api')
ret = MM.login(bearer='1jfwchd4w7nzurmyrx14ugwg5y')

if not ret or 'id' not in ret or not ret['id']:
    raise ConnectionError("Login Error")


# ret = MM.find_user_by_email('dmitriy.eremenkov@my.games')
# print(type(ret) == dict)
# print(ret)
# exit()

mm_channels = [
    # "37c1pjd77jfp9cg18m3e5d9rsc",
    # "et5m7acpnpn4xjbggs86fzpyby",
    # "jp5wfg1seide7m4119w95cnwge",
    # "nouj6ggrx7fo9cc3yy1mzbhe6h",
    # "qkp5pgntkty98ksti1m94ymu7r",
    # "rowk4nk9otngz8s1ro7qpnu67a",
    # "t7q7qubtyi8qzrr8xoy5mkc1ur",
    # "8nnc4ewy73y1zr9cj6jcj3je5w"
]

for channel_id in mm_channels:
    print("\n" + str(channel_id))
    with open("mm/" + channel_id + ".csv", newline="\n") as fp_read:
        reader = csv.reader(fp_read, delimiter=";", quotechar='"')
        for row in reader:
            user_email = row[0]
            if not user_email or len(user_email) < 5:
                continue
            if user_add_to_channel(channel_id, user_email):
                print(user_email + ": True")
            else:
                print(user_email + ": False")
