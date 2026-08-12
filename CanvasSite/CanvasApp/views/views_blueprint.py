import pandas as pd
from .views_base import BaseView

from ..models import School, Blueprint
from ..forms import IdForm

from canvas_full_scripts import CanvasScripts


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