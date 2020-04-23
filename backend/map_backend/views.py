from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core import serializers
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from haystack.query import SearchQuerySet
from .requirement_handler import BinOp, Parser
import json
import time

from .models import Course, Program, RequirementGroup, RequirementItem

AND = 0
OR = 1

class SearchCourse(View):

	def get(self, request):

		query = request.GET.get('q', '')

		if len(query) > 30:
			return JsonResponse({"error" : "long query"}) 

		res = SearchQuerySet().filter(content=query)
		suggestions = []

		for course in res:
			course_data = {
				"courseID": course.object.course_id,
				"courseCode": course.object.code,
				"courseName": course.object.name,
				"courseDesc": course.desc,
				"courseFall": course.offered_fall,
				"courseWinter": course.offered_winter,
				"courseSummer": course.offered_summer,
				"courseSpring": course.offered_spring
			}

			suggestions.append(course_data)


		response_data = {
			'results' : suggestions # in list to maintain order/ranking
		}

		return JsonResponse(response_data)


# /api/GetCourseData?faculty=<faculty name>
# returns the courselists for the given faculty.
# if the faculty parameter is omitted, it returns courselists for all faculties.
class GetCourseData(View):

	def get(self, request):
		# faculty to filter by
		faculty = request.GET.get('faculty', '')

		if faculty == "":
			courses = Course.objects.all()
		else:
			courses = Course.objects.filter(department=faculty)

		# need to build json object to send back that matches the API spec
		response_data = {
			"courseLists": {
				"Spring": defaultdict(list),
				"Summer": defaultdict(list),
				"Fall": defaultdict(list),
				"Winter": defaultdict(list)
			}
		}
		# iterate over courses
		for course in courses:
			# build the course data
			course_data = {
				"courseID": course.course_id,
				"courseCode": course.code,
				"courseName": course.name,
				"courseDesc": course.desc
			}

			# insert into the response based on season, department
			if course.offered_fall:
				response_data['courseLists']["Fall"][course.department].append(course_data)
			if course.offered_winter:
				response_data['courseLists']["Winter"][course.department].append(course_data)
			if course.offered_summer:
				response_data['courseLists']["Summer"][course.department].append(course_data)
			if course.offered_spring:
				response_data['courseLists']["Spring"][course.department].append(course_data)

		# return data
		return JsonResponse(response_data)


# Request:
# /api/GetCourseDetails?courseid=1234567
class GetCourseDetails(View):

	def get(self, request):
		# course_id to filter by
		course_id = request.GET.get('courseid', '')

		if course_id == "":
			return JsonResponse({"error" : "Invalid Course ID"})
		
		try:
			course = Course.objects.get(course_id=course_id)
		except:
			return JsonResponse({"error" : "Invalid Course ID"})

		response_data = defaultdict(str)

		response_data["courseCode"] = course.code
		response_data["courseName"] = course.name
		response_data["courseDesc"] = course.desc

		return JsonResponse(response_data)

