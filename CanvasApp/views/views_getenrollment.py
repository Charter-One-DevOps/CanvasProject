from .views_base import BaseView

from canvas_full_scripts import CanvasScripts


class GetEnrollmentView(BaseView):

    def output_function(self, school_name, form):
        CanvasScripts.get_all_enrollments(instance=school_name, local_path=self.manual_csv)
        return ["file is in box"]