from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from django.apps import apps
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
import json
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from jwt_api.models import *
import bcrypt, hashlib
reference = apps.get_app_config("jwt_api").my_object
# Create your views here.

def hash_password(password:str):
    salt = bcrypt.gensalt()
    password_bytes = password.encode("utf-8")
    return (bcrypt.hashpw(password_bytes, salt))
def hash_to_sha_256(password:str):
    return (hashlib.sha256(password.encode("utf-8")).hexdigest())

def get_http_authorization(request):
    try:
        return (request.META.get('HTTP_AUTHORIZATION', ''))
    except:
        return None

def get_body_from_request(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        return data
    except:
        return None
@require_http_methods(["GET"])
@csrf_exempt
def get_keys(request):
    data = None
    try:
        # get the username and password from the user
        data = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({'error':"data is not sent properly"})
    username=data["username"]
    password=data["password"]
    # validate if the username and password are valid
    #.........
    # let's check if the token is cashed  
    cached_token, expiration_date = reference.TokenManager.abstract_token_validation_get_reqs(username, password)
    if cached_token:
        return JsonResponse({"JWT":cached_token, "expired_date":expiration_date})
    # not cached then make a new one
    tooken, expdate = reference.TokenManager.make_configured_token(username, password, {"username":"meftah"})
    print("making a new one")
    # we can cach the token here 
    reference.TokenManager.cash_token(username, password, tooken)
    # print("caching the new one")
    return JsonResponse({"JWT":tooken, "expired_date":expdate})



@require_http_methods(["POST"])
@csrf_exempt
def login(request):
    """"
    this view signs in  a client
    """
    import time
    time.sleep(3)
    unauthorized = HttpResponseForbidden({"error":"authentication failed !"}) 
    data = get_body_from_request(request)
    if not data:
        return unauthorized
    if not data["username"] or not data["password"]:
        return unauthorized
    username = data["username"]
    password = data["password"]
    if not username or not password:
        return unauthorized
    print("log", username, password)
    # let's check if the token is cashed
    # well we're using the hashed password and username to
    # check for caching , so that's pretty safe, giving the only
    # way to get a valid cach if stored, is to know the username,
    # and the original password , all of this to spare the database

    # used sha-256 because the same value gives the same hash, bycrypt changes cause of the salt
    hashed_user_pass = hash_to_sha_256(password)
    cached_token, expiration_date = reference.TokenManager.abstract_token_validation_get_reqs(username, hashed_user_pass)
    # if it's cached
    if cached_token:
        print("from cach")
        return JsonResponse({"JWT":cached_token, "expired_date":expiration_date})
    # if no cach was found, we can hit the db
    # sinse each user has a unique username
    try:
        potential_user = Users.objects.select_related('role_ref').get(user_username=username)
        # if no user then return a 404
        # just to be safe we'll test for a None Value because I don't know
        # if the query always raise not found
        if not potential_user:
            return unauthorized
    except:
        # the query is empty
        return unauthorized

    # if the hashed user passed password doesn't equal the one stored in the db
    if not bcrypt.checkpw(password.encode("utf-8"), potential_user.user_password.encode('utf-8')):
        print("wrong password")
        print("userpass = ", password.decode('utf-8'))
        print("db_pass  = ", potential_user.user_password)
        return unauthorized
    #if passwords are match , create a new token and cach it then return it to the user
    tooken, expdate = reference.TokenManager.make_configured_token(username, password, {
        "username":potential_user.user_username, 
        "id":potential_user.user_id,
        "role":potential_user.role_ref.role_name
        })
    reference.TokenManager.cash_token(username, hashed_user_pass, tooken)
    print(tooken)
    return JsonResponse({"JWT":tooken, "expired_date":expdate})





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
        return JsonResponse({"error parsing token":True})

    try:
        body = request.body.decode('utf-8')
        body = json.loads(body)
    except Exception as e:
        print(e)
        return JsonResponse({"error parsing body":True})

    if not body["username"] or not body["password"]:
         return JsonResponse({"autherror":False})
    decrepted_token = reference.TokenManager.abstract_token_validation(obj_token["JWT"])
    if not decrepted_token:
        return JsonResponse({"unauthorized":"True"})

    return JsonResponse({"ok":decrepted_token})

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
        "./"
    )
    return JsonResponse({"ok":'kkk'})
