from django.urls import path

from . import views

urlpatterns = [
    path("", views.SelectSchoolView.as_view(), name= "mainView"),
    # path("", views.upload_file, name= "mainView"),
    path("<str:school_name>/", views.SchoolView.as_view(), name= "schoolView"),
    path("<str:school_name>/Blueprint/", views.BlueprintView.as_view(), name="blueprintView"),
    path("<str:school_name>/Enrollment/", views.GetEnrollmentView.as_view(), name="enrollmentView"),
    path("<str:school_name>/Observer/", views.ObserverView.as_view(), name="observerView"),
]