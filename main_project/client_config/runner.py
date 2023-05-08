from socket import *
import select
from src.core.message_processor import MessageProcessor
from src.core.log_decorator import Log
from threading import Thread

import logging
from client_config.loger import config_client_log
from client_config.client_verifier import ClientVerifier
from client_config.db.client_db import DB as ClientDB
from client_config.db.db_config import Config

CLIENT_LOG = logging.getLogger("client")


class Client(metaclass=ClientVerifier):

    BLOCK_LEN: int = 1024
    EOM: bytes = b'ENDOFMESSAGE___'
    ENCODING_ = 'utf-8'

    messanger = MessageProcessor

    _socket = socket(AF_INET, SOCK_STREAM)

    def __init__(self, host: str, port: int, login: str = None, password: str = None) -> None:
        self.host = host
        self.port = port
        self.db = ClientDB(Config.__dict__)
        self._socket.connect((self.host, self.port))
        self.login = login
        self.password = password

    def __del__(self):
        self._socket.close()

    # @Log(CLIENT_LOG)
    def parse_message(self, message):
        message = message.decode(self.ENCODING_)
        parsed_message = self.messanger.get_object_from_json(message)
        return parsed_message

    # @Log(CLIENT_LOG)
    def get_data(self):
        data = None
        while data is None:
            data = self._socket.recv(self.BLOCK_LEN)
        return data

    # @Log(CLIENT_LOG)
    def send_message(self, action: str = None, message: str = None):

        if self.login is None:
            print("Введите логин")
            self.login = input('> : ')

        if action == "presence":
            gen_message = self.messanger.create_presence_message(
                from_user=self.login, password=self.password)
            gen_message_json = gen_message.encode_to_json()
            self._socket.send(gen_message_json.encode(self.ENCODING_))

        else:
            gen_message = self.messanger.create_message_to_chat(
                from_user=self.login, message=message)
            gen_message_json = gen_message.encode_to_json()
            self._socket.send(gen_message_json.encode(self.ENCODING_))

    def read_server_response(self):
        while True:
            try:
                response = self.get_data()
                response = self.parse_message(response)
                print(f'Статус: {response.response}, {response.alert}')
            except Exception:
                print(response)

    # @Log(CLIENT_LOG)
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
