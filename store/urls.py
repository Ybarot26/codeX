from django.urls import path

from .views import Registration, Logout, Login

app_name = "store"

urlpatterns = [

    path("registration/", Registration.as_view()),

    path("logout/", Logout.as_view()),

    path("login/", Login.as_view()),

]
