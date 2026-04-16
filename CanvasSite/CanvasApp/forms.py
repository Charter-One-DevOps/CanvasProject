from django import forms
from .models import School
from django.core.validators import FileExtensionValidator

class SchoolForm(forms.Form):
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        label="School",
        empty_label="Select a school",
    )

class IdForm(forms.Form):
    blueprint_id = forms.CharField(label="new blueprint id", max_length=1000, required= False)

class FileForm(forms.Form):
    file = forms.FileField(validators=[FileExtensionValidator(['csv'])], required= False)

class BasicForm(forms.Form):

    def __init__(self, dictionary, *args, **kwargs):
        super().__init__(*args, **kwargs)

        correct_field = {
            int: forms.IntegerField(required=False),
            str: forms.CharField(max_length=200, required=False),
            bool: forms.BooleanField(required=False),
        }

        for name, param_type in dictionary.items():
            # setattr(self, name,correct_field[param_type])
            self.fields[name] = correct_field[param_type]


