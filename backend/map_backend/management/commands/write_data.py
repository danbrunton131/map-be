import bs4, re
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os, json

# catalog ID will change each year and needs to be updated.
CATALOG_ID = 38

# base URLs (should only change in catalog ID each year, everything else adapts)
BASE_URL = "http://m.academiccalendars.romcmaster.ca/mobile_functions.php?catalog={CID}&type=degree&showtypes"
PROGRAM_URL = "http://m.academiccalendars.romcmaster.ca/mobile_functions.php?catalog={CID}&program_id={HID}&page={PAGE}&showprograms"
DETAILS_URL = "http://m.academiccalendars.romcmaster.ca/mobile_functions.php?catalog={CID}&type=program&oid={OID}&showdetails"
SELECTION_URL = "http://m.academiccalendars.romcmaster.ca/mobile_functions.php?catalog={CID}&type=program&oid={OID}&coreid={CORE}&showdetails"
REQ_URL = "http://m.academiccalendars.romcmaster.ca/mobile_functions.php?catalog={CID}&type=program&oid={OID}&coreid={CORE}&showdetails"
COURSE_URL = "http://m.academiccalendars.romcmaster.ca/mobile_functions.php?catalog={CID}&type=course&oid={OID}&showdetails"

# base scraping function, start at the program header (?) level and drill down.
def scrape_headers():
    # dict of program headers
    headers = {}
    # pull the program data
    data = uReq(BASE_URL.format(CID=CATALOG_ID))
    # check status code
    if data.getcode() < 200 or data.getcode() > 299:
        print("Error code received from scraping the academic calendar.")
        exit(-1)
    # read the text of the program header page
    text = data.read()
    # close the stream
    data.close()

    # parse the HTML data
    page_soup = soup(text, 'lxml')
    # retrieve the list items
    hdata = page_soup.findAll('li')

    # iterate through each header
    for h in hdata:
        # get the name of the program header
        name = h.text
        # get the ID to be used in the URL
        id = h.find('a').get('onclick')
        id = id.split("(")[1].split(")")[0]
        # only care about headers starting with bachelor (for now...)
        if name.startswith('Bachelor'):
            headers[name] = id

    # now go through each header and scrape programs
    for h in headers:
        # DEV NOTE: restricted only to bachelor of science for now, since faculties have different admission/requirement setups and some faculties just have 'complete a lvl1 program'.
        if h == 'Bachelor of Science (Honours)':
            print(h)
            scrape_programs(headers[h])

# scrapes programs
def scrape_programs(hid):
    # dict mapping program IDs to names
    programs = {}
    # we want to account for potentially multiple pages.
    page = 1
    while True:
        # track programs from current page
        pprograms = {}
        # pull programs data
        data = uReq(PROGRAM_URL.format(CID=CATALOG_ID, HID=hid, PAGE=page).replace('\'', ''))
        # check status code
        if data.getcode() < 200 or data.getcode() > 299:
            print("Error code received from scraping the academic calendar.")
            exit(-1)
        # read the text of the programs page
        text = data.read()
        # close the stream
        data.close()

        # parse the HTML data
        page_soup = soup(text, 'lxml')
        # retrieve the list items
        pdata = page_soup.findAll('li')

        # iterate over all programs
        for p in pdata:
            # error handling
            if p == None:
                continue
            # get name and ID
            name = p.text
            id = p.find('a')
            # error handling
            if id == None:
                continue
            id = id.get('onclick')
            id = id.split("(")[1].split(")")[0]
            # append ID and name into the current page dict
            # we exclude elements that start+end with 'Show'+'...' as thats just a page link.
            if not name.startswith('Show') and not name.endswith('...'):
                pprograms[id] = name
        # if no contents were added, all pages analyzed
        if pprograms == {}:
            break
        # else, go to next page
        page += 1
        # include into global programs dict for this header
        for p in pprograms:
            programs[p] = pprograms[p]
    # get the details for the programs
    get_details(programs)

