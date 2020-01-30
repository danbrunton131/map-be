from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core import serializers

from .models import Course, Program, Requirement

# /api/GetCourseData?faculty=<faculty name>
# returns the courselists for the given faculty.
# if the faculty parameter is omitted, it returns courselists for all faculties.
class GetCourseData(View):

    # todo: implement the faculty filtering.
    def get(self, request):
        # faculty to filter by
        faculty = request.GET.get('faculty', '')
        # a .filter should be used instead of .all to filter by faculty
        courses = Course.objects.all()
        # need to build json object to send back that matches the API spec
        response_data = {
            "courseLists": {
                "Spring": {
                },
                "Summer": {
                },
                "Fall": {
                },
                "Winter": {
                }
            }
        }
        # iterate over courses
        for course in courses:
            # build the course data
            course_data = {
                "courseID": course.course_id,
                "courseCode": course.course_code
            }
            # insert into the response based on season, department
            if not course.course_department in response_data['courseLists'][course.course_season]:
                response_data['courseLists'][course.course_season][course.course_department] = []
                response_data['courseLists'][course.course_season][course.course_department].append(course_data)
        # return data
        return JsonResponse(response_data)




    
