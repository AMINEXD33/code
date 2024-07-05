from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from django.apps import apps
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
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

reference = apps.get_app_config("jwt_api").my_object
# Create your views here.


def hash_password(password: str):
    salt = bcrypt.gensalt()
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, salt)


def hash_to_sha_256(password: str):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_http_authorization(request):
    try:
        return request.META.get("HTTP_AUTHORIZATION", "")
    except:
        return None


def get_body_from_request(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        return data
    except:
        return None


@require_http_methods(["GET"])
@csrf_exempt
def get_keys(request):
    data = None
    try:
        # get the username and password from the user
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "data is not sent properly"})
    username = data["username"]
    password = data["password"]
    # validate if the username and password are valid
    # .........
    # let's check if the token is cashed
    cached_token, expiration_date = (
        reference.TokenManager.abstract_token_validation_get_reqs(username, password)
    )
    if cached_token:
        return JsonResponse({"JWT": cached_token, "expired_date": expiration_date})
    # not cached then make a new one
    tooken, expdate = reference.TokenManager.make_configured_token(
        username, password, {"username": "meftah"}
    )
    print("making a new one")
    # we can cach the token here
    reference.TokenManager.cash_token(username, password, tooken)
    # print("caching the new one")
    return JsonResponse({"JWT": tooken, "expired_date": expdate})


