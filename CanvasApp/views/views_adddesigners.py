from .views_base import BaseView

from canvas_full_scripts import CanvasScripts


class AddDesignersView(BaseView):
    import_csv = "import.csv"
    auto_params = {"delete_designers": bool}

    def output_function(self, school_name, form):
        return CanvasScripts.add_designers(
            instance=school_name,
            import_path=self.import_csv,
            delete_designers=form.get("delete_designers")
        )