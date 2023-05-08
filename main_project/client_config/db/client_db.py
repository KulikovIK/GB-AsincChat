from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DisconnectionError
import os
from client_config.db.models.client_db import ClientDB

class DB(object):
    DB_BASE = ClientDB()

    def __init__(self, config_dict):
        self.config = config_dict
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
        self.DB_BASE.metadata.create_all(self.engine)

    def drop_tables(self):
        self.DB_BASE.metadata.drop_all(self.engine)