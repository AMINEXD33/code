
from django.urls import path
from jwt_api import views
urlpatterns = [
    path('dec/', views.get_dec),
    path('makesession/', views.create_session),
    path('login/', views.login),
    path('refresh/', views.refresh),
    path('test/', views.test_token),
    path('getactivesessions/', views.get_all_active_sessions),
    path('getallgroups/', views.get_all_groups)
]
