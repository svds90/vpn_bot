from pprint import pprint
import os
import requests
from config import *

api = os.getenv("VPN_API_URL")

responce = requests.get(f"{api}/access-keys", verify=False)

pprint(responce.json())
