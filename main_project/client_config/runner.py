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


CLIENT_LOG = logging.getLogger("client")

secret_key = b'our_secret_key'


socket_lock = threading.Lock()

class Client(threading.Thread, metaclass=ClientVerifier):

    BLOCK_LEN: int = 1024
    EOM: bytes = b'ENDOFMESSAGE___'
    ENCODING_ = 'utf-8'

    messanger = MessageProcessor

    _socket = socket(AF_INET, SOCK_STREAM)

    def __init__(self, host: str, port: int, login: str = None, password: str = None) -> None:
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.db = ClientDB()
        self.session = self.db.session
        self.connect()


    def __del__(self):
        self._socket.close()

    def connect(self):
        self._socket.connect((self.host, self.port))
        gen_message = self.messanger.create_presence_message(
                from_user=self.login, password=self.password)
        gen_message_json = gen_message.encode_to_json()
        self._socket.send(gen_message_json.encode(self.ENCODING_))


    def client_authenticate(connection):
        """Аутентификация клиента"""
        message = connection.recv(32)
        hash = hmac.new(b'our_secret_key', message, digestmod = hashlib.sha256)
        digest = hash.digest()
        connection.send(digest)

    def get_contacts(self):
        """Запрос списка контактов"""
        return json.dumps({"action": "get_contacts","time": time.ctime(),"user_login": self.name})

    def add_contact(self, nickname):
        """Запрос на добавление контакта"""
        return json.dumps({"action": "add_contact","user_id": nickname,"time": time.ctime(),"user_login": self.name})

    def del_contact(self, nickname):
        """Запрос на удаление контакта"""
        return json.dumps({"action": "del_contact","user_id": nickname,"time": time.ctime(),"user_login": self.name})

    def create_presence_msg(self):
        """Формирование presence сообщение"""
        return json.dumps({"action": "presence",
                "time": time.ctime(),
                "user":{"name": self.login,"status": "here"}})

    def create_exit_msg(self):
        """Формирование сообщения о выходе"""
        return json.dumps({"action": "exit",
                           "time": time.ctime(),
                           "user": {"name": self.login, "status": "here"}})

    def create_msg(self,to_user, text):
        """Формирование сообщения"""
        return json.dumps({"action": "msg",
                           "text":text,
                "time": time.ctime(),
                "user":{"name": self.name,"status": "here"},
                          'to_user':to_user})

    def send(self, msg):
        """Функция отправки запросов и сообщений"""
        try:
            self._socket.send(msg.encode('utf-8'))
            CLIENT_LOG.debug(f'The message {msg} is sent')
            msg= json.loads(msg)
            if msg['action']=="msg":
               self.add_msg_in_history(msg, True)
            elif msg['action'] == "add_contact":
                self.contact_in_database(msg['user_id'], 'add')
            elif msg['action'] == "del_contact":
                self.contact_in_database(msg['user_id'], 'del')
            elif msg['action'] == "get_contacts":
                self.contact_in_database(msg['user_login'], 'get')

        except AttributeError as e:
            print(e)
            CLIENT_LOG.error(e)

    def contact_in_database(self, nickname, command):
        """Добавление контакта в базу данных клиента"""
        try:
            client=self.session.query(User).filter_by(name=self.login).first()
            contact = self.session.query(User).filter_by(name=nickname).first()
            if contact is None:
                contact = User(nickname)
                self.session.add(contact)
                self.session.commit()
            if client is None:
                client = User(self.login)
                self.session.add(client)
                self.session.commit()
            if command == 'add':
                contact_list = self.session.query(Contact_list).filter_by(contact_id=contact.id, host_id=client.id).first()

                if contact_list is None:
                    contact_list = Contact_list(client.id, contact.id)
                    self.session.add(contact_list)
                    self.session.commit()
                else: CLIENT_LOG.debug(f'{nickname} уже в списке контактов')
            elif command=='del':
                try:
                    contact_list = self.session.query(Contact_list).filter_by(contact_id=contact.id,
                                                                         host_id=client.id).first()
                    self.session.delete(contact_list)
                    self.session.commit()
                    CLIENT_LOG.debug(f'{nickname} удален из списка контактов')
                except:
                    CLIENT_LOG.debug(f'{nickname} ошибка удаления')
            elif command=='get':
                result=[]
                contact_list = self.session.query(Contact_list).all()
                for line in contact_list:
                    contact=self.session.query(User).filter_by(id=line.contact_id).first()
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
                    client=self.session.query(User).filter_by(name=self.name).first()
                    if client is None:
                        client = User(self.name)
                        self.session.add(client)
                    contact = self.session.query(User).filter_by(name=msg['to_user']).first()
                    if contact is None:
                        contact = User(msg['to_user'])
                        self.session.add(contact)
                    msg = Message_history(client.name, contact.name, msg['text'])
                    self.session.add(msg)
                    self.session.commit()
                except:
                    self.session.rollback()
                    CLIENT_LOG.debug('Error, can`t add message into database')
            else:
                try:
                    client=self.session.query(User).filter_by(name=msg['to_user']).first()
                    if client is None:
                        client = User(self.name)
                        self.session.add(client)
                    contact = self.session.query(User).filter_by(name=msg['user']['name']).first()
                    if contact is None:
                        contact = User(msg['to_user'])
                        self.session.add(contact)
                    msg = Message_history(contact.name, client.name, msg['text'])
                    self.session.add(msg)
                    self.session.commit()

                    self.got_message = True
                except:
                    self.session.rollback()
                    CLIENT_LOG.debug('Error, can`t add message into database')

    def user_communication(self):
        name=input('Please, enter your name')
        while 1:
            msg=input('Enter your message, or q for exit')
            if msg=='q':
                break
            else:
                self.send(self.create_msg(name, msg), self._socket)

    def recieve(self):
        """Функция получения сообщений"""
        time.sleep(2)
        while True:
            try:
                data = self._socket.recv(10000)
                CLIENT_LOG.debug(f'The message {data.decode("utf-8")} is recieved ')
                data= data.decode("utf-8")
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

    def message_bot_sender(self):

        msg = self.create_presence_msg()
        msg_2 = self.create_msg('all', "Anybody is here?")
        msg_3 = self.create_msg('Thomas', "It seems, there are nobody")
        msg_5 = self.create_presence_msg()
        msg_4 = self.create_msg('all', "Good bue")
        msg_5= self.get_contacts()
        msg_6=self.add_contact('Thomas')
        msg_7=self.del_contact('Bill')
        msg_8=self.add_contact('Bill')
        msg_9 = self.add_contact('Bob')
        msgs = [msg, msg_2, msg_5, msg_4]

        for msg in msgs:
            self.send(msg)
            time.sleep(5)
