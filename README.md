# MAP back-end

Since we don't have access to the API to retrieve data from, there are some json files that can be used to populate the database.  


# How to run

Use the **requirements.txt** stored with any virtual environment. Might include some extra stuff that are no longer needed (I forgot to uninstall some stuff no longer needed, will fix later)

To start run: **py manage.py runserver**

## Populating the database

A temporary method of populating the database with science courses are provided.  Make sure to makemigrations and migrate before. Use admin panel to verify results

 **py manage.py load_courses courses.json**
 
 **py manage.py load_courselist course_list.json**
 
 **py manage.py load_programs programs.json**
 
 **py manage.py load_requirements requirements.json**

## Building index to search

 **py manage.py rebuild_index **

# Endpoints

There is no error checking right now so requests must be crafted carefully. 

### GET to search
Request:
/api/Search?q=<QUERY HERE>

Must run "rebuild_index" in order to search any courses
	
	
### 1 GET to populate frontend initially

Request:
/api/GetCourseData (This gets all courses)
/api/GetCourseData?faculty=MATH


### GET to retrieve course name and desc, given a course ID

Request:
/api/GetCourseDetails?courseid=1234567


### POST for submitting course selections for calculation
Request:

/api/SubmitCourseSelections
Body:
{
	"selections": [
		1234567,
		0101010,
		5564732,
		1238921
	]
}

