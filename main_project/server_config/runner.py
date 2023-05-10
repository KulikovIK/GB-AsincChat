from socket import *
import select
from src.core.message_processor import MessageProcessor
from src.core.log_decorator import Log
from threading import Thread

import logging
from server_config.loger import config_server_log
from src.core.log_decorator import Log

import hmac
import hashlib
import os
import json

from server_config.server_verifier import ServerVerifier
from server_config.db.server_db import DB as ServerDB
from server_config.db.models.messanger_db import User, User_history, Contact_list

SERVER_LOG = logging.getLogger("server")


class Server(metaclass=ServerVerifier):

    BLOCK_LEN: int = 1024
    EOM: bytes = b'ENDOFMESSAGE___'
    ENCODING_ = 'utf-8'

    messanger = MessageProcessor

    _socket = socket(AF_INET, SOCK_STREAM)
    connections = []
    clients = []
    client_host_port = {}
    names = {}

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.db = ServerDB()
        self._socket.bind((self.host, self.port))
        self._socket.listen(5)
        self._socket.settimeout(0.5)
        self.session = self.db.session
        super().__init__()

    def __del__(self):
        self._socket.close()
       

    def run(self):
        """Функция запуска сервера."""
        while True:
            try:
                client, addr = self._socket.accept()
            except OSError:
                pass
            
            else:
                print(f'Запрос получен от {str(addr)}')
                SERVER_LOG.debug(f'Запрос получен от {str(addr)}')
                self.identify(client)
                self.server_authenticate(client)
                self.client_host_port[client] = addr
                # client.settimeout(5)
                self.clients.append(client)

            responce_ = []
            write_ = []
            errors_ = []

            try:
                if self.clients:
                    responce_, write_, errors_ = select.select(self.clients, self.clients, [], 0)
            except OSError as err:
                SERVER_LOG.error(f'Ошибка работы с сокетами: {err.errno}')
            if write_:
                # for client_message in write_:
                msgs, names = self.recieve(write_, self.names, self.clients, self.client_host_port)
                if 'all' in msgs:
                    self.send_to_all(msgs, responce_)
                if msgs:
                    self.send_to_user(names, msgs)


    def server_authenticate(self, connection):
        """Аутентификация клиента"""
        message = os.urandom(32)
        connection.send(message)
        hash = hmac.new(b'our_secret_key', message, digestmod = hashlib.sha256)
        digest = hash.digest()
        response = connection.recv(len(digest))
        print(digest)
        print(response)
        if hmac.compare_digest(digest, response)== False:
            connection.close()

    def identify(self, client):
        """Идентификация клиента"""
        name_password = client.recv(10000)
        name_password=json.loads(name_password.decode('utf-8'))
        client_password = self.session.query(User).filter_by(name=name_password['name']).first()

        if client_password is None:
            solt = os.urandom(16)
            hash_password = hashlib.pbkdf2_hmac('sha256', name_password['password'].encode(), solt, 100000)
            
            hash = solt + hash_password

            client_password = User(password=hash, name=name_password['name'])

            self.session.add(client_password)
            self.session.commit()
            print('Client are registered. Try to enter again')
            client.close()
        else:

            solt= client_password.password[:16]
            hash_password = hashlib.pbkdf2_hmac('sha256', name_password['password'].encode(), solt, 100000)
            if hash_password!=client_password.password[16:]:
                print('Идентификация не пройдена')
                client.close()


    # def log(func):
    #     @wraps(func)
    #     def call(*args, **kwargs):
    #         main_func=inspect.stack()[-2][-3]
    #         logger.debug(f'Func {func.__name__}{args, kwargs} was called from {main_func}')
    #         return func(*args, **kwargs)
    #     return call
    # @log

    @Log(SERVER_LOG)
    def send_to_all(self, msgs, w):
        """Отправка сообщения всем"""
        try:
            group_messages= msgs['all']
            if type(group_messages)==list:
                for msg in group_messages:
                    for c in w:
                        try:
                            c.send(msg.encode('utf-8'))
                            SERVER_LOG.debug(f'{msg} is sent')
                        except:
                            c.close()
                            self.clients.remove(c)
                            SERVER_LOG.error('Клиент отключился')
                msgs.pop('all')
            else:
                for c in w:
                    try:
                        c.send(group_messages.encode('utf-8'))
                        SERVER_LOG.debug(f'{group_messages} is sent')
                    except:
                        c.close()
                        self.clients.remove(c)
                        SERVER_LOG.error('Клиент отключился')
        except BaseException as e:
            SERVER_LOG.error(e)

    def send_to_user(self, names, msgs):
        """Отправка сообщения клиенту"""
        try:
            for key in msgs:
                if key in names:
                    msg=msgs[key]
                    client=names[key]
                    if type(msg)==list:
                        for m in msg:
                            client.send(m.encode('utf-8'))
                            SERVER_LOG.debug(f'{m} is sent')
                    else:
                        client.send(msg.encode('utf-8'))
                        SERVER_LOG.debug(f'{msg} is sent')

                else:
                    SERVER_LOG.error('Такого пользователя в чате нет')
        except BaseException as e:
            SERVER_LOG.error(e)

    def recieve(self, r, names, clients, client_host_port):
        """Получение сообщений, разбор, перенаправление"""
        msgs= {}
        for client in r:
            try:
                data = client.recv(100000)
                try:
                    data=data.decode('utf-8')
                    data= data.replace('}{', '};{')
                    msgs_in_data=data.split(';')
                    for msg in msgs_in_data:
                        json_data = json.loads(msg)
                        if json_data['action'] == 'presence':
                            SERVER_LOG.debug('got presence')
                            names[json_data['user']['name']]=client

                            self.client_login(json_data['user']['name'], ip=str(client_host_port[client]))

                            msgs[json_data['user']['name']]=[json.dumps({'response': 200, 'alert': 'ok'})]

                        elif json_data['action'] == 'exit':
                            pass
                        elif json_data['action'] == 'msg':
                            SERVER_LOG.debug('got message')
                            try:
                                msgs[json_data['to_user']].append(json.dumps(json_data))
                            except:
                                msgs[json_data['to_user']] = json.dumps(json_data)

                        elif json_data['action'] == 'get_contacts' and json_data['user_login'] in names:
                            SERVER_LOG.debug('got get contacts')
                            contact_list=self.client_contact_list(json_data['user_login'])
                            answer= json.dumps({'response': 202, 'alert': contact_list})
                            msgs[json_data['user_login']]=answer

                        elif json_data['action'] == 'add_contact':
                            SERVER_LOG.debug('got add contact')
                            msgs[json_data['user_login']]=self.add_contact(json_data['user_id'], json_data['user_login'])

                        elif json_data['action'] == 'del_contact':
                            SERVER_LOG.debug('got del contact')
                            msgs[json_data['user_login']]=self.del_contact(json_data['user_id'], json_data['user_login'])

                    return msgs, names
                except:
                    json_data = json.loads(data)
                    if json_data['action'] == 'presence':
                        SERVER_LOG.debug('got presence')
                        names[json_data['user']['name']] = client

                        self.client_login(json_data['user']['name'], ip=str(client_host_port[client]))

                        msgs[json_data['user']['name']]=[json.dumps({'response': 200, 'alert': 'ok'})]

                    elif json_data['action'] == 'msg':
                        SERVER_LOG.debug('got message')
                        try:
                            msgs[json_data['to_user']].append(json.dumps(json_data))
                        except:
                            msgs[json_data['to_user']]=json.dumps(json_data)

                    elif json_data['action'] == 'get_contacts':
                        SERVER_LOG.debug('got get contacts')

                        msgs[json_data['user_login']] = [
                        json.dumps({'response': 202, 'alert': self.client_contact_list(json_data['user_login'])})]

                    return msgs, names

            except BaseException as e:
                for key, val in names.items():
                    if val==client:
                        self.client_logout(key)
                SERVER_LOG.error(e)
                self.clients.remove(client)
                return msgs, names

    # def get_socket(self):
    #     """Создание подключения"""
    #     s=socket(AF_INET, SOCK_STREAM)
    #     s.bind((self.host, self.port))
    #     s.settimeout(0.5)

    #     s.listen(10)

    #     return s

    def del_contact(self, nickname, name):
        """Удаление контакта"""
        contact = self.session.query(User).filter_by(name=nickname).first()
        if contact is None:
            answer = json.dumps({'response': 400, 'alert': f'{nickname} not in contacts'})
            return answer

        try:
            del_contact=self.session.query(Contact_list).filter_by(contact_id=contact.id).first()
            self.session.delete(del_contact)
            self.session.commit()
            answer = json.dumps({'response': 200, 'alert': f'{nickname} deleted from contacts'})
        except:
            answer = json.dumps({'response': 400, 'alert': f'{nickname} not in your contacts'})

        return answer

    def add_contact(self, nickname, name):
        """Добавление контакта"""
        new_contact = self.session.query(User).filter_by(name=nickname).first()
        print("*"*50)
        print(nickname)
        print(name)
        print(new_contact)
        print("*"*50)
        if new_contact is None:
            new_contact = User(name=nickname, is_active=False)
            self.session.add(new_contact)
            self.session.commit()
        else:
            checking= self.session.query(Contact_list).filter_by(contact_id=new_contact.id).first()
            if checking is None:
                host= self.session.query(User).filter_by(name=name).first()
                contact_for_list=Contact_list(host.id, new_contact.id)
                self.session.add(contact_for_list)
                self.session.commit()
                answer=json.dumps({'response': 200, 'alert': f'{nickname} add into contacts'})
            else:
                answer=json.dumps({'response': 400, 'alert': 'Already in contacts'})

        return answer

    def client_contact_list(self, name):
        """Формирует список контактов клиента"""
        try:
            host = self.session.query(User).filter_by(name=name).first()
            client_list=self.session.query(Contact_list).filter_by(host_id=host.id).all()
            result = []
            for client in client_list:
                contact=self.session.query(User).filter_by(id=client.contact_id).first()
                if contact is None:
                    break
                result.append(contact.name)
            return result
        except:
            SERVER_LOG.error('DataBase error')

    def client_logout(self, name):
        """Фиксирует выход клиента"""
        try:
            client = self.session.query(User).filter_by(name=name).first()
            client.is_active=False
            print('Session. Changes:', self.session.dirty)
            self.session.commit()

        except:
            self.session.rollback()

    def client_login(self, name, ip):
        """Фиксирует вход клиента"""
        try:
            client= self.session.query(User).filter_by(name=name).first()
            if client is None:
                client = User(name)
                self.session.add(client)

            client.is_active=True
            client_history = User_history(ip, client.name)

            self.session.add(client)
            self.session.add(client_history)

            print('Session. New objects:', self.session.new)
            self.session.commit()

        except:
            return SERVER_LOG.error('Basedata error')

