# FONDREN.PY
# Fondren API


import urllib2
import collections
import api

from flask import request, jsonify
from bs4 import BeautifulSoup

from app import app, db
from app.database import Reservation


@app.route('/api/library/rooms')
def fondren_rooms_api():
    """
    Function selector for API interface for Fondren reservation system. First validates passed parameters, then
    calls either the database version or the live version of the reservation API.
    """
    # Parameters from URL
    api_key = request.args.get("key", "")
    filter_room = request.args.get("room", "")
    live = request.args.get("live", "").lower() == "true"

    # Initial error handling
    # Check valid API key
    if not api.is_api_key_valid(api_key):
        return api.error("Invalid or unauthorized API key")
    # Check valid (int-castable) year
    if len(filter_room) > 0:
        try:
            int(filter_room)
        except:
            return api.error("Invalid room number " + filter_room)

    # Choose whether to use the cached results or get live results
    return fondren_api_live(filter_room) if live else fondren_api_database(filter_room)


@app.route('/api/library/hours')
def fondren_hours_api():
    # Check valid API key
    if not api.is_api_key_valid(request.args.get("key", "")):
        return api.error("Invalid or unauthorized API key")

    return get_open_hours()


def fondren_api_live(filter_room):
    """
    API interface for Fondren reservation system. Retrieves data live from Fondren. Prohibitively slow, hence
    the reason for the database caching.
    """
    # Get the live data
    reservation_data = get_all_reservation_data()

    # Filter results if room parameter is non-null
    if len(filter_room) > 0:
        for room in dict(reservation_data["rooms"]):
            if str(room) != str(filter_room):
                del reservation_data["rooms"][room]

    return jsonify(reservation_data)


def fondren_api_database(filter_room):
    """
    Database cached version of the API. Fast!
    """
    # Update the database if it's empty
    if len(Reservation.query.all()) == 0:
        update_fondren_database()

    # Query the database, format strings accordingly, and JSON-ify everything
    result = collections.defaultdict(dict)
    for room in Reservation.query.all():
        times = {}
        for date_and_availability in room.availability.split("|"):
            if len(date_and_availability) > 0:
                times[date_and_availability[:10]] = [time for time in date_and_availability[11:].split(";") if len(time) > 0]
        result[room.room_number]["available_times"] = dict(times)
        result[room.room_number]["description"] = room.description

    # Assemble JSON to return
    json = {
        "message": None,
        "result": "success",
        "rooms": dict(result)
    }

    # Filter results if room parameter is non-null
    if len(filter_room) > 0:
        for room in dict(json["rooms"]):
            print str(room), str(filter_room), str(room) != str(filter_room)
            if str(room) != str(filter_room):
                del json["rooms"][room]

    return jsonify(json)


@app.route('/api/library/rooms/update')
def update_fondren_database():
    """
    Updates the database with the latest reservation times.
    """
    # Get live data
    reservation_data = get_all_reservation_data()
    # Delete current rows in table (they're being updated right now)
    Reservation.query.delete()
    # Add new data into database
    for room in reservation_data["rooms"]:
        availability = ""
        for date in reservation_data["rooms"][room]["available_times"]:
            # Availability string format: date:time;time;time;|date:time;time;...
            availability += date + ":" + "".join([time + ";" for time in reservation_data["rooms"][room]["available_times"][date]]) + "|"
        db.session.add(Reservation(int(room), reservation_data["rooms"][room]["description"], availability))
    db.session.commit()
    return "Update success"


def get_all_reservation_data():
    """
    Gets all reservation data for the next three days from Fondren's room reservation system and
    returns it as a dictionary, for both live presentation and storage in a database
    """
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
        date = map(str, start[0:start.index("%")].split("-"))
        formatted_date = date[1] + "-" + date[2] + "-" + date[0]
        start = str(start[13:-2].replace("%3A", ""))
        end = end[13:-2].replace("%3A", "")
        # Add to result dictionary
        result[rooms[room_id]["number"]]["description"] = rooms[room_id]["description"]
        result[rooms[room_id]["number"]]["available_times"][formatted_date].append(start)

    # Assemble JSON to return
    json = {
        "message": None,
        "result": "success",
        "rooms": dict(result)
    }

    return json


def get_open_hours():
    """
    Gets Fondren's open hours, live
    """
    # Read and soup the HTML
    soup = BeautifulSoup("".join(urllib2.urlopen("http://library.rice.edu/library-hours").readlines()[24:50]))
    data = filter(lambda s: len(s) > 0, map(str, soup.get_text().split("\n")))

    # Construct the open/close times dictionary
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    hours = {day: {"open": None, "close": None, "24_hours": False} for day in days}
    for i in range(len(days)):
        if "open at" in data[i].lower():
            hours[days[i]]["open"] = data[i].lstrip("Open at")
            hours[days[i]]["close"] = "12am"
        elif "close at" in data[i].lower():
            hours[days[i]]["open"] = "12am"
            hours[days[i]]["close"] = data[i].lstrip("Close at")
        elif "to" in data[i].lower():
            open_time, close_time = data[i].replace(" ", "").split("to")
            hours[days[i]]["open"] = open_time
            hours[days[i]]["close"] = close_time
        elif "24hours" in data[i].lower():
            hours[days[i]]["open"] = hours[days[i]]["close"] = "12am"
            hours[days[i]]["24_hours"] = True
        elif "closed" in data[i].lower():
            hours[days[i]]["open"] = hours[days[i]]["close"] = "closed"
        else:
            hours[days[i]]["open"] = hours[days[i]]["close"] = "Error - contact Kevin (kevinlin@rice.edu)"

    # Assemble JSON for return
    json = {
        "message": None,
        "result": "success",
        "hours": dict(hours)
    }

    return jsonify(json)