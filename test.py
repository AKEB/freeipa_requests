import requests
from urllib3.exceptions import InsecureRequestWarning

headers = {
    'Accept': 'text/plain',
    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
}
post = {
    'user': 'login',
    'password': 'pass'
}

requests.packages.urllib3.disable_warnings(
    category=InsecureRequestWarning)

s = requests.Session()

r = s.post('https://httpbin.org/post', data=post,
           headers=headers, verify=False, timeout=10)

print(r.text)
