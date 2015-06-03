#!/usr/bin/python2.7
# -*- encoding: utf8 -*-

"""
    Copyright (C) 2012-2015 Rudolf Cardinal (rudolf@pobox.com).
    Department of Psychiatry, University of Cambridge.
    Funded by the Wellcome Trust.

    This file is part of CamCOPS.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import xml.etree.cElementTree as ElementTree
# ... cElementTree is a faster implementation
# ... http://docs.python.org/2/library/xml.etree.elementtree.html
# ... http://effbot.org/zone/celementtree.htm

import rnc_web as ws

from cc_logger import logger
import cc_pls


# =============================================================================
# Localization strings
# =============================================================================

def cache_strings():
    """
    Caches strings from the main XML string file.
    The string file looks like this:
        <?xml version="1.0" encoding="UTF-8"?>
        <resources>
            <string name="NAME">VALUE</string>
            <!-- ... -->
        </resources>
    """
    if cc_pls.pls.stringDict is not None:
        return
    if cc_pls.pls.CAMCOPS_STRINGS_FILE_ABSOLUTE is None:
        raise AssertionError(
            "pls.CAMCOPS_STRINGS_FILE_ABSOLUTE is None -- likely use of "
            "LSTRING/WSTRING in classmethod, before initialization via "
            "the WSGI application entry point")
    logger.debug("Loading XML file: " +
                 cc_pls.pls.CAMCOPS_STRINGS_FILE_ABSOLUTE)
    parser = ElementTree.XMLParser(encoding="UTF-8")
    tree = ElementTree.parse(cc_pls.pls.CAMCOPS_STRINGS_FILE_ABSOLUTE,
                             parser=parser)
    cc_pls.pls.stringDict = {}
    # find all children of the root with tag "string" and attribute "name"
    for e in tree.findall("./string[@name]"):
        cc_pls.pls.stringDict[e.attrib.get("name")] = e.text


def LSTRING(stringname):  # equivalent of Titanium's L()
    """Looks up a string from the XML string file."""
    cache_strings()
    return cc_pls.pls.stringDict.get(stringname,
                                     "XML_STRING_NOT_FOUND_" + stringname)


def WSTRING(stringname):
    """Returns a web-safe version of a string from the XML string file."""
    return ws.webify(LSTRING(stringname))


def cache_extra_strings():
    """
    Caches strings from the all the extra XML string files.
    The extra string files look like this:
        <?xml version="1.0" encoding="UTF-8"?>
        <resources>
            <task name="TASK_1">
                <string name="NAME_1">VALUE</string>
                <string name="NAME_2">VALUE WITH\nNEWLINE</string>
                <!-- ... -->
            </task>
            <!-- ... -->
        </resources>
    """
    if cc_pls.pls.extraStringDicts is not None:
        return
    if cc_pls.pls.EXTRA_STRING_FILES is None:
        raise AssertionError(
            "pls.EXTRA_STRING_FILES is None -- likely use of "
            "XSTRING/WXSTRING in classmethod, before initialization via "
            "the WSGI application entry point")
    cc_pls.pls.extraStringDicts = {}
    for filename in cc_pls.pls.EXTRA_STRING_FILES:
        logger.debug("Loading XML file: " + filename)
        parser = ElementTree.XMLParser(encoding="UTF-8")
        tree = ElementTree.parse(filename, parser=parser)
        root = tree.getroot()
        for taskroot in root.findall("./task[@name]"):
            taskname = taskroot.attrib.get("name")
            if taskname not in cc_pls.pls.extraStringDicts:
                cc_pls.pls.extraStringDicts[taskname] = {}
            for e in taskroot.findall("./string[@name]"):
                stringname = e.attrib.get("name")
                value = e.text
                cc_pls.pls.extraStringDicts[taskname][stringname] = value


def XSTRING(taskname, stringname, default=None):
    """Looks up a string from one of the optional extra XML string files."""
    if default is None:
        default = "EXTRA_STRING_NOT_FOUND({}.{})".format(taskname, stringname)
    cache_extra_strings()
    if taskname not in cc_pls.pls.extraStringDicts:
        return default
    return cc_pls.pls.extraStringDicts[taskname].get(stringname, default)


def WXSTRING(taskname, stringname, default=None):
    """Returns a web-safe version of an XSTRING (see above)."""
    return ws.webify(XSTRING(taskname, stringname, default))


def get_all_extra_strings():
    """Returns all extra strings, as a list of (task, name, value) tuples."""
    cache_extra_strings()
    rows = []
    for task, subdict in cc_pls.pls.extraStringDicts.iteritems():
        for name, value in subdict.iteritems():
            rows.append((task, name, value))
    return rows


def task_extrastrings_exist(taskname):
    """Has the server been supplied with extra strings for a specific task?"""
    cache_extra_strings()
    return taskname in cc_pls.pls.extraStringDicts
