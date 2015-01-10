# API.PY
# Handles logic related to the API itself.


import urllib2

from flask import request
import flask

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
    people = []
    person = {"name": None, "year": None, "college": None, "major": None, "address": None, "email": None}
    for line in data.readlines()[200:]:
        if "name: " in line:
            try:
                name_list = line.strip().lstrip("name: <b>").rstrip(">b/<").split(", ")
                person["name"] = name_list[1] + " " + name_list[0]
            except:
                pass
        if "class: " in line:
            try:
                person["year"] = line.strip()[7:].split()[0].capitalize()
            except:
                pass
        if "college: " in line:
            try:
                person["college"] = line.strip()[9:]
            except:
                pass
        if "major: " in line:
            try:
                person["major"] = line.strip()[7:]
            except:
                pass
        if "address: " in line:
            try:
                person["address"] = line.strip()[9:]
            except:
                pass
        if "email: " in line:
            try:
                temp = line.strip()[23:]
                person["email"] = temp[:temp.index("'")]
                # Email is the last field, so add this new person to the list at this point
                people.append(person)
                person = dict({"name": None, "year": None, "college": None, "major": None, "address": None})
            except:
                pass
    json = {
        "result": "success",
        "message": "null",
        "people": people
    }
    return flask.jsonify(**json)


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
    return flask.jsonify(**json)



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
    return flask.jsonify(**json)