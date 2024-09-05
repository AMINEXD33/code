from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from django.apps import apps
from django.shortcuts import render
from django.http import (
    JsonResponse,
    HttpResponseForbidden,
    HttpResponseServerError,
    HttpResponseBadRequest,
    HttpResponse,
)
import json, time
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from jwt_api.models import *
import bcrypt, hashlib
from ipware import get_client_ip
from jwt_api.utils.refresh_tokens import Refresh_tokens_manager
from jwt_api.models import Refresh_tokens
from django.db import transaction
from django.db.utils import IntegrityError, DatabaseError
from logs_util.log_core import LogCore
from jwt_api.serializers import *
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import connection
from collections import namedtuple

reference = apps.get_app_config("jwt_api").my_object
# Create your views here.
def dictfetchall(cursor):
        """
        Return all rows from a cursor as a dict.
        Assume the column names are unique.
        """
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def removeSpaces(some_str: str):
    """
    this function removes every sigle space in a string
    """
    txt = ""
    for letter in some_str:
        if letter != " ":
            txt += letter
    return txt


def allow_(jwt_encrypted_token, authority="user"):
    """
    this function checks a the authority of a request
    valid: authorities
        1. user
        2. admin
        3. superadmin
    """
    s = LogCore("views.py", False)
    try:
        flag = reference.TokenManager.abstract_token_validation(jwt_encrypted_token)
        if flag is False:
            return False

        # the flag contains the decrypted jwt now
        role: str = flag.get("role")
        # retrurn fals if no role was in the jwt , how ? idk but we're preping for the end of the world here :)
        if not role:
            return False
        # if authorized
        if role == authority:
            return flag

        return False
    except Exception as e:
        s.log_exception(str(e))
        return False


def hash_password(password: str):
    salt = bcrypt.gensalt()
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, salt)


def hash_to_sha_256(password: str):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_refresh_token_http_header(request):
    try:
        refresh_token = request.META.get("HTTP_REFRESH", "")
        if not refresh_token:
            return None
        return refresh_token
    except:
        return None


def get_body_from_request(request) -> dict | None:
    try:
        data = json.loads(request.body.decode("utf-8"))
        return data
    except:
        return None


