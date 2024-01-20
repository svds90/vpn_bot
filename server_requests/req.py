import sys
from pprint import pprint
import os
import requests
from config import bot_ip, bot_token, vpn_token
pprint(sys.path)


api = os.getenv("VPN_API_URL")

response = requests.get(f"{api}/access-keys", verify=False)
response_dict = response.json()

#   if response.status_code == 200:
#       print('OK')
#       print(f"{response.status_code}, OK")
#   else:
#       print(response.status_code)


pprint(response_dict["accessKeys"])

for item in response_dict["accessKeys"]:
    print(item["name"])

print(bot_token)
