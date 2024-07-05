from django.db import models
from django.db import transaction
import bcrypt, uuid
from hashlib import sha384
import random, os
import datetime
from datetime import timedelta
from django.utils import timezone
from jwt_api.utils.refresh_tokens import Refresh_tokens_manager

class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=50, null=False)
    def __repr__(self):
        return(
            f"""
                            ROLE
            -----------------------------------------
            role_id = {self.role_id}
            role_name = {self.role_name}
            -----------------------------------------
            """
        )

class Users(models.Model):
    user_id = models.CharField(max_length=36, primary_key=True)
    user_username = models.CharField(max_length=100, null=False, unique=True)
    user_email = models.CharField(max_length=200, null=False, unique=True)
    user_password = models.CharField(max_length=72, null=False)
    user_firstName = models.CharField(max_length=100, null=False)
    user_lastName = models.CharField(max_length=100,null=False) 
    date_ofBirth = models.DateField(null=False)
    phone_number = models.CharField(max_length=100, null= False)
    role_ref = models.ForeignKey(Role, on_delete=models.CASCADE)
    record_date = models.DateTimeField(auto_now=True)
    img_src = models.CharField(max_length=200)
    def __repr__(self):
        return (
            f"""
                            USERS
            -----------------------------------------
            user_id = {self.user_id}
            user_username = {self.user_username}
            user_email = {self.user_email}
            user_password = {self.user_password}
            user_firstName = {self.user_firstName}
            user_lastName = {self.user_lastName}
            date_ofBirth = {self.date_ofBirth}
            phone_number = {self.phone_number}
            role_ref = {self.role_ref}
            record_date = {self.record_date}
            img_src = {self.img_src}
            -----------------------------------------
            """
        )
    
    def create(
        user_username:str,
        user_email:str,
        user_password:str,
        user_firstName:str,
        user_lastName:str,
        date_ofBirth:str,
        phone_number:str,
        role_ref:Role,
        img_src:str
    ):
        #hash password
        password_bytes = user_password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        print(hashed_password)
        # genereate a random uuid4 id
        uuid_random = uuid.uuid4()

        Users(
            user_id=uuid_random,
            user_username=user_username,
            user_email=user_email,
            user_password=hashed_password,
            user_firstName = user_firstName,
            user_lastName = user_lastName,
            date_ofBirth = date_ofBirth,
            phone_number = phone_number,
            role_ref = role_ref,
            img_src = img_src
        ).save()

class Session(models.Model):
    session_id = models.BigAutoField(primary_key=True)
    session_status = models.BooleanField(default=True)
    session_start_time = models.DateTimeField(auto_now=True)
    session_end_time = models.DateTimeField(null=True)
    session_allowed_to_run_code = models.BooleanField(default=True)
    session_starter = models.ForeignKey(Users, on_delete=models.CASCADE)
    def __repr__(self):
        return (
            f"""
                            SESSION
            -----------------------------------------
            session_id = {self.session_id}
            session_status = {self.session_status}
            session_start_time = {self.session_start_time}
            session_end_time = {self.session_end_time}
            session_allowed_to_run_code = {self.session_allowed_to_run_code}
            session_starter = {self.session_starter}
            -----------------------------------------
            """
        )

    def create(self, userInstance:Users):
        """
        creating a session should create:
        + a new Session_correction_pool record
        + a new Session_user_pool record
        + a new Session_user_pool record
        + a new Users_stats record
        """
        # let's check if the user is admin
        if not Users:
            print("no user passed")
            return None
        # create the objects
        try:
            session_starter = userInstance
            session = Session(session_starter=session_starter)
            session_correction_pool = Session_correction_pool(
                user_id_ref=session_starter,
                session_id_ref=session)
            session_user_pool = Session_user_pool(
                user_id_ref=session_starter,
                session_id_ref=session
            ) 
            users_stats = Users_stats(
                session_user_pool_ref=session_user_pool,
                user_id_ref=session_starter
            )
        except Exception as e:
            print("error while running creating session models +++++>", e)
            return None
        # save using a transaction
        try:
            with transaction.atomic():
                session.save()
                session_correction_pool.save()
                session_user_pool.save()
                users_stats.save()
        except Exception as e:
            print("error while executing transaction", e)
            return None
            
