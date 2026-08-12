from .views_base import BaseView

from canvas_full_scripts import CanvasScripts


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