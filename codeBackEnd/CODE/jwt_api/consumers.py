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
from .consumers_statistics import *
import threading
from logs_util.log_core import LogCore
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .consumers_soft_records_system import Jobs, Notif
log = LogCore("consumers.py", False)

# reference to the jwt_module to handle authentication
reference = apps.get_app_config("jwt_api").my_object

class track_stats(AsyncWebsocketConsumer):
    """
    a consumer class that is meant for tracking users stats
    """
    async def connect(self):
        self.authenticated = False
        self.userId = None
        self.username = None
        self.already_checked_session_validity = False
        self.expiration_date = None
        self.last_user_update = datetime.datetime.now()
        self.user = None
        self.jb = Jobs(reference.Redis)
        self.job_key = None
        await self.accept()

    async def disconnect(self, close_code):
        """
        this function disconnect the current websocket(NOT USED)
        """
        # superclass's disconnect method
        if self.job_key:
            self.jb.remove_job(self.job_key)
            # await self.channel_layer.group_discard(
            #     self.job_key,
            #     self.channel_name
            # )
        await super().disconnect(close_code)

    async def receive(self, bytes_data=None):
        """
        this function is the first receiver of the bytes_data
        
        Parameters
        ----------
        bytes_data : bytes
            the data received from the client
        """
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
        """
        this function maps some message type to it's propper handler
        
        Parameters
        ----------
        message_type : str
            the message type
        decompressed_data : str
            the decompressed data from the client
        """
        
        if message_type == "request":
            await self.handle_some_event(decompressed_data)
        elif message_type == "codingActivity":
            await self.handle_updating_code(decompressed_data)
        elif message_type == "susActivity":
            pass
        else:
            # Handle other messages
            await self.handle_no_such_message_type()

    async def handle_some_event(self, data):
        # Handle the event and decide to close the connection
        print("trying to send compressed data")
        # 
        await self.send(bytes_data=compressed_data)

    async def handle_no_such_message_type(self):
        """
        this functions sends an error message in case the user passes
        some unknown message type 
        """
        # Handle other messages
        compressed_data: bytes = compress(
            json.dumps({"type": "error", "content": "not a valid message type"})
        )
        await self.send(bytes_data=compressed_data)

    def thread_update(
        self,
        session_id: str,
        sfr: SoftRecords,
        username: str,
        data_to_update: tuple = ("none", None),
        ):
        """
        This is a thread function, meaning it runs on a separate thread.
        It checks the validity of the expiration dates of the session.
        Note: One thing that should be covered is a simple optimization.
        to prevent performance bottle-necks Since we're using Redis, we want all data
        to be handled in memory, but checking the session instance needs at least one DB hit.
        So that's what we did, each websocket connection will check the session expiration date
        from the database one time, and then we'll store a reference in the consumer instance for future
        references and checks, because each request needs to check the expiration date before doing anything.

        Parameters
        ----------
        session_id : str
            the id of the target sesssion
        sfr : SoftRecords
            an instance of a class ("consumers_soft_records_system")
        username : str
            the username of the client sending the updates 
        data_to_update : tuple
            a tupple that describes the kind of update that needs to be mapped , and the data
            fro each kind of update, each have it's own handler
        """
        try:
            # we don't want to keep querying the session to check validity every time, that would
            # defeat the whole using redis thing, so we're doing it one time, then we can just store
            # the expiration date for future references
            session = Session.objects.filter(session_id=session_id).first()
            if not self.already_checked_session_validity:
                if not check_expiration_date(session.session_end_time):
                    # close connection and delete the records in redis if they exists
                    sfr.delete_some_master_soft_record(session_id=session_id)
                    sfr.delete_some_user_soft_record(username=username, session_id=session_id)
                    async_to_sync(self.send)(
                        bytes_data=compress(json.dumps(
                            {"type": "expired", "content": "session is exprired"}
                        ))
                    )
                    async_to_sync(self.close)()
                    return False
                # keep the expiration date
                self.expiration_date = session.session_end_time
                session_metrics = sessionMetricsHardRecord.objects.filter(
                    sessionMetric_SessionRef=session
                ).first()
                # if no session or it's metrics are found in the db
                if not session or not session_metrics:
                    # no session or metrics records, not suppose to happen tho
                    sfr.delete_some_master_soft_record(session_id=session_id)
                    sfr.delete_some_user_soft_record(username=username, session_id=session_id)
                    async_to_sync(self.send)(
                        bytes_data=compress(json.dumps(
                            {"type": "error", "content": "can't find session and it's metrics"}
                        ))
                    )
                    async_to_sync(self.close)()
                    log.log_exception(
                        "not suppose to not find session or session_metrics in db"
                    )
                    return False
                # load from hard record and create soft records
                load_from_hard_records(
                    session_id=session_id, 
                    username=self.username, 
                    user_id=self.userId, 
                    sfr=sfr,
                    session=session
                    )
                self.already_checked_session_validity = (
                    True  # set the flag to not check db again
                )
                
            else:
                if not check_expiration_date(self.expiration_date):
                    # close connection if the session is expired , nothing to do here
                    sfr.delete_some_master_soft_record(session_id=session_id)
                    sfr.delete_some_user_soft_record(username=username, session_id=session_id)
                    async_to_sync(self.send)(
                        bytes_data=compress(json.dumps(
                            {"type": "expired", "content": "session is exprired"}
                        ))
                    )
                    async_to_sync(self.close)()
                    return False

            """ PHASE II : keep users sending data memoriezed """
            master_user_list = sfr.get_master_field(session_id=session_id, field_name="users")
            master_user_list = json.loads(master_user_list)
            found = False
            for user_id, _ in master_user_list:
                if int(user_id) == int(self.userId):
                    found = True
            if not found:
                master_user_list.append((self.userId, self.username))
                sfr.master_update_field(
                    session_id=session_id,
                    update_tuple=("users", master_user_list)
                )
            ## make a job to supply this user with periodic updates
            self.jb.add_job(username=self.username, session_id=str(session.session_id),userid=str(self.userId))
            self.job_key = self.username+str(self.userId)+str(session.session_id)
            # async_to_sync(self.channel_layer.group_add)(self.job_key, self.channel_name)
            """UPDATES MAP"""
            if data_to_update[0] == "update_code_metrics":
                code = (data_to_update[1])["code"]
                session_id = (data_to_update[1])["sessionid"]
                code_statistics_routine(code=code, sfr=sfr, username=self.username, session_id=str(session_id))
            elif data_to_update[0] == "":
                pass
            elif data_to_update[0] == "":
                pass
            elif data_to_update[0] == "":
                pass
            elif data_to_update[0] == "":
                pass
            elif data_to_update[0] == "":
                pass
        except Exception as e:
            log.log_exception("thread_update > "+str(e))
    async def respond_with_error_and_close(self, type_:str="", content:str=""):
        """
        a function that throws some kind of message type and close the connection
        """
        try:
            await self.send(
                bytes_data=compress(
                    json.dumps({"type": type_, "content": content})
                )
            )
            await self.close()
        except Exception as e:
            log.log_exception("respond_with_error_and_close"+str(e))

    async def handle_updating_code(self, decompressed_data):
        """
        this function is the driver for updating stats about code
        Parameters
        ----------
        decompressed_data : dict
            the decompressed data from the user 
        """
        try:
            sfr = SoftRecords(reference.Redis)
            code:bool= False
            sessionid:bool = False
            try:
                decompressed_data["code"]
                code = True
                decompressed_data["sessionid"]
                sessionid = True
            except:
                pass
            if not code or not sessionid:
                await self.respond_with_error_and_close("error", "code and session id can't be null")
                return
            if not str(decompressed_data["sessionid"]).isnumeric():
                await self.respond_with_error_and_close("error", "no session id was passed")
                return
            data_to_update = ("update_code_metrics", decompressed_data)
            update_thread = threading.Thread(
                target=self.thread_update,
                args=(
                    str(decompressed_data["sessionid"]),
                    sfr,
                    self.username,
                    data_to_update,
                ),
            )
            update_thread.start()
            update_thread.join()
        except Exception as e:
            log.log_exception("handle_updating_code > "+str(e))

    async def chat_message(self, event):
        # This method is called when a 'chat_message' type event is sent to the group
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

