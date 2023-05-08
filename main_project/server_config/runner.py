from socket import *
import select
from src.core.message_processor import MessageProcessor
from src.core.log_decorator import Log
from threading import Thread

import logging
from server_config.loger import config_server_log
from server_config.server_verifier import ServerVerifier
from server_config.db.server_db import DB as ServerDB

SERVER_LOG = logging.getLogger("server")


class Server(metaclass=ServerVerifier):

    BLOCK_LEN: int = 1024
    EOM: bytes = b'ENDOFMESSAGE___'
    ENCODING_ = 'utf-8'

    messanger = MessageProcessor

    _socket = socket(AF_INET, SOCK_STREAM)
    connections = []

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.db = ServerDB()
        self._socket.bind((self.host, self.port))
        self._socket.listen(5)
        self._socket.settimeout(0.5)
        

    def __del__(self):
        self._socket.close()

    # @Log(SERVER_LOG)
    def parse_message(self, message):
        message = message.decode(self.ENCODING_)
        parsed_message = self.messanger.get_object_from_json(message)
        return parsed_message

    # @Log(SERVER_LOG)
    def run(self):
        print(f"Сревер поднят на хосте: {self.host} с портом: {self.port}")
        while True:
            try:
                client, address = self._socket.accept()
            except OSError:
                pass
            else:
                print(f'Получен запрос на соединение от: {address}')
                self.connections.append(client)
            finally:
                responce_ = []
                write_ = []
                try:
                    responce_, write_, excepttions_ = select.select(
                        self.connections, self.connections, [], 0)
                except Exception:
                    pass
                for client in responce_:
                    try:
                        data = client.recv(self.BLOCK_LEN)
                        parsed_message = self.parse_message(data)

                        if parsed_message.action == "presence" and (client in write_):
                            # self.db.
                            self.send_responce(
                                client=client, code=200, alert=f"{parsed_message.from_user.name} {parsed_message.from_user.status} подключился к чату", all=True)
                        if (parsed_message.action == 'msg' and parsed_message.to_user == 'ALL') and (client in write_):
                            self.send_responce(
                                client=client, code=200, alert=f'{parsed_message.from_user.name}: {parsed_message.message}', all=True)
                    except:
                        print(f"Соединение разорвано c {client}")
                        self.connections.remove(client)

    # @Log(SERVER_LOG)
    def send_responce(self, client, code, alert=None, all=False):
        gen_response = self.messanger.create_response_message(code, alert)
        gen_response_json = gen_response.encode_to_json()
        if all:
            for client in self.connections:
                client.sendall(gen_response_json.encode(self.ENCODING_))
        client.send(gen_response_json.encode(self.ENCODING_))
