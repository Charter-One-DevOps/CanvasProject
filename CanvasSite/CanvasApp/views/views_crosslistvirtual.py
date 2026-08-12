from .views_base import BaseView

from canvas_full_scripts import CanvasScripts


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