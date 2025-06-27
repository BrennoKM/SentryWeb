import requests
import time

def check_url(url):
    try:
        inicio = time.time()
        with requests.get(url, timeout=5) as response:
            return response.status_code == 200
        fim = time.time()
        print(f"Tempo de resposta para {url}: {fim - inicio:.2f} segundos")
    except Exception:
        return False