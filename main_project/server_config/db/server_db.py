from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DisconnectionError
import os

from server_config.db.db_config import Config
from server_config.db.models.messanger_db import mapper_register

class DB(object):
    DB_BASE = mapper_register.metadata

    def __init__(self):
        self.config = Config.__dict__
        if self.config["DEBUG"]:
            echo = True
        else:
            echo = False
        self.engine = create_engine(self.config["SQLALCHEMY_DATABASE_URI"], echo=echo)
        self.create_tables()
        session = sessionmaker(bind=self.engine)
        self.session = session()

    def check_connection(self):
        result = False
        try:
            conn = self.engine.connect()
            result = True
        except DisconnectionError:
            pass
        finally:
            conn.close()

        return result

    def create_tables(self):   
        self.DB_BASE.create_all(self.engine)

    def drop_tables(self):
        self.DB_BASE.drop_all(self.engine)
