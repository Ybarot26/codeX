from django.urls import path

from .views import ErrorLoggingView


app_name = "logs"

urlpatterns = [

    path("errorlogging/", ErrorLoggingView.as_view()),

]
