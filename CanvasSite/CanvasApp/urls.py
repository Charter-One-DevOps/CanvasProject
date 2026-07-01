from django.urls import path

from . import views

urlpatterns = [
    path("", views.SelectSchoolView.as_view(), name= "mainView"),
    # path("", views.upload_file, name= "mainView"),
    path("<str:school_name>/", views.SchoolView.as_view(), name= "schoolView"),
    path("<str:school_name>/Admin/", views.AdminsView.as_view(), name="adminView"),
    path("<str:school_name>/Blueprint/", views.BlueprintView.as_view(), name="blueprintView"),
    path("<str:school_name>/LexBlueprint/", views.BPLexingtonView.as_view(), name="blueprintView"),
    path("<str:school_name>/Enrollment/", views.GetEnrollmentView.as_view(), name="enrollmentView"),
    path("<str:school_name>/Observer/", views.ObserverView.as_view(), name="observerView"),
    path("<str:school_name>/Designer/", views.AddDesignersView.as_view(), name="designerView"),
    path("<str:school_name>/CheckSisId/", views.SisIdView.as_view(), name="sisIdView"),
    path("<str:school_name>/VirtualCrosslist/", views.CrosslistVirtualView.as_view(), name="crosslistVirtualView"),
    path("<str:school_name>/RemovePeriod/", views.RemovePeriodsView.as_view(), name="removePeriodView"),

    # path("<str:school_name>/<str:script_name>/Progress/", views.ProgressView.as_view(), name="progressView"),
]