@require_http_methods(["POST"])
@csrf_exempt
def login(request):
    """
    this view signs in  a client
    """
    # re-referencing the global var for better performance
    global reference
    log = LogCore("views.py, def refresh", False)
    os_family = request.user_agent.os.family
    is_pc = request.user_agent.is_pc
    is_phone = request.user_agent.is_mobile
    browser = request.user_agent.browser.family
    ip = get_client_ip(request)[0]
    print("your ip is ", ip)
    unauthorized = HttpResponseForbidden({"error": "authentication failed !"})

    def get_initial_data():
        data = get_body_from_request(request)
        if not data or not data.get("username") or not data.get("password"):
            return False
        return data["username"], data["password"]

    def save_device(potential_user: Users):
        try:
            device_values = {
                "device": os_family + browser,
                "is_pc": is_pc,
                "is_phone": is_phone,
                "device_ip_address": ip,
                "user_ref": potential_user,
            }
            device, created = Users_devices.objects.get_or_create(
                device_ip_address=device_values["device_ip_address"],
                defaults=device_values,
            )
            return device
        except Exception as e:
            log.log_exception(e)
            return None

    def save_refreshtoken_device(potential_user: Users, refresh_token, aware_exp_date):
        try:
            with transaction.atomic():
                # try and create a new refresh token
                obj = Refresh_tokens.objects.create(
                    user_id_ref=potential_user,
                    refresh_token=refresh_token,
                    expires_at=aware_exp_date,
                )
                # record the logedin device if it dosn't already exist
                device = Users_devices.objects.create(
                    device=os_family + browser,
                    is_pc=is_pc,
                    is_phone=is_phone,
                    device_ip_address=ip,
                    user_ref=potential_user,
                )
        except Exception as e:
            # device already exist, create only the refresh_token
            try:
                with transaction.atomic():
                    obj = Refresh_tokens.objects.create(
                        user_id_ref=potential_user,
                        refresh_token=refresh_token,
                        expires_at=aware_exp_date,
                    )
            except Exception as e:
                log.log_exception(e)
                # some other error accured return unauthorized
                return unauthorized

    def devices_into_a_list(devices: Users_devices):
        result = []
        for device in devices:
            result.append(device.device_ip_address)
        return result

    username, password = get_initial_data()
    cached_token, expiration_date = (
        reference.TokenManager.abstract_token_validation_get_reqs(username)
    )

    # if it's cached and the refresh token is valid
    if cached_token is not False:
        if cached_token.get(
            "JWT"
        ) and Refresh_tokens_manager.check_cached_refresh_token(
            reference.Redis,
            cached_token["refresh_token"],
            cached_token["refresh_token_expiration_date"],
        ):
            return JsonResponse(
                {
                    "JWT": cached_token.get("JWT"),
                    "expiration_date": cached_token.get("expiration_date"),
                    "refresh_token": cached_token.get("refresh_token"),
                    "refresh_token_expiration_date": cached_token.get(
                        "refresh_token_expiration_date"
                    ),
                }
            )
    # if no cach was found, we can hit the db
    # sinse each user has a unique username
    potential_user = None
    try:
        potential_user = Users.objects.select_related("role_ref").get(
            user_username=username
        )
        # if no user then return a 404
        # just to be safe we'll test for a None Value because I don't know
        # if the query always raises not found
        if not potential_user:
            return unauthorized
    except:
        # the query is empty
        return unauthorized

    # if the hashed user passed password doesn't equal the one stored in the db
    if not bcrypt.checkpw(
        password.encode("utf-8"), potential_user.user_password.encode("utf-8")
    ):
        return unauthorized
    # check if the user has any refresh tokens, in db
    potetial_refresh_token = None
    try:
        potetial_refresh_token = Refresh_tokens.objects.select_related(
            "user_id_ref"
        ).get(user_id_ref=potential_user)
    except Exception as e:
        log.log_exception("error while getting refresh token " + str(e))

    devices = None
    devices_array = []
    try:
        # try and get the devices  connected using this account
        devices = Users_devices.objects.filter(user_ref=potential_user).all()
    except Exception as e:
        log.log_exception("error getting devices or no devices " + e)
    # extract an array of ips
    if devices:
        devices_array = devices_into_a_list(devices)
    # make sure to record this device
    devices_array.append(ip)
    if not potetial_refresh_token:
        # generate token
        refresh_token, re_expdate, aware_exp_date = (
            Refresh_tokens_manager.create_new_refresh_token()
        )
        # no refresh token found , then we create one
        # and add this device ip to the devices related to the user
        # if the device doesn't already exist
        save_refreshtoken_device(potential_user, refresh_token, aware_exp_date)
        # if passwords are match , create a new token and cach it then return it to the user
        tooken, expdate = reference.TokenManager.make_configured_token(
            {
                "username": potential_user.user_username,
                "id": potential_user.user_id,
                "role": potential_user.role_ref.role_name,
            }
        )
        # cache the needed values
        reference.TokenManager.cash_token(
            username,
            {
                "JWT": tooken,
                "expiration_date": expdate,
                "refresh_token": refresh_token,
                "refresh_token_expiration_date": aware_exp_date.isoformat(),
            },
        )
        Refresh_tokens_manager.cache_refresh_token(
            reference.Redis,
            refresh_token,
            aware_exp_date.isoformat(),
            devices_array,
            potential_user.user_username,
            potential_user.user_id,
            potential_user.role_ref.role_name,
        )
        return JsonResponse(
            {
                "JWT": tooken,
                "expiration_date": expdate,
                "refresh_token": refresh_token,
                "refresh_token_expiration_date": aware_exp_date.isoformat(),
            }
        )

    # refresh token exists ,and it's not valid
    if not Refresh_tokens_manager.check_cached_refresh_token(
        reference.Redis,
        potetial_refresh_token.refresh_token,
        potetial_refresh_token.expires_at,
    ):
        # try and record this device
        if not save_device(potential_user):
            return HttpResponseForbidden(
                "some error accured, but the result is that you're not allowed in anyways"
            )
        # the refresh token is expired
        # refreshing the refreshtoken
        refresh_token, re_expdate, aware_exp_date = (
            Refresh_tokens_manager.create_new_refresh_token()
        )
        try:
            potetial_refresh_token.refresh_token = refresh_token
            potetial_refresh_token.expires_at = aware_exp_date
            potetial_refresh_token.save()
        except:
            return unauthorized
        tooken, expdate = reference.TokenManager.make_configured_token(
            {
                "username": potential_user.user_username,
                "id": potential_user.user_id,
                "role": potential_user.role_ref.role_name,
            }
        )
        reference.TokenManager.cash_token(
            username,
            {
                "JWT": tooken,
                "expiration_date": expdate,
                "refresh_token": refresh_token,
                "refresh_token_expiration_date": aware_exp_date.isoformat(),
            },
        )
        Refresh_tokens_manager.cache_refresh_token(
            reference.Redis,
            refresh_token,
            aware_exp_date.isoformat(),
            devices_array,
            potential_user.user_username,
            potential_user.user_id,
            potential_user.role_ref.role_name,
        )
        return JsonResponse(
            {
                "JWT": tooken,
                "expiration_date": expdate,
                "refresh_token": refresh_token,
                "refresh_token_expiration_date": aware_exp_date.isoformat(),
            }
        )
    # refresh token exists and it's valid
    else:
        # try and record this device
        if not save_device(potential_user):
            return HttpResponseForbidden(
                "some error accured, but the result is that you're not allowed in anyways"
            )
        tooken, expdate = reference.TokenManager.make_configured_token(
            {
                "username": potential_user.user_username,
                "id": potential_user.user_id,
                "role": potential_user.role_ref.role_name,
            }
        )
        reference.TokenManager.cash_token(
            username,
            {
                "JWT": tooken,
                "expiration_date": expdate,
                "refresh_token": potetial_refresh_token.refresh_token,
                "refresh_token_expiration_date": potetial_refresh_token.expires_at.isoformat(),
                "devices_array": devices_array,
            },
        )
        Refresh_tokens_manager.cache_refresh_token(
            reference.Redis,
            potetial_refresh_token.refresh_token,
            potetial_refresh_token.expires_at.isoformat(),
            devices_array,
            potential_user.user_username,
            potential_user.user_id,
            potential_user.role_ref.role_name,
        )
        return JsonResponse(
            {
                "JWT": tooken,
                "expiration_date": expdate,
                "refresh_token": potetial_refresh_token.refresh_token,
                "refresh_token_expiration_date": potetial_refresh_token.expires_at.isoformat(),
            }
        )
    return JsonResponse({"err": "can't provide you with a token"})


