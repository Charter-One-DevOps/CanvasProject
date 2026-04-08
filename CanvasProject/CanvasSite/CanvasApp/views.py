import pandas as pd
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .models import School, Blueprint
from .forms import SchoolForm, AutoForm, IdForm, FileForm



from canvas_full_scripts import CanvasScripts #type: ignore
from dotenv import load_dotenv

#Create you views here.

class SchoolView(View):
    template = "school.html"
    def get(self, request, school_name):
        return render(request, self.template)

    def post(self, request, school_name):
        nextScreen = request.POST.get("action")
        return HttpResponseRedirect(f"/Canvas/{school_name}/{nextScreen}")

class BlueprintView(View):
    saved_csv: str = "testing.csv"
    template = "blueprint.html"

    def get(self, request, school_name):
        school_object = School.objects.get(name= school_name)
        context = {"school": school_object, "id_form": IdForm(), "file_form": FileForm(), "auto_form": AutoForm()}
        return render(request, self.template, context)

    def post(self, request, school_name):
        if sis_id := request.POST.get("delete"):
            Blueprint.objects.get(school= School.objects.get(name= school_name), sis_id=sis_id).delete()

        elif request.POST.get("action") == "id":
            form = IdForm(request.POST, request.FILES)
            if form.is_valid():
                sis_id = form.cleaned_data['blueprint_id']
                if not Blueprint.objects.filter(school= School.objects.get(name= school_name), sis_id=sis_id).exists():
                    new_item = Blueprint.objects.create(school= School.objects.get(name= school_name), sis_id=sis_id)
                    new_item.save()
        elif request.POST.get("action") == "manual":
            self.handle_uploaded_file(request.FILES["file"])
            load_dotenv("canvas.env")
            load_dotenv("box.env")
            try:
                CanvasScripts.add_blueprint_to_course_manual(instance= school_name, import_path= "import.csv", from_path= self.saved_csv, dissociate=False)
            except Exception as e:
                return HttpResponse(e)
        elif request.POST.get("action") == "auto":
            form = AutoForm(request.POST, request.FILES)
            if form.is_valid():
                bp_rule = form.cleaned_data['bp_rule']
                box_code = form.cleaned_data['box_code']
                dissociate = form.cleaned_data['dissociate']
                self.write_blueprints(school_name)
                load_dotenv("canvas.env")
                load_dotenv("box.env")

                try:
                    CanvasScripts.add_blueprint_to_course(instance=school_name,
                                                          import_path="import.csv",
                                                          box_path="box.csv",
                                                          course_id_prefix="",
                                                          bp_rule=bp_rule,
                                                          sis_mapping_path="requiredpath.csv",
                                                          remote_box_code=box_code,
                                                          dissociate=dissociate)
                except Exception as e:
                    return HttpResponse(e)
        return self.get(request, school_name)

    def handle_uploaded_file(self, f):
        with open(self.saved_csv, "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def write_blueprints(self, school_name):
        objects = Blueprint.objects.all()
        print(objects)
        df = pd.DataFrame({"ALA": objects})
        df.to_csv("requiredpath.csv", index=False)


class TestClass(View):

    def get(self, request):
        context = {"form": SchoolForm()}
        return render(request, "select.html", context)

    def post(self, request):
        #invalid form
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            # return render(request, "buttons.html", self.context)
            return HttpResponseRedirect(f"/Canvas/{form.cleaned_data['school']}")
        return HttpResponse("invalid data")

