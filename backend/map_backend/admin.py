from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db.models import TextField
from .models import Course, CourseList, RequirementGroup, RequirementItem, Program

class RequirementItemInline(admin.TabularInline):
	model = RequirementItem
	readonly_fields = ('id',)
	raw_id_fields = ('req_list',)

class RequirementGroupAdmin(admin.ModelAdmin):
	model = RequirementGroup
	search_fields = ['desc']
	inlines = [
		RequirementItemInline,
	]
	formfield_overrides = {
		TextField: {'widget': Textarea(attrs={'rows':2, 'cols':25})},
	}

class CourseListAdmin(admin.ModelAdmin):
	filter_horizontal = ["courses"]
	search_fields = ['name']

class ProgramAdmin(admin.ModelAdmin):
	filter_horizontal = ["requirements"]
	formfield_overrides = {
		TextField: {'widget': Textarea(attrs={'rows':4, 'cols':30})},
	}

class CourseAdmin(admin.ModelAdmin):
	search_fields = ['name']

admin.site.register(Course, CourseAdmin)
admin.site.register(RequirementGroup, RequirementGroupAdmin)
admin.site.register(CourseList, CourseListAdmin)
admin.site.register(Program, ProgramAdmin)