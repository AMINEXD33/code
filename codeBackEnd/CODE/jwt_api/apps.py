from django.apps import AppConfig
import threading
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from redis import Redis

def periodic_stats_updates(jb, nt, sfr):
    from .consumers_statistics import calculate_stats
    def send_to_group(group_key, message):
        
        async_to_sync(channel_layer.group_send)(
            group_key,
            {
            'type': 'supply_update',  # Calls the chat_message method in the consumer
            'message': message,
            }
    )
    while True:
        time.sleep(10)
        channel_layer = get_channel_layer()
        all_jobs = jb.get_jobs()
        all_notify_targets = nt.get_notis()
        
        # print("FROM UPDATE THREAD >>", end="")
        # print(f"type of {type(all_jobs)}   > {all_jobs}")
        # print(f"type of {type(all_notify_targets)}   > {all_notify_targets}")
        for group_key in all_notify_targets:
            print("sending to the group ", group_key)
            session_id = json.loads(all_notify_targets[group_key])["session_id"]
            data = calculate_stats(session_id=session_id, sfr=sfr)
            send_to_group(group_key=group_key, message=json.dumps(data))


class JwtApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jwt_api"
    my_object = None

    def ready(self):
        print("initialized")
        from jwt_multi_workers.jwt_impl import JWT_IMP

        self.my_object = JWT_IMP()
        """A very importent step to synch keys befor doing anything with them"""
        self.my_object.sync_keys()

        from .consumers_soft_records_system import Jobs, Notif, SoftRecords
        self.jb = Jobs(self.my_object.Redis)
        self.nt = Notif(self.my_object.Redis)
        self.sfr = SoftRecords(self.my_object.Redis)
        th = threading.Thread(target=periodic_stats_updates, args=(self.jb,self.nt ,self.sfr, ))
        th.start()