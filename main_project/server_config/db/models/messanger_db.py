from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine, DateTime, Boolean, Text
from sqlalchemy.orm import registry
from datetime import datetime
from sqlalchemy import create_engine
from server_config.db.db_config import Config


# metadata = MetaData()
mapper_register = registry()

user = Table(
            'User', 
            mapper_register.metadata,
            Column('id', Integer, primary_key=True),
            Column('login', String(24), nullable=False),
            Column('password', String(120), nullable=False),
            Column('is_active', Boolean),
        )

user_history = Table(
            'User_history', 
            mapper_register.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, ForeignKey('User.id', ondelete='CASCADE'), nullable=False),
            Column('entry_time', DateTime, default=datetime.utcnow),
            Column('ip_address', String(256), nullable=False)
        )

contact_list = Table(
        'Contact_list', 
        mapper_register.metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', ForeignKey('User.id', ondelete='CASCADE'), nullable=False),
        Column('contact_id', ForeignKey('User.id', ondelete='CASCADE'), nullable=False)
        )



# engine = create_engine(Config.__dict__["SQLALCHEMY_DATABASE_URI"], echo=True)

# mapper_register.metadata.create_all(engine)


class User:
    pass
    # def __init__(self, login, password, is_active):
    #     self.login = login
    #     self.password = password
    #     self.is_active = is_active

class User_history:
    pass
    # def __init__(self, user_id, entry_time, ip_address):
    #     self.user_id = user_id
    #     self.entry_time = entry_time
    #     self.ip_address = ip_address

class Contact_list:
    pass
    # def __init__(self, user_id, contact_id):
    #     self.user_id = user_id
    #     self.contact_id = contact_id

mapper_register.map_imperatively(User, user)
mapper_register.map_imperatively(Contact_list, contact_list)
mapper_register.map_imperatively(User_history, user_history)
