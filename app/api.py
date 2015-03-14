# API.PY
# Handles logic related to the API itself.


import urllib2
import collections

from flask import request, jsonify

from app import app
from app.database import User
import config

from bs4 import BeautifulSoup


@app.route('/api/people')
def people_api():
    """
    API interface for looking up people
    """
    if not is_api_key_valid(request.args.get("key", "")):
        return error("Invalid or unauthorized API key")

    # Parameters from URL
    lookup_net_id = request.args.get("net_id", None)
    lookup_name = request.args.get("name", None)
    # Replace spaces in name with plus sign, if they exist
    if lookup_name:
        lookup_name = "+".join(lookup_name.split())

    # Rice 411 lookup directory
    # Prioritize search by Net ID
    if lookup_net_id is not None:
        url = "http://fouroneone.rice.edu/query.php?tab=people&search=" + lookup_net_id + "&department=&phone=&action=Search"
    elif lookup_name is not None:
        url = "http://fouroneone.rice.edu/query.php?tab=people&search=" + lookup_name + "&department=&phone=&action=Search"
    else:
        return error("One of Net ID or Name in URL parameters must be non-null")
    data = urllib2.urlopen(url)

    # Parsing HTML data like this is highly unpredictable. Thus, a bunch of try-excepts:
    students, faculty = [], []
    name, year, department, title, mailstop, office, phone, website, email, college, major, address = (None, None, None, None, None, None, None, None, None, None, None, None)
    for line in data.readlines()[200:]:
        if "name: " in line:
            try:
                name_list = line.strip().lstrip("name: <b>").rstrip(">b/<").split(", ")
                name = name_list[1] + " " + name_list[0]
            except:
                pass
        if "class: " in line:
            try:
                year = line.strip()[7:].split()[0].capitalize()
            except:
                pass
        if "college: " in line:
            try:
                college = line.strip()[9:]
            except:
                pass
        if "major: " in line:
            try:
                major = line.strip()[7:]
            except:
                pass
        if "address: " in line:
            try:
                address = line.strip()[9:]
            except:
                pass
        if "department: " in line:
            try:
                department = line.strip()[12:]
            except:
                pass
        if "title: " in line:
            try:
                title = line.strip()[7:]
            except:
                pass
        if "mailstop: " in line:
            try:
                mailstop = line.strip()[10:]
            except:
                pass
        if "office: " in line:
            try:
                office = line.strip()[8:]
            except:
                pass
        if "phone: " in line:
            try:
                phone = line.strip()[7:]
            except:
                pass
        if "homepage: " in line:
            try:
                temp = line.strip()[26:]
                website = temp[:temp.index("'")]
            except:
                pass
        if "email: " in line:
            try:
                temp = line.strip()[23:]
                email = temp[:temp.index("'")]
                # Email is the last field, so add this new person to the list at this point
                if year.lower() == "staff" or year.lower() == "faculty":
                    faculty.append(dict({"name": name, "department": department, "title": title, "mailstop": mailstop, "office": office, "phone": phone, "website": website, "email": email}))
                else:
                    students.append(dict({"name": name, "year": year, "college": college, "major": major, "address": address}))
                # Reset all variables to null
                name, year, department, title, mailstop, office, phone, website, email, college, major, address = (None, None, None, None, None, None, None, None, None, None, None, None)
            except:
                pass
    json = {
        "result": "success",
        "message": "null",
        "people": {
            "students": students,
            "faculty": faculty
        }
    }
    return jsonify(json)