# /api/SubmitCourseSelections
# send as a POST.
# body should contain one key 'selections' with a value of an array of course IDs selected.
# still in progress
class SubmitCourseSelections(View):

	# temp exempt for testing
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super(SubmitCourseSelections, self).dispatch(request, *args, **kwargs)

	def post(self, request):
		# get programs
		# to do -> calculator ID should only filter a select number of courses

		selected_courses = json.loads(request.body)["selections"]
		if len(selected_courses) > 15:
			return JsonResponse({"error" : "too many courses"})

		programs = Program.objects.all()

		response_json = {
			"matchedPrograms" : [
			]
		}

		for program in programs:

			# create our course list and counter
			course_list = selected_courses.copy()
			original_course_list = set(selected_courses.copy())

			total_completed_courses = total_required_courses = 0

			# get all requirements
			requirement_groups = program.requirements.all().order_by('order').prefetch_related('requirementitem_set')

			for requirement in requirement_groups:
				#requirement_items = RequirementItem.objects.filter(parent_group=requirement)
				requirement_items = requirement.requirementitem_set.all()

				# TODO: merge == 1 and multi together
				
				if len(requirement_items) == 1:

					units = requirement_items[0].req_units
					check_list = list((requirement_items[0].req_list.courses.all().values_list('course_id', 'units')))
					check_list = (units, check_list)

					# apply calculations
					completed_courses, required_courses, course_list = self.calculate(check_list, course_list)

					# update total counter
					total_completed_courses += completed_courses
					total_required_courses += required_courses


				else:

					build_requirements = []

					# We are converting a complex requirement_group 
						# Ex. Group connector is OR 
						# 
						# -     |   3 units from List 1
						# AND   |   3 units from List 2
						# OR    |   3 units from List 3
						# AND   |   3 units from List 4
						#
						# This is converted to 
						# output -> (3 units from L1 AND 3 units from L2) OR (3 units from L3 AND 3 units from L4) 

					for i, item in enumerate(requirement_items):
						# We skip the connector for the first item
						if i != 0:
							build_requirements.append(item.connector)

						units = item.req_units
						check_list = list((item.req_list.courses.all().values_list('course_id', 'units')))
						check_list = (units, check_list)
	
						build_requirements.append(check_list)

					# Now we build a parse tree
					# Parser takes in a precedence which is opposite of connector
					# 	 -> mosaic's connector is the opposite of the precedence
					# This will output something like 
						# -> (3 units from L1 AND 3 units from L2) OR (3 units from L3 AND 3 units from L4)
					check_list = Parser(build_requirements, not requirement.connector).parse()
					


					# apply calculations
					completed_courses, required_courses, course_list = self.calculate(check_list, course_list)
					# update total counter
					total_completed_courses += completed_courses
					total_required_courses += required_courses


			# append answer to our result
			res = {
				"programName" : program.name,
				"programDescription" : program.desc,
				"programPercentage" :  round(total_completed_courses / total_required_courses, 2) if total_required_courses != 0 else 0,
				"programRequirements": program.requirement_equation(),
				"fufilledCourses": list(original_course_list - set(course_list))
			}
			response_json["matchedPrograms"].append(res)


		return JsonResponse(response_json)

	def calculate(self, tree, course_list):

		# base case
		if not isinstance(tree, BinOp):
			units, check_list = tree
			req_units = units
			# convert check_list to set for const lookup
			units_for_course = dict(check_list)

			check_list = set(units_for_course.keys())

			new_course_list = course_list.copy()

			for course in course_list:
				if course in check_list:
					units -= units_for_course[course]
					# course_list is still a list to maintain ordering
					new_course_list.remove(course)
					if units == 0:
						break

			course_list = new_course_list

			if units == 0:
				return req_units, req_units, course_list
			else:
				return req_units - units, req_units, course_list 

		if tree.op == AND:
			left_completed_courses, left_required_coures, left_course_list = self.calculate(tree.left, course_list)
			# Since we have an AND, we use the updated course_list from the left
			right_completed_courses, right_required_courses, right_course_list = self.calculate(tree.right, left_course_list)

			return (left_completed_courses + right_completed_courses), (left_required_coures + right_required_courses), right_course_list
		else:
			# OR case
			# Keep a copy to prevent aliasing
			course_list_copy = course_list.copy()
			left_completed_courses, left_required_coures, left_course_list = self.calculate(tree.left, course_list)
			# Since we have an AND, we use the updated course_list from the left
			right_completed_courses, right_required_courses, right_course_list = self.calculate(tree.right, course_list_copy)

			# if left side of equation is True, we propogate that up
			if left_completed_courses == left_required_coures or ((left_required_coures - left_completed_courses) < (right_required_courses - right_completed_courses)):
				return left_completed_courses, left_required_coures, left_course_list
			else:
				return right_completed_courses, right_required_courses, right_course_list 