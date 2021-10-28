import requests
import json
import time

# few things we need to get from the API:
# 1. need to get all undergrad courses. This can be done by iterating over all UGRD plans, inspecting requirements groups -> inspecting courselists -> inspecting courses.
# 2. need to get all courselists. each courselist has an ID and includes a group of courses.
# 3. need to get all requirements. each set of requirements is built from courselists.
# 4. need to get all programs (aka plans), each plan has its own ID.

# probably easiest to store all plans in one list, then iterate down and build up the other pieces.

# GLOBAL VARIABLES
clientId = '49c9205d5d15312e85e3c0f07af77ad4'
headers = {
    'X-IBM-Client-Id': clientId,
    'accept': "application/json"
}
reqGroups = None
courseListDict = {}
courseCatalogSearchDict = {}

def sanitizeLink(link):
    # old api: https://apis.mcmaster.ca/mcmaster-university/production/academy/

    return link.replace('https://academic-map-service-academic-map.apps.ocp.mcmaster.ca/', 'https://academic-map.apps.ocpprd01.mcmaster.ca/')

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

    # Currently no endpoint for get all courses

    all_courses = {}
    print("COURSE LIST")
    print("-------------")
    print(courselist)
    if not 'courseListItems' in courselist:
        try:
            print("No course for course list", courselist['code'])
        except:
            print("Error", courselist)
        return ('', {})
    for course in courselist['courseListItems']:
    
    # next((link['href'] for link in itemDetail['links'] if link['rel'] == 'courseList'), None)
        link = next((link['href'] for link in course['links'] if link['rel'] == 'courseCatalogSearch'), None)
        newLink = sanitizeLink(link)
        
        # create dictionary of links so that no duplicate api calls are made
        global courseCatalogSearchDict
        if newLink not in courseCatalogSearchDict:
            print("add to courseCatalogSearchDict")
            req = requests.get(newLink, headers=headers)
            courseCatalogSearchDict[newLink] = req.json()
        else:
            print("Found courseCatalogSearchDict in dict")
            
        coursedata = courseCatalogSearchDict[newLink]
        
        # TODO create dictionary of links so that no duplicate API calls are made
        #req = requests.get(newLink, headers=headers)
        #if int(req.status_code) not in range(200,300):
        #    print ("Failed to make API call for course catalog info.")
        #    continue
        #coursedata = req.json()
        # get the course info that's relevant
        if not 'content' in coursedata:
            selfHref = next((link['href'] for link in coursedata['links'] if link['rel'] == 'self'), None)
            print ("Course data contains no offerings", selfHref)
            continue
        for offering in coursedata['content']:
            cid = offering['code']
            code = offering['subjectCode'] + " " + offering['catalogNumber']
            name = (offering['shortDescription'] if 'shortDescription' in offering else "")
            desc = (offering['description'] if 'description' in offering else "")
            all_courses[cid] = {
                'code': code,
                'name': name,
                'desc': desc,
                'units': 3
                # TODO: units not provided
            }
    return (courselist['code'], all_courses)

# extracts a list of courselists from requirement group data.
# returns a triple; first element is a structure representing program requirements, second element in the tuple is the courselist data, third element is the list of courses.
def extract_courselists(group):

    # Currently no get all endpoint is provided for courselists

    all_courses = {}
    all_courselists = {}
    if not 'requirements' in group:
        selfHref = next((link['href'] for link in group['links'] if link['rel'] == 'self'), None)
        print("No requirements for requirements group", selfHref)
        return ([], {}, {})
    # go over each requirement
    overall_reqs = []
    for requirement in group['requirements']:
        item_reqs = []
        if not 'requirementItems' in requirement:
            selfHref = next((link['href'] for link in group['links'] if link['rel'] == 'self'), None)
            print("No requirement items for requirement group ", requirement['code'], " in group", selfHref)
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
            
            description = (item['description'] if 'description' in item else '')
            shortDescription = (item['shortDescription'] if 'shortDescription' in item else '')
            
            # take a look at each item detail
            # maintain a record for the requirements for this item
            reqs = []
            for itemDetail in item['itemDetails']:
                # possible itemDetailTypes: Course List, Derived Course List, ...?
                if itemDetail['itemDetailType'] == "Course List":
                    # get the link to the actual courselist                    
                    courseLink = next((link['href'] for link in itemDetail['links'] if link['rel'] == 'courseList'), None)
                    newLink = sanitizeLink(courseLink)
                    
                    # create dictionary of links so that no duplicate api calls are made
                    global courseListDict
                    if newLink not in courseListDict:
                        print("add to courseListDict")
                        req = requests.get(newLink, headers=headers)
                        try:
                            courseListDict[newLink] = req.json()
                        except:
                            print("Invalid JSON response from API")
                            break;
                    else:
                        print("Found courselist in dict")
                        
                    courselist = courseListDict[newLink]
                        
                    # read it
                    #req = requests.get(newLink, headers=headers)
                    #print('-------')
                    #print(req)
                    #if int(req.status_code) not in range(200,300):
                    #    print ("Failed to make API call for course list.")
                    #    continue
                    #try:
                    #    courselist = req.json()
                    #except:
                    #    print ("Invalid JSON response from API")
                    
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
            item_reqs.append({'type': (item['connector'] if 'connector' in item else ' '), 'reqs': reqs, 'minCourse': minCourse, 'maxCourse': maxCourse, 'minUnits': minUnit, 'maxUnits': maxUnit, 'description': description, 'shortDescription': shortDescription})
        overall_reqs.append({'type': (requirement['connector'] if 'connector' in requirement else ' '), 'reqs': item_reqs})
    return (overall_reqs, all_courselists, all_courses)

