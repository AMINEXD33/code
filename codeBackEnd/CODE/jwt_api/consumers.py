# chat/consumers.py
import json
from typing import Callable
from channels.generic.websocket import WebsocketConsumer
from jwt_multi_workers.redis_server_conf import custom_redis
from channels.generic.websocket import AsyncWebsocketConsumer

from .consumers_methods import *
redis_conn = custom_redis().conn
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.authenticated = False
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, bytes_data=None):
        decompressed_data:str = decompress(bytes_data)
        try:
            # here it should return a dict but the type i get is str
            text_data_json:dict = json.loads(json.loads(decompressed_data))
            print(text_data_json["type"])
            print(text_data_json)
            message_type:str = text_data_json.get("type")
            if message_type == "auth":
                token = text_data_json.get("token")
                self.authenticated = await self.authenticate(token)
                if not self.authenticated:
                    await self.close()
                else:
                    print("sending ok message")
                    compressed_data:bytes = compress(json.dumps({"type":"info", "message": "ok"}))
                    await self.send(bytes_data=compressed_data)
            elif message_type == "echoback":
                await self.handle_some_event(decompressed_data)
            elif self.authenticated:
                # Handle other messages
                await self.handle_other_messages(text_data_json)
        except Exception as e:
            print(e)

    async def authenticate(self, token):
        # Implement your token validation logic here
        return token == "your_valid_token"

    async def handle_some_event(self, daya):
        # Handle the event and decide to close the connection
        compressed_data:bytes = compress(json.dumps(data))
        await self.send(
            bytes_data=compressed_data
        )
        await self.close()

    async def handle_other_messages(self, message):
        # Handle other messages
        compressed_data:bytes = compress(json.dumps({"type": "message", "content": message}))
        await self.send(bytes_data=compressed_data)


class track_stats(AsyncWebsocketConsumer):
    async def connect(self):
        self.authenticated = False
        await self.accept()

    async def disconnect(self, close_code):
        client_ip = self.scope['client'][0]
        

        #superclass's disconnect method 
        await super().disconnect(close_code)

    async def authenticate(self, token):
        # Implement your token validation logic here
        return token == "your_valid_token"

    async def receive(self, bytes_data=None):
        decompressed_data:str = decompress(bytes_data)
        try:
            text_data_json:dict = json.loads(json.loads(decompressed_data))
            message_type:str = text_data_json.get("type")
            if message_type == "auth":
                token = text_data_json.get("token")
                self.authenticated = await self.authenticate(token)
                if not self.authenticated:
                    await self.close()
                else:
                    print("sending ok message")
                    compressed_data:bytes = compress(json.dumps({"type":"info", "message": "ok"}))
                    await self.send(bytes_data=compressed_data)
            
            # only authenticated connections are allowed to send 
            # message types
            if self.authenticated == True:
                self.FUNCTION_handle_message_type_callBack(message_type, decompressed_data)

        
        except Exception as e:
            print(e)

    async def FUNCTION_handle_message_type_callBack(message_type:str, decompressed_data:str):
        if message_type == "echoback":
            self.FUNCTION_handle_message_type_callBack(decompressed_data)
            await self.handle_some_event(decompressed_data)
        else:
            # Handle other messages
            await self.handle_other_messages(text_data_json)

    async def handle_some_event(self, daya):
        # Handle the event and decide to close the connection
        compressed_data:bytes = compress(json.dumps(data))
        await self.send(
            bytes_data=compressed_data
        )
        await self.close()

    async def handle_other_messages(self, message):
        # Handle other messages
        compressed_data:bytes = compress(json.dumps({"type": "message", "content": message}))
        await self.send(bytes_data=compressed_data)