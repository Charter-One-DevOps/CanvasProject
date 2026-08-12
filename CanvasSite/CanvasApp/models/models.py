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