# gets details (i.e. reqs) for programs
def get_details(programs):
    # iterate over all the found programs
    for program in programs:
        # pull details data
        data = uReq(DETAILS_URL.format(CID=CATALOG_ID, OID=program).replace('\'', ''))
        # check status code
        if data.getcode() < 200 or data.getcode() > 299:
            print("Error code received from scraping the academic calendar.")
            exit(-1)
        # read the text of the programs page
        text = data.read()
        # close the stream
        data.close()

        # parse the HTML data
        page_soup = soup(text, 'lxml')
        # retrieve the list items
        pdata = page_soup.findAll('li')

        link_id = ''

        reqs = []

        # iterate over the links
        for l in pdata:
            name = l.text
            # we only care about 'Admission'
            if name != 'Admission':
                continue
            # get the link id
            link_id = l.find('a').get('onclick')
            link_id = link_id.split("','")[1].replace("')","")
            break
        # fetch the link info
        if not link_id == '':
            # read the admission links
            uClient = uReq(SELECTION_URL.format(CID=CATALOG_ID, OID=program, CORE=link_id))
            page_html = uClient.read()
            uClient.close()
            page_soup = soup(page_html, 'lxml')
            links = page_soup.findAll('li')

            # iterate over all links
            for link in links:
                # ignore links with non-unit-based requirements.
                if "units" not in link.text:
                    continue
                # get the number of units
                units = link.text
                units = int(units.replace(" units", ""))
                # get the link to the courses which satisfy this link
                link_id = link.find('a').get('onclick')
                link_id = link_id.split(",")[0].split("':'")[1].replace("'", "")
                requirement = {
                    units: get_requirements(program, link_id)
                }
                reqs.append(requirement)
        print(reqs)

# gets courses fulfilling a requirement, given the program and requirement IDs                
def get_requirements(program, req):
    # pull details data
    data = uReq(REQ_URL.format(CID=CATALOG_ID,OID=program,CORE=req))
    # check status code
    if data.getcode() < 200 or data.getcode() > 299:
        print("Error code received from scraping the academic calendar.")
        exit(-1)
    # read the text of the programs page
    text = data.read()
    # close the stream
    data.close()

    # parse the HTML data
    page_soup = soup(text, 'lxml')
    # retrieve the list items
    pdata = page_soup.findAll('li', {"class": "arrow"})

    courses = []
    for link in pdata:
        if "List" in link:
            return ["LIST"]
        course_id = link.find('a').get('onclick')
        course_id = course_id.split("(")[1].split(")")[0]
        courses.append(course_id)
        get_one_course(course_id)

    return courses

courses = {}
# gets details (name+desc) of specific courses.
def get_one_course(course_id):
    uClient = uReq(COURSE_URL.format(CID=CATALOG_ID,OID=course_id))
    page_html = uClient.read()
    uClient.close()

    page_soup = soup(page_html, 'lxml')
    title = page_soup.findAll('h2')
    title = title[0].text
    inside = page_soup.findAll('p')
    units = inside[0].findAll('span', class_='text')[0].text

    try:
        dsrp = inside[1]
    except:
        dsrp = inside[0]

    try:
        dsrp.span.unwrap()
    except:
        pass

    try:
        dsrp.a.unwrap()
    except:
        pass
    
    try:
        dsrp.em.unwrap()
    except:
        pass

    try:
        dsrp.strong.unwrap()
    except:
        pass

    dsrp = dsrp.text.replace("<br/>", "\n")

    title = title.split(" - ")

    courses[course_id] = {
        "code" : title[0],
        "name" : title[1],
        "desc" : dsrp,
        "units" : int(units)
    }

class Command(BaseCommand):
    help = 'Writes parsed requirements to files to be loaded'

    def handle(self, *args, **options):
        print('\nWriting out data...\n')
        scrape_headers()
        fp = os.path.abspath(os.path.join(settings.BASE_DIR, 'data', 'courses.json'))
        with open(fp, 'w') as f: json.dump(courses, f, indent=4)
        print('\nParsed and written\n')
