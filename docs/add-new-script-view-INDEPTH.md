### Examples and Extra Info

---

---

#### Creating a new file

There are 2 imports you have to have. 

```
from .views_base import BaseView

from canvas_full_scripts import CanvasScripts
```

---

#### Adding onto post

Add all the new things posts needs to do.

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

Always return BaseClass's post.

```
   return super().post(request, school_name)
```

---

#### Adding a class to "views/_\_init__.py" file

Get your finished class

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


Add the class to the "views/_\_init__.py" file

      from .views import *
      from .views_adddesigners import AddDesignersView
      from .views_admins import AdminsView
      from .views_blueprint import BlueprintView
      from .views_bplexington import BPLexingtonView
      from .views_crosslistvirtual import CrosslistVirtualView
      from .views_getenrollment import GetEnrollmentView
      from .views_observer import ObserverView
      from .views_sisid import SisIdView
      
      from .views_removeperiod import RemovePeriodsView   # Adding in the brand new class