@require_http_methods(["POST"])
@csrf_exempt
def refresh(request):
    # re-referencing the global var for better performance
    global reference
    log = LogCore("views.py, def refresh", False)
    unauthorized = HttpResponseForbidden({"err": "plz re-log in"})
    refresh_token_from_request = get_refresh_token_http_header(request)

    ip_client = get_client_ip(request)[0]

    def is_this_ip_valid(current_ip: list, cached_refresh_token: dict):
        ip_array = cached_refresh_token.get("devices_array")
        if not ip_array:
            # this user shouldn't be using this refresh token
            return False
        # note that the format of allowed_ip is (ip, flag)
        for allowed_ip in ip_array:
            if allowed_ip == current_ip:
                return True
        return False

    def get_refresh_token(token):
        try:
            refresh_token = Refresh_tokens.objects.filter(refresh_token=token).first()
            return refresh_token
        except:
            return None

    def get_devices(refresh_toke: Refresh_tokens):
        try:
            devices = (
                Users_devices.objects.filter(user_ref=refresh_token.user_id_ref)
                .only("device_ip_address")
                .all()
            )
            return devices
        except:
            return None

    def get_user(refresh_token: Refresh_tokens):
        try:
            user = Users.objects.filter(user_id=refresh_token.user_id_ref).first()
            if not user:
                return None
            return user
        except:
            return None

    def make_new_token_and_cachit(user: Users, refresh_token: Refresh_tokens):
        tooken, expdate = reference.TokenManager.make_configured_token(
            {
                "username": user.user_username,
                "id": user.user_id,
                "role": user.role_ref.role_name,
            }
        )
        reference.TokenManager.cash_token(
            username,
            {
                "JWT": tooken,
                "expiration_date": expdate,
                "refresh_token": refresh_token.refresh_token,
                "refresh_token_expiration_date": refresh_token.expires_at,
            },
        )
        return tooken, expdate, refresh_token.refresh_token, refresh_token.expires_at

    def make_new_token_and_cachit_from_cache(
        username_cache: str,
        id_cache: str,
        role_cache: str,
        refresh_token: str,
        refresh_expdate: str,
    ):
        tooken, expdate = reference.TokenManager.make_configured_token(
            {
                "username": username_cache,
                "id": id_cache,
                "role": role_cache,
            }
        )
        reference.TokenManager.cash_token(
            username_cache,
            {
                "JWT": tooken,
                "expiration_date": expdate,
                "refresh_token": refresh_token,
                "refresh_token_expiration_date": refresh_expdate,
            },
        )
        return tooken, expdate, refresh_token, refresh_expdate

    if not refresh_token_from_request:
        print("no refresh token from request")
        return unauthorized
    # we check cach first
    cached_refresh_token = Refresh_tokens_manager.get_refresh_token_from_cach(
        reference.Redis, refresh_token_from_request
    )
    if cached_refresh_token:
        # check if the ip is allowed and the refresh token is valid
        if is_this_ip_valid(
            ip_client, cached_refresh_token
        ) and Refresh_tokens_manager.check_cached_refresh_token(
            reference.Redis,
            refresh_token_from_request,
            cached_refresh_token.get("exp_date"),
        ):
            user = get_user(refresh_token_from_request)
            token, expdate, refresh_token, refresh_tk_exp_date = (
                make_new_token_and_cachit_from_cache(
                    cached_refresh_token.get("username"),
                    cached_refresh_token.get("id"),
                    cached_refresh_token.get("role"),
                    refresh_token_from_request,
                    cached_refresh_token.get("exp_date"),
                )
            )
            return JsonResponse(
                {
                    "JWT": token,
                    "expiration_date": expdate,
                    "refresh_token": refresh_token,
                    "refresh_token_expiration_date": refresh_tk_exp_date,
                }
            )
        print("not a valide ip address")
        return unauthorized
    # if no cash we'll have to hit the db
    refresh_token = get_refresh_token(refresh_token_from_request)
    if not refresh_token:
        print("no refresh token")
        return unauthorized

    devices = get_devices(refresh_token.user_id_ref)
    if not devices:
        print("no device")
        return unauthorized

    flag = False
    for device in devices:
        if device.device_ip_address == ip_client:
            flag = True
            break

    # the current device is not in the allowed list
    if flag is False:
        print("current device is not allowed in")
        return unauthorized

    # the device is allowed, now checking if the refresh_token is valid
    valid = Refresh_tokens_manager.check_cached_refresh_token(
        reference.Redis, refresh_token.refresh_token, refresh_token.expires_at
    )
    if valid:
        # if refresh token is valid then we return a new configured token
        user = get_user(refresh_token)
        if not user:
            print("no user")
            return unauthorized
        # configure the token
        token, expdate, refresh_token, refresh_tk_exp_date = make_new_token_and_cachit(
            user, refresh_token
        )

        return JsonResponse(
            {
                "JWT": token,
                "expiration_date": expdate,
                "refresh_token": refresh_token,
                "refresh_token_expiration_date": refresh_tk_exp_date,
            }
        )
    print("not a valid refresh token")
    return unauthorized


