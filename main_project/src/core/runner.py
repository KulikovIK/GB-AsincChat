from socket import *
import select
from src.core.message_processor import MessageProcessor
from src.core.log_decorator import Log
from abc import ABC, abstractmethod

import logging
from src.log import config_client_log
from src.log import config_server_log


SERVER_LOG = logging.getLogger("server")
CLIENT_LOG = logging.getLogger("client")


class Runner(ABC):

    BLOCK_LEN: int = 1024
    EOM: bytes = b'ENDOFMESSAGE___'
    ENCODING_ = 'utf-8'

    messanger = MessageProcessor

    _socket = socket(AF_INET, SOCK_STREAM)

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def __del__(self):
        self._socket.close()

    @abstractmethod
    def run(self):
        pass

    @Log(SERVER_LOG)
    def parse_message(self, message):
        message = message.decode(self.ENCODING_)
        parsed_message = self.messanger.get_object_from_json(message)
        return parsed_message


class Server(Runner):

    connections = []

    def __init__(self, host: str, port: int) -> None:
        super().__init__(host=host, port=port)

        self._socket.bind((self.host, self.port))
        self._socket.listen(5)
        self._socket.settimeout(0.5)
        print(f"Сревер поднят на хосте: {self.host} с портом: {self.port}")

    @Log(SERVER_LOG)
    def run(self):
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
                    data = client.recv(self.BLOCK_LEN)
                    parsed_message = self.parse_message(data)
                    try:
                        if parsed_message.action == 'presence' and (client in write_):
                            self.send_responce(
                                client=client, code=200, alert=f'{parsed_message.user.name} {parsed_message.user.status}')
                    except:
                        self.connections.remove(client)
    @Log(SERVER_LOG)
    def send_responce(self, client, code, alert=None):
        gen_response = self.messanger.create_response_message(code, alert)
        gen_response_json = gen_response.encode_to_json()
        client.send(gen_response_json.encode(self.ENCODING_))


class Client(Runner):

    def __init__(self, host: str, port: int) -> None:
        super().__init__(host=host, port=port)
        self._socket.connect((self.host, self.port))
        self.login = None

    @Log(CLIENT_LOG)
    def get_data(self):
        data = None
        while data is None:
            data = self._socket.recv(self.BLOCK_LEN)

    @Log(CLIENT_LOG)
    def send_message(self, action='presence'):
        if self.login is None:
            self.login = 'Guest'
        print(self.__class__.__name__)
        gen_message = self.messanger.create_presence_message(
            name=self.login, action=action)
        gen_message_json = gen_message.encode_to_json()
        self._socket.send(gen_message_json.encode(self.ENCODING_))

    @Log(CLIENT_LOG)
    def run(self):
        self.send_message()
        response_encoded = self._socket.recv(self.BLOCK_LEN)
        response = self.parse_message(response_encoded)
        print(f'Статус: {response.response}, {response.alert}')
