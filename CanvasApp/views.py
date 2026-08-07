import pandas as pd
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from .models import School, Blueprint, LexingtonBlueprint, Script, SubAccountId, Variable
from .forms import SchoolForm, BasicForm, IdForm, LexingtonIdForm, FileForm

from canvas_full_scripts import CanvasScripts, SchoolInfo
from gib_admin.config import MSL_ENGINE_CONFIG
from gib_admin.engine.msl import MSLEngine
import csv
import os
from pybox import BoxDrive
from dotenv import load_dotenv

import re


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



class BaseView(View):
    manual = False
    manual_csv: str = "manual.csv"
    template: str = "main.html"
    extra_info: str = None
    extra_context: dict = {}
    auto_params: dict = {}
    manual_params: dict = {}
    var_params: dict = {}
    var_csv: str = "var.csv"
    uploaded_file: str = None
    uploaded_folder: str = None


    def get(self, request, school_name):
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
        school = School.objects.get(name= school_name)
        variables = {}

        for var_name, var_type in self.var_params.items():
            variables[var_name] = {
                "instance": Variable.objects.get_or_create(name=var_name, defaults= {"value": "no value"}, school=school)[0],
                "form": BasicForm({var_name: var_type})}
        return variables

    def post(self, request, school_name):
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
        return []

    def output_function_manual(self, school_name, form):
        return []

    def update_variables_csv(self, school_name, variable_name, value):
        df = pd.read_csv(self.var_csv, index_col=0)
        if school_name in df.columns:
            df[school_name] = df[school_name].astype(str)
        df.loc[variable_name, school_name] = str(value)
        df.to_csv(self.var_csv)
        self.upload_to_box("ALL VARIABLES.csv", self.var_csv, "395540144538")

    def upload_to_box(self, remote_name, local_file = None, box_folder = None):
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


class AdminsView(BaseView):
    manual = True
    manual_params = {"account_id": int, "user_id": int, "role_id": int, "send_confirmation": bool}
    extra_info = "admin.html"
    add_params = {"account_name": str, "account_ids": str}
    var_params = {"admin_role_id": int}
    extra_context = {"add_form": BasicForm(add_params)}
    import_csv = "import.csv"
    staff_csv = r"C:\Users\cphill\Documents\GitHub\Canvas-FullScripts\test_list.csv"
    uploaded_file = "box.csv"
    uploaded_folder = "395540144538"


    def output_function(self, school_name, form):
        self.update_staff_list()
        school = School.objects.get(name=school_name)
        subaccounts_and_ids = dict(
            SubAccountId.objects
            .filter(school=school)
            .values_list("name", "account_id")
        )
        output = CanvasScripts.add_admins_using_schoolinfo(
            SchoolInfo(school_name, Variable.objects.get(name= "admin_role_id", school= school).value, subaccounts_and_ids),
            local_path=self.import_csv,
            from_path=self.staff_csv,
        )

        return [item for sublist in output for item in sublist]

    def output_function_manual(self, school_name, form):
        account_id, user_id, role_id, send_confirmation = form["account_id"], form["user_id"], form["role_id"], form["send_confirmation"]
        return CanvasScripts.add_admins_manual(instance=school_name, account_id=account_id, user_id=user_id, role_id=role_id, send_confirmation=send_confirmation)

    def update_staff_list(self):
        ENGINE = MSLEngine(MSL_ENGINE_CONFIG)
        ENGINE.download_latest()

        with open(r"C:\Users\cphill\Documents\GitHub\Canvas-FullScripts\test_list.csv", mode="w", newline="",
                  encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["First Name", "Last Name", "Email", "Location"])  # Header row

            for staff in ENGINE.get_admin_staff():
                try:
                    # Directly access object attributes from Employee
                    first_name = getattr(staff, "first_name", "")
                    last_name = getattr(staff, "last_name", "")
                    email = getattr(staff, "work_email", "")
                    location = getattr(staff, "location_name", "")

                    writer.writerow([first_name, last_name, email, location])
                    print(f"✅ Added: {first_name} {last_name} ({email}) - {location}")

                except Exception as e:
                    print(f"⚠️ Could not process staff object: {staff} — Error: {e}")
                    writer.writerow(["", "", "", ""])

        print("\n🎉 Staff list exported to 'staff_list.csv'")

    def post(self, request, school_name):
        if account_name := request.POST.get("delete"):
            SubAccountId.objects.get(school= School.objects.get(name= school_name), name=account_name).delete()
            self.turn_dict_to_csv(school_name)
        elif request.POST.get("action") == "id":
            form = BasicForm(self.add_params, request.POST, request.FILES)
            if form.is_valid():
                subaccount_names = form.cleaned_data['account_name'].split()
                subaccount_ids = form.cleaned_data['account_ids'].split()
                for account_name, account_id in zip(subaccount_names, subaccount_ids):
                    if not SubAccountId.objects.filter(school= School.objects.get(name= school_name),
                                                       name=account_name).exists():
                        new_item = SubAccountId.objects.create(school= School.objects.get(name= school_name),
                                                               name=account_name, account_id=account_id)
                        new_item.save()
                        self.turn_dict_to_csv(school_name)
        return super().post(request, school_name)

    def turn_dict_to_csv(self, school_name):
        school = School.objects.get(name=school_name)
        subaccounts_and_ids = dict(
            SubAccountId.objects
            .filter(school=school)
            .values_list("name", "account_id")
        )
        df = pd.DataFrame.from_dict(subaccounts_and_ids, orient='index', columns=['SubaccountId'])
        df.index.name = "Subaccount"
        df.to_csv(self.uploaded_file)
        self.upload_to_box(school_name + " - AdminSubaccounts.csv")


