from django.contrib import admin
from .models import Blueprint, School, Script, LexingtonBlueprint, SubAccountId, Variable

# Register your models here.
admin.site.register(Blueprint)
admin.site.register(School)
admin.site.register(Script)
admin.site.register(LexingtonBlueprint)
admin.site.register(SubAccountId)
admin.site.register(Variable)