class get_updates(AsyncWebsocketConsumer):
    """
    a consumer class that is meant for tracking users stats
    """
    async def connect(self):
        self.authenticated = False
        self.userId = None
        self.username = None
        self.already_checked_session_validity = False
        self.expiration_date = None
        self.last_user_update = datetime.datetime.now()
        self.user = None
        self.nf = Notif(reference.Redis)
        self.nf_key = None
        self.session_id = None
        await self.accept()

    async def disconnect(self, close_code):
        """
        this function disconnect the current websocket(NOT USED)
        """
        # superclass's disconnect method
        if self.nf_key:
            self.nf.remove_noti(self.nf_key)
        
            await self.channel_layer.group_discard(
                self.nf_key,
                self.channel_name
            )
        await super().disconnect(close_code)

    async def receive(self, bytes_data=None):
        """
        this function is the first receiver of the bytes_data
        
        Parameters
        ----------
        bytes_data : bytes
            the data received from the client
        """
        # note that the authenticate method will only othenticate the user one time and then it will
        # map all requests to the FUNCTION_handle_message_type_callBack to handle message types
        # so it's not a bottle neck if you think so.
        await authenticate(
            self,
            self.FUNCTION_handle_message_type_callBack,
            reference,
            "admin",
            bytes_data,
        )

    async def FUNCTION_handle_message_type_callBack(
        self, message_type: str, decompressed_data: str
        ):
        if message_type == "notifme":
            if decompressed_data["sessionId"] == None:
                self.close()
            self.session_id = decompressed_data["sessionId"]
            self.nf_key = self.username+str(self.userId)+str(self.session_id)
            self.nf.add_noti(userid=str(self.userId), session_id=str(self.session_id), username=self.username)
            await self.channel_layer.group_add(self.nf_key, self.channel_name)
        

    async def handle_some_event(self, data):
        # Handle the event and decide to close the connection
        print("trying to send compressed data")
        # 
        await self.send(bytes_data=compressed_data)

    async def respond_with_error_and_close(self, type_:str="", content:str=""):
        """
        a function that throws some kind of message type and close the connection
        """
        try:
            await self.send(
                bytes_data=compress(
                    json.dumps({"type": type_, "content": content})
                )
            )
            await self.close()
        except Exception as e:
            log.log_exception("respond_with_error_and_close"+str(e))

    async def supply_update(self, event):
        # This method is called when a 'chat_message' type event is sent to the group
        message = event['message']

        # Send message to WebSocket
        await self.send(bytes_data=compress(json.dumps({
            'message': message
        })))