from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from django.apps import apps
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError
import json, time
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


reference = apps.get_app_config("jwt_api").my_object
# Create your views here.

def allow_(jwt_encrypted_token, authority="user"):
    """
    this function checks a the authority of a request
    valid: authorities
        1. user
        2. admin
        3. superadmin
    """
    try:
        flag = reference.TokenManager.abstract_token_validation(jwt_encrypted_token)
        if flag is False: return False

        # the flag contains the decrypted jwt now
        role:str = flag["role"]
        # retrurn fals if no role was in the jwt , how ? idk but we're preping for the end of the world here :)
        if not role: return False
        # if authorized
        if role == authority:
            return flag
        
        return False
    except Exception as e:
        print("from allow_()"+str(e))
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


def get_body_from_request(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        return data
    except:
        return None


@require_http_methods(["POST"])
@csrf_exempt
def login(request):
    """ "
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
    cached_token, expiration_date = reference.TokenManager.abstract_token_validation_get_reqs(username)
    
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
    print("HERE")
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
    s = LogCore("views.py", False)
    try:
        body:dict = get_body_from_request(request)
        # flag = allow_(body["data"]["JWT"], authority="admin")
        print(body)
        return JsonResponse({"data": body})
    
    
    except Exception as e:
        s.log_exception("from get_all_active_sessions"+str(e))
        return HttpResponseServerError

    return JsonResponse({"data": "ok"})

@require_http_methods(["POST"])
@csrf_exempt
def test_token(request):
    body:dict = get_body_from_request(request)
    s = LogCore("views.py", True)
    isvalid:bool|str = reference.TokenManager.abstract_token_validation(body["data"]['JWT'])
    if not isvalid:
        return (JsonResponse({"response": False}))
    return (JsonResponse({"response": True}))



@require_http_methods(["POST"])
@csrf_exempt
def get_all_active_sessions(request):
    s = LogCore("views.py", False)
    data = []
    try:
        body:dict = get_body_from_request(request)
        flag = allow_(body["data"]["JWT"], authority="admin")

        print(type(flag))
        print(flag)
        id:str = flag["id"]
        print("we're lokking for the id = ", id)
        if not id:
            return HttpResponseServerError("can't get the id from the token!")
        sessions = Session.objects.filter(session_starter=id).all()
        for session in sessions:           
            data.append(Session_serializer(session).data)
    except Exception as e:
        s.log_exception("from get_all_active_sessions"+str(e))
        return HttpResponseServerError

    return JsonResponse({"data": data})


@require_http_methods(["POST"])
@csrf_exempt
def get_all_groups(request):
    s = LogCore("views.py", False)
    data = []
    try:
        body:dict = get_body_from_request(request)
        flag = allow_(body["data"]["JWT"], authority="admin")

        id:str = flag["id"]
        print("we're lokking for the id = ", id)
        if not id:
            return HttpResponseServerError("can't get the id from the token!")
        groups = Session_users_groupe.objects.all()
        for group in groups:           
            data.append(Session_users_groupe_serializer(group).data)
    except Exception as e:
        s.log_exception("from get_all_active_sessions"+str(e))
        return HttpResponseServerError

    return JsonResponse({"data": data})