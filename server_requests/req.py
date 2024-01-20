import os
import requests

api = os.getenv("VPN_API_URL")

response = requests.get(f"{api}/access-keys", verify=False)
response_dict = response.json()
