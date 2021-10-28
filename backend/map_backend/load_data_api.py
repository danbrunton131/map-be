import requests
import json

# few things we need to get from the API:
# 1. need to get all undergrad courses. This can be done by iterating over all UGRD plans, inspecting requirements groups -> inspecting courselists -> inspecting courses.
# 2. need to get all courselists. each courselist has an ID and includes a group of courses.
# 3. need to get all requirements. each set of requirements is built from courselists.
# 4. need to get all programs (aka plans), each plan has its own ID.

# probably easiest to store all plans in one list, then iterate down and build up the other pieces.

# processes the complex-form requirements into a form which is easier to insert into the DB.
def process_requirements(reqs, lists, courses):
    # top level: each high-level group
    final_reqs = []
    for group in reqs:
        final_counts = []
        # mid-level: each item in the group, this level specifies the unit counts, course counts
        for item in group['reqs']:
            # bottom-level: builds a course requirement from course lists.
            final_cl = []
            for req in item['reqs']:
                # type can be several options: Base = base list, Intersection with = AND, Subtract from = NOT IN,....
                if req['type'] == 'Base':
                    final_cl = lists[str(req['list'])]
                elif req['type'] == 'Intersection with':
                    final_cl = [c for c in final_cl if c in lists[str(req['list'])]]
                elif req['type'] == 'Subtract from':
                    final_cl = [c for c in final_cl if c not in lists[str(req['list'])]]
                elif req['type'] == 'Union with':
                    final_cl = final_cl + lists[str(req['list'])]
            final_counts.append({'list': final_cl, 'minCourse': item['minCourse'], 'maxCourse': item['maxCourse'], 'minUnits': item['minUnits'], 'maxUnits': item['maxUnits'], 'connector': item['type']})
        final_reqs.append({'reqs': final_counts, 'connector': group['type']})
    return final_reqs

# extracts a list of courses from courselist data.
# returns a tuple of the courselist ID, and a dictionary mapping course IDs to courses found in the specific list.
def extract_courses(courselist):
    all_courses = {}
    if not 'courseListItems' in courselist:
        print("No courses for course list", courselist['_links']['self']['href'])
        return ('', {})
    for course in courselist['courseListItems']:
        link = course['_links']['courseCatalogSearch']['href']
        req = requests.get(link, verify=False)
        if int(req.status_code) not in range(200,300):
            print ("Failed to make API call for course catalog info.")
            continue
        coursedata = req.json()
        # get the course info that's relevant
        if not '_embedded' in coursedata or not 'courseOfferings' in coursedata['_embedded']:
            print ("Course data contains no offerings", coursedata['_links']['self']['href'])
            continue
        for offering in coursedata['_embedded']['courseOfferings']:
            cid = offering['code']
            code = offering['subjectCode'] + " " + offering['catalogNumber']
            name = (offering['shortDescription'] if 'shortDescription' in offering else "")
            desc = (offering['description'] if 'description' in offering else "")
            all_courses[cid] = {
                'code': code,
                'name': name,
                'desc': desc,
                'units': 3, # TODO: units not provided, assume all 3 units for now
            }
    return (courselist['code'], all_courses)

# extracts a list of courselists from requirement group data.
# returns a triple; first element is a structure representing program requirements, second element in the tuple is the courselist data, third element is the list of courses.
def extract_courselists(group):
    all_courses = {}
    all_courselists = {}
    if not 'requirements' in group:
        print("No requirements for requirements group", group['_links']['self']['href'])
        return ([], {}, {})
    # go over each requirement
    overall_reqs = []
    for requirement in group['requirements']:
        item_reqs = []
        if not 'requirementItems' in requirement:
            print("No requirement items for requirement group", requirement['code'], "in group", group['_links']['self']['href'])
            continue
        # go over each item inside the requirement (multiple items have set logic to form a requirement)
        for item in requirement['requirementItems']:
            if 'creditIncludeMode' not in item or item['creditIncludeMode'] != "Include In All Statistics":
                print("Credits to be verified and not included, impossible to account for")
                continue
            minCourse = (item['minimumCourses'] if 'minimumCourses' in item else 0)
            maxCourse = (item['maximumCourses'] if 'maximumCourses' in item else 0)
            minUnit = (item['minimumUnits'] if 'minimumUnits' in item else 0)
            maxUnit = (item['maximumUnits'] if 'maximumUnits' in item else 0)
            # take a look at each item detail
            # maintain a record for the requirements for this item
            reqs = []
            for itemDetail in item['itemDetails']:
                # possible itemDetailTypes: Course List, Derived Course List, ...?
                if itemDetail['itemDetailType'] == "Course List":
                    # get the link to the actual courselist
                    courselink = itemDetail['_links']['courseList']['href']
                    # read it
                    req = requests.get(courselink, verify=False)
                    if int(req.status_code) not in range(200,300):
                        print ("Failed to make API call for course list.")
                        continue
                    try:
                        courselist = req.json()
                    except:
                        print ("Invalid JSON response from API")
                    # get all the courses out of the list
                    c = extract_courses(courselist)
                    # append to the full list of courses
                    for c_ in c[1]:
                        if not c_ in all_courses:
                            all_courses[c_] = c[1][c_]
                    # map the courses found in this courselist to the courselist id
                    all_courselists[c[0]] = [x for x in c[1]]
                    # update the requirements for this item
                    reqs.append({'type': (itemDetail['listIncludeMode'] if 'listIncludeMode' in itemDetail else 'Base'), 'list': c[0]})
                elif itemDetail['itemDetailType'] == "Derived Course List":
                    listItem = -1
                    # check listRecallMode to see what this course list is derived from
                    # different derived courselists receive different NEGATIVE list IDs. we can then process these at the very end.
                    if itemDetail['listRecallMode'] == "Courses in Target Career":
                        listItem = -1
                    elif itemDetail['listRecallMode'] == "Grade Category":
                        listItem = -2
                    # just append this in
                    reqs.append({'type': (itemDetail['listIncludeMode'] if 'listIncludeMode' in itemDetail else 'Base'), 'list': listItem})
            item_reqs.append({'type': (item['connector'] if 'connector' in item else ' '), 'reqs': reqs, 'minCourse': minCourse, 'maxCourse': maxCourse, 'minUnits': minUnit, 'maxUnits': maxUnit})
        overall_reqs.append({'type': (requirement['connector'] if 'connector' in requirement else ' '), 'reqs': item_reqs})
    return (overall_reqs, all_courselists, all_courses)

