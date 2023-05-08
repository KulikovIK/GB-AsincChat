from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
from datetime import datetime


class ClientDB:
    metadata = MetaData()
    def __init__(self):
        self.user = Table(
            'User', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String)
        )

        self.contact_list = Table(
            'contact_list', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('host_id', ForeignKey('User.id')),
            Column('contact_id', ForeignKey('User.id')),
            )

        self.user_history = Table(
            'user_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('time', DateTime),
            Column('from_', ForeignKey('User.name')),
            Column('to_', ForeignKey('User.name')),
            Column('msg', Text),
            )

