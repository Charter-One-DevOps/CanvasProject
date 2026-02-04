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