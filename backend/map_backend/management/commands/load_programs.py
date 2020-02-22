from django.core.management.base import BaseCommand, CommandError
from map_backend.models import Program 
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

def load_program(file):
	with open(file) as json_file:
		data = json.load(json_file)
			
		for d in data:
			program_id = d
			name = data[d]
			c = Program(program_id=d, name=name)
			c.save()

class Command(BaseCommand):
		help = 'Loads program data'

		def add_arguments(self, parser):
				parser.add_argument('file_dir', type=lambda x: is_valid_file(parser,x))

		def handle(self, *args, **options):
				program_data = options['file_dir']
				print('\nUploading Program Data...\n')
				load_program(program_data)
				print('\nSucessfully Upload\n')
				

				