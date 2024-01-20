import os
from dotenv import load_dotenv

load_dotenv()

bot_ip = os.getenv("BOT_IP")
bot_token = os.getenv("BOT_TOKEN")
vpn_token = os.getenv("VPN_API_URL")
