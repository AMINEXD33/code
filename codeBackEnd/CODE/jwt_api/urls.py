from django.urls import path
from jwt_api import views

urlpatterns = [
    path("dec/", views.get_dec),
    path("makesession/", views.create_session),
    path("login/", views.login),
    path("refresh/", views.refresh),
    path("test/", views.test_token),
    path("getactivesessions/", views.get_all_active_sessions),
    path("getallgroups/", views.get_all_groups),
    path("getallgroupsandlangages/", views.get_all_groups_and_langages),
    path("getallsessionsstudents/", views.get_all_active_sessions_student),
    path("renamesession/", views.change_session_name),
    path("deletesession/", views.delete_session),
    path("getsessionusers/", views.get_session_users),
    path("redirecttopage/", views.redirect_to_page)
]