@require_http_methods(["POST"])
@csrf_exempt
def get_dec(request):
    json_token = get_http_authorization(request)
    obj_token = None
    body = None
    # try and get the token and the username and password
    try:
        obj_token = json.loads(json_token)
        # print(obj_token)
    except Exception as e:
        print(e)
        return JsonResponse({"error parsing token": True})

    try:
        body = request.body.decode("utf-8")
        body = json.loads(body)
    except Exception as e:
        print(e)
        return JsonResponse({"error parsing body": True})

    if not body["username"] or not body["password"]:
        return JsonResponse({"autherror": False})
    decrepted_token = reference.TokenManager.abstract_token_validation(obj_token["JWT"])
    if not decrepted_token:
        return JsonResponse({"unauthorized": "True"})

    return JsonResponse({"ok": decrepted_token})


@require_http_methods(["POST"])
@csrf_exempt
def create_session(request):
    from .consumers_soft_records_system import SoftRecords

    s = LogCore("views.py", False)
    try:
        body: dict = get_body_from_request(request)
        flag = allow_(body["data"]["JWT"], authority="admin")
        if not flag:
            return HttpResponseForbidden()
        # see if the request respects some logic
        allowed_to_run_code = body["data"]["allowru"]
        duration_of_the_session = body["data"]["duration"]
        target_group = body["data"]["group"]
        title = body["data"]["title"]
        task = body["data"]["task"]
        topics = body["data"]["topics"]
        lang_target = body["data"]["langue"]

        # duration can't be more than 10hours or smaller than 0.5hour
        if duration_of_the_session > 10:
            return HttpResponseBadRequest("duration can't be that long")

        if duration_of_the_session < 0.5:
            return HttpResponseBadRequest("duration can't be that short")

        # all inputs needs to be at least one character
        for x in [[title, "title"], [task, "task"], [topics, "topics"]]:
            if len(x[0]) == 0:
                return HttpResponseBadRequest(f"field {x[1]} is too short")

        # calculate the ending time
        session_ends_time = datetime.datetime.now() + timedelta(
            hours=duration_of_the_session
        )
        session_ends_time = timezone.make_aware(session_ends_time)

        current_time = timezone.make_aware(datetime.datetime.now())

        if session_ends_time <= current_time:
            return HttpResponseBadRequest("bad session duration")

        # does the lang exist
        lang = Languages.objects.filter(languages_id=lang_target).first()
        if not lang:
            return HttpResponseBadRequest("no language with that name")

        # find an appropriat group
        group_object = Session_users_groupe.objects.filter(
            session_users_groupe=target_group
        ).first()
        if not group_object:
            return HttpResponseBadRequest("no groupe with that name")

        # needs to have a valid user
        user = Users.objects.filter(user_id=flag["id"]).first()
        if not user:
            return HttpResponseBadRequest("who are yaaa bradaaa?")

        # record the session
        new_session = None
        new_metricRecord = None

        students_count = Session_users_groupe_refs.objects.filter(
            user_group_refs_users_groupe=group_object
        ).count()

        does_have_session = Session.objects.filter(
            session_starter=user, session_status=True
        ).all()
        print(len(does_have_session))
        if len(does_have_session) >= 5:
            return HttpResponseBadRequest(
                "you've reached the maximum number of session allowed, delete some , or wait for them to  finish"
            )
        for session in does_have_session:
            if removeSpaces(session.session_title) == removeSpaces(title):
                return HttpResponseBadRequest(
                    "you can't have two sessions with the same title"
                )

        new_session = Session(
            session_status=True,
            session_title=title,
            session_starter=user,
            session_topics=topics,
            session_task=task,
            session_allowed_to_run_code=allowed_to_run_code,
            session_target_group=group_object,
            session_end_time=session_ends_time,
            session_language_ref=lang,
        )
        new_metricRecord = sessionMetricsHardRecord(
            sessionMetric_total_students=students_count,
            sessionMetric_SessionRef=new_session,
        )
        # commit the two records as a transaction
        with transaction.atomic():
            new_session.save()
            new_metricRecord.save()

        sft_rec = SoftRecords(reference.Redis)
        tmp_flag = True
        print("YEEEEEEYE"+str(new_session.session_id))
        if sft_rec.create_master_soft_record(str(new_session.session_id)) == True:
            tmp_flag = False

        if tmp_flag == True:
            s.log_exception("can't create master soft record for a session")
            new_session.delete()
            new_metricRecord.delete()
            return HttpResponseServerError("can't create a record")
        print(
            f"""
        allowed to run = {allowed_to_run_code} [{type(allowed_to_run_code)}]
        duration = {duration_of_the_session} [{type(duration_of_the_session)}]
        target group = {target_group} [{type(target_group)}]
        title = {title} [{type(title)}]
        task = {task} [{type(task)}]
        topics = {topics} [{type(topics)}]
        """
        )

        print("OKO")
        return JsonResponse({"msg": "session was created successfully"})

    except ValidationError as e:
        if "Duplicate entry" in e.message_dict or "Duplicate" in e.message_dict:
            s.log_exception("can't commit with a duplicated data" + str(e))
            return HttpResponseBadRequest("can't commit with a duplicated data")

    except Exception as e:
        s.log_exception("from create session" + str(e))
        return HttpResponseServerError("can't create the session")