if __name__=='__main__':

    server= Server(port, ip)

    server.daemon = True
    server.run()

    # # @Log(SERVER_LOG)
    # def parse_message(self, message):
    #     message = message.decode(self.ENCODING_)
    #     parsed_message = self.messanger.get_object_from_json(message)
    #     return parsed_message

    # # @Log(SERVER_LOG)
    # def run(self):
    #     print(f"Сревер поднят на хосте: {self.host} с портом: {self.port}")
    #     while True:
    #         try:
    #             client, address = self._socket.accept()
    #         except OSError:
    #             pass
    #         else:
    #             print(f'Получен запрос на соединение от: {address}')
    #             self.connections.append(client)
    #         finally:
    #             responce_ = []
    #             write_ = []
    #             try:
    #                 responce_, write_, excepttions_ = select.select(
    #                     self.connections, self.connections, [], 0)
    #             except Exception:
    #                 pass
    #             for client in responce_:
    #                 try:
    #                     data = client.recv(self.BLOCK_LEN)

    #                     parsed_message = self.parse_message(data)                        
    #                     if parsed_message.action == "presence" and (client in write_):
    #                         # self.db.
    #                         self.send_responce(
    #                             client=client, code=200, alert=f"{parsed_message.from_user.name} {parsed_message.from_user.status} подключился к чату", all=True)
    #                     if (parsed_message.action == 'msg' and parsed_message.to_user == 'ALL') and (client in write_):
    #                         self.send_responce(
    #                             client=client, code=200, alert=f'{parsed_message.from_user.name}: {parsed_message.message}', all=True)
    #                 except:
    #                     print(f"Соединение разорвано c {client}")
    #                     self.connections.remove(client)

    # # @Log(SERVER_LOG)
    # def send_responce(self, client, code, alert=None, all=False):
    #     gen_response = self.messanger.create_response_message(code, alert)
    #     gen_response_json = gen_response.encode_to_json()
    #     if all:
    #         for client in self.connections:
    #             client.sendall(gen_response_json.encode(self.ENCODING_))
    #     client.send(gen_response_json.encode(self.ENCODING_))
