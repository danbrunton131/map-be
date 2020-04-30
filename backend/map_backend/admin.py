from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db.models import TextField
from .models import Course, CourseList, RequirementGroup, RequirementItem, Program, Calculator
from .requirement_handler import Parser

class RequirementItemInline(admin.TabularInline):
	model = RequirementItem
	readonly_fields = ['id']
	extra = 0
	raw_id_fields  = ['req_list']

class RequirementGroupAdmin(admin.ModelAdmin):
	model = RequirementGroup
	search_fields = ['desc']
	inlines = [
		RequirementItemInline,
	]
	formfield_overrides = {
		TextField: {'widget': Textarea(attrs={'rows':2, 'cols':25})},
	}

	readonly_fields = ['requirement_equation']

	def requirement_equation(self, obj):
		requirement_items = obj.requirementitem_set.all()

		if len(requirement_items) == 0:
			return ""

		build_requirements = []

		for i, item in enumerate(requirement_items):
			# We skip the connector for the first item
			if i != 0:
				build_requirements.append(item.connector)

			units = item.req_units
			check_list = list((item.req_list.courses.all().values_list('code', flat=True)))
			check_list = f"{units} Units from {check_list}" 

			build_requirements.append(check_list)

		check_list = Parser(build_requirements, not obj.connector).parse()
		return str(check_list)


class CourseListAdmin(admin.ModelAdmin):
	filter_horizontal = ["courses"]
	search_fields = ['name', 'courses__code']
	list_display = ['name', 'list_courses']

	def list_courses(self, obj):
		courses = []
		for c in obj.courses.all():
			courses.append(c.code)
			if len(courses) > 5:
				return ", ".join(courses) + " ... ... "

		return ", ".join(courses)

class ProgramAdmin(admin.ModelAdmin):
	filter_horizontal = ["requirements"]
	formfield_overrides = {
		TextField: {'widget': Textarea(attrs={'rows':4, 'cols':30})},
	}
	readonly_fields = ['requirement_equation']

	def requirement_equation(self, obj):
		output_requirements = []

		requirement_groups = obj.requirements.all().order_by('order')

		for requirement in requirement_groups:
			requirement_items = requirement.requirementitem_set.all()

			build_requirements = []

			for i, item in enumerate(requirement_items):
				# We skip the connector for the first item
				if i != 0:
					build_requirements.append(item.connector)

				units = item.req_units
				check_list = list((item.req_list.courses.all().values_list('code', flat=True)))
				check_list = f"{units} Units from {check_list}" 

				build_requirements.append(check_list)

			check_list = Parser(build_requirements, not requirement.connector).parse()
			output_requirements.append(str(check_list))

		return "\n".join(output_requirements)

class CourseAdmin(admin.ModelAdmin):
	search_fields = ['name', 'code']

class CalculatorAdmin(admin.ModelAdmin):
	filter_horizontal = ["courses", "programs"]

admin.site.register(Course, CourseAdmin)
admin.site.register(RequirementGroup, RequirementGroupAdmin)
admin.site.register(CourseList, CourseListAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Calculator, CalculatorAdmin)
