# MAP back-end

Test and developed on Python 3.8.1 on a Windows environment.
# How to run

### Create an environment
Use the **requirements.txt**  with any virtual environment to install the necessary dependencies. 
***

#### venv
Create a virtual environment
  **py -m venv /path/to/new/virtual/environment**

Activate the virual environment (Following is for windows)
  **C:\> <venv>\Scripts\activate.bat**

Once activated, you can install all dependencies from the requirements.txt file
  **pip3 install -r requirements.txt**
  ***

TODO: add docker instructions

### Install Postgres Verision 11
Once installed create user with the name "postgres" and password "password"
create a database named "db_map_be" using default port (5432)

### Running the server
To start run: ``` py manage.py runserver ``` 

***
## Preparing the database
By default, an sqllite database will be automatically created by Django. You should run the following commands:

``` py manage.py makemigrations map_backend ```
 
``` py manage.py migrate ```

## Populating the database

The fastest way to populate the database is with the json files included in the /data/ folder. You can automatically upload them using the following commands.

 ```py manage.py load_data courses.json programs.json```

## Building index to search

 ``` py manage.py rebuild_index ```

## Create a superuser

``` py backend/manage.py createsuperuser ```
 
# How to Run Using Docker
### Setup Database and Backend

Run **docker-compose up** to create the database and backend

### Initialize the Backend and Create A SuperUser

In a new terminal run **docker exec -it map_backend sh** to go into the backend container and run the following commands

 ``` py backend/manage.py makemigrations map_backend ```
 
 ``` py backend/manage.py migrate ```

 ``` py backend/manage.py load_data courses.json programs.json```
 
 ``` py backend/manage.py rebuild_index ```
 
 ``` py backend/manage.py createsuperuser ```
 
Exit out of this container by running **exit**

***
# Endpoints

### Searching (GET)
Request:
```
/api/Search?q=<QUERY HERE>
```

Must run "rebuild_index" in order to search any courses. See "Rebuilding index to search" section.
	
	
### Populating the frontend with courses and a title (GET)

Request:
```
/api/GetCourseData?calc_id=<id>
```

Response:
```
{"calcTitle": "test", "courseLists": {"Spring": {}, "Summer": {}, "Fall": {}, "Winter": {}}}
```

This will return the list of courses and the title of the calculator

### Retrieve course name and description (GET)

Request:
```
/api/GetCourseDetails?courseid=<id>
```
Response:
```
{"courseCode": "", "courseName": "", "courseDesc": ""}
```

### Calculate program requirement completion (POST)
Request:
```
/api/SubmitCourseSelections
Body:
{
	"selections": [
		<List of course ids>,
	],
	"calc_id": <calculator id>
}
```

Response:
```
{"matchedPrograms": [
                        {
                        "programName": "",
                        "programHref": "",
                        "programId": 0,
                        "programPercentage": 0,
                        "programRequirements": {
                            "requirements": []
                        },
                        "fulfilledCourses": []
                        }
                    ]}
```
