import pandas as pd
from django.shortcuts import redirect
from .views_base import BaseView

from ..models import LexingtonBlueprint
from ..forms import LexingtonIdForm

from canvas_full_scripts import CanvasScripts


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