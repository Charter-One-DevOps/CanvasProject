import pandas as pd
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from ..models import School, Script, Variable
from ..forms import BasicForm, FileForm

import os
from pybox import BoxDrive
from dotenv import load_dotenv

import re


class BaseView(View):
    """The base logic for all script views."""

    template: str = "main.html"  # The base template that every view uses
    extra_info: str = None # An extra template that can be used to add extra information
    extra_context: dict = {} # The information the extra template needs

    manual = False  # Decides whether the manual run section is shown
    manual_params: dict = {} # The parameters that will be passed to "output_function_manual". Format: *parameter name* : *parameter type*
    auto_params: dict = {} # The non-sticky parameters that will be passed to "output_function". Format: *parameter name* : *parameter type*

    var_params: dict = {} # The sticky parameters that will be passed to "output_function". Format: *parameter name* : *parameter type*
    var_csv: str = "var.csv" # The file that all the vars are saved in

    uploaded_file: str = None # The file that will be uploaded to box when running un-specified "upload_to_box"
    uploaded_folder: str = None # The folder that the uploaded_file will be sent to when running un-specified "upload_to_box"


    def get(self, request, school_name):
        """
        sends context to the template.
        Generally won't need to be replaced
        :param request:
        :param school_name:
        :return:
        """
        variables = self.set_variables(school_name)
        school_object = School.objects.get(name=school_name)
        script_name = re.findall(r"/([^/]+)/$", request.path)[0]
        context = {"extra_info": self.extra_info,
                   "school": school_object,
                   "script": Script.objects.get(school=school_object, script_name= script_name),
                   "variables": variables,
                   "output": request.session.get(request.path + "Output"),
                   "file_form": FileForm(),
                   "auto_form": BasicForm(self.auto_params),
                   "manual": self.manual,
                   "manual_form": BasicForm(self.manual_params)} | self.extra_context

        return render(request, self.template, context)

    def set_variables(self, school_name):
        """
        Sets the variables to be sent to the template.
        Won't need to be replaced
        :param school_name:
        :return:
        """
        school = School.objects.get(name= school_name)
        variables = {}

        for var_name, var_type in self.var_params.items():
            variables[var_name] = {
                "instance": Variable.objects.get_or_create(name=var_name, defaults={"value": "no value"}, school=school)[0],
                "form": BasicForm({var_name: var_type})}
        return variables

    def post(self, request, school_name):
        """
        Handles variables, running manual, and running automatic.
        Will need to be added onto if you need post to handle any extra info. Return this function
        :param request:
        :param school_name:
        :return:
        """
        if name := request.POST.get("variable"):
            form = BasicForm({name: self.var_params[name]}, request.POST, request.FILES)
            if form.is_valid():
                obj = Variable.objects.get(school=School.objects.get(name=school_name), name=name)
                obj.value = form.cleaned_data[name]
                self.update_variables_csv(school_name, name, obj.value)
                obj.save()

        elif request.POST.get("action") == "redirect":
            return HttpResponseRedirect(f"/Canvas/{school_name}/")

        elif request.POST.get("action") == "auto":
            form = BasicForm(self.auto_params,request.POST, request.FILES)
            if form.is_valid():
                load_dotenv("canvas.env")
                load_dotenv("box.env")
                try:
                    request.session[request.path + "Output"] = self.output_function(school_name, form.cleaned_data)
                except Exception as e:
                    request.session[request.path + "Output"] = ["ERROR:", str(e)]
            else:
                request.session[request.path + "Output"] = ["ERROR:", str(form.errors)]

        elif self.manual and request.POST.get("action") == "manual":
            form = BasicForm(self.manual_params, request.POST, request.FILES)
            if form.is_valid():
                load_dotenv("canvas.env")
                load_dotenv("box.env")
                try:
                    request.session[request.path + "Output"] = self.output_function_manual(school_name, form.cleaned_data)
                except Exception as e:
                    request.session[request.path + "Output"] = ["ERROR:", str(e)]
            else:
                request.session[request.path + "Output"] = ["ERROR:", str(form.errors)]

        return redirect(request.path)

    def output_function(self, school_name, form):
        """
        What will run when running automatically
        :param school_name:
        :param form:
        :return:
        """
        return []

    def output_function_manual(self, school_name, form):
        """
        What will run when running manually
        :param school_name:
        :param form:
        :return:
        """
        return []

    def update_variables_csv(self, school_name, variable_name, value):
        """
        Handles saving variables to a csv that will be used by the server
        :param school_name:
        :param variable_name:
        :param value:
        :return:
        """
        df = pd.read_csv(self.var_csv, index_col=0)
        if school_name in df.columns:
            df[school_name] = df[school_name].astype(str)
        df.loc[variable_name, school_name] = str(value)
        df.to_csv(self.var_csv)
        self.upload_to_box("ALL VARIABLES.csv", self.var_csv, "395540144538")

    def upload_to_box(self, remote_name, local_file = None, box_folder = None):
        """
        uploads csvs to box
        :param remote_name:
        :param local_file:
        :param box_folder:
        :return:
        """
        if local_file is None:
            local_file = self.uploaded_file
        if box_folder is None:
            box_folder = self.uploaded_folder

        load_dotenv("box.env")
        BOX_CLIENT_ID = os.environ["BOX_CLIENT_ID"]
        BOX_CLIENT_SECRET = os.environ["BOX_CLIENT_SECRET"]
        BOX_ENTERPRISE_ID = os.environ["BOX_ENTERPRISE_ID"]
        b_drive = BoxDrive(BOX_CLIENT_ID, BOX_CLIENT_SECRET, BOX_ENTERPRISE_ID)

        b_drive.upload_file(local_file,
                            remote_name,
                            box_folder,
                            True)

    def handle_uploaded_file(self, f):
        with open(self.manual_csv, "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)