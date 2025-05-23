from messaging.consumer import start_consumer

def handle_task(task):
    print("[x] Nova tarefa recebida:", task)
    if task["type"] == "url_check":
        from monitor.url_checker import check_url
        status = check_url(task["url"])
        print(f"[✓] Resultado da verificação: {status}")

if __name__ == "__main__":
    start_consumer(handle_task)