@require_http_methods(["POST"])
@csrf_exempt
def test_token(request):
    body: dict = get_body_from_request(request)
    s = LogCore("views.py", True)
    isvalid: bool | str = reference.TokenManager.abstract_token_validation(
        body["data"]["JWT"]
    )
    if not isvalid:
        return JsonResponse({"response": False})
    return JsonResponse({"response": True})


@require_http_methods(["POST"])
@csrf_exempt
def get_all_active_sessions(request):
    from django.db import connection
    from collections import namedtuple

    def dictfetchall(cursor):
        """
        Return all rows from a cursor as a dict.
        Assume the column names are unique.
        """
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    s = LogCore("views.py", False)
    data = []
    query = """
    SELECT
        session_id,
        session_status,
        session_start_time,
        session_end_time,
        session_allowed_to_run_code,
        session_starter_id,
        session_task,
        session_title,
        session_topics,
        session_target_group_id,
        languages_name,
        session_users_groupe_name
    FROM
        jwt_api_session
    INNER JOIN  jwt_api_session_users_groupe ON session_target_group_id = session_users_groupe
    INNER JOIN jwt_api_languages on languages_id = session_language_ref_id
    WHERE session_status = 1 AND session_starter_id = %s;
    """
    try:
        body: dict = get_body_from_request(request)
        flag = allow_(body["data"]["JWT"], authority="admin")
        if flag == False:
            return HttpResponseForbidden("you're not allowed to make such requests")
        id: str = flag["id"]

        if not id:
            return HttpResponseServerError("can't get the id from the token!")
        sessions = ()
        with connection.cursor() as cursor:
            cursor.execute(query, [id])
            sessions = dictfetchall(cursor)

        for session in sessions:
            tmp_dict = {}
            for variable in session:
                tmp_dict[variable] = session[variable]
            data.append(tmp_dict)

    except Exception as e:
        s.log_exception("from get_all_active_sessions" + str(e))
        return HttpResponseServerError("some error accured while getting sessions")

    return JsonResponse({"data": data})


