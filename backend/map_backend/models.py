from django.db import models

class Course(models.Model):
	""" Course, e.g. COMPSCI 1MD3 """

	# ID of the course (just a unique number)
	course_id = models.IntegerField(primary_key=True)
	# course code, e.g. COMPSCI 1MD3
	code = models.CharField(max_length=20)
	# course name, e.g. Principles of Programming
	name = models.CharField(max_length=100)
	# course desc, e.g. Learn how to program in Python
	desc = models.TextField()
	# is course in fall
	offered_fall = models.BooleanField()
	# is course in winter
	offered_winter = models.BooleanField()
	# is course in summer
	offered_summer = models.BooleanField()
	# is course in spring
	offered_spring = models.BooleanField()
	# numbe of units (typically 3 units a course)
	units = models.PositiveSmallIntegerField()
	# department
	department = models.CharField(max_length=50)


	def __str__(self):
		""" Displays course as a string """
		return "{} : {}".format(self.code, self.name)

class CourseList(models.Model):
	""" A list of courses """

	# only used when importing from API
	list_id = models.IntegerField(blank=True, null=True)
	# list desc, to allow for common reuse (ex. Science Level 1 courses)
	name = models.CharField(max_length=100, default=None)
	# a course list may have many courses
	courses = models.ManyToManyField(Course)

	def __str__(self):
		return "{}".format(self.name)


class RequirementGroup(models.Model):
	""" represents a requirement group which must be satisfied for a program """

	AND = 0
	OR = 1
	CHOICES_CONNECTORS = (
		(AND, 'AND'),
		(OR, 'OR')
	)

	# logic connector
	connector = models.PositiveSmallIntegerField(choices=CHOICES_CONNECTORS, default=AND)
	# description 
	desc = models.TextField(blank=True, null=True, max_length=500)
	# order 
	order = models.IntegerField(help_text="Order at which requirement is checked - checks from low to high")

	def __str__(self):
		return "{} - Order #{}".format(self.desc, self.order)


class RequirementItem(models.Model):
	"""
	Items that fall within a requirement group
	First requirement item under a group must not have any connector 
	Precedence of connectors is used from parent RequirementGroup
	Example:
		If main connector is AND, the child ORs will be grouped together:
		Parent: 
		  -  AND
		Children: 
		  - Null A
		  - OR B
		  - AND C
		  - OR D
		In this example, A OR B AND C OR D becomes (A OR B) AND (C OR D) 
			
	"""
	AND = 0
	OR = 1
	CHOICES_CONNECTORS = (
		(AND, 'AND'),
		(OR, 'OR')
	)

	# parent requirement group
	parent_group = models.ForeignKey(RequirementGroup, on_delete=models.CASCADE)
	# the first connector will always be null
	connector = models.PositiveSmallIntegerField(choices=CHOICES_CONNECTORS, blank=True, null=True, help_text="The first requirement item must have an empty connector")
	# description 
	desc = models.CharField(blank=True, null=True, max_length=255)
	# number of units
	req_units = models.PositiveSmallIntegerField()
	# course list
	req_list = models.ForeignKey(CourseList, on_delete=models.PROTECT, blank=True, null=True)


	def __str__(self):
		return "{}".format(self.desc)


class Program(models.Model):
	""" A program offered """

	program_id = models.IntegerField(primary_key=True)
	# name of the program
	name = models.TextField()
	# description of the program
	desc = models.TextField()
	# requirement groups
	requirements = models.ManyToManyField(RequirementGroup)


	def __str__(self):
		return "{} - {}".format(self.pk, self.name)


class Calculator(models.Model):
	""" A calculator contains specific courses/programs to display to the user """
	
	# ID of calculator	
	calculator_id = models.IntegerField(primary_key=True)
	# calculator description
	desc = models.TextField()
	# courses to display to use to select from
	courses = models.ManyToManyField(Course)
	# programs available to check user's input against
	programs = models.ManyToManyField(Program)