from .views_base import BaseView

from ..models import School, Variable


from canvas_full_scripts import CanvasScripts


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