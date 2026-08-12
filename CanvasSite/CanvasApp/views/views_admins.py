import pandas as pd
from .views_base import BaseView

from ..models import School, SubAccountId, Variable
from ..forms import BasicForm

from canvas_full_scripts import CanvasScripts, SchoolInfo
from gib_admin.config import MSL_ENGINE_CONFIG
from gib_admin.engine.msl import MSLEngine
import csv


class AdminsView(BaseView):
    manual = True
    manual_params = {"account_id": int, "user_id": int, "role_id": int, "send_confirmation": bool}
    extra_info = "admin.html"
    add_params = {"account_name": str, "account_ids": str}
    var_params = {"admin_role_id": int}
    extra_context = {"add_form": BasicForm(add_params)}
    import_csv = "import.csv"
    staff_csv = r"staff_list.csv"
    uploaded_file = "box.csv"
    uploaded_folder = "395540144538"


    def output_function(self, school_name, form):
        self.update_staff_list()
        school = School.objects.get(name=school_name)
        subaccounts_and_ids = dict(
            SubAccountId.objects
            .filter(school=school)
            .values_list("name", "account_id")
        )
        output = CanvasScripts.add_admins_using_schoolinfo(
            SchoolInfo(school_name, Variable.objects.get(name= "admin_role_id", school= school).value, subaccounts_and_ids),
            local_path=self.import_csv,
            from_path=self.staff_csv,
        )

        return [item for sublist in output for item in sublist]

    def output_function_manual(self, school_name, form):
        account_id, user_id, role_id, send_confirmation = form["account_id"], form["user_id"], form["role_id"], form["send_confirmation"]
        return CanvasScripts.add_admins_manual(instance=school_name, account_id=account_id, user_id=user_id, role_id=role_id, send_confirmation=send_confirmation)

    def update_staff_list(self):
        ENGINE = MSLEngine(MSL_ENGINE_CONFIG)
        ENGINE.download_latest()

        with open(self.staff_csv, mode="w", newline="",
                  encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["First Name", "Last Name", "Email", "Location"])  # Header row

            for staff in ENGINE.get_admin_staff():
                try:
                    # Directly access object attributes from Employee
                    first_name = getattr(staff, "first_name", "")
                    last_name = getattr(staff, "last_name", "")
                    email = getattr(staff, "work_email", "")
                    location = getattr(staff, "location_name", "")

                    writer.writerow([first_name, last_name, email, location])
                    print(f"✅ Added: {first_name} {last_name} ({email}) - {location}")

                except Exception as e:
                    print(f"⚠️ Could not process staff object: {staff} — Error: {e}")
                    writer.writerow(["", "", "", ""])

        print("\n🎉 Staff list exported to 'staff_list.csv'")

    def post(self, request, school_name):
        if account_name := request.POST.get("delete"):
            SubAccountId.objects.get(school= School.objects.get(name= school_name), name=account_name).delete()
            self.turn_dict_to_csv(school_name)

        elif request.POST.get("action") == "id":
            form = BasicForm(self.add_params, request.POST, request.FILES)
            if form.is_valid():
                subaccount_names = form.cleaned_data['account_name'].split()
                subaccount_ids = form.cleaned_data['account_ids'].split()
                for account_name, account_id in zip(subaccount_names, subaccount_ids):
                    if not SubAccountId.objects.filter(school= School.objects.get(name= school_name),
                                                       name=account_name).exists():
                        new_item = SubAccountId.objects.create(school= School.objects.get(name= school_name),
                                                               name=account_name, account_id=account_id)
                        new_item.save()
                        self.turn_dict_to_csv(school_name)

        return super().post(request, school_name)

    def turn_dict_to_csv(self, school_name):
        school = School.objects.get(name=school_name)
        subaccounts_and_ids = dict(
            SubAccountId.objects
            .filter(school=school)
            .values_list("name", "account_id")
        )
        df = pd.DataFrame.from_dict(subaccounts_and_ids, orient='index', columns=['SubaccountId'])
        df.index.name = "Subaccount"
        df.to_csv(self.uploaded_file)
        self.upload_to_box(school_name + " - AdminSubaccounts.csv")