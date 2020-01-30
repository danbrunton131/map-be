from django.db import models

# represents one course (either high school or university)
class Course(models.Model):
    # ID of the course (just a unique number)
    course_id = models.IntegerField(primary_key=True)
    # course code, e.g. COMPSCI 1MD3
    course_code = models.TextField()
    # course name, e.g. Principles of Programming
    course_name = models.TextField()
    # course desc, e.g. Learn how to program in Python
    course_desc = models.TextField()
    # todo: might need a faculty column as well.

# represents one program
class Program(models.Model):
    # unique ID for the program
    program_id = models.IntegerField(primary_key=True)
    # name of the program
    program_name = models.TextField()
    # description of the program
    program_desc = models.TextField()
    # base requirement from which requirement parsing begins
    program_base_requirement = models.ForeignKey(Requirement, on_delete=models.SET_NULL)
    
# represents a requirement which must be satisfied for a program
class Requirement(models.Model):
    # ID for this requirement
    requirement_id = models.IntegerField(primary_key=True)
    # ID of the referenced requirement, could match up to any of:
    # requirement ID, course ID
    req_1_id = models.IntegerField()
    # type of the referenced requirement, could be one of:
    # 0 - RequirementID
    # 1 - CourseID
    req_1_type = models.IntegerField()
    # type of logical connector between the requirements, could be one of:
    # 0 - AND
    # 1 - OR
    logic_connector = models.IntegerField()
    # ID of the referenced requirement, could be one of:
    # requirement ID, course ID
    req_2_id = models.IntegerField()
    # type of the referenced requirement, could be one of:
    # 0 - RequirementID
    # 1 - CourseID
    req_2_type = models.IntegerField()