class BlueprintView(BaseView):
    extra_info = "blueprint.html"
    var_params = {"bp_rule": bool, "box_code": str}
    auto_params = {"dissociate": bool, "reset_and_dissociate": bool}
    extra_context = {"id_form": IdForm()}
    import_csv = "import.csv"
    mapping_csv = "mapping.csv"

    uploaded_folder = "395540144538"
    uploaded_file = mapping_csv

    def post(self, request, school_name):
        if sis_id := request.POST.get("delete"):
            Blueprint.objects.get(school= School.objects.get(name= school_name), sis_id=sis_id).delete()
            self.write_blueprints(school_name)
        elif request.POST.get("action") == "id":
            form = IdForm(request.POST, request.FILES)
            if form.is_valid():
                sis_ids = form.cleaned_data['blueprint_id'].split(" ")
                for sis_id in sis_ids:
                    if not Blueprint.objects.filter(school= School.objects.get(name= school_name), sis_id=sis_id).exists():
                        new_item = Blueprint.objects.create(school= School.objects.get(name= school_name), sis_id=sis_id)
                        new_item.save()
                        self.write_blueprints(school_name)
        return super().post(request, school_name)

    def output_function(self, school_name, form):
        self.write_blueprints(school_name)
        bp_rule, box_code, dissociate, reset_and_dissociate = form["bp_rule"], form["box_code"], form["dissociate"], form["reset_and_dissociate"]
        return CanvasScripts.add_blueprint_to_course(instance=school_name,
                                              import_path=self.import_csv,
                                              box_path=self.import_csv,
                                              course_id_prefix="",
                                              bp_rule=bp_rule,
                                              sis_mapping_path=self.mapping_csv,
                                              remote_box_code=box_code,
                                              dissociate=dissociate,
                                              reset_and_dissociate=reset_and_dissociate)

    def output_function_manual(self, school_name, form):
        return CanvasScripts.add_blueprint_to_course_manual(
            instance=school_name,
            import_path= self.import_csv,
            from_path= self.manual_csv,
            dissociate= form.cleaned_data["dissociate"])


    def write_blueprints(self, school_name):
        objects = list(Blueprint.objects.filter(school__name=school_name).values_list('sis_id', flat=True))
        df = pd.DataFrame({school_name: objects})
        df.to_csv(self.mapping_csv, index=False)
        self.upload_to_box(f"{school_name} - Blueprints.csv")

