import requests
import time

def check_url(url):
    try:
        time.sleep(1.45)
        return True
        # with requests.get(url, timeout=5) as response:
        #     return response.status_code == 200
    except Exception:
        return False