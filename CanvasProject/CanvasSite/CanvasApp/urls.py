from django.urls import path

from . import views

urlpatterns = [
    path("", views.TestClass.as_view(), name= "mainView"),
    # path("", views.upload_file, name= "mainView"),
    path("<str:school_name>/", views.test, name= "test")
]