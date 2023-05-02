from socket import *
import select
from src.core.message_processor import MessageProcessor
from src.core.log_decorator import Log
from abc import ABC, abstractmethod
from threading import Thread

import logging
from src.log import config_client_log
from src.log import config_server_log
# from src.verifiers.client_verifier import ClientVerifier
# from src.verifiers.server_verifier import ServerVerifier
from src.db.db import DB
from src.db.db_config import Config
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
        self.db = DB(Config.__dict__)

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
                        if parsed_message.action == "presence" and (client in write_):
                            self.send_responce(
                                client=client, code=200, alert=f"{parsed_message.from_user.name} {parsed_message.from_user.status} подключился к чату", all=True)
                        if (parsed_message.action == 'msg' and parsed_message.to_user == 'ALL') and (client in write_):
                            self.send_responce(client=client, code=200, alert=f'{parsed_message.from_user.name}: {parsed_message.message}', all=True)
                    except:
                        self.connections.remove(client)
    
    @Log(SERVER_LOG)
    def send_responce(self, client, code, alert=None, all=False):
        gen_response = self.messanger.create_response_message(code, alert)
        gen_response_json = gen_response.encode_to_json()
        if all:
            for client in self.connections:
                client.sendall(gen_response_json.encode(self.ENCODING_))
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
        return data

    @Log(CLIENT_LOG)
    def send_message(self, action:str="presence", message:str=None):
        
        if self.login is None:
            print("Введите логин")
            self.login = input('> : ')

        if action == "presence":
            gen_message = self.messanger.create_presence_message(
                from_user=self.login, action=action)
            gen_message_json = gen_message.encode_to_json()
            self._socket.send(gen_message_json.encode(self.ENCODING_))
        
        else:
            gen_message = self.messanger.create_message_to_chat(
                from_user=self.login, action=action, message=message)
            gen_message_json = gen_message.encode_to_json()
            self._socket.send(gen_message_json.encode(self.ENCODING_))

    def read_server_response(self):
        while True:
            response = self.get_data()
            response = self.parse_message(response)
            print(f'Статус: {response.response}, {response.alert}')
    
    @Log(CLIENT_LOG)
    def run(self):
        self.send_message(action="presence")
        response_encoded = self.get_data()
        response = self.parse_message(response_encoded)
        thread = Thread(target=self.read_server_response)
        thread.daemon = True
        thread.start()

        while True:
            message = input('> : ')

            if message == '/q':
                break

            self.send_message(action='msg', message=message)
