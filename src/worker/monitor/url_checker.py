import requests

def check_url(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        return False
