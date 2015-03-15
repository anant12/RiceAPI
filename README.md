# RiceAPI

Rice API is a tool designed to allow students and faculty easy access to publicly accessible data about the university. The current supported functionality include retrieving information about a person (e.g. a student), retrieving a list of courses based on search criteria, and getting information about Fondren Library. Data is returned by the API in a friendly, JSON format. Anyone with a valid Rice Net ID is permitted to use the tool.

This API interface was developed out of moderate frustration over the difficulty for developers to access information about the university without resorting to clumsy, line-by-line parsing of HTML data. This API does said clumsy parsing for you.

## Features
* Easy-to-process JSON API response
* Get information on Rice students and faculty
* Get information on courses via search criteria
* Get information on Fondren's available study rooms and open hours

## API Key Registration
As a security measure, only Rice students and faculty (e.g. those with a valid Net ID) are permitted to use this API. Thus, the API will only respond to requests supplemented with a valid API key.

To obtain an API key, [simply log in with your Net ID](http://api.riceapps.org/login) and click on "Generate API key." The server will automatically generate a unique, alphanumeric API key that will be associated with your Net ID. You are permitted (theoretically) unlimited requests with your key through this application.

## Usage
To use the API, simply execute an HTTP GET request to the following URL:

`http://api.riceapps.org/api/action?key=API_KEY&parameter=SOME_CRITERION`

where `action` specifies the API action, as specified below, `key` is your API key (required for all requests), and `parameter` (of which there can be several) specifies different parameters for that action (also specified below). Only HTTP (not HTTPS) requests are currently supported.

Full descriptions of parameters and actions supported by the API are detailed as follows (asterisks designate required parameters):

### Actions
| Action | Description |
|--------|-------------|
|people|Look up information about Rice students and faculty. Data is pulled from [fouroneone.rice.edu](http://fouroneone.rice.edu)|
|courses|Retrieve a list of courses matching some search criteria. Data is pulled from [courses.rice.edu](http://courses.rice.edu)
|library/rooms|Gets details on the times that each study room is available for reservation. Data is pulled from [library.rice.edu](http://library.rice.edu)|
|library/hours|Gets live details on Fondren's open hours for this week. Data is pulled from [library.rice.edu](http://library.rice.edu)|

## API Reference
Please see the below for full details on the parameters each API call accepts and the form of the data returned by the request.

### People API

#### Parameters
| Parameter | Description |
|-----------|-------------|
|key*|API key generated and authorized by this application.
|net_id|Executes a 411 directory lookup of the specified Net ID. If this parameter is non-null, it will override the name parameter.
|name|Executes a 411 directory lookup of the specified name. The passed string can contain spaces. The contents of this parameter will be overridden if the net_id parameter is non-null.

#### Response
The API separates people search results into students and faculty.

| Response field | Description |
|-----------|-------------|
|response.result|"Success" or "failure" depending on whether the API request was successful or unsuccessful, respectively
|response.message|Error message if the API request was unsuccessful; null otherwise
|response.people|List of people in search results, separated into students and faculty arrays (people.students[] and people.faculty[]). Either array can be of size 0 if no search results matched the search criteria
|response.people.students[].address|Campus address of the person
|response.people.students[].college|Residential college of the person
|response.people.students[].email|Published Rice email address of the person
|response.people.students[].major|Declared major(s) of the person
|response.people.students[].name|Published name of the person, in order first-middle-last
|response.people.students[].year|Class standing of the person. Based on number of credit hours, not matriculation year.
|response.people.faculty[].department|Department of the person
|response.people.faculty[].email|Published Rice email address of the person
|response.people.faculty[].mailstop|Campus mailstop code of the person
|response.people.faculty[].office|Campus office location of the person
|response.people.faculty[].phone|Campus phone number of the person
|response.people.faculty[].website|Website URL of the faculty member

Sample request:
```
GET http://api.riceapps.org/api/people?key=nfkv05mmalawcba6ta00mhz536denf&net_id=kl38
```

Sample response:
```
Content-Type: application/json

{
  "message": "null",
  "people": {
    "students": [
      {
        "address": "Sid Richardson Coll MS-746, 6360 Main Street, , TX 77005-1847",
        "college": "Sid Richardson College",
        "email": "kevinlin@rice.edu",
        "major": "Electrical Engineering, Computer Science",
        "name": "Kevin Lin",
        "year": "Junior"
      }
    ],
    "faculty": []
  }
  "result": "success"
}
```

### Courses API

#### Parameters
| Parameter | Description |
|-----------|-------------|
|key*|API key generated and authorized by this application. See API key registration.
|term*|Semester term. Acceptable inputs are "Fall," "Spring," and "Summer."
|year*|Year corresponding to the semester term, e.g., "2015"
|code|Course code, e.g., "ELEC 241" or "241"
|title|Title of the course, e.g., "Fund Electrical Engineering I." It is not recommended to use this search option, since courses.rice.edu only returns results for exact matches (e.g. "Fundamentals of Electrical Engineering I" will return no results, but "Fund Electrical Engineering I" will)
|instructor|Name(s) of the course instructor(s). It is not recommended to use this search option for the same reason as above.
|subject|Four-letter subject code, e.g., "ELEC"

#### Response
| Response field | Description |
|-----------|-------------|
|response.result|"Success" or "failure" depending on whether the API request was successful or unsuccessful, respectively
|response.message|Error message if the API request was unsuccessful; null otherwise
|response.courses[]|List of courses in search results. Can be of size 0 if no search results matched the search criteria
|response.courses[].code|Course code in the format subject code section, e.g., "ELEC 241 001"
|response.courses[].credits|Number of credits of the course
|response.courses[].instructor|Name of the instructor(s) of the course, in format last, first
|response.courses[].length|Description of the length of the course
|response.courses[].number|Course number
|response.courses[].time|Scheduled meeting time(s) of the course. Format start time - end time days, where the start and end times are 12-hours string representations of the time, and days is a one or two-letter abbreviation of the day of the week.
|response.courses[].title|Course title

Sample request:
```
GET http://api.riceapps.org/api/courses?key=nfkv05mmalawcba6ta00mhz536denf&term=spring&year=2015&code=MATH 212
```

Sample response:
```
Content-Type: application/json

{
  "courses": [
  {
    "code": "MATH 212 001",
    "credits": "3",
    "instructor": "Shadrach, Richard H.",
    "length": "Full Term",
    "number": "20197",
    "time": "09:00AM - 09:50AM MWF",
    "title": "MULTIVARIABLE CALCULUS"
  },
  {
    "code": "MATH 212 002",
    "credits": "3",
    "instructor": "Tanimoto, Sho",
    "length": "Full Term",
    "number": "20198",
    "time": "11:00AM - 11:50AM MWF",
    "title": "MULTIVARIABLE CALCULUS"
  },
  {
    "code": "MATH 212 003",
    "credits": "3",
    "instructor": "Kiselev, Alexander",
    "length": "Full Term",
    "number": "20580",
    "time": "09:25AM - 10:40AM TR",
    "title": "MULTIVARIABLE CALCULUS"
    },
    ...
  ],
  "message": "null",
  "result": "success"
}
```

### Library API

#### Parameters - api/library/rooms
| Parameter | Description |
|-----------|-------------|
|key*|API key generated and authorized by this application. See API key registration.
|room|The room for which reservation details should be retrieved. If this parameter is omitted, the API will return data for all rooms.
|live|By default, the API returns reservation data cached in a local database that is automatically and periodically updated with the latest room reservation data.* Set this parameter to `true` to force the API to query Fondren's reservation system directly to get live data. (It is highly recommended to omit this parameter or set it to `false` because querying Fondren directly is very slow.)

*To manually request the server to update the database of reservation data, simply execute a GET request (no authorization necessary) to `http://api.riceapps.org/library/rooms/update`.

#### Response - api/library/rooms
| Response field | Description |
|-----------|-------------|
|response.result|"Success" or "failure" depending on whether the API request was successful or unsuccessful, respectively
|response.message|Error message if the API request was unsuccessful; null otherwise
|response.rooms|List of rooms with reservation data
|response.rooms.description|Description of the study room, i.e. "Room 201 - 14 chairs, TV, video capture"
|response.rooms.available_times.date[]|List of times as 24-hour strings that represent 30-minute blocks for which a reservation is available, for that particular date, formatted as `MM-DD-YYYY`. For example, the date `03-14-2015` mapped to list `["0000", "0030"]` indicates that times 12:00 AM - 12:30 AM and 12:30 AM - 1:00 AM are available for reservation on 3/14/2015.

Sample request:
```
GET http://api.riceapps.org/api/library/rooms?key=nfkv05mmalawcba6ta00mhz536denf&room=201
```

Sample response:
```
Content-Type: application/json

{
  "message": null,
  "result": "success",
  "rooms": {
    "201": {
      "available_times": {
        "03-14-2015": [
          "1900",
          "1930",
          "2000",
          "2030",
          "2100",
          "2130",
          "2200",
          "2230",
          "2300",
          "2330"
        ],
        "03-15-2015": [
          "0000",
          "0030",
          "0100",
          "0130",
          "0200",
          ...
        ],
        "03-16-2015": [
          "0000",
          "0030",
          "0100",
          "0130",
          "0200",
          ...
        ]
      },
      "description": "Room 201 - 14 chairs, TV, video capture"
    }
  }
}
```

#### Parameters - api/library/hours
| Parameter | Description |
|-----------|-------------|
|key*|API key generated and authorized by this application. See API key registration. No other parameters are required.

#### Response - api/library/rooms
| Response field | Description |
|-----------|-------------|
|response.result|"Success" or "failure" depending on whether the API request was successful or unsuccessful, respectively
|response.message|Error message if the API request was unsuccessful; null otherwise
|response.hours.day|Details for the opening and closing times for day, which is a string Sunday through Saturday. The data is current and live--the data returned is for whatever calendar week is active when the API call is executed.
|response.hours.day.24_hours|True if Fondren is open 24 hours that day; false otherwise
|response.hours.day.open|Time that Fondren opens that day, in the format #am/pm (no number padding). "Closed" if Fondren is closed that day.
|response.hours.day.close|Time that Fondren closes that day, in the format #am/pm (no number padding). "Closed" if Fondren is closed that day.

Sample request:
```
GET http://api.riceapps.org/api/library/hours?key=nfkv05mmalawcba6ta00mhz536denf
```

Sample response:
```
Content-Type: application/json

{
  "hours": {
    "Friday": {
      "24_hours": false,
      "close": "10pm",
      "open": "12am"
    },
    "Monday": {
      "24_hours": true,
      "close": "12am",
      "open": "12am"
    },
    "Saturday": {
      "24_hours": false,
      "close": "10pm",
      "open": "9am"
    },
    "Sunday": {
      "24_hours": false,
      "close": "12am",
      "open": "12pm"
    },
    "Thursday": {
      "24_hours": true,
      "close": "12am",
      "open": "12am"
    },
    "Tuesday": {
      "24_hours": true,
      "close": "12am",
      "open": "12am"
    },
    "Wednesday": {
      "24_hours": true,
      "close": "12am",
      "open": "12am"
    }
  },
  "message": null,
  "result": "success"
}
```

## Compiling from source
You are welcome to compile this application from source and run it locally. In order to do so, you must meet the following requirements:

* Python 2.7
* Flask (via `pip install flask`)
* Flask-CAS (via `pip install flask-cas`)
* Flask-SQLAlchemy (via `pip install flask-sqlalchemy`)
* BeautifulSoup (via `pip install beautifulsoup4`)

First, grab the full source code from Github. After cloning the repository or unzipping its contents locally, you must first create the SQLite database storing Net IDs and API keys:

```
> from app import db
> db.create_all()
```

Then, you can start the app in a Python shell:

```
> python RiceAPI.py
* Running on http://0.0.0.0:5000/
* Restarting with reloader
```

You can now access the same features available on the web API locally at the following URL:

```
http://localhost:5000/
```

All functionality is identical sans the URL. The same rules regarding parameters and API keys still apply.
