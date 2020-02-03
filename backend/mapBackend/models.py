from django.db import models

# represents one course (either high school or university)
class Course(models.Model):
    SUMMER = 'Summer'
    FALL = 'Fall'
    WINTER = 'Winter'
    SPRING = 'Spring'
    SEASONS = (
        (SUMMER, 'Summer'),
        (FALL, 'Fall'),
        (WINTER, 'Winter'),
        (SPRING, 'Spring')
    )
    # ID of the course (just a unique number)
    course_id = models.IntegerField(primary_key=True)
    # course code, e.g. COMPSCI 1MD3
    course_code = models.TextField()
    # course name, e.g. Principles of Programming
    course_name = models.TextField()
    # course desc, e.g. Learn how to program in Python
    course_desc = models.TextField()
    # course season, should be one of summer, fall, winter, spring
    course_season = models.TextField(choices=SEASONS, default=FALL)
    
    # todo for both of the below:
    # consider creating separate structural tables for Faculty, Department
    # so we can enforce foreign key relationships on them, make it easier
    # to make large modifications.
    # faculty column, indicates the overarching faculty
    course_faculty = models.TextField()
    # department column, indicates the department
    course_department = models.TextField()

# represents a requirement which must be satisfied for a program
class Requirement(models.Model):
    REQUIREMENT = 'RequirementID'
    COURSE = 'CourseID'
    CHOICES_REQS = (
        (REQUIREMENT, 'Nested Requirement'),
        (COURSE, 'Required Course')
    )

    AND = 'AND'
    OR = 'OR'
    CHOICES_CONNECTORS = (
        (AND, 'AND'),
        (OR, 'OR')
    )
    
    # ID for this requirement
    requirement_id = models.IntegerField(primary_key=True)
    # ID of the referenced requirement, could match up to any of:
    # requirement ID, course ID
    req_1_id = models.IntegerField()
    # type of the referenced requirement, could be one of:
    # Requirement, Course
    req_1_type = models.TextField(choices=CHOICES_REQS, default=REQUIREMENT)
    # type of logical connector between the requirements, could be one of:
    # AND,OR
    logic_connector = models.TextField(choices=CHOICES_CONNECTORS, default=AND)
    # ID of the referenced requirement, could be one of:
    # requirement ID, course ID
    req_2_id = models.IntegerField()
    # type of the referenced requirement, could be one of:
    # 0 - RequirementID
    # 1 - CourseID
    req_2_type = models.TextField(choices=CHOICES_REQS, default=REQUIREMENT)

# represents one program
class Program(models.Model):
    # unique ID for the program
    program_id = models.IntegerField(primary_key=True)
    # name of the program
    program_name = models.TextField()
    # description of the program
    program_desc = models.TextField()
    # base requirement from which requirement parsing begins
    program_base_requirement = models.ForeignKey(Requirement, on_delete=models.SET_NULL, null=True)
