# Automatically and periodically update the Fondren room reservation database
# Updates every 10 minutes

import urllib2, time

APP_URL = "http://api.riceapps.org"

while True:
    print "Debug: Requesting database update"
    try:
        urllib2.urlopen(APP_URL + "/api/library/update")
        print "Debug: Database updated successfully!"
    except:
        print "Debug: Failed to update database!"
    time.sleep(10*60)