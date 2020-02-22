import json

def upload_coures():
	with open('courses.json') as json_file:
		data = json.load(json_file)
		
		for d in data:
			course_id = d
			code = data[d]["code"]
			name = data[d]["name"]
			desc = data[d]["desc"]

			print(course_id, code, name)
			#course = Course(course_id=d, )
	pass



upload_coures()