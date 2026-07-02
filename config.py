import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')
PAYPAL_LINK = os.getenv('PAYPAL_LINK', 'https://paypal.me/Eman388/35')
PAYPAL_EMAIL = os.getenv('PAYPAL_EMAIL', 'Amouna585@yahoo.com')
ADMIN_IDS = os.getenv('ADMIN_IDS', '8858189268')
FREE_TIER_LIMIT = 3
VIP_PRICE = 35
