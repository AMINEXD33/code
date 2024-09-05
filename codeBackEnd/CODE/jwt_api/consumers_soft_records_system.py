import redis
from logs_util.log_core import LogCore
import json, datetime

log = LogCore("consumers_soft_recodrs_system.py", False)
"""Exceptions"""


class KeyPassedIsNotValid(Exception):
    pass


"""
RULES:
    uploaded code:
        1- the threshold for storing code in the database is 100 lines
        2- analitics need to execute upon arrival, the result serve to the client, then the code shall be save(felt like talking in old engl XD)
        3- over all , even if a code didn't reach the size of 100 lines
        once the client sent over 5 updates well write that to the database

"""
class Jobs():
    def __init__(self, redis_connection: redis.Redis):
        self.redis_instance = redis_connection
        self.jobshset = "jobs"
    def add_job(self, username:str, userid:str, session_id:str):
        key = username+userid+session_id
        exists = self.redis_instance.hexists(self.jobshset, key)
        if exists:
            return
        self.redis_instance.hset(self.jobshset, key, json.dumps({"session_id":session_id, "username":username, "userid":userid}))
        print(f" a job with was added with key = {key}")
    def remove_job(self, jobkey:str):
        self.redis_instance.hdel(self.jobshset, jobkey)
        print(f" a job with was removed with key = {jobkey}")
    def get_jobs(self):
        data = self.redis_instance.hgetall(self.jobshset)
        return data

class Notif():
    def __init__(self, redis_connection: redis.Redis):
        self.redis_instance = redis_connection
        self.notohset = "notify"
    def add_noti(self, username:str, userid:str, session_id:str):
        key = username+userid+session_id
        exists = self.redis_instance.hexists(self.notohset, key)
        if exists:
            return
        self.redis_instance.hset(self.notohset, key, json.dumps({"session_id":session_id, "username":username, "userid":userid}))
        print(f" a job with was added with key = {key}")
    def remove_noti(self, notikey:str):
        self.redis_instance.hdel(self.notohset, notikey)
        print(f" a job with was removed with key = {notikey}")
    def get_notis(self):
        data = self.redis_instance.hgetall(self.notohset)
        return data




