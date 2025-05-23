from messaging.emitter import send_message

def main():
    task = {
        "type": "url_check",
        "url": "https://example.com",
        "interval": 60  # segundos até a próxima execução
    }
    send_message(task)
    print("Tarefa enviada:", task)


if __name__ == "__main__":
    main()
