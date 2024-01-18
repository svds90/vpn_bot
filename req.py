from dotenv import load_dotenv
from pprint import pprint
import os
import requests
from config import *

load_dotenv()

print(os.getenv("VPN_API_URL"))

api = os.getenv("VPN_API_URL")

print(f"{api}/server")

responce = requests.get(f"{api}/server", verify=False)

pprint(responce.text)
