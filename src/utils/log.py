from datetime import datetime
from zoneinfo import ZoneInfo

def log(msg):
    now = datetime.now(ZoneInfo("America/Sao_Paulo"))
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")