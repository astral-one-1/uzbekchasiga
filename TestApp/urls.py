from django.contrib import admin
from django.urls import path, include
from TestApp import views


app_name = "TestApp"  # namespace ishlatish uchun

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("dashboard/", views.user_dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("my_result/", views.my_result, name = "my_result"),
    path("profile/", views.profile, name = "profile"),
    path("tests/", views.tests, name = "tests"),
    path("test/<int:module_id>/", views.start_test, name="start_test"),
    path("bigges/user/<int:user_id>/", views.admin_user_profile, name="admin_user_profile"),
]