@app.route('/api/courses')
def courses_api():
    """
    API interface for course search
    """
    # Parameters from URL
    api_key = request.args.get("key", "")
    term = request.args.get("term", "").capitalize()
    year = request.args.get("year", "")
    code = request.args.get("code", "")
    title = request.args.get("title", "")
    instructor = request.args.get("instructor", "")
    subject = request.args.get("subject", "").upper()
    # Replace spaces with plus sign as necessary
    code = "+".join(code.split())
    instructor = "+".join(instructor.split())
    title = "+".join(title.split())

    # Initial error handling
    # Check valid API key
    if not is_api_key_valid(api_key):
        return error("Invalid or unauthorized API key")
    # Check valid (int-castable) year
    try:
        int(year)
    except:
        return error("Invalid year " + year)
    # Check valid other parameters
    if len(code) == 0 and len(title) == 0 and len(instructor) == 0 and len(subject) == 0:
        return error("Not enough parameters for search")
    if len(subject) != 4 and len(subject) != 0:
        return error("Invalid subject code " + subject)

    # Create term code
    term_code = ""
    # Session
    if term == "Fall":
        term_code += "10"
    elif term == "Spring":
        term_code += "20"
    elif term == "Summer":
        term_code += "30"
    else:
        return error("Invalid term " + term)
    # Year
    if term == "Fall":
        year = str(int(year) + 1)
    term_code = year + term_code

    # Initialize BeautifulSoup and URL
    url = "https://courses.rice.edu/admweb/!SWKSCAT.cat?p_action=QUERY&p_term=" + term_code + "&p_name=" + code + "&p_title=" + title + "&p_instr=" + instructor + "&p_subj=" + subject + "&p_spon_coll=&p_df=&p_ptrm=&p_mode=AND"
    data = urllib2.urlopen(url).read()
    html_data = BeautifulSoup(data)

    # Parse HTML
    course_numbers = [course_number_link.a.string for course_number_link in html_data.find_all("td", {"class": "searchSection"})]
    course_numbers = map(str, course_numbers)
    course_codes = [course_code.string for course_code in html_data.find_all("td", {"class": "searchCourse"})]
    course_lengths = [course_length.string for course_length in html_data.find_all("td", {"class": "searchSession"})]
    course_titles = [course_title.string for course_title in html_data.find_all("td", {"class": "searchTitle"})]
    course_instructors = [course_instructor.string for course_instructor in html_data.find_all("td", {"class": "searchInstructor"})]
    course_times = [course_time.string for course_time in html_data.find_all("td", {"class": "searchMeeting"})]
    course_credits = [course_credit.string for course_credit in html_data.find_all("td", {"class": "credits"})]

    # Assemble JSON object
    courses = []
    for i in range(len(course_numbers)):
        course = {
            "number": course_numbers[i],
            "code": course_codes[i],
            "length": course_lengths[i],
            "title": course_titles[i],
            "instructor": course_instructors[i],
            "time": course_times[i],
            "credits": course_credits[i].lower()
        }
        courses.append(dict(course))
    json = {
        "result": "success",
        "message": "null",
        "courses": courses
    }
    return jsonify(json)


@app.route('/api/fondren')
def fondren_api():
    """
    API interface for Fondren reservation system
    """
    # Parameters from URL
    api_key = request.args.get("key", "")
    filter_room = request.args.get("room", "")

    # Initial error handling
    # Check valid API key
    if not is_api_key_valid(api_key):
        return error("Invalid or unauthorized API key")
    # Check valid (int-castable) year
    if len(filter_room) > 0:
        try:
            int(filter_room)
        except:
            return error("Invalid room number " + filter_room)

    # Soup the reservation system page
    soup = BeautifulSoup(urllib2.urlopen("https://rooms.library.rice.edu/Web/view-schedule.php?&sfw=1").read())

    # Get all room ID's and descriptions and room numbers
    rooms = collections.defaultdict(dict)  # {id: room # (int)}
    for room in soup.find_all("a", {"class": "resourceNameSelector"}):
        rooms[int(room.attrs["resourceid"])]["description"] = str(room.contents[0])
        rooms[int(room.attrs["resourceid"])]["number"] = int(str(room.contents[0])[5:8])

    # Begin constructing reservation dictionary
    result = collections.defaultdict(dict)
    # Take care of Python-specific dictionary things
    for room in rooms:
        result[rooms[room]["number"]]["available_times"] = collections.defaultdict(list)
    # Iterate through all HTMl elements with the "reservable" class
    for reservable in soup.find_all("td", {"class": "reservable clickres slot"}):
        # Get HTML elements
        room_id = reservable.find_all("input", {"class": "href"})[0].attrs["value"]  # Room ID
        start = reservable.find_all("input", {"class": "start"})[0].attrs["value"]  # Start time of available reservation
        end = reservable.find_all("input", {"class": "end"})[0].attrs["value"]  # End time of available reservation
        # Trim and format elements as necessary
        room_id = int(room_id[20:room_id.index("&")])
        date = map(int, start[0:start.index("%")].split("-"))
        formatted_date = str(date[1]) + "-" + str(date[2]) + "-" + str(date[0])
        start = str(start[13:-2].replace("%3A", ""))
        end = end[13:-2].replace("%3A", "")
        # Add to result dictionary
        result[rooms[room_id]["number"]]["description"] = rooms[room_id]["description"]
        result[rooms[room_id]["number"]]["available_times"][formatted_date].append(start)

    # Filter results if room parameter is non-null
    if len(filter_room) > 0:
        for room in dict(result):
            if int(room) != int(filter_room):
                del result[room]

    # Assemble JSON to return
    json = {
        "message": None,
        "result": "success",
        "rooms": dict(result)
    }

    return jsonify(json)



def is_api_key_valid(api_key):
    """
    Checks if the given API key is valid, i.e., it exists in the database
    """
    # API key must be of length API_KEY_LENGTH
    # API key must correspond to a non-null database entry
    return len(api_key) == config.API_KEY_LENGTH and User.query.filter_by(api_key=api_key).first() is not None


def error(message):
    """
    Returns a generically formatted JSON object indicating an error with the provided message.
    """
    json = {
        "result": "failure",
        "message": message
    }
    return jsonify(json)