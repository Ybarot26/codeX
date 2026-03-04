from django.urls import path

from .views import EmployeeManagement, FetchEmployeesList, Registration, Logout, Login, StoreDetailsManagement

app_name = "store"

urlpatterns = [

    path("registration/", Registration.as_view()),

    path("logout/", Logout.as_view()),

    path("login/", Login.as_view()),

    path("employee/", EmployeeManagement.as_view()),

    path("employee_list/", FetchEmployeesList.as_view()),

    path("store_details_management/", StoreDetailsManagement.as_view()),

]
