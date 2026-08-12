import pandas as pd
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from ..models import School
from ..forms import SchoolForm


class SelectSchoolView(View):
    def get(self, request):
        context = {"form": SchoolForm()}
        return render(request, "select.html", context)

    def post(self, request):
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            return HttpResponseRedirect(f"/Canvas/{form.cleaned_data['school']}")
        return HttpResponse("invalid data")


class SchoolView(View):
    template = "school.html"
    def get(self, request, school_name):
        context = {"school": School.objects.get(name= school_name)}
        return render(request, self.template, context)

    def post(self, request, school_name):
        if request.POST.get("action") == "redirect":
            return HttpResponseRedirect(f"/Canvas/")
        elif nextScreen := request.POST.get("action"):
            return HttpResponseRedirect(f"/Canvas/{school_name}/{nextScreen}")
        return redirect(request.path)