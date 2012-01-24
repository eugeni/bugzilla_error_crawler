#!/usr/bin/python
#
# Extracts bug attachments from saved files
#

import xml.etree.cElementTree as ET
import sys
from glob import glob
import traceback
import re
import base64

# optimizations
try:
    import psyco
    psyco.full()
except:
    print "No runtime optimization."
    pass

# from http://boodebr.org/main/python/all-about-python-and-unicode#UNI_XML
RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
        u'|' + \
        u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
        (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))
regex = re.compile(RE_XML_ILLEGAL)

def parse_bugs(file):
    """Locates similar or duplicated bugs"""
    data = open(file).read()

    try:
        res = ET.fromstring(data)
    except SyntaxError:
        # looks like we found an invalid character
        print >>sys.stderr, "Invalid characters found, stripping..",
        # this is slow, but it is the best we can do right now..
        for match in regex.finditer(data):
            data = data[:match.start()] + "?" + data[match.end():]
        res = ET.fromstring(data)

    baseurl = res.get("urlbase")
    for bug in res:
        # Check if bug is valid
        if bug.get("error"):
            continue
        # XPATH
        bug_id = bug.findtext("./bug_id")
        short_desc = bug.findtext("./short_desc", "Bug %s (no short description)" % bug_id)
        curbug = "%s/%s" % (baseurl, bug_id)
        # is it a duplicated bug?
        dup_id = bug.findtext("./dup_id")
        if dup_id:
            print "!! Duplicate found: %s -> %s!" % (bug_id, dup_id)
        # TODO: use hash?
        #print short_desc.__hash__()
        for attach in bug.findall("./attachment"):
            for filename in attach.findall("./filename"):
                if filename.text.find("error_state") >= 0:
                    print "Found possible error_state for %s: %s" % (bug_id, filename.text)
                    fd = open("error_state.%s.%s" % (bug_id, filename.text), "w")
                    for data in attach.findall("./data"):
                        fd.write(base64.b64decode(data.text))
                    fd.close()

if __name__ == "__main__":
    # looking for files
    files = glob("*xml")
    for file in files:
        # are we doing one file at a time?
        print >>sys.stderr, "Parsing %s.." % file,
        try:
            parse_bugs(file)
            print >>sys.stderr, "ok"
        except:
            traceback.print_exc()
            print >>sys.stderr, "error parsing %s: %s" % (file, sys.exc_value)
            sys.exit(1)
