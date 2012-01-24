#!/usr/bin/python
#
# Gets all bugs which carry i915_error_state
#

import xml.etree.cElementTree as ET
import sys
import urllib2
import sys
import time
import traceback

BUGZILLA="https://bugs.freedesktop.org/show_bug.cgi" # &id=<ids>
QUERY="https://bugs.freedesktop.org/buglist.cgi?field0-0-0=attachments.filename&query_format=advanced&type0-0-0=substring&value0-0-0=error_state&ctype=csv"

def list_bugs(last_date=None):
    """List bugs matching error_state pattern"""
    bugs = []
    query = QUERY
    if last_date != None:
        query += "&chfieldfrom=%s" % last_date


    data = urllib2.urlopen(query).readlines()
    for line in data[1:]:
        fields = line.split(",")
        bug_id = fields[0]
        bugs.append(bug_id)
    return bugs

def bugs_details(bugs, bugs_at_once=25):
    """Lists details of bugs"""
    # To prevent bugzilla from timing out, let's query for at most **bugs-at_once** bugs at once
    for start in range(0, len(bugs), bugs_at_once):
        end = start + bugs_at_once
        if end >= len(bugs):
            end = len(bugs) - 1
        parameters =  "ctype=xml&" + "&id=".join(bugs[start:end])
        fd = open("bugs_%s_%s.xml" % (start, end), "w")
        print "Saving bugs %s..%s" % (start, end)
        data = urllib2.urlopen(BUGZILLA, parameters).read()
        fd.write(data)
        fd.close()

if __name__ == "__main__":
    bugs = list_bugs()
    bugs_details(bugs)
