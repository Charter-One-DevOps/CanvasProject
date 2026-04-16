import pandas as pd
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .models import School, Blueprint
from .forms import SchoolForm, BasicForm, IdForm, FileForm


from canvas_full_scripts import CanvasScripts #type: ignore
from dotenv import load_dotenv

#Create you views here.

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
        return self.get(request, school_name)


class SelectSchoolView(View):

    def get(self, request):
        context = {"form": SchoolForm()}
        return render(request, "select.html", context)

    def post(self, request):
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            return HttpResponseRedirect(f"/Canvas/{form.cleaned_data['school']}")
        return HttpResponse("invalid data")


class BaseView(View):
    manual = True
    manual_csv: str = "manual.csv"
    template: str = "base.html"
    extra_info: str = None
    extra_context: dict = {}
    auto_params: dict = {}
    manual_params: dict = {}
    #possibly add script output saving accross screens
    output = None



    def get(self, request, school_name):
        school_object = School.objects.get(name=school_name)
        context = {"extra_info": self.extra_info,
                   "school": school_object,
                   "output": self.output,
                   "file_form": FileForm(),
                   "auto_form": BasicForm(self.auto_params),
                   "manual": self.manual,
                   "manual_form": BasicForm(self.manual_params)} | self.extra_context
        return render(request, self.template, context)

    def post(self, request, school_name):
        if request.POST.get("action") == "redirect":
            return HttpResponseRedirect(f"/Canvas/{school_name}/")
        elif request.POST.get("action") == "auto":
            form = BasicForm(self.auto_params,request.POST, request.FILES)
            if form.is_valid():
                load_dotenv("canvas.env")
                load_dotenv("box.env")
                self.extra_auto_functions(school_name, form.cleaned_data)
            # try:
                self.output = self.output_function(school_name, form.cleaned_data)
            # except Exception as e:
            #     return HttpResponse(e)
        elif self.manual and request.POST.get("action") == "manual":
            form = BasicForm(self.manual_params, request.POST, request.FILES)
            self.handle_uploaded_file(request.FILES["file"])
            load_dotenv("canvas.env")
            load_dotenv("box.env")
            self.extra_manual_functions()
        # try:
            self.output = self.output_function_manual(school_name, form.cleaned_data)
        # except Exception as e:
        #   return HttpResponse(e)

        return self.get(request, school_name)

    def output_function(self, school_name, form):
        return []

    def output_function_manual(self, school_name, form):
        return []

    def extra_auto_functions(self, school_name, form):
        return None

    def extra_manual_functions(self):
        return None

    def handle_uploaded_file(self, f):
        with open(self.manual_csv, "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)

class BlueprintView(BaseView):
    extra_info = "blueprint.html"
    auto_params = {"bp_rule": bool, "box_code": str, "dissociate": bool}
    manual_params = {"dissociate": bool}
    extra_context = {"id_form": IdForm()}
    import_csv = "import.csv"


    def post(self, request, school_name):
        if sis_id := request.POST.get("delete"):
            Blueprint.objects.get(school= School.objects.get(name= school_name), sis_id=sis_id).delete()
        elif request.POST.get("action") == "redirect":
            return HttpResponseRedirect(f"/Canvas/{school_name}/")
        elif request.POST.get("action") == "id":
            form = IdForm(request.POST, request.FILES)
            if form.is_valid():
                sis_ids = form.cleaned_data['blueprint_id'].split(" ")
                for sis_id in sis_ids:
                    if not Blueprint.objects.filter(school= School.objects.get(name= school_name), sis_id=sis_id).exists():
                        new_item = Blueprint.objects.create(school= School.objects.get(name= school_name), sis_id=sis_id)
                        new_item.save()
        return super().post(request, school_name)

    def extra_auto_functions(self, school_name, form):
        self.write_blueprints(school_name)

    def output_function(self, school_name, form):
        bp_rule, box_code, dissociate = form["bp_rule"], form["box_code"], form["dissociate"]
        return CanvasScripts.add_blueprint_to_course(instance=school_name,
                                              import_path=self.import_csv,
                                              box_path=self.import_csv,
                                              course_id_prefix="",
                                              bp_rule=bp_rule,
                                              sis_mapping_path=self.manual_csv,
                                              remote_box_code=box_code,
                                              dissociate=dissociate)

    def output_function_manual(self, school_name, form):
        return CanvasScripts.add_blueprint_to_course_manual(instance=school_name, import_path= self.import_csv, from_path= self.manual_csv, dissociate= form.cleaned_data["dissociate"])


    def write_blueprints(self, school_name):
        objects = Blueprint.objects.all()
        df = pd.DataFrame({school_name: objects})
        df.to_csv(self.manual_csv, index=False)


class ObserverView(BaseView):
    auto_params = {"box_observer_code": str, "box_user_code": str}

    import_user_csv = "user.csv"
    import_observer_csv = "observer.csv"

    def output_function(self, school_name, form):
        return CanvasScripts.add_observers(
            importing_user_path=self.import_user_csv,
            importing_observer_path=self.import_observer_csv,
            instance=school_name,
            box_user_code=form.get("box_user_code"),
            box_observer_code=form.get("box_observer_code"),
        )

    def output_function_manual(self, school_name, form):
        return CanvasScripts.add_observers_manual(
            importing_user_path=self.import_user_csv,
            importing_observer_path=self.import_observer_csv,
            instance=school_name
        )



class GetEnrollmentView(BaseView):
    manual = False

    def output_function(self, school_name, form):
        CanvasScripts.get_all_enrollments(instance=school_name, local_path=self.manual_csv)
        return ["file is in box"]


class AddAdmins(BaseView):
    import_csv = "import.csv"
    from_csv = "from.csv"

    def output_function(self, school_name, form):
        return CanvasScripts.add_admins(
            local_path=self.import_csv,
            from_path=self.from_csv,
            #Blah blah blah
            #add admins is gonna need lots of code for its dicts. probably gonna use extra info to save ids and its things
        )