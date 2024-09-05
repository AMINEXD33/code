# chat/consumers.py
import json
from typing import Callable
from channels.generic.websocket import WebsocketConsumer
from jwt_multi_workers.redis_server_conf import custom_redis
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from .consumers_methods import *
from .models import *
from .consumers_soft_records_system import SoftRecords
# reference to the jwt_module to handle authentication
reference = apps.get_app_config("jwt_api").my_object


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.authenticated = False
        self.soft_records = SoftRecords(reference.Redis)
        await self.accept()amines

    async def disconnect(self, close_code):
        pass

    async def receive(self, bytes_data=None):
        decompressed_data: str = decompress(bytes_data)
        try:
            # here it should return a dict but the type i get is str
            text_data_json: dict = json.loads(json.loads(decompressed_data))
            print(text_data_json["type"])
            print(text_data_json)
            message_type: str = text_data_json.get("type")
            if message_type == "auth":
                token = text_data_json.get("token")
                self.authenticated = await self.authenticate(token)
                if not self.authenticated:
                    await self.close()
                else:
                    print("sending ok message")
                    compressed_data: bytes = compress(
                        json.dumps({"type": "info", "message": "ok"})
                    )
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
        compressed_data: bytes = compress(json.dumps(data))
        await self.send(bytes_data=compressed_data)
        await self.close()

    async def handle_other_messages(self, message):
        # Handle other messages
        compressed_data: bytes = compress(
            json.dumps({"type": "message", "content": message})
        )
        await self.send(bytes_data=compressed_data)


class track_stats(AsyncWebsocketConsumer):
    async def connect(self):
        self.authenticated = False
        self.userId = None
        self.username = None
        await self.accept()

    async def disconnect(self, close_code):
        client_ip = self.scope["client"][0]

        # superclass's disconnect method
        await super().disconnect(close_code)

    async def authenticate(self, token):
        # Implement your token validation logic here
        return token == "your_valid_token"

    async def receive(self, bytes_data=None):
        # note that the authenticate method will only othenticate the user one time and then it will
        # map all requests to the FUNCTION_handle_message_type_callBack to handle message types
        # so it's not a bottle neck if you think so.
        await authenticate(
            self,
            self.FUNCTION_handle_message_type_callBack,
            reference,
            "user",
            bytes_data,
        )

    async def FUNCTION_handle_message_type_callBack(
        self, message_type: str, decompressed_data: str
    ):

        print(
            f"CALLBACK FUNCTION GOT [[[[[[[[{message_type}, decompressed_data]]]]]]]]"
        )
        print("hereeeeee!@#")
        if message_type == "request":
            await self.handle_some_event(decompressed_data)
        elif message_type == "codingActivity":
            await self.handle_some_event(decompressed_data)
        elif message_type == "susActivity":
            await self.handle_updating_code(decompressed_data)
        else:
            # Handle other messages
            await self.handle_other_messages(text_data_json)
    
    async def handle_some_event(self, data):
        # Handle the event and decide to close the connection
        print("trying to send compressed data")
        compressed_data: bytes = compress(data)
        await self.send(bytes_data=compressed_data)

    async def handle_other_messages(self, message):
        # Handle other messages
        compressed_data: bytes = compress(
            json.dumps({"type": "message", "content": message})
        )
        await self.send(bytes_data=compressed_data)

    async def handle_updating_code(self, decompressed_data):
        parsed_data = json.loads(decompressed_data)
        print(parsed_data)
 amines
asda