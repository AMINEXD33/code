import gzip
from jwt_multi_workers.redis_server_conf import custom_redis
import redis, json
from logs_util.log_core import LogCore
import datetime
from datetime import timedelta
from django.utils import timezone
from jwt_api.models import Session_user_tracking_record, Users, Session, sessionMetricsHardRecord
from jwt_api.consumers_soft_records_system import SoftRecords
from jwt_api.consumers_statistics import calculate_stats

log = LogCore("consumers.py", False)


def compress(data: str) -> bytes:
    print("commpress this >", data)
    try:
        commpressed_data = gzip.compress(data.encode("utf-8"))
    except Exception as e:
        print(e)
        log.log_exception(f"the error accured here, and data is of type {type(data)}"+str(e))
    return commpressed_data


def decompress(data: bytes) -> str:
    return gzip.decompress(data).decode("utf-8")


async def authenticate(
    self_reference,
    FUNCTION_handle_message_type_callBack,
    reference,
    userAuthorization,
    bytes_data: bytes = None,
    ):
    """
    this function takes a self_reference to a consumer class to execute some inner function is the "AsyncWebsocketConsumer" class , second it takes a function callback that will be responsible for
    mapping action to propper executing methods, and finally the bytes_data comming from the client
    Note: the data sent from the client is compressed

    Parameters
    ----------
    self_reference : obj
        a reference to the self variable in a class of type AsyncWebsocketConsumer
    FUNCTION_handle_message_type_callBack : function
        a callBack function to some mapper that can interprete the message_type comming from the client
    reference : JWT_IMP
        a reference to the jwt implementation to authenicate the user
    bytes_data : bytes
        the data comming from the client
    """
    if not bytes_data:
        return False
    try:
        decompressed_data: str = decompress(bytes_data)
        text_data_json:dict = json.loads(json.loads(decompressed_data))
        decompressed_data = text_data_json.get("data")
        message_type: str = text_data_json.get("type")
        if message_type == "auth":
            token = text_data_json.get("token")
            potential_token = reference.TokenManager.abstract_token_validation(token)
            if potential_token:
                if potential_token["role"] != userAuthorization:
                    await self_reference.close()
                    print("unauthorized !")
                    return  # not authorized
                print(potential_token)
                self_reference.userId = potential_token["id"]
                self_reference.username = potential_token["username"]
                self_reference.authenticated = True

            if not self_reference.authenticated:
                compressed_data: bytes = compress(
                    json.dumps({"type": "unauthorized", "message": "fuck you"})
                )
                await self_reference.send(bytes_data=compressed_data)
                await self_reference.close()
            else:
                print("sending ok message")
                self_reference.user = self_reference.scope['user']
                self_reference.user_group_name = f"user_{self_reference.userId}"

                # Add the WebSocket connection to the user's group
                await self_reference.channel_layer.group_add(
                    self_reference.user_group_name,
                    self_reference.channel_name
                )
                compressed_data: bytes = compress(
                    json.dumps({"type": "info", "message": "ok"})
                )
                await self_reference.send(bytes_data=compressed_data)
        # only authenticated connections are allowed to send
        # message types
        else:
            print("not an auth checking if authenticated to handle a request")
            if self_reference.authenticated == True:
                print("not an auth reauest and you're already authenticated")
                await FUNCTION_handle_message_type_callBack(
                    message_type, decompressed_data
                )
            else:
                print("not authenticated :(")
                print(self_reference.authenticated)
                self_reference.close()

    except Exception as e:
        log.log_exception(str(e))
        self_reference.close()


def check_expiration_date(date: datetime.datetime):
    date_obj = date
    currtime = timezone.make_aware(datetime.datetime.now())

    # the session is still going
    if currtime < date_obj:
        return True
    # the session is finished
    return False


def load_from_hard_records(session_id:str, username:str, user_id:str, sfr: SoftRecords, session:Session):
    def create_soft_records(session_id, username):
        sfr.create_master_soft_record(session_id=session_id)
        sfr.create_user_soft_recod(session_id=session_id, username=username)
    try:
        compute = True
        # get the target user
        user =  Users.objects.filter(user_id= user_id).first()

        # get the target hard record
        hard_record = Session_user_tracking_record.objects.filter(
            Session_user_tracking_record_session_Ref = session,
            Session_user_tracking_record_user_Ref = user).first()
        # no hard records just start the soft records
        if not hard_record:
            create_soft_records(session_id=session_id, username=username)
            log.log_exception("def load_from_hard_records, can't get hard record , creating empty soft records")
            return
        # if hard records, then load the last saved data
        vals = (
            ("code",hard_record.Session_user_tracking_record_lines_of_code),
            # time frame
            ("activityStartedAt", hard_record.Session_user_tracking_record_activity_starts_at),
            ("activityEndedAt", hard_record.Session_user_tracking_record_activity_ends_at),
            #code quality
            ("compilations", hard_record.Session_user_tracking_record_compilations),
            ("errors", hard_record.Session_user_tracking_record_errors),
            ("submitions", hard_record.Session_user_tracking_record_submitions),
            ("sus", hard_record.Session_user_tracking_record_suspicious),
            ("code_complexity", hard_record.Session_user_tracking_record_code_complexity),
            # code data
            ("line_code", hard_record.Session_user_tracking_record_lines_of_code),
            ("words", hard_record.Session_user_tracking_record_words),
            # summarized data
            ("sum_line_code", hard_record.Session_user_tracking_record_summarized_lines_of_code),
            ("sum_words", hard_record.Session_user_tracking_record_summarized_word),
        )
        # we will use this pre-def tuple to express what type of data we're expecting and
        sub_keys = (
            ("code", ""),
            ("activityStartedAt", ""),
            ("activityEndedAt", ""),
            ("sessionid", session_id),
            ("errors", json.dumps([])),
            ("submitions", json.dumps([])),
            ("compilations", 0),
            ("line_code", 0),
            ("sum_line_code", json.dumps([0])),
            ("words", 0),
            ("sum_words", json.dumps([0])),
            ("sus", json.dumps([])),
            ("modification", 0),
            ("lines_delta", 0),
            ("words_delta", 0),
            ("code_complexity", 0),
            ("ttl", 0)
            )
        # load data into redis
        for field, data in vals:
            for pre_field, pre_def_value in sub_keys:
                if field != pre_field:
                    break
                # if the data stored in the db is not the expected type , we're just going to load the default value
                if type(data) != type(pre_def_value):
                    sfr.user_update_field(session_id=session_id, username=username, update_tuple=(pre_field, pre_def_value))
                    log.log_exception(f"def load_from_hard_records, a type didn't match what is expected, expected{type(data)} but got {type(pre_def_value)}")
                    break
                # we can load the data from the db, the types are a match
                sfr.user_update_field(session_id=session_id, username=username, update_tuple=(field, data))
    except Exception as e:
        log.log_exception(f"def load_from_hard_records unexpected error > {str(e)}")


def save_master_soft_record(session_id:str, session:Session, sfr:SoftRecords):
    """
    
    """
    data = calculate_stats(session_id=session_id, sfr=sfr)
    hardRec = sessionMetricsHardRecord.objects.filter(sessionMetric_SessionRef=session).first()
    if not hardRec or not data:
        log.log_exception("not suppose to not find a 'sessionMetricsHardRecord' at save_master_soft_record()")
        return False
    hardRec.sessionMetric_avgCodeComplexity = data["avg_complexity"]
    hardRec.sessionMetric_avgerrors = data["avg_errors"]
    hardRec.sessionMetric_avglines = data["avg_lines"]
    hardRec.sessionMetric_avgwordswriten = data["avg_words"]

