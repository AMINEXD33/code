from django.db import models
from django.db import transaction
import bcrypt, uuid
from hashlib import sha384
import random, os
import datetime
from datetime import timedelta
from django.utils import timezone
from jwt_api.utils.refresh_tokens import Refresh_tokens_manager
from logs_util.log_core import LogCore

log = LogCore("models.py", False)


class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=50, null=False)

    def __repr__(self):
        return f"""
                            ROLE
            -----------------------------------------
            role_id = {self.role_id}
            role_name = {self.role_name}
            -----------------------------------------
            """


class Languages(models.Model):
    languages_id = models.BigAutoField(primary_key=True)
    languages_name = models.CharField(max_length=100, null=False)

    def __repr__(self):
        return f"""
                            languages
            -----------------------------------------
            language_id = {self.language_id}
            language_name = {self.language_name}
            -----------------------------------------
            """


class Users(models.Model):
    user_id = models.CharField(max_length=36, primary_key=True)
    user_username = models.CharField(max_length=100, null=False, unique=True)
    user_email = models.CharField(max_length=200, null=False, unique=True)
    user_password = models.CharField(max_length=72, null=False)
    user_firstName = models.CharField(max_length=100, null=False)
    user_lastName = models.CharField(max_length=100, null=False)
    date_ofBirth = models.DateField(null=False)
    phone_number = models.CharField(max_length=100, null=False)
    role_ref = models.ForeignKey(Role, on_delete=models.CASCADE)
    record_date = models.DateTimeField(auto_now=True)
    img_src = models.CharField(max_length=200)

    def __repr__(self):
        return f"""
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

    def create(
        user_username: str,
        user_email: str,
        user_password: str,
        user_firstName: str,
        user_lastName: str,
        date_ofBirth: str,
        phone_number: str,
        role_ref: Role,
        img_src: str,
    ):
        # hash password
        password_bytes = user_password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
        # genereate a random uuid4 id
        uuid_random = uuid.uuid4()

        Users(
            user_id=uuid_random,
            user_username=user_username,
            user_email=user_email,
            user_password=hashed_password,
            user_firstName=user_firstName,
            user_lastName=user_lastName,
            date_ofBirth=date_ofBirth,
            phone_number=phone_number,
            role_ref=role_ref,
            img_src=img_src,
        ).save()


class Session_users_groupe(models.Model):
    session_users_groupe = models.BigAutoField(primary_key=True)
    session_users_groupe_name = models.CharField(max_length=200, unique=True)
    session_users_groupe_creation_date = models.DateTimeField(auto_now=True)
    session_users_groupe_creator = models.ForeignKey(Users, on_delete=models.CASCADE)

    def __repr__(self):
        return f"""
                                USERS_STATS
            ----------------------------------------------------
            session_users_groupe = {self.session_users_groupe}
            session_users_groupe_name = {self.session_users_groupe_name}
            session_users_groupe_creation_date = {self.session_users_groupe_creation_date}
            session_users_groupe_creator = {self.session_users_groupe_creator}
            ---------------------------------------------------
            """


class Session(models.Model):
    session_id = models.BigAutoField(primary_key=True)
    session_status = models.BooleanField(default=True)
    session_title = models.CharField(max_length=200, null=False, unique=True)
    session_topics = models.TextField(null=True)
    session_task = models.TextField(null=True)
    session_start_time = models.DateTimeField(auto_now=True)
    session_end_time = models.DateTimeField(null=True)
    session_allowed_to_run_code = models.BooleanField(default=True)
    session_starter = models.ForeignKey(Users, on_delete=models.CASCADE)
    session_target_group = models.ForeignKey(
        Session_users_groupe, null=False, on_delete=models.CASCADE
    )
    session_language_ref = models.ForeignKey(Languages, on_delete=models.CASCADE)

    def __repr__(self):
        return f"""
                            SESSION
            -----------------------------------------
            session_id = {self.session_id}
            session_status = {self.session_status}
            session_start_time = {self.session_start_time}
            session_end_time = {self.session_end_time}
            session_allowed_to_run_code = {self.session_allowed_to_run_code}
            session_starter = {self.session_starter}
            session_language_ref = {self.session_language_ref}
            -----------------------------------------
            """

class Session_user_tracking_record(models.Model):
    Session_user_tracking_record_id = models.BigAutoField(primary_key=True)
    Session_user_tracking_record_session_Ref = models.ForeignKey(
        Session, on_delete=models.CASCADE
    )
    Session_user_tracking_record_user_Ref = models.ForeignKey(
        Users, on_delete=models.CASCADE
    )
    Session_user_tracking_record_code = models.TextField(default="")
    Session_user_tracking_record_activity_starts_at = models.DateField(null=True)
    Session_user_tracking_record_activity_ends_at = models.DateField(null=True)
    Session_user_tracking_record_errors = models.TextField(default="")
    Session_user_tracking_record_submitions = models.TextField(default="")
    Session_user_tracking_record_compilations = models.IntegerField(default=0)
    Session_user_tracking_record_lines_of_code = models.IntegerField(default=0)
    Session_user_tracking_record_words = models.IntegerField(default=0)
    Session_user_tracking_record_summarized_lines_of_code = models.TextField(default="")
    Session_user_tracking_record_summarized_word = models.TextField(default="")
    Session_user_tracking_record_suspicious = models.TextField(default="")
    Session_user_tracking_record_code_complexity = models.IntegerField(default=0)



class Session_correction_pool(models.Model):
    session_correction_pool_id = models.BigAutoField(primary_key=True)
    correction = models.TextField(null=True)
    grade = models.IntegerField(default=0)
    note = models.TextField(null=True)
    user_id_ref = models.ForeignKey(Users, on_delete=models.CASCADE)
    session_id_ref = models.ForeignKey(Session, on_delete=models.CASCADE)

    class META:
        constraints = [
            models.UniqueConstraint(
                fields=["user_id_ref", "session_id_ref"], name="unique combination1"
            )
        ]

    def __repr__(self):
        return f"""
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