# finds the requirements for a program based on the link to its requirement groups.
def find_requirements(program):

    # TODO calling get all endpoint. Should store all values in a variable and just search it each time instead of repeatedly calling it
    #reqGroupResult = requests.get("https://academic-map.apps.ocpprd01.mcmaster.ca/requirementGroups", headers=headers)
    #if int(reqGroupResult.status_code) not in range(200,300):
    #    print("Failed to make API call for requirement groups.")
    #    return ([], {}, {})
    
    #reqGroupsJson = reqGroupResult.json()["content"]
    req = None
    
    # TODO: not handling cases with multiple requirement groups, should just be joining together? idk
    for reqGroup in reqGroups:
        rglink = next((link['href'] for link in reqGroup['links'] if link['rel'] == 'plan'), None)

        if rglink != None and program[2] in rglink:
            req = reqGroup
            break

    # get requirements groups
    #reqlink = program[1].replace('https://academic-map-service-academic-map.apps.ocp.mcmaster.ca/', 'https://academic-map.apps.ocpprd01.mcmaster.ca/')
    #req = requests.get(reqlink, headers=headers)
    #if int(req.status_code) not in range(200,300):
    #    print ("Failed to make API call for requirement groups.")
    #    return ([], {}, {})
    #reqgroups = req.json()
    
    #reqgroups = req
    
    # check that requirement groups actually exist, some joint programs seem not to have any.
    if req == None:
        print("No requirement groups for program", program[0])
        return ([], {}, {})
    
    print('EXTRACT COURSE LISTS')
    print('--------')
    print(req)
    (r,cl,c) = extract_courselists(req)
    
    
    ### TODO MIGHT NOT NEED TO DO THIS
    ### seems they changed the get all endpoint to include all data
    # open each individual requirement group
    #for rg in reqgroups['content']:
    #    rglink = next((link['href'] for link in rg['links'] if link['rel'] == 'self'), None)
    #    newLink = sanitizeLink(rglink)
    #    # rglink = rg['links']['self']['href']
    #    # time.sleep(38)
    #    req = requests.get(newLink, headers=headers)
    #    if int(req.status_code) not in range(200,300):
    #        print ("Failed to make API call for requirement group.")
    #        continue
    #    group = req.json()
    #    
    #    rgList = rgList + [group]
    #    # extract all the courselists from the requirement group
    #    (r,cl,c) = extract_courselists(group)
        
    # TODO remove this
    # json.dump(rgList, open("rgTEST.json", 'w'), indent=4)
    
    return (r,cl,c)

def get_programdata():
    all_programs = {}
    # retrieve base API data
    req = requests.get("https://academic-map.apps.ocpprd01.mcmaster.ca/", headers=headers)
    # req = requests.get("http://academic-map-service-academic-map.apps.ocp.mcmaster.ca/")
    if int(req.status_code) not in range(200,300):
        print ("Failed to make initial API call.")
        print(req)
        # return
    apidata = req.json()
    # get link to plans
    print("Retrieving all plans...")
    req = requests.get("https://academic-map.apps.ocpprd01.mcmaster.ca/plans", headers=headers)
    # req = requests.get(apidata['_links']['plans']['href'])
    if int(req.status_code) not in range(200,300):
        print ("Failed to make API call for program data.")
        return
    print("Plans retrieved")
    programdata = req.json()
    # iterate over all programs, find the ones that are in the UGRD career, and put them into a list of programs.
    # TODO add ability to only get stuff by faculty
    for program in programdata['content']:
        if program['program']['career']['code'] == "UGRD" and program['program']['faculty']['code'] == "02":
            # for now store both the description (= program name) and the req groups link as a tuple
            # this can be filtered later
            # all_programs[program['code']] = program
            all_programs[program['code']] = (program['description'], next((link['href'] for link in program['links'] if link['rel'] == 'requirementGroups'), None), program["code"])
            # all_programs[program['code']] = (program['description'], program['links']['requirementGroups']['href'])
    # print programs out to a file
    json.dump(all_programs, open("programs.json", 'w'), indent=4)
    
    print('Created programs.json')
    
    print("Retrieving all requirement groups...")
    # create requirementGroups list for use later
    reqGroupResult = requests.get("https://academic-map.apps.ocpprd01.mcmaster.ca/requirementGroups", headers=headers)
    if int(reqGroupResult.status_code) not in range(200,300):
        print("Failed to make API call for requirement groups.")
        return
    
    global reqGroups
    reqGroups = reqGroupResult.json()["content"]
    print("Requirement groups retrieved")
    json.dump(reqGroups, open("rgListTest.json", 'w'), indent=4)
    
    # TODO might need to still run this func to get proper formatted object
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
        
        print("Found all requirements for ", program[0])
        #print(r)
        #print(cl)
        #print(c)

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
        
        # wait to not hit 100 calls/hr api limit
        # 1 call every 38secs = ~94 calls per hour
        # time.sleep(38)
    
    
    # add the -1 courselist to reperesent all undegrad courses, as generated
    all_courselists['-1'] = [c_ for c_ in all_courses]
    all_courselists['-2'] = []
    # TODO change to dump into backend/data folder
    json.dump(all_courses, open("courses.json", 'w'), indent=4)
    json.dump(all_courselists, open("course_list.json", 'w'), indent=4)
    # now, process requirements
    for r in reqs:
        fr = process_requirements(reqs[r], all_courselists, all_courses)
        all_requirements[r] = fr
    json.dump(all_requirements, open("requirements.json", 'w'), indent=4)

if __name__ == "__main__":
    get_programdata()
