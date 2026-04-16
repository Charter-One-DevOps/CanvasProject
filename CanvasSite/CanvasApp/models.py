from django.db import models

# Create your models here.
class School (models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Blueprint(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    sis_id = models.CharField(max_length=100)

    def __str__(self):
        return self.sis_id

class Script(models.Model):
    possible_scripts = {
        "Observer": "Observer script",
        "Enrollment": "Enrollment script",
        "Blueprint": "Blueprint script",
    }
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    script_name = models.CharField(max_length=50, choices=possible_scripts)

    def __str__(self):
        return self.script_name