import platform
import subprocess
import time

params = {}
if platform.system().lower() == 'windows':
    params = {'creationflags': subprocess.CREATE_NEW_CONSOLE}
process = []

if __name__ == '__main__':
    while True:
        action = input('Выберите действие: q - выход , s - запустить сервер и клиентов, x - закрыть все окна:')
        if action == 'q':
            break
        elif action == 's':
            clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
            # Запуска сервера:
            process.append(subprocess.Popen(['python3', 'server.py'], **params))
            time.sleep(1)
            # Запуск клиентов:
            for i in range(clients_count):
                process.append(subprocess.Popen(['python3', 'client.py',], **params))
        elif action == 'x':
            while process:
                process.pop().kill()