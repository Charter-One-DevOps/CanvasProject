# Add New Script View

1. Create a new views file in the "views_***scriptname***.py" format in the "views" directory.
2. Create a new views class with "BaseClass" as its parent.
   1. BaseClass has many attributes and functions that can be changed and used. Read "views/views_base.py" to find information on all of it.
3. Import the new class into "views/_\_init__.py".
4. Add the class into "views/urls.py".
5. Add the new script information to the "Script" model in "models/models_script.py".
6. Login onto admin; user: c1 password: Raise123!
7. Go to the script model and add the new script for each of the schools.
8. Then you should be complete!