class Session_correction_pool(models.Model):
    session_correction_pool_id = models.BigAutoField(primary_key=True)
    correction = models.TextField(null=True)
    grade = models.IntegerField(default=0)
    note = models.TextField(null=True)
    user_id_ref = models.ForeignKey(Users, on_delete=models.CASCADE)
    session_id_ref = models.ForeignKey(Session, on_delete=models.CASCADE)
    def __repr__(self):
        return (
            f"""
                            SESSION_COR.._POOL
            -------------------------------------------------------
            session_correction_pool_id = {self.session_correction_pool_id}
            correction = {self.correction}
            grade = {self.grade}
            note = {self.note}
            user_id_ref = {self.user_id_ref}
            session_id_ref = {self.session_id_ref}
            -------------------------------------------------------
            """
        )

class Session_user_pool(models.Model):
    session_user_pool_id = models.BigAutoField(primary_key=True)
    user_id_ref = models.ForeignKey(Users, on_delete=models.CASCADE)
    session_id_ref = models.ForeignKey(Session, on_delete=models.CASCADE)
    flaged = models.BooleanField(default=False)
    code_content = models.TextField(null= True)
    def __repr__(self):
        return (
            f"""
                            SESSSION_USER_POOL
            -------------------------------------------------------
            session_user_pool_id = {self.session_user_pool_id}
            user_id_ref = {self.user_id_ref}
            session_id_ref = {self.session_id_ref}
            flaged = {self.flaged}
            code_content = {self.code_content}
            -------------------------------------------------------
            """
        )

class Users_stats(models.Model):
    users_stats_id = models.BigAutoField(primary_key=True)
    session_user_pool_ref = models.ForeignKey(Session_user_pool, on_delete=models.CASCADE)
    user_id_ref = models.ForeignKey(Users, on_delete=models.CASCADE)
    words_per_minute = models.IntegerField(default=0)
    lines_of_code = models.IntegerField(default=0)
    syntax_errors_number = models.IntegerField(default=0)
    code_complexity = models.IntegerField(default=999)
    def __repr__(self):
        return (
            f"""
                              USERS_STATS
            ----------------------------------------------------
            users_stats_id = {self.users_stats_id}
            session_user_pool_ref = {self.session_user_pool_ref}
            user_id_ref = {self.user_id_ref}
            words_per_minute = {self.words_per_minute}
            lines_of_code = {self.lines_of_code}
            syntax_errors_number = {self.syntax_errors_number}
            code_complexity = {self.code_complexity}
            ---------------------------------------------------
            """
        )

class Users_devices(models.Model):
    id_users_device = models.BigAutoField(primary_key=True)
    device = models.TextField(null= False)
    device_ip_address = models.CharField(null=False, max_length=120, unique=True)
    user_ref = models.ForeignKey(Users, on_delete=models.CASCADE)
    is_pc = models.BooleanField(default=False)
    is_phone = models.BooleanField(default=False)
    def __repr__(self):
        f"""
                    USERS DEVICES
        --------------------------------------------
        id_users_device = {self.id_Users_device}
        device = {self.device}
        device_ip_address = {self.device_ip_address}
        user_ref = {self.user_ref}
        """

class Refresh_tokens(models.Model):
    id_refresh_token = models.BigAutoField(primary_key=True)
    user_id_ref = models.ForeignKey(Users, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=150, null= False)
    expires_at = models.DateTimeField(null=False)

    def __repr__(self):
        f"""
                    REFRESH_TOKENS
        -----------------------------------------
        id_refresh_token = {self.id_refresh_token}
        refresh_token = {self.refresh_from_db}
        expires_at = {self.expires_at}
        """
    def create2(user_ref_id:str, token:str, exp_date:str):
        try:
            # see if there was an other old token
            obj = Refresh_tokens(
            refresh_token=token,
            user_id_ref= user_ref_id,
            expires_at= exp_date
            ).save()
            return obj
        except Exception as e:
            print("error creating refresh token  ", e)
        return False
