from django.core.management.base import BaseCommand, CommandError
from map_backend.models import Program, RequirementGroup, RequirementItem, CourseList, Course
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

def load_requirements(file):
	with open(file) as json_file:
		data = json.load(json_file)
		
		for d in data:
			program_id = d
			program = Program.objects.get(program_id=program_id)

			print(program.name)
			req_groups = []

			order = 1
			for req in data[program_id]:
				unit, preq_courses = (next(iter(req.items())))
				req = RequirementGroup(order=order, desc="{} - requirement #{}".format(program.name, order))
				req.save()

				 # base case -> science course list
				if preq_courses == []:
					course_list = CourseList.objects.get(list_id=1)
				else:
					course_list = CourseList(name="{} - list for req #{}".format(program.name, order))
					course_list.save()

					for course in preq_courses:
						course_list.courses.add(Course.objects.get(course_id=course))

					course_list.save()


				req_item = RequirementItem(parent_group=req, req_units=unit, req_list=course_list, desc="{} - requirement item {}".format(program.name, order))

				req_item.save()

				req_groups.append(req)

				order += 1

			print(req_groups)
			for req in req_groups:
				program.requirements.add(req)

			program.save()


class Command(BaseCommand):
		help = 'Loads program data'

		def add_arguments(self, parser):
				parser.add_argument('file_dir', type=lambda x: is_valid_file(parser,x))

		def handle(self, *args, **options):
				req_data = options['file_dir']
				print('\nUploading Program Data...\n')
				load_requirements(req_data)
				print('\nSucessfully Upload\n')
				

				