class BPLexingtonView(BaseView):
    extra_info = "lexingtonblueprint.html"
    import_csv = "import.csv"
    mapping_csv = "mapping.csv"

    uploaded_folder = "395540144538"
    uploaded_file = mapping_csv

    def get(self, request, school_name):
        self.extra_context = {"blueprints": LexingtonBlueprint.objects.all(), "id_form": LexingtonIdForm()}
        return super().get(request, school_name)

    def output_function(self, school_name, form):
        self.write_blueprints(school_name)
        output = CanvasScripts.add_blueprint_lexington(
            local_path=self.import_csv,
            mapping_path= self.mapping_csv
        )

        return [item for sublist in output for item in sublist]

    def post(self, request, school_name):
        if info := request.POST.get("delete"):
            course, blueprint_id = info.split(" to ", 1)
            LexingtonBlueprint.objects.get(blueprint_id= blueprint_id, course= course).delete()
            self.write_blueprints()
            return redirect(request.path)
        elif request.POST.get("action") == "id":
            form = LexingtonIdForm(request.POST, request.FILES)
            if form.is_valid():
                blueprint_ids = form.cleaned_data['blueprint_id'].strip().split(",")
                courses = form.cleaned_data['course'].strip().split(",")
                for course, blueprint_id in zip(courses,blueprint_ids):
                    if not LexingtonBlueprint.objects.filter(blueprint_id= blueprint_id, course= course).exists():
                        new_item = LexingtonBlueprint.objects.create(blueprint_id= blueprint_id, course= course)
                        new_item.save()
                        self.write_blueprints()
            return redirect(request.path)
        return super().post(request, school_name)

    def write_blueprints(self):
        courses = LexingtonBlueprint.objects.values_list("course", flat=True)
        blueprints = LexingtonBlueprint.objects.values_list("blueprint_id", flat=True)
        df = pd.DataFrame({"course": courses, "blueprint_id": blueprints})
        df.to_csv(self.mapping_csv, index=False)
        self.upload_to_box("ALALEXINGTON - Blueprints.csv")



class ObserverView(BaseView):
    var_params = {"box_user_code": str, "box_observer_code": str}

    import_user_csv = "user.csv"
    import_observer_csv = "observer.csv"

    def output_function(self, school_name, form):
        school = School.objects.get(name=school_name)
        output = CanvasScripts.add_observers(
            importing_user_path=self.import_user_csv,
            importing_observer_path=self.import_observer_csv,
            instance=school_name,
            box_user_code=Variable.objects.get(name= "box_user_code", school= school).value,
            box_observer_code=Variable.objects.get(name= "box_observer_code", school= school).value,
        )
        return [item for sublist in output for item in sublist]

    def output_function_manual(self, school_name, form):
        return CanvasScripts.add_observers_manual(
            importing_user_path=self.import_user_csv,
            importing_observer_path=self.import_observer_csv,
            instance=school_name
        )



class GetEnrollmentView(BaseView):

    def output_function(self, school_name, form):
        CanvasScripts.get_all_enrollments(instance=school_name, local_path=self.manual_csv)
        return ["file is in box"]

class AddDesignersView(BaseView):
    import_csv = "import.csv"
    auto_params = {"delete_designers": bool}

    def output_function(self, school_name, form):
        return CanvasScripts.add_designers(
            instance=school_name,
            import_path=self.import_csv,
            delete_designers=form.get("delete_designers")
        )

class SisIdView(BaseView):
    auto_params = {"student": bool, "teacher": bool}
    import_csv = "import.csv"
    problem_csv = "problem.csv"

    def output_function(self, school_name, form):
        output = CanvasScripts.check_and_change_sis_id(
            instance=school_name,
            local_path=self.import_csv,
            student=form.get("student"),
            teacher=form.get("teacher"),
            problem_path=self.problem_csv,
        )
        return [item for sublist in output for item in sublist]

class CrosslistVirtualView(BaseView):
    mapping_csv = "mapping.csv"
    import_csv = "import.csv"
    box_csv = "box.csv"

    var_params = {"remote_code": str}

    def output_function(self, school_name, form):
        return CanvasScripts.crosslist_virtual(
            mapping_path=self.mapping_csv,
            local_path=self.import_csv,
            box_path=self.box_csv,
            remote_code=form.get("remote_code"),
        )

class RemovePeriodsView(BaseView):
    import_csv = "import.csv"

    def output_function(self, school_name, form):
        output = CanvasScripts.remove_period(
            instance=school_name,
            local_path= self.import_csv,
        )
        return [item for sublist in output for item in sublist]

# from django.contrib.auth import get_user_model
# User = get_user_model()
# user = User.objects.get(username='cphill')
# user.set_password('Raise123!')
# user.save()
# exit()