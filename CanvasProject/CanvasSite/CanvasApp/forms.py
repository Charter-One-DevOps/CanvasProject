from django import forms
from .models import School
from django.core.validators import FileExtensionValidator

class SchoolForm(forms.Form):
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        label="School",
        empty_label="Select a school",
    )

    file = forms.FileField(validators=[FileExtensionValidator(['csv'])])