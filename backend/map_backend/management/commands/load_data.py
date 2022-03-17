from django.core.management.base import BaseCommand, CommandError
from map_backend.models import Course, Calculator, Program, RequirementGroup, RequirementItem, CourseList
from django.conf import settings
import os, json

def load_data(courses_path, programs_path):
    # create/save calculator model instance
    calc = Calculator(calculator_id=1, title="Science Calculator")
    calc.save()

    # load first passed courses file path and read as json
    with open(courses_path) as courses_open:
        courses_data = json.load(courses_open)

        # use a dictionary for quick access of a course using the code as key
        course_from_code = {}
        
        # iterate through course data 
        for data in courses_data:

            # create/save course model instance for each
            course = Course(
                course_id=data["id"], code=data["code"], 
                name=data["name"], desc=data["description"], units=3, 
                offered_fall=data["term"]["fall"], 
                offered_winter=data["term"]["winter"], 
                offered_spring=False, offered_summer=False)
            course.save()

            # add to dictionary and calculator
            course_from_code[data["code"]] = course.course_id
            calc.courses.add(course)        

    # load second passed program file path and read as json
    with open(programs_path) as programs_open:
        programs_data = json.load(programs_open)

        # iterate through program data 
        for data in programs_data:

            # create/save a programs model instance
            program = Program(program_id=data["id"], 
                name=data["name"], href=data["href"])
            program.save()

            calc.programs.add(program)

            # write requirement id to help name/track courselist from their source
            # TODO find better naming schema/optimize courselists

            requirement_id = 0

            # iterate through program requirements
            for requirement in data["requirements"]:

                # create/save a courselist named after the program name joined with the requirement id
                course_list = CourseList(
                    name="{}-{}".format(data["name"], requirement_id))
                course_list.save()

                # create/save a requirement group model instance
                # NOTE requirement group models have no purpose currently and could be removed
                requirement_group = RequirementGroup(order=1)
                requirement_group.save()

                # create/save a requirement item model instance passing courselist and requirement group
                requirement_item = RequirementItem(
                    parent_group=requirement_group,
                    req_units=requirement["count"] * 3,
                    req_list=course_list)
                requirement_item.save()

                # iterate over courses in course_requirement_data
                for course_code in requirement["from"]:
                    # retrieve the course using the course code dictionary
                    course = course_from_code[course_code]

                    # add course to course list
                    course_list.courses.add(course)

                # add requirement group to program
                program.requirements.add(requirement_group)
                
                requirement_id += 1

def is_valid_file(parser, arg):
    dir_path = os.path.abspath(os.path.join(
            settings.BASE_DIR, 'data', arg))

    if not os.path.exists(dir_path):
        parser.error("The file does not exist" % dir_path)
    else:
        return(dir_path)

class Command(BaseCommand):
    help = "Assembles and loads all the data from programs.json and courses.json"

    def add_arguments(self, parser):
        parser.add_argument('file_dir', type=lambda x: is_valid_file(parser, x))
        parser.add_argument('file_dir2', type=lambda x: is_valid_file(parser, x))

    def handle(self, *args, **options):
        courses_path = options['file_dir']
        programs_path = options['file_dir2']

        print('\nUploading Course/Program Data to create a Science Calculator with id 1...\n')
        load_data(courses_path, programs_path)
        print('\nSucessfully Upload\n')