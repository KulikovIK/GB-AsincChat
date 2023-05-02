from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from datetime import datetime


class MessangerDB:
    metadata = MetaData()
    def __init__(self):

        self.user = Table(
            'user', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('login', String(24), nullable=False),
            Column('first_name', String(24), nullable=False),
            Column('last_name', String(60), nullable=False),
            Column('password', String(120), nullable=False)
        )

        self.user_history = Table(
            'user_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
            Column('entry_time', DateTime, default=datetime.utcnow),
            Column('ip_address', String(256), nullable=False)
        )

        self.contact_list = Table(
            'contact_list', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
            Column('contact_id', ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
        )
