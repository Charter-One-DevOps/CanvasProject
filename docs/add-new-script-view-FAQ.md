### Frequently Asked Questions

---

---

#### What imports does every script need?

There are 2 imports you have to have. 

```
from .views_base import BaseView

from canvas_full_scripts import CanvasScripts
```

---

#### How do I add functionality to post?

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

#### How do I add a class to the "views/_\_init__.py" file?

Get your finished class

      from .views_base import BaseView
      
      from canvas_full_scripts import CanvasScripts
      
      class NewScriptView(BaseView):
          import_csv = "import.csv"
      
          def output_function(self, school_name, form):
              output = CanvasScripts.new_script(
                  instance= school_name,
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
      
      from .views_newscript import NewScriptView  # Adding in the brand new class

---

#### How do I add script information to the "script" model?

You will have to add to 3 dictionaries.

The first dictionary is "possible_scripts". \
The key must be the exact letters of the url. If this "path('<\str:school_name>/***NewScript***/', views.NewScriptView.as_view(), name='newScriptView')," is the new item in the urls.py file, ***NewScript*** needs to be the key \
The value is what will be shown when a user chooses a script


    possible_scripts = {
        "Admin": "Add Admins script",
        ...
        "RemovePeriod": "Remove Period script",

        "NewScript": "New Scripr script"  # The new addition
    }

The second dictionary is "brief". \
The key must be the same as the first dictionaries key.\
The value is a brief description of what the new script does.

    brief = {
        "Admin": "Adds admins",
        ...
        "RemovePeriod": "Remove Period from course name",

        "NewScript": "Makes scripts new"  # The new addition
    }

The third dictionary is "full" \
The key must be the same as the first dictionaries key.\
The value is a full description of what the new script does.

    full = {
        "Admin": (
            "The Admin script uses the staff list created by GIB Admin to add administrators "
            "to the correct accounts."
        ),
        ...
        "RemovePeriod": (
            "The RemovePeriod script finds courses with 'Period' in the course name and removes it."
        ),

        "NewScript": (
            "Goes through each script then makes the script brand new if it needs to be new"
            
        )  # The new addition
    }