@require_http_methods(["POST"])
@csrf_exempt
def login(request):
    """ "
    this view signs in  a client
    """
    os_family = request.user_agent.os.family
    is_pc = request.user_agent.is_pc
    is_phone = request.user_agent.is_mobile
    browser = request.user_agent.browser.family
    ip = get_client_ip(request)
    unauthorized = HttpResponseForbidden({"error": "authentication failed !"})
    def get_initial_data():
        data = get_body_from_request(request)
        if not data or not data.get("username") or not data.get("password"):
            return False
        return data["username"], data["password"]
    def make_refreshtk_save_device(potential_user, refresh_token, aware_exp_date):
        try:
            with transaction.atomic():
                print("trying the atomic transaction")
                # try and create a new refresh token
                obj = Refresh_tokens.objects.create(
                    user_id_ref=potential_user,
                    refresh_token=refresh_token,
                    expires_at=aware_exp_date,
                )
                # record the logedin device if it dosn't already exist 
                device = Users_devices.objects.create(
                    device= os_family + browser,
                    is_pc= is_pc,
                    is_phone= is_phone,
                    device_ip_address=ip,
                    user_ref = potential_user
                )
        except Exception as e:
            print("error device already exists", e)
            # device already exist, create only the refresh_token
            try:
                with transaction.atomic():
                    obj = Refresh_tokens.objects.create(
                    user_id_ref=potential_user,
                    refresh_token=refresh_token,
                    expires_at=aware_exp_date,
                    )
            except Exception as e:
                print(e)
                # some other error accured return unauthorized
                return unauthorized

    username, password = get_initial_data()
    print("log", username, password)
    # let's check if the token is cashed
    # well we're using the hashed password and username to
    # check for caching , so that's pretty safe, giving the only
    # way to get a valid cach if stored, is to know the username,
    # and the original password , all of this to spare the database

    # used sha-256 because the same value gives the same hash, bycrypt changes cause of the salt
    hashed_user_pass = hash_to_sha_256(password)
    cached_token, expiration_date = (
        reference.TokenManager.abstract_token_validation_get_reqs(
            username, hashed_user_pass
        )
    )
    # if it's cached and the refresh token is valid
    if cached_token is not False:
        if cached_token.get("JWT") and \
            Refresh_tokens_manager.check_cached_refresh_token(reference.Redis, 
            cached_token["refresh_token"], cached_token["refresh_token_expiration_date"]):
            print("from cach")
            return JsonResponse(
                {"JWT": cached_token.get("JWT"), 
                "expiration_date": cached_token.get("expiration_date"),
                "refresh_token": cached_token.get("refresh_token"),
                "refresh_token_expiration_date": cached_token.get("refresh_token_expiration_date"),
                })
    # if no cach was found, we can hit the db
    # sinse each user has a unique username
    potential_user = None
    try:
        potential_user = Users.objects.select_related("role_ref").get(
            user_username=username
        )
        print("got the user!!!!")
        # if no user then return a 404
        # just to be safe we'll test for a None Value because I don't know
        # if the query always raises not found
        if not potential_user:
            print("didnt find a user")
            return unauthorized
    except:
        # the query is empty
        print("didnt find a user")
        return unauthorized

    # if the hashed user passed password doesn't equal the one stored in the db
    if not bcrypt.checkpw(
        password.encode("utf-8"), potential_user.user_password.encode("utf-8")
    ):
        print("wrong password")
        print("userpass = ", password.decode("utf-8"))
        print("db_pass  = ", potential_user.user_password)
        return unauthorized
    # check if the user has any refresh tokens, in db
    potetial_refresh_token = None
    try:
        potetial_refresh_token = Refresh_tokens.objects.select_related("user_id_ref").get(user_id_ref=potential_user)
        print("we've found an already stored token for this user ", potetial_refresh_token)
    except Exception as e:
        print("error while getting refresh token", e)

    devices = []
    try:
        devices = Users_devices.objects.filter(user_ref=potential_user).all()
    except Exception as e:
        print("error getting devices or no devices", e)

    if not potetial_refresh_token:
        # generate token
        refresh_token, re_expdate, aware_exp_date = Refresh_tokens_manager.create_new_refresh_token()
        # no refresh token found , then we create one
        # and add this device ip to the devices related to the user
        # if the device doesn't already exist
        make_refreshtk_save_device(potential_user, refresh_token, aware_exp_date)
        # if passwords are match , create a new token and cach it then return it to the user
        tooken, expdate = reference.TokenManager.make_configured_token(
            username,
            password,
            {
                "username": potential_user.user_username,
                "id": potential_user.user_id,
                "role": potential_user.role_ref.role_name,
            },
        )
        reference.TokenManager.cash_token(
            username, hashed_user_pass, {
            "JWT": tooken,
            "expiration_date": expdate,
            "refresh_token": refresh_token,
            "refresh_token_expiration_date": aware_exp_date.isoformat()
            }
        )
        return JsonResponse(
        {"JWT": tooken, 
        "expiration_date": expdate,
        "refresh_token": refresh_token,
        "refresh_token_expiration_date": aware_exp_date.isoformat(),
        })
        
    # refresh token exists , checking if it's valid
    if not Refresh_tokens_manager.check_cached_refresh_token(
        reference.Redis,
        potetial_refresh_token.refresh_token,
        potetial_refresh_token.expires_at
        ):
        # the refresh token is expired
        print("refresh token is expired")
        # refreshing the refreshtoken
        refresh_token, re_expdate, aware_exp_date = Refresh_tokens_manager.create_new_refresh_token()
        try:
            potetial_refresh_token.refresh_token = refresh_token
            potetial_refresh_token.expires_at = aware_exp_date
            potetial_refresh_token.save()
        except:
            return unauthorized
        tooken, expdate = reference.TokenManager.make_configured_token(
            username,
            password,
            {
                "username": potential_user.user_username,
                "id": potential_user.user_id,
                "role": potential_user.role_ref.role_name,
            },
        )
        reference.TokenManager.cash_token(
            username, hashed_user_pass, {
            "JWT": tooken,
            "expiration_date": expdate,
            "refresh_token": refresh_token,
            "refresh_token_expiration_date": aware_exp_date.isoformat()
            }
        )
        return JsonResponse(
        {"JWT": tooken, 
        "expiration_date": expdate,
        "refresh_token": refresh_token,
        "refresh_token_expiration_date": aware_exp_date.isoformat(),
        })
    else:
        tooken, expdate = reference.TokenManager.make_configured_token(
            username,
            password,
            {
                "username": potential_user.user_username,
                "id": potential_user.user_id,
                "role": potential_user.role_ref.role_name,
            },
        )
        reference.TokenManager.cash_token(
            username, hashed_user_pass, {
            "JWT": tooken,
            "expiration_date": expdate,
            "refresh_token": potetial_refresh_token.refresh_token,
            "refresh_token_expiration_date": potetial_refresh_token.expires_at.isoformat()
            }
        )
        return JsonResponse(
        {"JWT": tooken, 
        "expiration_date": expdate,
        "refresh_token": potetial_refresh_token.refresh_token,
        "refresh_token_expiration_date": potetial_refresh_token.expires_at.isoformat(),
        })
    return JsonResponse({"err": "can't provide you with a token"})


@require_http_methods(["GET"])
@csrf_exempt
def refresh(request):
    ip_client = get_client_ip(request)
    if not ip_client:
        return HttpResponseForbidden
    Refresh_tokens.create(ip_client)
    return JsonResponse({"done": "ok"})


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


@require_http_methods(["GET"])
@csrf_exempt
def create_session(request):

    r = Role.objects.filter(role_name="admin").first()
    Users.create(
        "firsttest",
        "test@gmail.com",
        "amine",
        "amine",
        "amine",
        "2000-12-12",
        "453636363",
        r,
        "./",
    )
    return JsonResponse({"ok": "kkk"})
