from django.test import TestCase
from django.test.client import Client
from .models import *

import json


class TestGetCourse(TestCase):
    """
    Gets data for a single course
    """

    def setUp(self):
        self.client = Client()
        Course.objects.create(
                        course_id=3,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

    def test_get_course(self):
        response = self.client.get('/api/GetCourseDetails/?courseid=3')
        data = dict(json.loads(response.content))
        self.assertEqual(data['courseCode'], "CHEM 1A03")
        self.assertEqual(data['courseName'], "Chemistry Course")
        self.assertEqual(data['courseDesc'], "description")

class TestNoCourse(TestCase):
    """
    Gets data for an invalid course
    """

    def setUp(self):
        self.client = Client()
        Course.objects.create(
                        course_id=3,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

    def test_get_course(self):
        response = self.client.get('/api/GetCourseDetails/?courseid=1')
        data = dict(json.loads(response.content))
        self.assertEqual(data['error'], "Invalid Course ID")


class TestNoCalc(TestCase):
    """
    There is no Calculator created or specified
    """

    def setUp(self):
        self.client = Client()

    def test_no_data_get(self):
        response = self.client.get('/api/GetCourseData/')
        data = dict(json.loads(response.content))
        self.assertEqual(data["error"], "no such calc_id exists")


class TestCalculator(TestCase):
    """
    Gets all courses for a calculator which has 2 courses and 1 program
    """

    def setUp(self):
        self.client = Client()

        # Create two courses
        c1 = Course.objects.create(
                        course_id=1,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

        c2 = Course.objects.create(
                        course_id=2,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

        p1 = Program.objects.create(
                        program_id=1,
                        name="Program",
                        desc="NA")

        c = Calculator.objects.create(
                        calculator_id=1,
                        title="test calc")

        c.courses.add(c1)
        c.courses.add(c2)
        c.programs.add(p1)


    def test_get_course(self):
        response = self.client.get('/api/GetCourseData/?calc_id=1')
        data = dict(json.loads(response.content))
        self.assertEqual(data, {'calcTitle': 'test calc',
                'courseLists': {'Spring': {},
                                                'Summer': {'Chemistry': [{'courseID': 1, 'courseCode': 'CHEM 1A03', 'courseName': 'Chemistry Course', 'courseDesc': 'description'},
                                                                {'courseID': 2, 'courseCode': 'CHEM 1A03', 'courseName': 'Chemistry Course', 'courseDesc': 'description'}]},
                                                'Fall': {'Chemistry': [{'courseID': 1, 'courseCode': 'CHEM 1A03', 'courseName': 'Chemistry Course', 'courseDesc': 'description'},
                                                                {'courseID': 2, 'courseCode': 'CHEM 1A03', 'courseName': 'Chemistry Course', 'courseDesc': 'description'}]},
                                                'Winter': {}}})

class TestCalculator(TestCase):
    """
    Gets all courses for a calculator which has nothing!
    """

    def setUp(self):
        self.client = Client()

        c = Calculator.objects.create(
                        calculator_id=2,
                        title="test calc")

    def test_get_course(self):
        response = self.client.get('/api/GetCourseData/?calc_id=2')
        data = dict(json.loads(response.content))
        self.assertEqual(data, {'calcTitle': 'test calc',
                'courseLists': {'Spring': {},
                                                'Summer': {},
                                                'Fall': {},
                                                'Winter': {}}})

class TestCalculation(TestCase):
    """
    Tests a program with 100% completition
    """

    def setUp(self):
        self.client = Client()
        c1 = Course.objects.create(
                        course_id=1,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")
        p1 = Program.objects.create(
                        program_id=1,
                        name="Program",
                        desc="NA")
        c = Calculator.objects.create(
                        calculator_id=1,
                        title="test calc")

        clist = CourseList(name="test")
        clist.save()
        rg = RequirementGroup(order=1)
        rg.save()
        ri = RequirementItem(parent_group=rg, req_units=3, req_list=clist)
        ri.save()

        clist.courses.add(c1)
        c.courses.add(c1)
        c.programs.add(p1)
        p1.requirements.add(rg)

    def test_complete_program(self):
        data = {"selections" : [1], "calc_id": 1}
        response = self.client.post('/api/SubmitCourseSelections/',
                                                                json.dumps(data),
                                                                content_type="application/json")
        data = dict(json.loads(response.content))
        # We should be 100% eligible for the program
        self.assertEqual(data, {"matchedPrograms": [
                                                                        {"programName": "Program",
                                                                         "programDescription": "NA",
                                                                         "programId": 1,
                                                                         "programPercentage": 1.0,
                                                                         "programRequirements":
                                                                         {"requirements": ["3 units of CHEM 1A03"]},
                                                                         "fulfilledCourses": [["CHEM 1A03"]]}]})

class Test0PercentProgram(TestCase):
    """
    Tests a program with 0% completition
    """

    def setUp(self):
        self.client = Client()
        c1 = Course.objects.create(
                        course_id=1,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")
        c2 = Course.objects.create(
                        course_id=5,
                        code="CHEM 1AA3",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")
        p1 = Program.objects.create(
                        program_id=1,
                        name="Program",
                        desc="NA")
        c = Calculator.objects.create(
                        calculator_id=1,
                        title="test calc")

        clist = CourseList(name="test")
        clist.save()
        rg = RequirementGroup(order=1)
        rg.save()
        ri = RequirementItem(parent_group=rg, req_units=3, req_list=clist)
        ri.save()

        clist.courses.add(c2)
        c.courses.add(c1)
        c.programs.add(p1)
        p1.requirements.add(rg)

    def test_noncomplete_program(self):
        data = {"selections" : [1], "calc_id": 1}
        response = self.client.post('/api/SubmitCourseSelections/',
                                                                json.dumps(data),
                                                                content_type="application/json")
        data = dict(json.loads(response.content))
        # We should be 0% eligible for the program
        self.assertEqual(data['matchedPrograms'][0]['programPercentage'], 0)


class Test50PercentProgram(TestCase):
    """
    Tests a program with 50% completition
    """

    def setUp(self):
        self.client = Client()
        c1 = Course.objects.create(
                        course_id=1,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")
        c2 = Course.objects.create(
                        course_id=5,
                        code="CHEM 1AA3",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

        p1 = Program.objects.create(
                        program_id=1,
                        name="Program",
                        desc="NA")
        c = Calculator.objects.create(
                        calculator_id=1,
                        title="test calc")

        clist = CourseList(name="test")
        clist.save()
        rg = RequirementGroup(order=1)
        rg.save()
        ri = RequirementItem(parent_group=rg, req_units=6, req_list=clist)
        ri.save()

        clist.courses.add(c2)
        clist.courses.add(c1)
        c.courses.add(c1)
        c.programs.add(p1)
        p1.requirements.add(rg)

    def test_complete_program(self):
        data = {"selections" : [1], "calc_id": 1}
        response = self.client.post('/api/SubmitCourseSelections/',
                                                                json.dumps(data),
                                                                content_type="application/json")
        data = dict(json.loads(response.content))
        # We should be 0% eligible for the program
        self.assertEqual(data['matchedPrograms'][0]['programPercentage'], 0.5)


class Test2ReqGroupProgram(TestCase):
    """
    Tests a program with two requirement groups
    """

    def setUp(self):
        self.client = Client()
        c1 = Course.objects.create(
                        course_id=1,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")
        c2 = Course.objects.create(
                        course_id=5,
                        code="CHEM 1AA3",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

        p1 = Program.objects.create(
                        program_id=1,
                        name="Program",
                        desc="NA")
        c = Calculator.objects.create(
                        calculator_id=1,
                        title="test calc")

        clist = CourseList(name="test")
        clist.save()
        rg = RequirementGroup(order=1)
        rg.save()
        ri = RequirementItem(parent_group=rg, req_units=3, req_list=clist)
        ri.save()

        clist2 = CourseList(name="test")
        clist2.save()
        rg2 = RequirementGroup(order=1)
        rg2.save()
        ri2 = RequirementItem(parent_group=rg2, req_units=3, req_list=clist2)
        ri2.save()

        clist.courses.add(c1)
        clist2.courses.add(c2)
        c.courses.add(c1)
        c.courses.add(c2)
        c.programs.add(p1)
        p1.requirements.add(rg)
        p1.requirements.add(rg2)

    def test_complete_program(self):
        data = {"selections" : [1, 5], "calc_id": 1}
        response = self.client.post('/api/SubmitCourseSelections/',
                                                                json.dumps(data),
                                                                content_type="application/json")
        data = dict(json.loads(response.content))
        # We should be 0% eligible for the program
        self.assertEqual(data['matchedPrograms'][0]['programPercentage'], 1)


class Test2ReqItemProgramAND(TestCase):
    """
    Tests a program with a single requirement group but two requirement items with an AND
    """

    def setUp(self):
        self.client = Client()
        c1 = Course.objects.create(
                        course_id=1,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")
        c2 = Course.objects.create(
                        course_id=5,
                        code="CHEM 1AA3",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

        p1 = Program.objects.create(
                        program_id=1,
                        name="Program",
                        desc="NA")
        c = Calculator.objects.create(
                        calculator_id=1,
                        title="test calc")

        clist = CourseList(name="test")
        clist.save()
        clist2 = CourseList(name="test")
        clist2.save()

        rg = RequirementGroup(order=1)
        rg.save()
        ri = RequirementItem(parent_group=rg, req_units=3, req_list=clist)
        ri.save()
        ri2 = RequirementItem(connector=0, parent_group=rg, req_units=3, req_list=clist2)
        ri2.save()

        clist.courses.add(c1)
        clist2.courses.add(c2)
        c.courses.add(c1)
        c.courses.add(c2)
        c.programs.add(p1)
        p1.requirements.add(rg)

    def test_complete_program(self):
        data = {"selections" : [1, 5], "calc_id": 1}
        response = self.client.post('/api/SubmitCourseSelections/',
                                                                json.dumps(data),
                                                                content_type="application/json")
        data = dict(json.loads(response.content))
        # We should be 100% eligible for the program
        self.assertEqual(data['matchedPrograms'][0]['programPercentage'], 1)

class Test2ReqItemProgramAND50(TestCase):
    """
    Tests a program with a single requirement group but two requirement items with an AND
    But only 1 portion of the equation is satisified -> 50%
    C1 AND C2 but only given C1
    """

    def setUp(self):
        self.client = Client()
        c1 = Course.objects.create(
                        course_id=1,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")
        c2 = Course.objects.create(
                        course_id=5,
                        code="CHEM 1AA3",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

        p1 = Program.objects.create(
                        program_id=1,
                        name="Program",
                        desc="NA")
        c = Calculator.objects.create(
                        calculator_id=1,
                        title="test calc")

        clist = CourseList(name="test")
        clist.save()
        clist2 = CourseList(name="test")
        clist2.save()

        rg = RequirementGroup(order=1)
        rg.save()
        ri = RequirementItem(parent_group=rg, req_units=3, req_list=clist)
        ri.save()
        ri2 = RequirementItem(connector=0, parent_group=rg, req_units=3, req_list=clist2)
        ri2.save()

        clist.courses.add(c1)
        clist2.courses.add(c2)
        c.courses.add(c1)
        c.courses.add(c2)
        c.programs.add(p1)
        p1.requirements.add(rg)

    def test_complete_program(self):
        data = {"selections" : [1], "calc_id": 1}
        response = self.client.post('/api/SubmitCourseSelections/',
                                                                json.dumps(data),
                                                                content_type="application/json")
        data = dict(json.loads(response.content))
        # We should be 50% eligible for the program
        self.assertEqual(data['matchedPrograms'][0]['programPercentage'], 0.5)

class Test2ReqItemProgramOR(TestCase):
    """
    Tests a program with a single requirement group but two requirement items with an OR
    But only 1 portion of the equation is satisified -> 100%
    C1 OR C2 but only given C1
    """

    def setUp(self):
        self.client = Client()
        c1 = Course.objects.create(
                        course_id=1,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")
        c2 = Course.objects.create(
                        course_id=5,
                        code="CHEM 1AA3",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

        p1 = Program.objects.create(
                        program_id=1,
                        name="Program",
                        desc="NA")
        c = Calculator.objects.create(
                        calculator_id=1,
                        title="test calc")

        clist = CourseList(name="test")
        clist.save()
        clist2 = CourseList(name="test")
        clist2.save()

        rg = RequirementGroup(order=1)
        rg.save()
        ri = RequirementItem(parent_group=rg, req_units=3, req_list=clist)
        ri.save()
        ri2 = RequirementItem(connector=1, parent_group=rg, req_units=3, req_list=clist2)
        ri2.save()

        clist.courses.add(c1)
        clist2.courses.add(c2)
        c.courses.add(c1)
        c.courses.add(c2)
        c.programs.add(p1)
        p1.requirements.add(rg)

    def test_complete_program(self):
        data = {"selections" : [1], "calc_id": 1}
        response = self.client.post('/api/SubmitCourseSelections/',
                                                                json.dumps(data),
                                                                content_type="application/json")
        data = dict(json.loads(response.content))
        # We should be 100% eligible for the program
        self.assertEqual(data['matchedPrograms'][0]['programPercentage'], 1)

class TestSameCourseCannotBeUsed(TestCase):
    """
    Two Requirement Groups. Must make sure the same course cannot be used twice
    Requirement #1 -> Needs C1
    Requirement #2 -> Also needs C1
    given C1, you should only be satsifying Req1 => 50%
    """

    def setUp(self):
        self.client = Client()
        c1 = Course.objects.create(
                        course_id=1,
                        code="CHEM 1A03",
                        name="Chemistry Course",
                        desc="description",
                        offered_fall=True,
                        offered_winter=False,
                        offered_summer=True,
                        offered_spring=False,
                        units=3,
                        department="Chemistry")

        p1 = Program.objects.create(
                        program_id=1,
                        name="Program",
                        desc="NA")
        c = Calculator.objects.create(
                        calculator_id=1,
                        title="test calc")

        clist = CourseList(name="test")
        clist.save()
        rg = RequirementGroup(order=1)
        rg.save()
        ri = RequirementItem(parent_group=rg, req_units=3, req_list=clist)
        ri.save()

        clist2 = CourseList(name="test")
        clist2.save()
        rg2 = RequirementGroup(order=1)
        rg2.save()
        ri2 = RequirementItem(parent_group=rg2, req_units=3, req_list=clist2)
        ri2.save()

        clist.courses.add(c1)
        clist2.courses.add(c1)
        c.courses.add(c1)
        c.programs.add(p1)
        p1.requirements.add(rg)
        p1.requirements.add(rg2)

    def test_complete_program(self):
        data = {"selections" : [1], "calc_id": 1}
        response = self.client.post('/api/SubmitCourseSelections/',
                                                                json.dumps(data),
                                                                content_type="application/json")
        data = dict(json.loads(response.content))
        # We should be 100% eligible for the program
        self.assertEqual(data['matchedPrograms'][0]['programPercentage'], 0.5)
