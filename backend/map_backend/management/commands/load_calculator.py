from django.core.management.base import BaseCommand, CommandError
from map_backend.models import Course, Calculator, Program
from django.conf import settings
import os, json

def is_valid_file(parser, arg):
    dir_path = os.path.abspath(os.path.join(
            settings.BASE_DIR, 'data', arg
            ))

    if not os.path.exists(dir_path):
        parser.error("The file does not exist" % dir_path)
    else:
        return(dir_path)

def load_course(course_data, program_data):
    calc = Calculator(calculator_id=1, title="Science Calculator")
    calc.save()

    with open(course_data) as json_file:
        data = json.load(json_file)

        for d in data:
            course = Course.objects.get(course_id=d)
            calc.courses.add(course)

    with open(program_data) as json_file:
        data = json.load(json_file)

        for d in data:
            program = Program.objects.get(program_id=d)
            calc.programs.add(program)

    calc.save()

class Command(BaseCommand):
    help = 'Creates a calculator'

    def add_arguments(self, parser):
        parser.add_argument('file_dir', type=lambda x: is_valid_file(parser,x))
        parser.add_argument('file_dir2', type=lambda x: is_valid_file(parser,x))

    def handle(self, *args, **options):
        course_data = options['file_dir']
        program_data = options['file_dir2']
        print('\nUploading Course/Program Data to create a Science Calculator with id 1...\n')
        load_course(course_data, program_data)
        print('\nSucessfully Upload\n')
