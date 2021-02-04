from django.db import models
from .requirement_handler import Parser

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
    # short description
    shortDesc = models.TextField(blank=True, null=True, max_length=200)
    # order
    order = models.IntegerField(help_text="Order at which requirement is checked - checks from low to high")
    # course ranking Scheme how the requirementGroups are ordered
    #   e.g. possible value is "Chronological"
    #   1st entry is lvl 1 requirements, 2nd is lvl 2 etc
    courseRankingScheme = models.TextField(blank=True, null=True, max_length=500)

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

    def requirement_equation(self):
        output_requirements = []

        requirement_groups = self.requirements.all().order_by('order')

        for requirement in requirement_groups:
            requirement_items = requirement.requirementitem_set.all()

            build_requirements = []

            for i, item in enumerate(requirement_items):
                # We skip the connector for the first item
                if i != 0:
                    build_requirements.append(item.connector)

                units = item.req_units
                check_list = list((item.req_list.courses.all().values_list('code', flat=True)))

                check_list = f"{units} units of {', '.join(c for c in check_list)}"

                build_requirements.append(check_list)

            check_list = Parser(build_requirements, not requirement.connector).parse()
            output_requirements.append(str(check_list))

        return {"requirements": output_requirements}

class Calculator(models.Model):
    """ A calculator contains specific courses/programs to display to the user """

    # ID of calculator
    calculator_id = models.IntegerField(primary_key=True)
    # calculator title
    title = models.TextField(help_text="This will be the title of the webpage for that calculator")
    # courses to display to use to select from
    courses = models.ManyToManyField(Course)
    # programs available to check user's input against
    programs = models.ManyToManyField(Program)

    def __str__(self):
        return self.title
