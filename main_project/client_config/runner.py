from socket import *
import time
from src.core.message_processor import MessageProcessor
from src.core.log_decorator import Log
import threading
import json

import hmac
import hashlib

import logging
from client_config.loger import config_client_log

from client_config.client_verifier import ClientVerifier
from client_config.db.client_db import DB as ClientDB
from client_config.db.models.client_db import User, Message_history, Contact_list
from src.core.message_processor import MessageProcessor


CLIENT_LOG = logging.getLogger("client")

secret_key = b'our_secret_key'


socket_lock = threading.Lock()


class Client(threading.Thread, metaclass=ClientVerifier):

    BLOCK_LEN: int = 1024
    EOM: bytes = b'ENDOFMESSAGE___'
    ENCODING = 'utf-8'

    messanger = MessageProcessor

    _socket = socket(AF_INET, SOCK_STREAM)

    def __init__(self, host: str, port: int, login: str = None, password: str = None) -> None:
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.db = ClientDB()
        self.session = self.db.session
        self.get_user_from_db(name=login)
        self._socket.connect((self.host, self.port))

        self.login_user(login=login, password=password)

        # self.send(MessageProcessor.create_presence_message(from_user=self.db_user))

    def __del__(self):
        self._socket.close()

    def login_user(self, login, password):
        "Подключение к серверу"
        self._socket.send(json.dumps(
            {'name': login, 'password': password}).encode(self.ENCODING))
        time.sleep(1)
        self.client_authenticate()

    def client_authenticate(self):
        """Аутентификация клиента"""
        message = self._socket.recv(self.BLOCK_LEN)
        hash = hmac.new(b'our_secret_key', message, digestmod=hashlib.sha256)
        digest = hash.digest()
        self._socket.send(digest)

    def get_data_as_dict(self):
        """Получение данных с сервера и преобразование их в словарь"""
        data = self._socket.recv(self.BLOCK_LEN)
        data.decode(self.ENCODING)
        return json.loads(data)

    def get_user_from_db(self, name):
        """Получение данных о пользователе из локальной базы данных"""
        self.db_user = self.session.query(User).filter_by(name=name).first()
        if self.db_user is None:
            self.db_user = User(name=name)
            self.session.add(self.db_user)
            self.session.commit()

    def get_contact_list_from_db(self):
        """Получение контактов из локальной базы данных"""
        result = []
        contact_list = self.session.query(
            Contact_list).filter_by(host_id=self.db_user.id).all()
        for contact in contact_list:
            contact = self.session.query(User).filter_by(
                id=contact.contact_id).first()
            result.append(contact.name)
        return result

    def add_contact(self, nickname):
        contact = self.session.query(User).filter_by(name=nickname).first()
        if contact is None:
            contact = User(name=nickname)
            self.session.add(contact)
            self.session.commit()
            contact = self.session.query(User).filter_by(name=nickname).first()

        self.session.add(Contact_list(
            host_id=self.db_user.id, 
            contact_id=contact.id))
        
        self.session.commit()

        return MessageProcessor.add_contact(from_user=self.db_user, user_id=contact.id)

    def add_message_to_db(self, message: dict):

        history = Message_history(
            from_=message.__dict__["from_user"].__dict__["name"],
            to_=message.__dict__["to_user"],
            message=message.__dict__["message"],
            time=message.__dict__["time"]
        )

        self.session.add(history)
        self.session.commit()

    def create_message(self, to_user, text):
        """Формирование сообщения"""
        return MessageProcessor.create_message_to_user(from_user=self.db_user, to_user=to_user, message=text)

    def send(self, data_for_send: MessageProcessor):
        """Функция отправки запросов и сообщений"""
        try:
            self._socket.send(
                data_for_send.encode_to_json().encode(self.ENCODING))
            CLIENT_LOG.debug(f'Сообщение {data_for_send} отправлено')
            self.add_message_to_db(data_for_send)
            # msg= json.loads(msg)
            # if msg['action']=="msg":
            #    self.add_msg_in_history(msg, True)
            # elif msg['action'] == "add_contact":
            #     self.contact_in_database(msg['user_id'], 'add')
            # elif msg['action'] == "del_contact":
            #     self.contact_in_database(msg['user_id'], 'del')
            # elif msg['action'] == "get_contacts":
            #     self.contact_in_database(msg['user_login'], 'get')

        except AttributeError as e:
            print(e)
            CLIENT_LOG.error(e)

    def contact_in_database(self, nickname, command):
        """Добавление контакта в базу данных клиента"""
        try:

            client = self.session.query(
                User).filter_by(name=self.login).first()
            contact = self.session.query(User).filter_by(name=nickname).first()
            if contact is None:
                contact = User(name=nickname)
                print("client", client)
                self.session.add(contact)
                self.session.commit()
            if client is None:
                client = User(name=self.login)
                print("contact", contact)
                self.session.add(client)
                self.session.commit()
            if command == 'add':
                contact_list = self.session.query(Contact_list).filter_by(
                    contact_name=contact.name, host_name=client.name).first()

                if contact_list is None:
                    contact_list = Contact_list(
                        host_name=client.name, contact_name=contact.name)
                    self.session.add(contact_list)
                    self.session.commit()
                else:
                    CLIENT_LOG.debug(f'{nickname} уже в списке контактов')
            elif command == 'del':
                try:
                    contact_list = self.session.query(Contact_list).filter_by(contact_id=contact.id,
                                                                              host_id=client.id).first()
                    self.session.delete(contact_list)
                    self.session.commit()
                    CLIENT_LOG.debug(f'{nickname} удален из списка контактов')
                except:
                    CLIENT_LOG.debug(f'{nickname} ошибка удаления')
            elif command == 'get':
                result = []
                contact_list = self.session.query(Contact_list).all()
                for line in contact_list:
                    contact = self.session.query(User).filter_by(
                        id=line.contact_id).first()
                    result.append(contact.name)
                CLIENT_LOG.debug(f'Cписок контактов: {result} ')
        except:
            self.session.rollback()
            CLIENT_LOG.debug('Error, can`t add/del/get contact ')

    def add_msg_in_history(self, msg, send=True):
        """Добаление сообщения в базу данных клиента"""
        with socket_lock:
            if send:
                try:
                    client = self.session.query(
                        User).filter_by(name=self.login).first()
                    if client is None:
                        client = User(self.login)
                        self.session.add(client)
                    contact = self.session.query(User).filter_by(
                        name=msg['to_user']).first()
                    if contact is None:
                        contact = User(msg['to_user'])
                        self.session.add(contact)
                    msg = Message_history(
                        client.login, contact.login, msg['text'])
                    self.session.add(msg)
                    self.session.commit()
                except:
                    self.session.rollback()
                    CLIENT_LOG.debug('Error, can`t add message into database')
            else:
                try:
                    client = self.session.query(User).filter_by(
                        name=msg['to_user']).first()
                    if client is None:
                        client = User(self.login)
                        self.session.add(client)
                    contact = self.session.query(User).filter_by(
                        name=msg['user']['name']).first()
                    if contact is None:
                        contact = User(msg['to_user'])
                        self.session.add(contact)
                    msg = Message_history(
                        contact.name, client.name, msg['text'])
                    self.session.add(msg)
                    self.session.commit()

                    self.got_message = True
                except:
                    self.session.rollback()
                    CLIENT_LOG.debug('Error, can`t add message into database')

    def user_communication(self):
        name = input('Please, enter your name')
        while 1:
            msg = input('Enter your message, or q for exit')
            if msg == 'q':
                break
            else:
                self.send(self.create_msg(name, msg), self._socket)

    def recieve(self):
        """Функция получения сообщений"""
        time.sleep(2)
        while True:
            try:
                data = self.get_data_as_dict()
                print("\n\nrecived     ", data)
                CLIENT_LOG.debug(
                    f'The message {data.decode("utf-8")} is recieved ')
                data = data.decode("utf-8")
                data = data.replace('}{', '};{')
                msgs_in_data = data.split(';')
                for msg in msgs_in_data:
                    json_data = json.loads(msg)
                    if json_data.get('action'):
                        self.add_msg_in_history(json_data, False)
            except BaseException as e:
                CLIENT_LOG.error(e)
                CLIENT_LOG.debug(f'recieve finished')
                break