class SoftRecords:
    def __init__(self, redis_connection: redis.Redis):
        self.redis_instance = redis_connection

    def create_user_soft_recod(self, session_id: str, username: str):
        """
        this function creates the keys for tracking user events,
        it creates the uncreated keys, if the keys already exist,
        not changes would be made.
        Parameters
        ----------
        session_id : str
            the id of the traget session
        user_name : str
            the id of the traget username
        """
        sub_keys = (
            ("code", ""),
            ("activityStartedAt", datetime.datetime.now().isoformat()),
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
            ("ttl", 0),
            ("blocked", "False")
        )
        if not session_id or not username:
            log.log_exception("nigga one is missing")
            return False
        try:
            session_key = "session" + session_id
            master_record_exist = self.redis_instance.exists(session_key)
            if master_record_exist == 0:
                return False
            user_key = username + session_id
            for sub_key in sub_keys:
                # create if not already , don't touch the created ones
                if not self.redis_instance.hexists(user_key, sub_key[0]):
                    self.redis_instance.hset(user_key, sub_key[0], sub_key[1])
        except Exception as e:
            log.log_exception("create_user_soft_recod" + str(e))
            return False
        return True

    def create_master_soft_record(
        self: str,
        session_id: str,
    ):
        """
        this function creates a user soft record,
        only keys that doesn't exist will be initiated

        Parameters
        ----------
        session_id : str
            the id of the traget session
        """
        sub_keys = (
            ("totallines", 0),
            ("totalwords", 0),
            ("blocked_students", 0),
            ("avgCodeCompexity", 0),
            ("totalStudentsdone", 0),
            ("activity", 0),
            ("ttl", 10),
            ("users", json.dumps([]))           
        )

        master_record = self.redis_instance.exists("session" + session_id)
        if master_record != 0:
            return True
        try:
            for sub_key in sub_keys:
                self.redis_instance.hset("session" + session_id, sub_key[0], sub_key[1])
            self.redis_instance.hset("session" + session_id, "session_id", session_id)
        except Exception as e:
            log.log_exception("create_master_soft_record > "+str(e))
            return False
        return True

    """
        FUNCTION TO DELETE A SOFT RECORD USER/MASTER
    """

    def delete_some_master_soft_record(self, session_id: str):
        """
        this function deletes a master soft record
        """
        self.redis_instance.delete("session" + str(session_id))

    def delete_some_user_soft_record(self, session_id: str, username: str):
        """
        this function deletes a user soft record
        """
        self.redis_instance.delete(str(username) + str(session_id))

    """
        UPDATE FUNCTION FOR MASTER SOFT RECORD
    """

    def master_update_field(
        self, session_id: str, update_tuple: tuple = ("none", None)
    ):
        """
        a function that can update some specific label in the master record
        only if the field specified is a valid feild, otherwise nothing will
        change
        Parameters
        ----------
        session_id : str
            the target session id
        update_tuple : tuple
            a tuple that represents the label and the update the data
        """
        sub_keys = (
            ("totallines", int),
            ("totalwords", int),
            ("blocked_students", int),
            ("avgCodeCompexity", int),
            ("totalStudentsdone", int),
            ("activity", int),
            ("ttl", int),
            ("users", list)   
        )
        key = "session" + str(session_id)
        for sub_key in sub_keys:
            if sub_key[0] == update_tuple[0]:
                if isinstance(update_tuple[1], sub_key[1]):
                    if isinstance(update_tuple[1], list) or isinstance(update_tuple[1], tuple):
                        self.redis_instance.hset(
                            key, sub_key[0], json.dumps(update_tuple[1])
                        )
                        break
                    self.redis_instance.hset(key, sub_key[0], update_tuple[1])
                    break
                else:
                    log.log_exception(
                        f"passed a wrong data type to the [key{sub_key[0]}]"
                    )
                    break

    """
        GET FUNCTION FOR MASTER SOFT RECORD
    """

    def get_master_field(self, session_id: str, field_name: str):
        """
        a function that get's the value of some label in the master record
        Parameters
        ----------
        session_id : str
            the target session id
        field_name : str
            the valid target field
        """
        sub_keys = (
            "totallines",
            "totalwords",
            "blocked_students",
            "avgCodeCompexity",
            "totalStudentsdone",
            "activity",
            "ttl",
            "users"
        )
        key = "session" + str(session_id)
        for sub_key in sub_keys:
            if sub_key == field_name:
                return self.redis_instance.hget(key, sub_key)

    """
        UPDATE FUNCTION FOR USER SOFT RECORD
    """

    def user_update_field(
        self, session_id: str, username: str, update_tuple: tuple = ("none", None)
    ):
        """
        a function that updates a key in the user record , only of the types matche
        to prevent unwanted data types that can cause errors
        Parameters
        ----------
        session_id: str
            the target session id
        username: str
            the target username
        update_tuple: tuple
            a tuple that represents the label and the update the data
        """
        sub_keys = (
            ("errors", tuple),
            ("submitions", tuple),
            ("compilations", int),
            ("line_code", int),
            ("sum_line_code", tuple),
            ("words", int),
            ("sum_words", tuple),
            ("sus", tuple),
            ("code", str),
            ("activityStartedAt", str),
            ("activityEndedAt", str),
            ("modification", int),
            ("lines_delta", int),
            ("words_delta", int),
            ("code_complexity", int),
            ("ttl", int),
            ("blocked", bool)
        )
        key = str(username) + str(session_id)
        for sub_key in sub_keys:
            if sub_key[0] == update_tuple[0]:
                if isinstance(update_tuple[1], sub_key[1]):
                    if isinstance(update_tuple[1], tuple):
                        self.redis_instance.hset(
                            key, sub_key[0], json.dumps(update_tuple[1])
                        )
                        break
                    self.redis_instance.hset(key, sub_key[0], update_tuple[1])
                    break
                else:
                    log.log_exception(
                        f"passed a wrong data type to the [key{sub_key[0]}]"
                    )
                    break

    """ 
        GET FUNCTION FOR USER SOFT RECORD
    """

    def get_user_field(self, session_id: str, username: str, field_name: str):
        """
        a function that get's the value of some label in the master record
        Parameters
        ----------
        session_id : str
            the target session id
        username: str
            the target username
        field_name : str
            the valid target field
        """
        sub_keys = (
            "errors",
            "submitions",
            "compilations",
            "line_code",
            "sum_line_code",
            "words",
            "sum_words",
            "sus",
            "code",
            "activityStartedAt",
            "activityEndedAt",
            "modification",
            "lines_delta",
            "words_delta",
            "code_complexity",
            "ttl",
            "blocked"
        )
        key = str(username) + str(session_id)
        for sub_key in sub_keys:
            if sub_key == field_name:
                return self.redis_instance.hget(key, sub_key)


    def decrement_ttl_user(self, session_id, username):
        curr_ttl = int(self.get_user_field(session_id=session_id, username=username))
        curr_ttl-=1
        self.user_update_field(session_id=session_id, username=username, update_tuple=("ttl", curr_ttl))
    
    def get_ttl_user(self, session_id, username):
        ttl = int(self.get_user_field(session_id=session_id, username=username))
        return ttl
    
    def decrement_ttl_master(self, session_id):
        curr_ttl = int(self.get_master_field(session_id=session_id, field_name="ttl"))
        curr_ttl-=1
        self.master_update_field(session_id=session_id, update_tuple=("ttl", curr_ttl))
    
    def get_ttl_master(self, session_id):
        ttl = int(self.get_master_field(session_id=session_id, field_name="ttl"))
        return ttl

    def reset_ttl_master(self, session_id):
        self.master_update_field(session_id=session_id, update_tuple=("ttl", 10))
    
    def reset_ttl_user(self, session_id, username):
        self.user_update_field(session_id=session_id, username=username, update_tuple=("ttl", 10))
    
    

