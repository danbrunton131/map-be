from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core import serializers

import json

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
    
# /api/SubmitCourseSelections
# send as a POST.
# body should contain one key 'selections' with a value of an array of course IDs selected.
class SubmitCourseSelections(View):

    def post(self, request):
        # get first program
        programs = Program.objects.all()
        # start building response json
        response_json = {
            "matchedPrograms": [
            ]
        }
        selected = self.convert_to_codes(json.loads(request.body)['selections'])
        # get the course codes for each selection
        for program in programs:
            # error handle programs without a base req
            if program.program_base_requirement == None:
                continue
            # just building a random list of selections
            selections = selected.copy()
            # get base req for a program
            program_basereq = program.program_base_requirement
            # traverse requirements
            req_tree = self.traverse_reqs(program_basereq)
            # now try to satisfy requirements
            is_sat = self.sat_tree(selections, req_tree)
            sat_frag = self.count_percent(is_sat[2])
            # insert the info into the response JSON
            new_prog = {
                "programName": program.program_name,
                "programPercentage": float(sat_frag[0] - sat_frag[1])/float(sat_frag[0]),
                "programDescription": program.program_desc
            }
            response_json['matchedPrograms'].append(new_prog)
        # return data
        return JsonResponse(response_json)
        
    # converts course ID list to course code list.
    # not actually good thing to do, but lazy
    # todo: fix this later.
    def convert_to_codes(self, selections):
        codes = []
        for c in selections:
            codes.append(Course.objects.filter(course_id=c).first().course_code)
        return codes
        
    # takes the sat tree and counts the %age of satisfied requirements.
    def count_percent(self, sats):
        potsat = 2
        unsat = 0
        # approach:
        # parse the tree like in sat_tree.
        # add 2 pts to potsat every branch.
        # if there is a non-1 in either side of an AND branch, add 1 pt to unsat.
        # if there is a non-1 in BOTH sides of an OR branch, add 1 pt to unsat.
        # add 1 pt to potsat for every non-branch (since we only count courses as being needed)
        
        if sats[0] == '&':
            if isinstance(sats[1], str):
                unsat += 1
            elif not isinstance(sats[1], int):
                (p,u) = self.count_percent(sats[1])
                potsat += p - 1
                unsat += u
            if isinstance(sats[2], str):
                unsat += 1
            elif not isinstance(sats[2], int):
                (p,u) = self.count_percent(sats[2])
                potsat += p - 1
                unsat += u
        else:
            if isinstance(sats[1], str) and isinstance(sats[2], str):
                unsat += 1
                
            if not isinstance(sats[1], int) and not isinstance(sats[1], str):
                (p,u) = self.count_percent(sats[1])
                potsat += p - 1
                unsat += u
                
            if not isinstance(sats[2], int) and not isinstance(sats[2], str):
                (p,u) = self.count_percent(sats[2])
                potsat += p - 1
                unsat += u

        return (potsat,unsat)
        
    # tree representation of the course satisfaction
    def sat_tree(self, selections, requirements):
        conn = requirements[0]
        lhs = False
        rhs = False
        # check connector to determine behaviour
        if conn == '&':
            # if side is string, then we check if course list satisfies
            if isinstance(requirements[1], str):
                # check if the selections contains the string
                if requirements[1] in selections:
                    # set to true and remove it
                    lhs = True
                    selections.remove(requirements[1])
                    requirements[1] = 1
            else:
                # if not a string, recurse down as it's a subtree
                (lhs,selections,rr) = self.sat_tree(selections, requirements[1])
                # update sat subtree
                requirements[1] = rr
            
            # if side is string, then we check if course list satisfies
            if isinstance(requirements[2], str):
                # check if the selections contains the string
                if requirements[2] in selections:
                    # set to true and remove it
                    rhs = True
                    selections.remove(requirements[2])
                    requirements[2] = 1
            else:
                # if not a string, recurse down as it's a subtree
                (rhs,selections,rr) = self.sat_tree(selections, requirements[2])
                # update sat subtree
                requirements[2] = rr
            
            # return true up iff both lhs and rhs satisfied
            return (lhs and rhs, selections, requirements)
        else:
            # if side is string, then we check if course list satisfies
            if isinstance(requirements[1], str):
                # check if the selections contains the string
                if requirements[1] in selections:
                    # set to true and remove it
                    lhs = True
                    selections.remove(requirements[1])
                    requirements[1] = 1
            else:
                # if not a string, recurse down as it's a subtree
                (lhs,selections,rr) = self.sat_tree(selections, requirements[1])
                # udpate sat subtree
                requirements[1] = rr
                
            # if lhs is True immediately return out
            if lhs:
                requirements[2] = 1
                return (lhs, selections, requirements)
            
            # if side is string, then we check if course list satisfies
            if isinstance(requirements[2], str):
                # check if the selections contains the string
                if requirements[2] in selections:
                    # set to true and remove it
                    rhs = True
                    selections.remove(requirements[2])
                    requirements[2] = 1
            else:
                # if not a string, recurse down as it's a subtree
                (rhs,selections,rr) = self.sat_tree(selections, requirements[2])
                requirements[2] = rr
            
            # return true up iff one of lhs or rhs satisfied
            return (lhs or rhs, selections, requirements)
        
    # attempts to satisfy all requirements one at a time using the selections.
    # built sat_tree function off of this, this is not needed now?
    def satisfy(self, selections, requirements):
        conn = requirements[0]
        lhs = False
        rhs = False
        # check connector to determine behaviour
        if conn == '&':
            # if side is string, then we check if course list satisfies
            if isinstance(requirements[1], str):
                # check if the selections contains the string
                if requirements[1] in selections:
                    # set to true and remove it
                    lhs = True
                    selections.remove(requirements[1])
            else:
                # if not a string, recurse down as it's a subtree
                (lhs,selections) = self.satisfy(selections, requirements[1])
            
            # if side is string, then we check if course list satisfies
            if isinstance(requirements[2], str):
                # check if the selections contains the string
                if requirements[2] in selections:
                    # set to true and remove it
                    rhs = True
                    selections.remove(requirements[2])
            else:
                # if not a string, recurse down as it's a subtree
                (rhs,selections) = self.satisfy(selections, requirements[2])
            
            # return true up iff both lhs and rhs satisfied
            return (lhs and rhs, selections)
        else:
            # if side is string, then we check if course list satisfies
            if isinstance(requirements[1], str):
                # check if the selections contains the string
                if requirements[1] in selections:
                    # set to true and remove it
                    lhs = True
                    selections.remove(requirements[1])
            else:
                # if not a string, recurse down as it's a subtree
                (lhs,selections) = self.satisfy(selections, requirements[1])
                
            # if lhs is True immediately return out
            if lhs:
                return (lhs, selections)
            
            # if side is string, then we check if course list satisfies
            if isinstance(requirements[2], str):
                # check if the selections contains the string
                if requirements[2] in selections:
                    # set to true and remove it
                    rhs = True
                    selections.remove(requirements[2])
            else:
                # if not a string, recurse down as it's a subtree
                (rhs,selections) = self.satisfy(selections, requirements[2])
            
            # return true up iff one of lhs or rhs satisfied
            return (lhs or rhs, selections)

    # builds a tree-ish structure from the program requirements
    def traverse_reqs(self,req):
        array_out = []
        array_out.append('&' if req.logic_connector == Requirement.AND else '|')
        if req.req_1_type == Requirement.COURSE:
            array_out.append(Course.objects.filter(course_id=req.req_1_id).first().course_code)
        elif req.req_1_type == Requirement.REQUIREMENT:
            array_out.append(self.traverse_reqs(Requirement.objects.filter(requirement_id=req.req_1_id).first()))
        
        if req.req_2_type == Requirement.COURSE:
            array_out.append(Course.objects.filter(course_id=req.req_2_id).first().course_code)
        elif req.req_2_type == Requirement.REQUIREMENT:
            array_out.append(self.traverse_reqs(Requirement.objects.filter(requirement_id=req.req_2_id).first()))

        return array_out