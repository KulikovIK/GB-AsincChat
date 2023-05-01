import json
import time
from typing import Any


class MessageProcessorEncoder(json.JSONEncoder):
    def default(self, obj) -> Any:
        return obj.__dict__

class MessageProcessor():

    def __init__(self, msg) -> None:
        for key, val in msg.items():
            if isinstance(val, dict):
                sub_val = MessageProcessor(val)
                setattr(self, key, sub_val)
            else:
                setattr(self, key, val)

    def encode_to_json(self):
        return MessageProcessorEncoder().encode(self)
    
    @staticmethod
    def _gen_default_message( from_user, action):
        return {
            "action": action, 
            "time": time.ctime(),
            "from_user":{
                "name": from_user,
                "status": "here",
            }
        }
    
    @staticmethod
    def get_object_from_json(json_obj):
        return json.JSONDecoder(object_hook=MessageProcessor).decode(json_obj)
    
    @staticmethod
    def create_presence_message(from_user, action):
        mesage = MessageProcessor._gen_default_message(from_user=from_user, action=action)
        return MessageProcessor(mesage)


    @staticmethod
    def create_message_to_user(from_user, action, to_user, message):
        mesage = MessageProcessor._gen_default_message(from_user, action)
        mesage['to_user'] = to_user
        mesage['message'] = message
        return MessageProcessor(mesage)
    
    @staticmethod
    def create_message_to_chat(from_user, action, message,):
        mesage = MessageProcessor._gen_default_message(from_user, action)
        mesage["to_user"] = "ALL"
        mesage["message"] = message
        return MessageProcessor(mesage)
    
    @staticmethod
    def join_chat(from_user, action, room_name):
        mesage = MessageProcessor._gen_default_message(from_user, action)
        mesage["room"] = room_name
        return MessageProcessor(mesage)
    
    @staticmethod
    def leave_chat(from_user, action, room_name):
        mesage = MessageProcessor._gen_default_message(from_user, action)
        mesage["room"] = room_name
        return MessageProcessor(mesage)

    @staticmethod
    def create_response_message(code, alert=None):
        return MessageProcessor({'response': code, 'alert': alert})