import pytz
from datetime import datetime

class SessionSniper:
    def __init__(self):
        self.sessions = {
            'London': {'open': '08:00', 'close': '17:00', 'timezone': 'Europe/London'},
            'New York': {'open': '08:00', 'close': '17:00', 'timezone': 'America/New_York'},
            'Tokyo': {'open': '09:00', 'close': '18:00', 'timezone': 'Asia/Tokyo'},
            'Sydney': {'open': '09:00', 'close': '18:00', 'timezone': 'Australia/Sydney'}
        }
    
    def get_best_times(self):
        return [
            {'name': 'London/New York Overlap', 'time': '13:00 - 17:00 UTC', 'description': 'Highest volatility - Best for scalping', 'pairs': 'EUR/USD, GBP/USD, USD/JPY'},
            {'name': 'Tokyo/London Overlap', 'time': '08:00 - 09:00 UTC', 'description': 'Medium volatility', 'pairs': 'GBP/JPY, EUR/JPY'}
        ]
    
    def is_market_open(self, session_name):
        if session_name not in self.sessions:
            return False
        session = self.sessions[session_name]
        tz = pytz.timezone(session['timezone'])
        now = datetime.now(tz).strftime('%H:%M')
        return session['open'] <= now <= session['close']
