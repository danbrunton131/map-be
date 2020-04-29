from django.core.management.base import BaseCommand, CommandError
from map_backend.models import Course 
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

def load_course(file):
	with open(file) as json_file:
		data = json.load(json_file)
			
		for d in data:
			course_id = d
			code = data[d]["code"]
			name = data[d]["name"]
			desc = data[d]["desc"]
			units = data[d]["units"]
			department = code.split(" ")[0]
			# print(course_id, code, name)
			c = Course(course_id=d, code=code, name=name, desc=desc, units=units, department=department, offered_fall=True, offered_winter=False, offered_summer=False, offered_spring=False)
			c.save()

class Command(BaseCommand):
		help = 'Loads course data'

		def add_arguments(self, parser):
				parser.add_argument('file_dir', type=lambda x: is_valid_file(parser,x))

		def handle(self, *args, **options):
				course_data = options['file_dir']
				print('\nUploading Course Data...\n')
				load_course(course_data)
				print('\nSucessfully Upload\n')
				

				