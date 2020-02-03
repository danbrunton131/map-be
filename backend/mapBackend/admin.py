from django.contrib import admin

from .models import Course, Program, Requirement

# Register your models here.
admin.site.register(Course)
admin.site.register(Program)
admin.site.register(Requirement)