# finds the requirements for a program based on the link to its requirement groups.
def find_requirements(program):
    # get requirements groups
    reqlink = program[1]
    req = requests.get(reqlink, verify=False)
    if int(req.status_code) not in range(200,300):  
        print ("Failed to make API call for requirement groups.")
        return ([], {}, {})
    reqgroups = req.json()
    # check that requirement groups actually exist, some joint programs seem not to have any.
    if not '_embedded' in reqgroups or not 'requirementGroups' in reqgroups['_embedded']:
        print("No requirement groups for program", program[0])
        return ([], {}, {})
    # open each individual requirement group
    for rg in reqgroups['_embedded']['requirementGroups']:
        rglink = rg['_links']['self']['href']
        req = requests.get(rglink, verify=False)
        if int(req.status_code) not in range(200,300):
            print ("Failed to make API call for requirement group.")
            continue
        group = req.json()
        # extract all the courselists from the requirement group
        (r,cl,c) = extract_courselists(group)
    # TODO: not handling cases with multiple requirement groups, should just be joining together? idk
    return (r,cl,c)

def get_programdata():
    all_programs = {}
    # retrieve base API data
    # TODO REMOVE verify=False on production,
    # I think it errors because i'm on a vpn
    req = requests.get("http://academic-map-service-academic-map.apps.ocp.mcmaster.ca/", verify=False)
    if int(req.status_code) not in range(200,300):
        print ("Failed to make initial API call.")
        return
    apidata = req.json()
    # get link to plans
    # TODO REMOVE verify=False on production
    req = requests.get(apidata['_links']['plans']['href'], verify=False)
    if int(req.status_code) not in range(200,300):
        print ("Failed to make API call for program data.")
        return
    programdata = req.json()
    # iterate over all programs, find the ones that are in the UGRD career, and put them into a list of programs.
    for program in programdata['_embedded']['plans']:
        if program['program']['career']['code'] == "UGRD":
            # for now store both the description (= program name) and the req groups link as a tuple
            # this can be filtered later
            all_programs[program['code']] = (program['description'], program['_links']['requirementGroups']['href'])
    # print programs out to a file
    json.dump(all_programs, open("programs.json", 'w'), indent=4)
    # now that we have all programs in a list, we can work through each program to find its requirements.
    #rq = process_requirements(r, cl, c)
    reqs = {}
    all_courses = {}
    all_courselists = {}
    all_requirements = {}
    # iterate over all programs
    for programname in all_programs:
        program = all_programs[programname]
        # get all requirements, courselists, courses
        (r,cl,c) = find_requirements(program)
        # add courses into the all_courses dict
        for c_ in c:
            if c_ not in all_courses:
                all_courses[c_] = c[c_]
        # add courselists into the all_courselists dict
        for c_ in cl:
            if c_ not in all_courselists:
                all_courselists[c_] = cl[c_]
        # add requirements into temp reqs dict, these require more processing later.
        reqs[programname] = r
    # add the -1 courselist to reperesent all undegrad courses, as generated
    all_courselists['-1'] = [c_ for c_ in all_courses]
    all_courselists['-2'] = []
    json.dump(all_courses, open("courses.json", 'w'), indent=4)
    json.dump(all_courselists, open("course_lists.json", 'w'), indent=4)
    # now, process requirements
    for r in reqs:
        fr = process_requirements(reqs[r], all_courselists, all_courses)
        all_requirements[r] = fr
    json.dump(all_requirements, open("requirements.json", 'w'), indent=4)

if __name__ == "__main__":
    get_programdata()
