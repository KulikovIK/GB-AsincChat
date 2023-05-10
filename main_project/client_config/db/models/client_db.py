from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
from sqlalchemy.orm import registry
from datetime import datetime


mapper_register = registry()

user = Table(
    'User', mapper_register.metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String)
)

contact_list = Table(
    'contact_list', mapper_register.metadata,
    Column('id', Integer, primary_key=True),
    # Column('host_id', ForeignKey('User.name')),
    Column('contact_id', ForeignKey('User.name')),
)

message_history = Table(
    'user_history', mapper_register.metadata,
    Column('id', Integer, primary_key=True),
    Column('time', DateTime),
    Column('from_', ForeignKey('User.name')),
    Column('to_', ForeignKey('User.name')),
    Column('message', Text),
)


class User:
    def __repr__(self) -> str:
        return User.name


class Message_history:
    pass


class Contact_list:
    pass


mapper_register.map_imperatively(User, user)
mapper_register.map_imperatively(Contact_list, contact_list)
mapper_register.map_imperatively(Message_history, message_history)