@require_http_methods(["POST"])
@csrf_exempt
def get_all_active_sessions_student(request):
    s = LogCore("views.py", False)
    data = []
    query = """
    SELECT
        session_id,
        session_status,
        session_start_time,
        session_end_time,
        session_allowed_to_run_code,
        session_starter_id,
        session_task,
        session_title,
        session_topics,
        session_target_group_id,
        languages_name,
        session_users_groupe_name
    FROM jwt_api_session_users_groupe_refs
    INNER JOIN jwt_api_session on session_target_group_id = user_group_refs_users_groupe_id
    INNER JOIN jwt_api_session_users_groupe on session_target_group_id = session_users_groupe
    INNER JOIN jwt_api_languages on languages_id = session_language_ref_id
    WHERE user_group_refs_user_ref_id = %s AND session_status = 1;
    """
    try:
        body: dict = get_body_from_request(request)
        flag = allow_(body["data"]["JWT"], authority="user")
        if flag == False:
            return HttpResponseForbidden("you're not allowed to make such requests")
        id: str = flag["id"]
        # print("we're lokking for the id = ", id)
        if not id:
            return HttpResponseServerError("can't get the id from the token!")
        sessions = ()
        with connection.cursor() as cursor:
            cursor.execute(query, [id])
            sessions = dictfetchall(cursor)

        for session in sessions:
            tmp_dict = {}
            for variable in session:
                tmp_dict[variable] = session[variable]
            data.append(tmp_dict)

    except Exception as e:
        s.log_exception("from get_all_active_sessions" + str(e))
        return HttpResponseServerError("some error accured while getting sessions")

    return JsonResponse({"data": data})


