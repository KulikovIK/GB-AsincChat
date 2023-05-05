from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from datetime import datetime


class ClientDB:
    metadata = MetaData()
    def __init__(self):

        self.contact_list = Table(
            'contact_list', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('contact_id', Integer)
        )

        self.user_history = Table(
            'user_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, ForeignKey('contact_list.contact_id', ondelete='CASCADE'), nullable=False),
            Column('entry_time', DateTime, default=datetime.utcnow),
            Column('ip_address', String(256), nullable=False)
        )

