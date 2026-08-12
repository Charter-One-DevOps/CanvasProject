from typing import Any

from django.db import models

# Create your models here.
class School (models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SchoolAdminInfo (models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Blueprint(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    sis_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.sis_id} for {self.school}"

class LexingtonBlueprint(models.Model):
    course = models.CharField(max_length=100)
    blueprint_id = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.course} to {self.blueprint_id}"

class SubAccountId(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    account_id = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name} for {self.school}"

class Script(models.Model):
    possible_scripts = {
        "Admin": "Add Admins script",
        "Blueprint": "Blueprint script",
        "Designer": "Designer script",
        "LexBlueprint": "Lexington specific blueprint script",
        "Observer": "Observer script",
        "Enrollment": "Enrollment script",
        "CheckSisId": "CheckSisId script",
        "VirtualCrosslist": "Virtual Crosslist script",
        "RemovePeriod": "Remove Period script",
    }

    brief = {
        "Admin": "Adds admins",
        "Blueprint": "Adds blueprints",
        "Designer": "Adds designers",
        "LexBlueprint": "Adds blueprints",
        "Observer": "Adds observers",
        "Enrollment": "Get enrollments and puts it into a box folder",
        "CheckSisId": "Update sis ids",
        "VirtualCrosslist": "cross list virtual",
        "RemovePeriod": "Remove Period from course name",
    }

    full = {
        "Admin": (
            "The Admin script uses the staff list created by GIB Admin to add administrators "
            "to the correct accounts."
        ),

        "Blueprint": (
            "The Blueprint script uses the provided Box file to attach blueprints to courses. "
            "If 'Dissociate' is checked, all existing blueprint associations are removed before "
            "new ones are added. Courses already attached to a blueprint cannot be attached to another."
        ),

        "Designer": (
            "The Designer script checks every non-completed course to ensure all teachers also "
            "have the designer role. Teachers missing the designer role are updated automatically. "
            "If 'Delete Designers' is checked, users who are designers but not teachers in the course "
            "will have their designer role removed."
        ),

        "LexBlueprint": (
            "The LexBlueprint script reviews every course and assigns the correct blueprint "
            "based on the course name."
        ),

        "Observer": (
            "The Observer script creates users from a provided Box file ('Box Observer Code') "
            "and then assigns those users as observers to users listed in another Box file "
            "('Box User Code')."
        ),

        "Enrollment": (
            "The Enrollment script retrieves enrollments from all non-completed courses and "
            "exports the results to a folder in Box."
        ),

        "CheckSisId": (
            "The CheckSisId script verifies that teacher SIS IDs begin with 't' and student "
            "SIS IDs begin with 's'. Users are identified by their email domains, using "
            "'@<school domain>.org' for teachers and '@stu.<school domain>.org' for students."
            "\nstudents/teachers without SIS IDs are not shown here."
        ),


        "VirtualCrosslist": (
            "The VirtualCrosslist script manages virtual cross-listing behavior for courses. "
            "The logic behind this process is being reviewed."
        ),

        "RemovePeriod": (
            "The RemovePeriod script finds courses with 'Period' in the course name and removes it."
        ),
    }
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    script_name = models.CharField(max_length=50, choices=possible_scripts)

    @property
    def brief_summary(self) -> str:
        return self.brief[str(self.script_name)]

    @property
    def description(self) -> str:
        return self.full[str(self.script_name)]


    def __str__(self):
        return f"{self.script_name} for {self.school}"

class Variable (models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.JSONField()
    def __str__(self):
        return f"{self.name} ({self.value}) for {self.school}"


# for school in ["ALA", "ALAJOHNSTON", "ALACHARLOTTE", "ALACOASTAL", "ALAMONROE", "WAKEPREP", "ALALEXINGTON"]:
#     for script in {
#         "Admin": "Add Admins script",
#         "Blueprint": "Blueprint script",
#         "Enrollment": "Enrollment script",
#         "CheckSisId": "CheckSisId script",
#         "RemovePeriod": "Remove Period script",
#     }.keys():
#         if not Script.objects.filter(school=School.objects.get(name=school), script_name=script).exists():
#             p = Script(school=School.objects.get(name= school), script_name=script)
#             p.save()