@require_http_methods(["POST"])
@csrf_exempt
def get_all_groups(request):
    s = LogCore("views.py", False)
    data = []
    try:
        body: dict = get_body_from_request(request)
        flag = allow_(body["data"]["JWT"], authority="admin")

        id: str = flag["id"]
        print("we're lokking for the id = ", id)
        if not id:
            return HttpResponseServerError("can't get the id from the token!")
        groups = Session_users_groupe.objects.all()
        for group in groups:
            data.append(Session_users_groupe_serializer(group).data)
    except Exception as e:
        s.log_exception("from get_all_active_sessions" + str(e))
        return HttpResponseServerError()

    return JsonResponse({"data": data})


@require_http_methods(["POST"])
@csrf_exempt
def get_all_groups_and_langages(request):
    s = LogCore("views.py", False)
    groups_list = []
    langs_list = []
    try:
        body: dict = get_body_from_request(request)
        flag = allow_(body["data"]["JWT"], authority="admin")
        id: str = flag["id"]
        print("we're lokking for the id = ", id)
        if not id:
            return HttpResponseServerError("can't get the id from the token!")
        groups = Session_users_groupe.objects.all()
        for group in groups:
            groups_list.append(Session_users_groupe_serializer(group).data)
        languages = Languages.objects.all()
        for language in languages:
            langs_list.append(Languages_serializer(language).data)
    except Exception as e:
        s.log_exception("from get_all_active_sessions" + str(e))
        return HttpResponseServerError()

    return JsonResponse({"data": {"groups": groups_list, "languages": langs_list}})

@require_http_methods(["POST"])
@csrf_exempt
def change_session_name(request):
    s = LogCore("views.py", False)
    try:
        body:dict = get_body_from_request(request)
        flag = allow_(body["JWT"], authority="admin")
        id: str = flag["id"]
        print("we're lokking for the id = ", id)
        if not id:
            return HttpResponseServerError("can't get the id from the token!")
        session = Session.objects.filter(session_id = body["sessionid"]).first()
        if session:
            if body["name"] == session.session_title:
                return HttpResponse("the session name is the same!")
            session.session_title = body["name"]
            session.save()
        else:
            return HttpResponseBadRequest("no session was found with this id")
    except Exception as e:
        s.log_exception("from change_session_name" + str(e))
        return HttpResponseServerError("can't delete the session")
    
    return HttpResponse("the session name was changed!")

@require_http_methods(["POST"])
@csrf_exempt
def delete_session(request):
    s = LogCore("views.py", False)
    try:
        body:dict = get_body_from_request(request)
        flag = allow_(body["JWT"], authority="admin")
        id: str = flag["id"]
        print("we're lokking for the id = ", id)
        if not id:
            return HttpResponseServerError("can't get the id from the token!")
        session = Session.objects.filter(session_id = body["sessionid"]).first()
        if not session:
            return HttpResponseServerError("can't find a session with that id!")
        tracking_record = sessionMetricsHardRecord.objects.filter(sessionMetric_SessionRef=session).first()
        if session:
            session.delete()
        if tracking_record:
            tracking_record.delete()
    except Exception as e:
        s.log_exception("from delete_session" + str(e))
        return HttpResponseServerError("can't delete the session")
    return HttpResponse("session deleted!")

@require_http_methods(["POST"])
@csrf_exempt
def get_session_users(request):
    query = """
    SELECT
    user_id,
    user_username,
    img_src
    FROM jwt_api_session
    INNER JOIN jwt_api_session_users_groupe_refs
    ON jwt_api_session_users_groupe_refs.user_group_refs_users_groupe_id = jwt_api_session.session_target_group_id
    INNER JOIN  jwt_api_users
    ON jwt_api_users.user_id = jwt_api_session_users_groupe_refs.user_group_refs_user_ref_id
    WHERE session_id = %s;
    """
    s = LogCore("views.py", False)
    try:
        body:dict = get_body_from_request(request)
        flag = allow_(body["JWT"], authority="admin")
        id: str = flag["id"]
        print("we're lokking for the id = ", id)
        if not id:
            return HttpResponseServerError("can't get the id from the token!")
        users = None
        session_id = body["sessionid"]
        with connection.cursor() as cursor:
            cursor.execute(query, [session_id])
            users = dictfetchall(cursor)
        print("USERS = >>>", users)
    except Exception as e:
        s.log_exception("get_session_users" + str(e))
        return HttpResponseServerError("can't delete the session")
    return JsonResponse(users, safe=False)