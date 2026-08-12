from .views_base import BaseView

from canvas_full_scripts import CanvasScripts

class RemovePeriodsView(BaseView):
    import_csv = "import.csv"

    def output_function(self, school_name, form):
        output = CanvasScripts.remove_period(
            instance=school_name,
            local_path= self.import_csv,
        )
        return [item for sublist in output for item in sublist]