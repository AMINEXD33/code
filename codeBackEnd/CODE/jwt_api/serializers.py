from rest_framework import serializers
from jwt_api.models import Users
from jwt_api.models import Role
from jwt_api.models import Session_correction_pool
from jwt_api.models import Session_user_pool
from jwt_api.models import Users_stats
from jwt_api.models import Session
from jwt_api.models import Session_users_groupe
from jwt_api.models import Session_users_groupe_refs
class Role_serializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
        'role_id',
        'role_name',
        ]

class Users_serializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            'user_id',
            'user_username',
            'user_email',
            'user_password',
            'user_firstName',
            'user_lastName',
            'date_ofBirth', 
            'phone_number',
            'role_ref',
            'record_date',
            'img_src'
        ]
class Session_serializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = [
            'session_id',
            'session_status',
            'session_title',
            'session_topics',
            'session_task',
            'session_start_time',
            'session_end_time',
            'session_allowed_to_run_code',
            'session_starter'
        ]
class Session_correction_pool_serializer(serializers.ModelSerializer):
    class Meta:
        model = Session_correction_pool
        fields= [
            'session_correction_pool_id',
            'correction',
            'note',
            'user_id_ref',
            'session_id_ref'
        ]
class Session_user_pool_serializer(serializers.ModelSerializer):
    class Meta:
        model = Session_user_pool
        fields = [
            'session_user_pool_id',
            'user_id_ref',
            'session_id_ref',
            'flaged',
            'code_content'
        ]
class Users_stats_serializer(serializers.ModelSerializer):
    class Meta:
        model = Users_stats
        fields = [
            'users_stats_id',
            'session_user_pool_ref',
            'user_id_ref',
            'words_per_minute',
            'lines_of_code',
            'syntax_errors_number',
            'code_complexity'
        ]

class Session_users_groupe_serializer(serializers.ModelSerializer):
    class Meta:
        model = Session_users_groupe
        fields = [
            'session_users_groupe',
            'session_users_groupe_name',
            'session_users_groupe_creation_date',
            'session_users_groupe_creator'
        ]