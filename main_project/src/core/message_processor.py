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
    def get_object_from_json(json_obj):
        return json.JSONDecoder(object_hook=MessageProcessor).decode(json_obj)
    
    @staticmethod
    def create_presence_message(name, action, time=time.ctime()):
        return MessageProcessor(
            {
                'action': action, 
                'time': time,
                'user':{
                    'name': name,
                    'status': 'here'
                }
            }
        )

    @staticmethod
    def create_response_message(code, alert=None):
        return MessageProcessor({'response': code, 'alert': alert})