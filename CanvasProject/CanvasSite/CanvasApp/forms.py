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

class AutoForm(forms.Form):
    #bp rule
    bp_rule = forms.BooleanField(required= False)
    #remote box code
    box_code = forms.CharField(label="remote box code", max_length=100, required= False)
    #dissociate
    dissociate = forms.BooleanField(required= False)