class Session_users_groupe_refs(models.Model):
    user_group_refs_id = models.BigAutoField(primary_key=True)
    user_group_refs_users_groupe = models.ForeignKey(
        Session_users_groupe, on_delete=models.CASCADE
    )
    user_group_refs_user_ref = models.ForeignKey(Users, on_delete=models.CASCADE)

class Users_devices(models.Model):
    id_users_device = models.BigAutoField(primary_key=True)
    device = models.TextField(null=False)
    device_ip_address = models.CharField(null=False, max_length=120, unique=True)
    user_ref = models.ForeignKey(Users, on_delete=models.CASCADE)
    is_pc = models.BooleanField(default=False)
    is_phone = models.BooleanField(default=False)

    def __repr__(self):
        return f"""
                    USERS DEVICES
        --------------------------------------------
        id_users_device = {self.id_users_device}
        device = {self.device}
        device_ip_address = {self.device_ip_address}
        user_ref = {self.user_ref}
        """


class Refresh_tokens(models.Model):
    id_refresh_token = models.BigAutoField(primary_key=True)
    user_id_ref = models.ForeignKey(Users, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=150, null=False)
    expires_at = models.DateTimeField(null=False)

    def __repr__(self):
        return f"""
                    REFRESH_TOKENS
        -----------------------------------------
        id_refresh_token = {self.id_refresh_token}
        refresh_token = {self.refresh_token}
        expires_at = {self.expires_at}
        """

    def create2(user_ref_id: str, token: str, exp_date: str):
        try:
            # see if there was an other old token
            obj = Refresh_tokens(
                refresh_token=token, user_id_ref=user_ref_id, expires_at=exp_date
            ).save()
            return obj
        except Exception as e:
            log.log_exception("error creating refresh token  " + str(e))
        return False


class sessionMetricsHardRecord(models.Model):
    sessionMetric_id = models.BigAutoField(primary_key=True)

    sessionMetric_total_students = models.IntegerField(default=0)
    sessionMEtric_students_done = models.IntegerField(default=0)
    sessionMetric_avglines = models.IntegerField(default=0)
    sessionMetric_avgerrors = models.IntegerField(default=0)
    sessionMetric_blockedstudents = models.IntegerField(default=0)
    sessionMetric_avgCodeComplexity = models.IntegerField(default=0)
    sessionMetric_avgwordswriten = models.IntegerField(default=0)
    sessionMetric_SessionRef = models.OneToOneField(Session, on_delete=models.CASCADE)

    def __repr__(self):
        return f"""
                    REFRESH_TOKENS
        -----------------------------------------
        sessionMetric_id = {self.sessionMetric_id}
        sessionMetric_total_students = {self.sessionMetric_total_students}
        sessionMEtric_students_done = {self.sessionMEtric_students_done}
        sessionMetric_avglines = {self.sessionMetric_avglines}
        sessionMetric_avgerrors = {self.sessionMetric_avgerrors}
        sessionMetric_blockedstudents = {self.sessionMetric_blockedstudents}
        sessionMetric_avgCodeComplexity = {self.sessionMetric_avgCodeComplexity}
        sessionMetric_avgwordswriten = {self.sessionMetric_avgwordswriten}
        sessionMetric_SessionRef = {self.sessionMetric_SessionRef}

        """
