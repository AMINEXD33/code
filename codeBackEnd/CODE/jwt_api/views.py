from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from .serializers import GroupSerializer, UserSerializer
from django.apps import apps
from django.shortcuts import render
from django.http import JsonResponse
import json
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
reference = apps.get_app_config("jwt_api").my_object
# Create your views here.
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
def get_dec(request):
    json_token = request.META.get('HTTP_AUTHORIZATION', '')
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
    if not reference.TokenManager.abstract_token_validation(
        body["username"], 
        body["password"],
        obj_token["JWT"]):
        return JsonResponse({"unauthorized":"True"})

    return JsonResponse({"ok":True})