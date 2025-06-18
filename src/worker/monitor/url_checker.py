import requests

def check_url(url):
    try:
        with requests.get(url, timeout=5) as response:
            return response.status_code == 200
    except Exception:
        return False