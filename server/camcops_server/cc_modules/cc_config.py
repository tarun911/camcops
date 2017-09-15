#!/usr/bin/env python
# camcops_server/cc_modules/cc_config.py

"""
===============================================================================
    Copyright (C) 2012-2017 Rudolf Cardinal (rudolf@pobox.com).

    This file is part of CamCOPS.

    CamCOPS is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CamCOPS is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CamCOPS. If not, see <http://www.gnu.org/licenses/>.
===============================================================================
"""

# There are CONDITIONAL AND IN-FUNCTION IMPORTS HERE; see below. This is to
# minimize the number of modules loaded when this is used in the context of the
# client-side database script, rather than the webview.

import codecs
import configparser
import contextlib
import datetime
import operator
import os
import logging
import string
from typing import Dict, Generator, List, Optional

from cardinal_pythonlib.configfiles import (
    get_config_parameter,
    get_config_parameter_boolean,
    get_config_parameter_loglevel,
    get_config_parameter_multiline
)
from cardinal_pythonlib.logs import BraceStyleAdapter
from cardinal_pythonlib.randomness import create_base64encoded_randomness
import cardinal_pythonlib.rnc_web as ws
from cardinal_pythonlib.sqlalchemy.logs import pre_disable_sqlalchemy_extra_echo_log  # noqa
from cardinal_pythonlib.sqlalchemy.schema import get_table_names
from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session as SqlASession

from .cc_baseconstants import (
    ENVVAR_CONFIG_FILE,
    INTROSPECTABLE_EXTENSIONS,
)
from .cc_cache import cache_region_static, fkg
from .cc_constants import (
    CONFIG_FILE_MAIN_SECTION,
    CONFIG_FILE_RECIPIENTLIST_SECTION,
    DEFAULT_CAMCOPS_LOGO_FILE,
    DEFAULT_DATABASE_TITLE,
    DEFAULT_LOCAL_INSTITUTION_URL,
    DEFAULT_LOCAL_LOGO_FILE,
    DEFAULT_LOCKOUT_DURATION_INCREMENT_MINUTES,
    DEFAULT_LOCKOUT_THRESHOLD,
    DEFAULT_MYSQL,
    DEFAULT_MYSQLDUMP,
    DEFAULT_PASSWORD_CHANGE_FREQUENCY_DAYS,
    DEFAULT_PLOT_FONTSIZE,
    DEFAULT_TIMEOUT_MINUTES,
    INTROSPECTION_BASE_DIRECTORY,
    PDF_ENGINE,
)
from .cc_filename import (
    filename_spec_is_valid,
    patient_spec_for_filename_is_valid,
)
from .cc_simpleobjects import IntrospectionFileDetails
from .cc_policy import (
    finalize_id_policy_valid,
    tokenize_finalize_id_policy,
    tokenize_upload_id_policy,
    upload_id_policy_valid,
)
from .cc_recipdef import RecipientDefinition

log = BraceStyleAdapter(logging.getLogger(__name__))

pre_disable_sqlalchemy_extra_echo_log()


# =============================================================================
# Demo config
# =============================================================================

DEFAULT_DB_NAME = 'camcops'
DEFAULT_DB_USER = 'YYY_USERNAME_REPLACE_ME'
DEFAULT_DB_PASSWORD = 'ZZZ_PASSWORD_REPLACE_ME'
DEFAULT_DB_READONLY_USER = 'QQQ_USERNAME_REPLACE_ME'
DEFAULT_DB_READONLY_PASSWORD = 'PPP_PASSWORD_REPLACE_ME'
DEFAULT_ANONSTAG_DB_NAME = 'anon_staging_camcops'
DEFAULT_ANONSTAG_DB_USER = 'UUU_USERNAME_REPLACE_ME'
DEFAULT_ANONSTAG_DB_PASSWORD = 'WWW_PASSWORD_REPLACE_ME'
DUMMY_INSTITUTION_URL = 'http://www.mydomain/'


def get_demo_config(camcops_base_dir: str = None,
                    extra_strings_dir: str = None,
                    lock_dir: str = None,
                    hl7_lockfile_stem: str = None,
                    static_dir: str = None,
                    summary_table_lock_file_stem: str = None) -> str:
    camcops_base_dir = camcops_base_dir or '/usr/share/camcops'
    _server_base_dir = os.path.join(camcops_base_dir, 'server')
    extra_strings_dir = extra_strings_dir or os.path.join(
        _server_base_dir, 'extra_strings')
    lock_dir = lock_dir or '/var/lock/camcops'
    hl7_lockfile_stem = hl7_lockfile_stem or os.path.join(
        lock_dir, 'camcops.hl7')
    static_dir = static_dir or os.path.join(_server_base_dir, 'static')
    summary_table_lock_file_stem = (
        summary_table_lock_file_stem or os.path.join(
            lock_dir, 'camcops.summarytables'
        )
    )
    session_cookie_secret = create_base64encoded_randomness(num_bytes=64)

    return string.Template("""
# =============================================================================
# Format of the CamCOPS configuration file
# =============================================================================
# COMMENTS. Hashes (#) and semicolons (;) mark out comments.
# SECTIONS. Sections are indicated with: [section]
# NAME/VALUE (KEY/VALUE) PAIRS.
# - The parser used is ConfigParser (Python).
# - It allows "name=value" or "name:value".
# - BOOLEAN OPTIONS. For Boolean options, TRUE values are any of: 1, yes, true,
#   on (case-insensitive). FALSE values are any of: 0, no, false, off.
# - UTF-8 encoding. Use this. For ConfigParser, the file is explicitly opened
#   in UTF-8 mode.
# - Avoid indentation.

# =============================================================================
# Main section: [server]
# =============================================================================

[server]

# -----------------------------------------------------------------------------
# Database connection/tools
# -----------------------------------------------------------------------------

# DB_URL: SQLAlchemy connection URL.
# See http://docs.sqlalchemy.org/en/latest/core/engines.html
# Examples:
# - MySQL under Linux via mysqlclient
#   $$ pip install mysqlclient
#   DB_URL = mysql+mysqldb://<username>:<password>@<host>:<port>/<database>?charset=utf8
#
#   (The default MySQL port is 3306, and 'localhost' is often the right host.)
#
# - SQL Server under Windows via ODBC and username/password authentication
#   C:\> pip install pyodbc
#   DB_URL = mssql+pyodbc://<username>:<password>@<odbc_dsn_name>
#
# - ... or via Windows authentication: 
#   DB_URL = mssql+pyodbc://@<odbc_dsn_name>

DB_URL = mysql+mysqldb://${DEFAULT_DB_USER}:P${DEFAULT_DB_PASSWORD}@localhost:3306/${DEFAULT_DB_NAME}?charset=utf8

# DB_ECHO: echo all SQL?

DB_ECHO = False

# MYSQL: Specify the full path to the mysql executable, by default
# /usr/bin/mysql (used for data dumps for privileged users).

MYSQL = /usr/bin/mysql

# MYSQLDUMP: Specify the full path to the mysqldump executable, by default
# /usr/bin/mysqldump (used for data dumps for privileged users).

MYSQLDUMP = /usr/bin/mysqldump

# -----------------------------------------------------------------------------
# Database title and ID descriptions
# -----------------------------------------------------------------------------
# NOTE: WHENEVER YOU CHANGE THESE, YOU MUST USE THE CAMCOPS COMMAND-LINE TOOL
# TO REWRITE THEM INTO THE DATABASE.

# DATABASE_TITLE: the friendly title of your database (as Unicode UTF-8).

DATABASE_TITLE = My First CamCOPS Database

# IDDESC_1 to IDDESC_8: full descriptions of each of the possible ID numbers.
# IDSHORTDESC_1 to IDSHORTDESC_8: short versions of the same descriptions.
# All are Unicode UTF-8.

IDDESC_1 = NHS number
IDSHORTDESC_1 = NHS
IDDESC_2 = CPFT RiO number
IDSHORTDESC_2 = RiO
IDDESC_3 = CPFT M number
IDSHORTDESC_3 = M
IDDESC_4 = Addenbrooke’s number
IDSHORTDESC_4 = Add
IDDESC_5 = Papworth number
IDSHORTDESC_5 = Pap
IDDESC_6 = Hinchingbrooke number
IDSHORTDESC_6 = Hinch
IDDESC_7 = Peterborough City Hosp number
IDSHORTDESC_7 = PCH
IDDESC_8 = Spare_8_idnum
IDSHORTDESC_8 = Spare8

# -----------------------------------------------------------------------------
# ID policies
# -----------------------------------------------------------------------------
# NOTE: WHENEVER YOU CHANGE THESE, YOU MUST USE THE CAMCOPS COMMAND-LINE TOOL
# TO REWRITE THEM INTO THE DATABASE.

# UPLOAD_POLICY and FINALIZE_POLICY define two ID policies. The upload policy
# is the looser policy, allowing upload from tablets to the server. The
# finalize policy is typically the same or stricter, and allows records to
# be deleted from the tablets. See documentation.
#
# Case-insensitive. Valid tokens are:
#   (
#   )
#   AND
#   OR
#   forename
#   surname
#   dob
#   sex
#   idnum1 ... idnum8
#
# Liaison psychiatry upload example, allowing upload with any of multiple
# institutional IDs, but finalizing only with the institution's core ID:
#
# UPLOAD_POLICY = forename AND surname AND dob AND sex AND (idnum1 OR idnum2 OR idnum3 OR idnum4 OR idnum5 OR idnum6 OR idnum7 OR idnum8)
# FINALIZE_POLICY = forename AND surname AND dob AND sex AND idnum1
#
# Research pseudonym example, in which a single number is used and no
# patient-identifying information:
#
# UPLOAD_POLICY = sex AND idnum1
# FINALIZE_POLICY = sex AND idnum1

UPLOAD_POLICY = forename AND surname AND dob AND sex AND (idnum1 OR idnum2 OR idnum3 OR idnum4 OR idnum5 OR idnum6 OR idnum7 OR idnum8)
FINALIZE_POLICY = forename AND surname AND dob AND sex AND idnum1

# -----------------------------------------------------------------------------
# URLs and paths
# -----------------------------------------------------------------------------

# =============================================================================
# Site URL configuration
# =============================================================================

# A quick note on absolute and relative URLs, and how CamCOPS is mounted.
#
# Suppose your CamCOPS site is visible at
#       https://www.somewhere.ac.uk/camcops_smith_lab/webview
#       ^      ^^                 ^^                ^^      ^
#       +------++-----------------++----------------++------+
#       |       |                  |                 |
#       1       2                  3                 4
#
# Part 1 is the protocol, and part 2 the machine name.
# Part 3 is the mount point. The main server (e.g. Apache) knows where the
# CamCOPS script is mounted (in this case /camcops_smith_lab). It does NOT
# tell the script via the script's WSGI environment. Therefore, if the script
# sends HTML including links, the script can operate only in relative mode.
# For it to operate in absolute mode, it would need to know (3).
# Part 4 is visible to the CamCOPS script.
#
# If CamCOPS used URLs starting with '/', it would need to be told at least
# part (3). To use absolute URLs, it would need to know all of (1), (2), (3).
# We will follow others (e.g. http://stackoverflow.com/questions/2005079) and
# use only relative URLs.

# LOCAL_INSTITUTION_URL: Clicking on your institution's logo in the CamCOPS
# menu will take you to this URL.
# Edit the next line to point to your institution:

LOCAL_INSTITUTION_URL = ${DUMMY_INSTITUTION_URL}

# LOCAL_LOGO_FILE_ABSOLUTE: Specify the full path to your institution's logo
# file, e.g. /var/www/logo_local_myinstitution.png . It's used for PDF
# generation; HTML views use the fixed string "static/logo_local.png", aliased
# to your file via the Apache configuration file).
# Edit the next line to point to your local institution's logo file:

LOCAL_LOGO_FILE_ABSOLUTE = ${DSTSTATICDIR}/logo_local.png

# CAMCOPS_LOGO_FILE_ABSOLUTE: similarly, but for the CamCOPS logo.
# It's fine not to specify this.

# CAMCOPS_LOGO_FILE_ABSOLUTE = ${DSTSTATICDIR}/logo_camcops.png

# EXTRA_STRING_FILES: multiline list of filenames (with absolute paths), read
# by the server, and used as EXTRA STRING FILES. Should at the MINIMUM point
# to the string file camcops.xml
# May use "glob" pattern-matching (see
# https://docs.python.org/3.5/library/glob.html).

EXTRA_STRING_FILES = ${DSTEXTRASTRINGS}/*

# INTROSPECTION: permits the offering of CamCOPS source code files to the user,
# allowing inspection of tasks' internal calculating algorithms. Default is
# true.

INTROSPECTION = true

# HL7_LOCKFILE: filename stem used for process locking for HL7 message
# transmission. Default is ${DSTHL7LOCKFILESTEM}
# The actual lockfile will, in this case, be called
#     ${DSTHL7LOCKFILESTEM}.lock
# and other process-specific files will be created in the same directory (so
# the CamCOPS script must have permission from the operating system to do so).
# The installation script will create the directory ${DSTLOCKDIR}

HL7_LOCKFILE = ${DSTHL7LOCKFILESTEM}

# SUMMARY_TABLES_LOCKFILE: file stem used for process locking for summary table
# generation. Default is ${DSTSUMMARYTABLELOCKFILESTEM}.
# The lockfile will, in this case, be called
#     ${DSTSUMMARYTABLELOCKFILESTEM}.lock
# and other process-specific files will be created in the same directory (so
# the CamCOPS script must have permission from the operating system to do so).
# The installation script will create the directory ${DSTLOCKDIR}

SUMMARY_TABLES_LOCKFILE = ${DSTSUMMARYTABLELOCKFILESTEM}

# WKHTMLTOPDF_FILENAME: for the pdfkit PDF engine, specify a filename for
# wkhtmltopdf that incorporates any need for an X Server (not the default
# /usr/bin/wkhtmltopdf). See http://stackoverflow.com/questions/9604625/ .
# A suitable one is bundled with CamCOPS, so you shouldn't have to alter this
# default. Default is None, which usually ends up calling /usr/bin/wkhtmltopdf

WKHTMLTOPDF_FILENAME =

# -----------------------------------------------------------------------------
# Login and session configuration
# -----------------------------------------------------------------------------

# SESSION_COOKIE_SECRET: Secret used for HTTP cookie signing via Pyramid.
# Put something random in here and keep it secret.

SESSION_COOKIE_SECRET = camcops_autogenerated_secret_${SESSION_COOKIE_SECRET}

# SESSION_TIMEOUT_MINUTES: Time after which a session will expire (default 30).

SESSION_TIMEOUT_MINUTES = 30

# PASSWORD_CHANGE_FREQUENCY_DAYS: Force password changes (at webview login)
# with this frequency (0 for never). Note that password expiry will not prevent
# uploads from tablets, but when the user next logs on, a password change will
# be forced before they can do anything else.

PASSWORD_CHANGE_FREQUENCY_DAYS = 0

# LOCKOUT_THRESHOLD: Lock user accounts after every n login failures (default
# 10).

LOCKOUT_THRESHOLD = 10

# LOCKOUT_DURATION_INCREMENT_MINUTES: Account lockout time increment (default
# 10).
# Suppose LOCKOUT_THRESHOLD = 10 and LOCKOUT_DURATION_INCREMENT_MINUTES = 20.
# After the first 10 failures, the account will be locked for 20 minutes.
# After the next 10 failures, the account will be locked for 40 minutes.
# After the next 10 failures, the account will be locked for 60 minutes, and so
# on. Time and administrators can unlock accounts.

LOCKOUT_DURATION_INCREMENT_MINUTES = 10

# DISABLE_PASSWORD_AUTOCOMPLETE: if true, asks browsers not to autocomplete the
# password field on the main login page. The correct setting for maximum
# security is debated (don't cache passwords, versus allow a password manager
# so that users can use better/unique passwords). Default: true.
# Note that some browsers (e.g. Chrome v34 and up) may ignore this.

DISABLE_PASSWORD_AUTOCOMPLETE = true

# -----------------------------------------------------------------------------
# Suggested filenames for saving PDFs from the web view
# -----------------------------------------------------------------------------
# Try with Chrome, Firefox. Internet Explorer may be less obliging.

# PATIENT_SPEC_IF_ANONYMOUS: for anonymous tasks, this string is used as the
# patient descriptor (see also PATIENT_SPEC, SUGGESTED_PDF_FILENAME below).
# Typically "anonymous".

PATIENT_SPEC_IF_ANONYMOUS = anonymous

# PATIENT_SPEC: string, into which substitutions will be made, that defines the
# {patient} element available for substitution into the *_FILENAME_SPEC
# variables (see below). Possible substitutions:
#
#   {surname}      : patient's surname in upper case
#   {forename}     : patient's forename in upper case
#   {dob}          : patient's date of birth (format "%Y-%m-%d", e.g.
#                    2013-07-24)
#   {sex}          : patient's sex (M, F, X)
#
#   {idshortdesc1} : short description of the relevant ID number, if that ID
#   ...              number is not blank; otherwise blank
#   {idshortdesc8}
#
#   {idnum1}       : ID numbers
#   ...
#   {idnum8}
#
#   {allidnums}    : all available ID numbers in "shortdesc-value" pairs joined
#                    by "_". For example, if ID numbers 1, 4, and 5 are
#                    non-blank, this would have the format
#                    idshortdesc1-idval1_idshortdesc4-idval4_idshortdesc5-idval5

PATIENT_SPEC = {surname}_{forename}_{allidnums}

# TASK_FILENAME_SPEC:
# TRACKER_FILENAME_SPEC:
# CTV_FILENAME_SPEC:
# Strings used for suggested filenames to save from the webview, for tasks,
# trackers, and clinical text views. Substitutions will be made to determine
# the filename to be used for each file. Possible substitutions:
#
#   {patient}   : Patient string. If the task is anonymous, this is
#                 PATIENT_SPEC_IF_ANONYMOUS; otherwise, it is defined by
#                 PATIENT_SPEC above.
#   {created}   : Date/time of task creation.  Dates/times are of the format
#                 "%Y-%m-%dT%H%M", e.g. 2013-07-24T2004. They are expressed in
#                 the timezone of creation (but without the timezone
#                 information for filename brevity).
#   {now}       : Time of access/download (i.e. time now), in local timezone.
#   {tasktype}  : Base table name of the task (e.g. "phq9"). May contain an
#                 underscore. Blank for to trackers/CTVs.
#   {serverpk}  : Server's primary key. (In combination with tasktype, this
#                 uniquely identifies not just a task but a version of that
#                 task.) Blank for trackers/CTVs.
#   {filetype}  : e.g. "pdf", "html", "xml" (lower case)
#   {anonymous} : evaluates to PATIENT_SPEC_IF_ANONYMOUS if anonymous,
#                 otherwise ""
#   ... plus all those substitutions applicable to PATIENT_SPEC
#
# After these substitutions have been made, the entire filename is then
# processed to ensure that only characters generally acceptable to filenames
# are used (see convert_string_for_filename() in the CamCOPS source code).
# Specifically:
#
#   - Unicode converted to 7-bit ASCII (will mangle, e.g. removing accents)
#   - spaces converted to underscores
#   - characters are removed unless they are one of the following: all
#     alphanumeric characters (0-9, A-Z, a-z); '-'; '_'; '.'; and the
#     operating-system-specific directory separator (Python's os.sep, a forward
#     slash '/' on UNIX or a backslash '\' under Windows).

TASK_FILENAME_SPEC = CamCOPS_{patient}_{created}_{tasktype}-{serverpk}.{filetype}
TRACKER_FILENAME_SPEC = CamCOPS_{patient}_{now}_tracker.{filetype}
CTV_FILENAME_SPEC = CamCOPS_{patient}_{now}_clinicaltextview.{filetype}

# -----------------------------------------------------------------------------
# Debugging options
# -----------------------------------------------------------------------------
# Possible log levels are (case-insensitive): "debug", "info", "warn"
# (equivalent: "warning"), "error", and "critical" (equivalent: "fatal").

# WEBVIEW_LOGLEVEL: Set the level of detail provided from the webview to the
# Apache server log. (Loglevel option; see above.)

WEBVIEW_LOGLEVEL = info

# DBCLIENT_LOGLEVEL: Set the log level for the tablet client database access
# script. (Loglevel option; see above.)

DBCLIENT_LOGLEVEL = info

# ALLOW_INSECURE_COOKIES: DANGEROUS option that removes the requirement that
# cookies be HTTPS (SSL) only.

ALLOW_INSECURE_COOKIES = false

# -----------------------------------------------------------------------------
# Export to a staging database for CRIS, CRATE, or similar anonymisation
# software (anonymisation staging database; ANONSTAG)
# -----------------------------------------------------------------------------

ANONSTAG_DB_SERVER = localhost
ANONSTAG_DB_PORT = 3306
ANONSTAG_DB_NAME = ${DEFAULT_ANONSTAG_DB_NAME}
ANONSTAG_DB_USER = ${DEFAULT_ANONSTAG_DB_USER}
ANONSTAG_DB_PASSWORD = ${DEFAULT_ANONSTAG_DB_PASSWORD}
EXPORT_CRIS_DATA_DICTIONARY_TSV_FILE = /tmp/camcops_cris_dd_draft.tsv

# =============================================================================
# List of HL7/file recipients, and then details for each one
# =============================================================================
# This section defines a list of recipients to which Health Level Seven (HL7)
# messages or raw files will be sent. Typically, you will send them by calling
# "camcops -7 CONFIGFILE" regularly from the system's /etc/crontab or other
# scheduling system. For example, a conventional /etc/crontab file has these
# fields:
#
#   minutes, hours, day_of_month, month, day_of_week, user, command
#
# so you could add a line like this to /etc/crontab:
#
#   * * * * *  root  camcops -7 /etc/camcops/MYCONFIG.conf
#
# ... and CamCOPS would run its exports once per minute. See "man 5 crontab"
# or http://en.wikipedia.org/wiki/Cron for more options.
#
# In this section, keys are ignored; values are section headings (one per
# recipient).

[recipients]

# Examples (commented out):

# recipient=recipient_A
# recipient=recipient_B

# =============================================================================
# Individual HL7/file recipient configurations
# =============================================================================
# Dates are YYYY-MM-DD, e.g. 2013-12-31, or blank

# Example (disabled because it's not in the list above)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# First example
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[recipient_A]

# TYPE: one of the following methods.
#   hl7
#       Sends HL7 messages across a TCP/IP network.
#   file
#       Writes files to a local filesystem.

TYPE = hl7

# -----------------------------------------------------------------------------
# Options applicable to HL7 messages and file transfers
# -----------------------------------------------------------------------------

# PRIMARY_IDNUM: which ID number (1-8) should be considered the "internal"
# (primary) ID number? Must be specified for HL7 messages. May be blank for
# file transmission.

PRIMARY_IDNUM = 1

# REQUIRE_PRIMARY_IDNUM_MANDATORY_IN_POLICY: defines behaviour relating to the
# primary ID number (as defined by PRIMARY_IDNUM).
# - If true, no message sending will be attempted unless the PRIMARY_IDNUM is a
#   mandatory part of the finalizing policy (and if FINALIZED_ONLY is false,
#   also of the upload policy).
# - If false, messages will be sent, but ONLY FROM TASKS FOR WHICH THE
#   PRIMARY_IDNUM IS PRESENT; others will be ignored.
# - For file sending only, this will be ignored if PRIMARY_IDNUM is blank.
# - For file sending only, this setting does not apply to anonymous tasks,
#   whose behaviour is controlled by INCLUDE_ANONYMOUS (see below).

REQUIRE_PRIMARY_IDNUM_MANDATORY_IN_POLICY = true

# START_DATE: earliest date for which tasks will be sent. Assessed against the
# task's "when_created" field, converted to Universal Coordinated Time (UTC) --
# that is, this date is in UTC (beware if you are in a very different time
# zone). Blank to apply no start date restriction.

START_DATE =

# END_DATE: latest date for which tasks will be sent. In UTC. Assessed against
# the task's "when_created" field (converted to UTC). Blank to apply no end
# date restriction.

END_DATE =

# FINALIZED_ONLY: if true, only send tasks that are finalized (moved off their
# originating tablet and not susceptible to later modification). If false, also
# send tasks that are uploaded but not yet finalized (they will then be sent
# again if they are modified later).

FINALIZED_ONLY = true

# TASK_FORMAT: one of: pdf, html, xml

TASK_FORMAT = pdf

# XML_FIELD_COMMENTS: if TASK_FORMAT is xml, then XML_FIELD_COMMENTS determines
# whether field comments are included. These describe the meaning of each field
# so add to space requirements but provide more information for human readers.
# (Default true.)

XML_FIELD_COMMENTS = true

# -----------------------------------------------------------------------------
# Options applicable to HL7 only (TYPE = hl7)
# -----------------------------------------------------------------------------

# HOST: HL7 hostname or IP address

HOST = myhl7server.mydomain

# PORT: HL7 port (default 2575)

PORT = 2575

# PING_FIRST: if true, requires a successful ping to the server prior to
# sending HL7 messages. (Note: this is a TCP/IP ping, and tests that the
# machine is up, not that it is running an HL7 server.) Default: true.

PING_FIRST = true

# NETWORK_TIMEOUT_MS: network time (in milliseconds). Default: 10000.

NETWORK_TIMEOUT_MS = 10000

# IDNUM_TYPE_1 ... IDNUM_TYPE_8: strings used as the HL7 identifier type code
# in the PID segment, field 3 (internal ID) list of identifiers. If one is
# blank, its information will not be sent. (If the PRIMARY_IDNUM's type is
# blank, the system will not process messages.)

IDNUM_TYPE_1 = NHS
IDNUM_TYPE_2 = RiO
IDNUM_TYPE_3 = M
IDNUM_TYPE_4 = Add
IDNUM_TYPE_5 = Pap
IDNUM_TYPE_6 = Hinch
IDNUM_TYPE_7 = PCH
IDNUM_TYPE_8 =

# IDNUM_AA_1 ... IDNUM_AA_8: strings used as the Assigning Authority in the PID
# segment, field 3 (internal ID) list of identifiers. Optional.

IDNUM_AA_1 = NHS
IDNUM_AA_2 = CPFT
IDNUM_AA_3 = CPFT
IDNUM_AA_4 = CUH
IDNUM_AA_5 = CUH
IDNUM_AA_6 = HHC
IDNUM_AA_7 = PSH
IDNUM_AA_8 =

# KEEP_MESSAGE: keep a copy of the entire message in the databaase. Default is
# false. WARNING: may consume significant space in the database.

KEEP_MESSAGE = false

# KEEP_REPLY: keep a copy of the reply (e.g. acknowledgement) message received
# from the server. Default is false. WARNING: may consume significant space.

KEEP_REPLY = false

# DIVERT_TO_FILE: Override HOST/PORT options and send HL7 messages to this
# (single) file instead. Each messages is appended to the file. Default is
# blank (meaning network transmission will be used). This is a debugging
# option, allowing you to redirect HL7 messages to a file and inspect them.

DIVERT_TO_FILE =

# TREAT_DIVERTED_AS_SENT: Any messages that are diverted to a file (using
# DIVERT_TO_FILE) are treated as having been sent (thus allowing the file to
# mimic an HL7-receiving server that's accepting messages happily). If set to
# false (the default), a diversion will allow you to preview messages for
# debugging purposes without "swallowing" them. BEWARE, though: if you have
# an automatically scheduled job (for example, to send messages every minute)
# and you divert with this flag set to false, you will end up with a great many
# message attempts!

TREAT_DIVERTED_AS_SENT = false

# -----------------------------------------------------------------------------
# Options applicable to file transfers only (TYPE = file)
# -----------------------------------------------------------------------------

# INCLUDE_ANONYMOUS: include anonymous tasks.
# - Note that anonymous tasks cannot be sent via HL7; the HL7 specification is
#   heavily tied to identification.
# - Note also that this setting operates independently of the
#   REQUIRE_PRIMARY_IDNUM_MANDATORY_IN_POLICY setting.

INCLUDE_ANONYMOUS = true

# PATIENT_SPEC_IF_ANONYMOUS: for anonymous tasks, this string is used as the
# patient descriptor (see also PATIENT_SPEC, FILENAME_SPEC below). Typically
# "anonymous".

PATIENT_SPEC_IF_ANONYMOUS = anonymous

# PATIENT_SPEC: string, into which substitutions will be made, that defines the
# {patient} element available for substitution into the FILENAME_SPEC (see
# below). Possible substitutions: as for PATIENT_SPEC in the main "[server]"
# section of the configuration file (see above).

PATIENT_SPEC = {surname}_{forename}_{idshortdesc1}{idnum1}

# FILENAME_SPEC: string into which substitutions will be made to determine the
# filename to be used for each file. Possible substitutions: as for
# SUGGESTED_PDF_FILENAME in the main "[server]" section of the configuration
# file (see above).

FILENAME_SPEC = /my_nfs_mount/mypath/CamCOPS_{patient}_{created}_{tasktype}-{serverpk}.{filetype}

# MAKE_DIRECTORY: make the directory if it doesn't already exist. Default is
# false.

MAKE_DIRECTORY = true

# OVERWRITE_FILES: whether or not to attempt overwriting existing files of the
# same name (default false). There is a DANGER of inadvertent data loss if you
# set this to true. (Needing to overwrite a file suggests that your filenames
# are not task-unique; try ensuring that both the {tasktype} and {serverpk}
# attributes are used in the filename.)

OVERWRITE_FILES = false

# RIO_METADATA: whether or not to export a metadata file for Servelec's RiO
# (default false).
# Details of this file format are in cc_task.py / Task.get_rio_metadata().
# The metadata filename is that of its associated file, but with the extension
# replaced by ".metadata" (e.g. X.pdf is accompanied by X.metadata).
# If RIO_METADATA is true, the following options also apply:
#   RIO_IDNUM: which of the ID numbers (as above) is the RiO ID?
#   RIO_UPLOADING_USER: username for the uploading user (maximum of 10
#       characters)
#   RIO_DOCUMENT_TYPE: document type as defined in the receiving RiO system.
#       This is a code that maps to a human-readable document type; for
#       example, the code "APT" might map to "Appointment Letter". Typically we
#       might want a code that maps to "Clinical Correspondence", but the code
#       will be defined within the local RiO system configuration.

RIO_METADATA = false
RIO_IDNUM = 2
RIO_UPLOADING_USER = CamCOPS
RIO_DOCUMENT_TYPE = CC

# SCRIPT_AFTER_FILE_EXPORT: filename of a shell script or other executable to
# run after file export is complete. You might use this script, for example, to
# move the files to a different location (such as across a network). If the
# parameter is blank, no script will be run. If no files are exported, the
# script will not be run.
# - Parameters passed to the script: a list of all the filenames exported.
#   (This includes any RiO metadata filenames.)
# - WARNING: the script will execute with the same permissions as the instance
#   of CamCOPS that's doing the export (so, for example, if you run CamCOPS
#   from your /etc/crontab as root, then this script will be run as root; that
#   can pose a risk!).
# - The script executes while the export lock is still held by CamCOPS (i.e.
#   further HL7/file transfers won't be started until the script(s) is/are
#   complete).
# - If the script fails, an error message is recorded, but the file transfer is
#   still considered to have been made (CamCOPS has done all it can and the
#   responsibility now lies elsewhere).
# - Example test script: suppose this is /usr/local/bin/print_arguments:
#       #!/bin/bash
#       for f in $$@
#       do
#           echo "CamCOPS has just exported this file: $$f"
#       done
#   ... then you could set:
#       SCRIPT_AFTER_FILE_EXPORT = /usr/local/bin/print_arguments

SCRIPT_AFTER_FILE_EXPORT =

    """).substitute(  # noqa
        DEFAULT_ANONSTAG_DB_NAME=DEFAULT_ANONSTAG_DB_NAME,
        DEFAULT_ANONSTAG_DB_PASSWORD=DEFAULT_ANONSTAG_DB_PASSWORD,
        DEFAULT_ANONSTAG_DB_USER=DEFAULT_ANONSTAG_DB_USER,
        DEFAULT_DB_NAME=DEFAULT_DB_NAME,
        DEFAULT_DB_PASSWORD=DEFAULT_DB_PASSWORD,
        DEFAULT_DB_USER=DEFAULT_DB_USER,
        DSTBASEDIR=camcops_base_dir,
        DSTEXTRASTRINGS=extra_strings_dir,
        DSTHL7LOCKFILESTEM=hl7_lockfile_stem,
        DSTLOCKDIR=lock_dir,
        DSTSTATICDIR=static_dir,
        DSTSUMMARYTABLELOCKFILESTEM=summary_table_lock_file_stem,
        DUMMY_INSTITUTION_URL=DUMMY_INSTITUTION_URL,
        SESSION_COOKIE_SECRET=session_cookie_secret,
    )


_OLD_BITS_DISABLED = """

# -----------------------------------------------------------------------------
# Analytics
# -----------------------------------------------------------------------------

# SEND_ANALYTICS: Send analytics to the CamCOPS base in Cambridge? (Boolean
# option; default true.) We'd be very grateful if you would leave this on, as
# it helps us to know how many users of CamCOPS there are and what tasks are
# popular. NO PATIENT-IDENTIFIABLE INFORMATION, PER-PATIENT INFORMATION, OR
# TASK DETAILS ARE SENT. If enabled, the following information is sent weekly
# to the CamCOPS base computer:
# - the date/time, including timezone (allowing us to get a rough idea of its
#   geographical distribution)
# - IP address (allowing us to get a rough idea of geographical/institutional
#   distribution)
# - the CamCOPS version number (so we know if old versions are still in use, or
#   if we can break them in an upgrade)
# - the total number of records in each table (allowing us to get an idea of
#   which tasks are popular)

SEND_ANALYTICS = true

"""


# =============================================================================
# Configuration class. (It gets cached on a per-process basis.)
# =============================================================================

class CamcopsConfig(object):
    """Process-local storage class. One instance per process. Persists across
    sessions thanks to mod_wsgi."""

    def __init__(self, config_filename: str) -> None:
        """Initialize from config file."""

        # ---------------------------------------------------------------------
        # Open config file
        # ---------------------------------------------------------------------
        self.camcops_config_file = config_filename
        if not self.camcops_config_file:
            raise AssertionError("{} not specified".format(ENVVAR_CONFIG_FILE))
        log.info("Reading from {}", self.camcops_config_file)
        config = configparser.ConfigParser()
        with codecs.open(self.camcops_config_file, "r", "utf8") as file:
            config.read_file(file)

        # ---------------------------------------------------------------------
        # Read from the config file: 1. Most stuff, in alphabetical order
        # ---------------------------------------------------------------------
        section = CONFIG_FILE_MAIN_SECTION

        self.allow_insecure_cookies = get_config_parameter_boolean(
            config, section, "ALLOW_INSECURE_COOKIES", False)

        self.camcops_logo_file_absolute = get_config_parameter(
            config, section, "CAMCOPS_LOGO_FILE_ABSOLUTE", str,
            DEFAULT_CAMCOPS_LOGO_FILE)

        self.ctv_filename_spec = get_config_parameter(
            config, section, "CTV_FILENAME_SPEC", str, None)

        self.database_title = get_config_parameter(
            config, section, "DATABASE_TITLE", str, DEFAULT_DATABASE_TITLE)
        self.db_url = config.get(section, "DB_URL")
        # ... no default: will fail if not provided
        self.db_echo = get_config_parameter_boolean(
            config, section, "DB_ECHO", False)
        self.dbclient_loglevel = get_config_parameter_loglevel(
            config, section, "DBCLIENT_LOGLEVEL", logging.INFO)
        logging.getLogger("camcops_server.database")\
            .setLevel(self.dbclient_loglevel)
        # ... MUTABLE GLOBAL STATE (if relatively unimportant); *** fix

        self.disable_password_autocomplete = get_config_parameter_boolean(
            config, section, "DISABLE_PASSWORD_AUTOCOMPLETE", True)

        self.export_cris_data_dictionary_tsv_file = get_config_parameter(
            config, section, "EXPORT_CRIS_DATA_DICTIONARY_TSV_FILE", str, None)
        self.extra_string_files = get_config_parameter_multiline(
            config, section, "EXTRA_STRING_FILES", [])

        self.hl7_lockfile = get_config_parameter(
            config, section, "HL7_LOCKFILE", str, None)

        # The ConfigParser forces all its keys to lower care.
        self.iddesc = {}  # type: Dict[int, str]
        self.idshortdesc = {}  # type: Dict[int, str]
        descprefix = "iddesc_"
        shortdescprefix = "idshortdesc_"
        for key, desc in config.items(section):
            if key.startswith(descprefix):
                nstr = key[len(descprefix):]
                try:
                    which_idnum = int(nstr)
                except (TypeError, ValueError):
                    raise AssertionError(
                        "Bad ID description config key: " + repr(key))
                if which_idnum <= 0:
                    raise AssertionError(
                        "Bad ID number: {} (must be >=1)".format(nstr))
                if not desc:
                    raise AssertionError(
                        "Bad description for ID {}: {}".format(
                            nstr, repr(desc)))
                shortdesc = get_config_parameter(
                    config, section, shortdescprefix + nstr, str, "")
                if not shortdesc:
                    raise AssertionError(
                        "ID number {} has description but no short "
                        "description".format(nstr))
                self.iddesc[which_idnum] = desc
                self.idshortdesc[which_idnum] = shortdesc

        self.id_policy_upload_string = get_config_parameter(
            config, section, "UPLOAD_POLICY", str, "")
        self.id_policy_finalize_string = get_config_parameter(
            config, section, "FINALIZE_POLICY", str, "")
        self.introspection = get_config_parameter_boolean(
            config, section, "INTROSPECTION", True)

        self.local_institution_url = get_config_parameter(
            config, section, "LOCAL_INSTITUTION_URL",
            str, DEFAULT_LOCAL_INSTITUTION_URL)
        self.local_logo_file_absolute = get_config_parameter(
            config, section, "LOCAL_LOGO_FILE_ABSOLUTE",
            str, DEFAULT_LOCAL_LOGO_FILE)
        self.lockout_threshold = get_config_parameter(
            config, section, "LOCKOUT_THRESHOLD",
            int, DEFAULT_LOCKOUT_THRESHOLD)
        self.lockout_duration_increment_minutes = get_config_parameter(
            config, section, "LOCKOUT_DURATION_INCREMENT_MINUTES",
            int, DEFAULT_LOCKOUT_DURATION_INCREMENT_MINUTES)

        self.mysql = get_config_parameter(
            config, section, "MYSQL", str, DEFAULT_MYSQL)
        self.mysqldump = get_config_parameter(
            config, section, "MYSQLDUMP", str, DEFAULT_MYSQLDUMP)

        self.password_change_frequency_days = get_config_parameter(
            config, section, "PASSWORD_CHANGE_FREQUENCY_DAYS",
            int, DEFAULT_PASSWORD_CHANGE_FREQUENCY_DAYS)
        self.patient_spec_if_anonymous = get_config_parameter(
            config, section, "PATIENT_SPEC_IF_ANONYMOUS", str, "anonymous")
        self.patient_spec = get_config_parameter(
            config, section, "PATIENT_SPEC", str, None)
        # currently not configurable, but easy to add in the future:
        self.plot_fontsize = DEFAULT_PLOT_FONTSIZE

        # self.send_analytics = get_config_parameter_boolean(
        #     config, section, "SEND_ANALYTICS", True)
        session_timeout_minutes = get_config_parameter(
            config, section, "SESSION_TIMEOUT_MINUTES",
            int, DEFAULT_TIMEOUT_MINUTES)
        self.session_cookie_secret = get_config_parameter(
            config, section, "SESSION_COOKIE_SECRET", str, None)
        self.session_timeout = datetime.timedelta(
            minutes=session_timeout_minutes)
        self.summary_tables_lockfile = get_config_parameter(
            config, section, "SUMMARY_TABLES_LOCKFILE", str, None)

        self.task_filename_spec = get_config_parameter(
            config, section, "TASK_FILENAME_SPEC", str, None)
        self.tracker_filename_spec = get_config_parameter(
            config, section, "TRACKER_FILENAME_SPEC", str, None)

        self.webview_loglevel = get_config_parameter_loglevel(
            config, section, "WEBVIEW_LOGLEVEL", logging.INFO)
        logging.getLogger().setLevel(self.webview_loglevel)  # root logger
        # ... MUTABLE GLOBAL STATE (if relatively unimportant) *** fix

        self.wkhtmltopdf_filename = get_config_parameter(
            config, section, "WKHTMLTOPDF_FILENAME", str, None)

        # ---------------------------------------------------------------------
        # Read from the config file: 2. HL7 section
        # ---------------------------------------------------------------------
        # http://stackoverflow.com/questions/335695/lists-in-configparser
        self.hl7_recipient_defs = []  # type: List[RecipientDefinition]
        try:
            hl7_items = config.items(CONFIG_FILE_RECIPIENTLIST_SECTION)
            for key, recipientdef_name in hl7_items:
                log.debug("HL7 config: key={}, recipientdef_name={}",
                          key, recipientdef_name)
                h = RecipientDefinition(
                    valid_which_idnums=self.get_which_idnums(),
                    config=config,
                    section=recipientdef_name)
                if h.valid:
                    self.hl7_recipient_defs.append(h)
        except configparser.NoSectionError:
            log.info("No config file section [{}]",
                     CONFIG_FILE_RECIPIENTLIST_SECTION)

        # ---------------------------------------------------------------------
        # Built from the preceding:
        # ---------------------------------------------------------------------

        self.introspection_files = []  # type: List[IntrospectionFileDetails]
        if self.introspection:
            # All introspection starts at INTROSPECTION_BASE_DIRECTORY
            rootdir = INTROSPECTION_BASE_DIRECTORY
            for dir_, subdirs, files in os.walk(rootdir):
                if dir_ == rootdir:
                    pretty_dir = ''
                else:
                    pretty_dir = os.path.relpath(dir_, rootdir)
                for filename in files:
                    basename, ext = os.path.splitext(filename)
                    if ext not in INTROSPECTABLE_EXTENSIONS:
                        continue
                    fullpath = os.path.join(dir_, filename)
                    prettypath = os.path.join(pretty_dir, filename)
                    self.introspection_files.append(
                        IntrospectionFileDetails(
                            fullpath=fullpath,
                            prettypath=prettypath,
                            ext=ext
                        )
                    )
            self.introspection_files = sorted(
                self.introspection_files,
                key=operator.attrgetter("prettypath"))

        valid_which_idnums = self.get_which_idnums()

        # Cache tokenized ID policies
        tokenize_upload_id_policy(policy=self.id_policy_upload_string,
                                  valid_which_idnums=valid_which_idnums)
        tokenize_finalize_id_policy(policy=self.id_policy_finalize_string,
                                    valid_which_idnums=valid_which_idnums)
        # ---------------------------------------------------------------------
        # Valid?
        # ---------------------------------------------------------------------
        if not upload_id_policy_valid():
            raise RuntimeError(
                "UPLOAD_POLICY invalid in config (policy: {})".format(
                    repr(self.id_policy_upload_string)))
        if not finalize_id_policy_valid():
            raise RuntimeError(
                "FINALIZE_POLICY invalid in config (policy: {})".format(
                    repr(self.id_policy_finalize_string)))

        if not self.patient_spec_if_anonymous:
            raise RuntimeError("Blank PATIENT_SPEC_IF_ANONYMOUS in [server] "
                               "section of config file")

        if not self.patient_spec:
            raise RuntimeError("Missing/blank PATIENT_SPEC in [server] section"
                               " of config file")
        if not patient_spec_for_filename_is_valid(
                patient_spec=self.patient_spec,
                valid_which_idnums=valid_which_idnums):
            raise RuntimeError("Invalid PATIENT_SPEC in [server] section of "
                               "config file")

        if not self.session_cookie_secret:
            raise RuntimeError("Invalid or missing SESSION_COOKIE_SECRET "
                               "setting in [server] section of config file")

        if not self.task_filename_spec:
            raise RuntimeError("Missing/blank TASK_FILENAME_SPEC in "
                               "[server] section of config file")
        if not filename_spec_is_valid(self.task_filename_spec,
                                      valid_which_idnums=valid_which_idnums):
            raise RuntimeError("Invalid TASK_FILENAME_SPEC in "
                               "[server] section of config file")

        if not self.tracker_filename_spec:
            raise RuntimeError("Missing/blank TRACKER_FILENAME_SPEC in "
                               "[server] section of config file")
        if not filename_spec_is_valid(self.tracker_filename_spec,
                                      valid_which_idnums=valid_which_idnums):
            raise RuntimeError("Invalid TRACKER_FILENAME_SPEC in "
                               "[server] section of config file")

        if not self.ctv_filename_spec:
            raise RuntimeError("Missing/blank CTV_FILENAME_SPEC in "
                               "[server] section of config file")
        if not filename_spec_is_valid(self.ctv_filename_spec,
                                      valid_which_idnums=valid_which_idnums):
            raise RuntimeError("Invalid CTV_FILENAME_SPEC in "
                               "[server] section of config file")

        # Moved out from CamcopsConfig:
        # ---------------------------------------------------------------------
        # Read from the WSGI environment
        # ---------------------------------------------------------------------
        # self.remote_addr = environ.get("REMOTE_ADDR")
        #       -> Request.remote_addr (Pyramid)
        # self.remote_port = environ.get("REMOTE_PORT")
        #       -> not in Pyramid Request object? Unimportant
        #          Will be available as request.environ["REMOTE_PORT"]
        # # self.SCRIPT_NAME = environ.get("SCRIPT_NAME", "")
        # self.SCRIPT_NAME = URL_RELATIVE_WEBVIEW
        #       -> Request.script_name (Pyramid)
        #       *** CHECK: script_name is different from URL_RELATIVE_WEBVIEW
        # self.SERVER_NAME = environ.get("SERVER_NAME")
        #       -> Request.server_name (Pyramid)
        # ---------------------------------------------------------------------
        # More complex, WSGI-derived
        # ---------------------------------------------------------------------
        #     # Reconstruct URL:
        #     # http://www.python.org/dev/peps/pep-0333/#url-reconstruction
        #     protocol = environ.get("wsgi.url_scheme", "")
        #     if environ.get("HTTP_HOST"):
        #         host = environ.get("HTTP_HOST")
        #     else:
        #         host = environ.get("SERVER_NAME", "")
        #     port = ""
        #     server_port = environ.get("SERVER_PORT")
        #     if (server_port and
        #             ":" not in host and
        #             not(protocol == "https" and server_port == "443") and
        #             not(protocol == "http" and server_port == "80")):
        #         port = ":" + server_port
        #     script = urllib.parse.quote(environ.get("SCRIPT_NAME", ""))
        #     path = urllib.parse.quote(environ.get("PATH_INFO", ""))
        #
        #     # But not the query string:
        #     # if environ.get("QUERY_STRING"):
        #     #    query += "?" + environ.get("QUERY_STRING")
        #     # else:
        #     #    query = ""
        #
        #     url = "{protocol}://{host}{port}{script}{path}".format(
        #         protocol=protocol,
        #         host=host,
        #         port=port,
        #         script=script,
        #         path=path,
        #     )
        #
        #     self.SCRIPT_PUBLIC_URL_ESCAPED = escape(url)
        #
        #           -> ***

    def create_engine(self) -> Engine:
        return create_engine(
            self.db_url,
            echo=self.db_echo,
            pool_pre_ping=True,
            # pool_size=0,  # no limit (for parallel testing, which failed)
        )

    @property
    @cache_region_static.cache_on_arguments(function_key_generator=fkg)
    def get_all_table_names(self) -> List[str]:
        engine = self.create_engine()
        return get_table_names(engine=engine)

    def get_which_idnums(self) -> List[int]:
        return sorted(list(self.iddesc.keys()))

    def get_id_desc(self, which_idnum: int,
                    default: str = None) -> Optional[str]:
        """Get server's ID description."""
        return self.iddesc.get(which_idnum, default)

    def get_id_shortdesc(self, which_idnum: int,
                         default: str = None) -> Optional[str]:
        """Get server's short ID description."""
        return self.idshortdesc.get(which_idnum, default)

    @contextlib.contextmanager
    def get_dbsession_context(self) -> Generator[SqlASession, None, None]:
        engine = self.create_engine()
        maker = sessionmaker(bind=engine)
        dbsession = maker()  # type: SqlASession
        # noinspection PyBroadException
        try:
            yield dbsession
            dbsession.commit()
        except Exception:
            dbsession.rollback()
        finally:
            dbsession.close()

    # def get_anonymisation_database(self) -> rnc_db.DatabaseSupporter:
    #     """Open the anonymisation staging database. That is not performance-
    #     critical and the connection does not need to be cached. Will raise
    #     an exception upon a connection error."""
    #     # Follows same security principles as above.
    #     config = configparser.ConfigParser()
    #     config.read_file(codecs.open(self.CAMCOPS_CONFIG_FILE, "r", "utf8"))
    #     section = CONFIG_FILE_MAIN_SECTION
    #
    #     server = get_config_parameter(
    #         config, section, "ANONSTAG_DB_SERVER", str, DEFAULT_DB_SERVER)
    #     port = get_config_parameter(
    #         config, section, "ANONSTAG_DB_PORT", int, DEFAULT_DB_PORT)
    #     database = get_config_parameter(
    #         config, section, "ANONSTAG_DB_NAME", str, None)
    #     if database is None:
    #         raise RuntimeError("ANONSTAG_DB_NAME not specified in config")
    #     user = get_config_parameter(
    #         config, section, "ANONSTAG_DB_USER", str, None)
    #     if user is None:
    #         raise RuntimeError("ANONSTAG_DB_USER not specified in config")
    #     # It is a potential disaster if the anonymisation database is the same
    #     # database as the main database - risk of destroying original data.
    #     # We mitigate this risk in two ways.
    #     # (1) We check here. Since different server/port combinations could
    #     #     resolve to the same host, we take the extremely conservative
    #     #     approach of requiring a different database name.
    #     if database == self.DB_NAME:
    #         raise RuntimeError("ANONSTAG_DB_NAME must be different from "
    #                            "DB_NAME")
    #     # (2) We prefix all tablenames in the CRIS staging database;
    #     #     see cc_task.
    #     try:
    #         password = get_config_parameter(
    #             config, section, "ANONSTAG_DB_PASSWORD", str, None)
    #     except:  # deliberately conceal details for security
    #         # noinspection PyUnusedLocal
    #         password = None
    #         raise RuntimeError("Problem reading ANONSTAG_DB_PASSWORD from "
    #                            "config")
    #     if password is None:
    #         raise RuntimeError("ANONSTAG_DB_PASSWORD not specified in config")
    #     try:
    #         db = rnc_db.DatabaseSupporter()
    #         db.connect_to_database_mysql(
    #             server=server,
    #             port=port,
    #             database=database,
    #             user=user,
    #             password=password,
    #             autocommit=False  # NB therefore need to commit
    #             # ... done in camcops.py at the end of a session
    #         )
    #     except:  # deliberately conceal details for security
    #         raise rnc_db.NoDatabaseError(
    #             "Problem opening or reading from database; details concealed "
    #             "for security reasons")
    #     finally:
    #         # Executed whether an exception is raised or not.
    #         # noinspection PyUnusedLocal
    #         password = None
    #     # -------------------------------------------------------------------
    #     # Password is now re-obscured in all situations. Onwards...
    #     # -------------------------------------------------------------------
    #     return db

    def get_database_title_html(self) -> str:
        """Database title as HTML-safe unicode."""
        if not self.database_title:
            return ""
        return "Database: <b>{}</b>.".format(ws.webify(self.database_title))


# =============================================================================
# Get config filename from an appropriate environment (WSGI or OS)
# =============================================================================

def get_config_filename(environ: Dict[str, str] = None) -> str:
    config_filename = None
    if environ is not None:
        # This may be used for WSGI environments
        config_filename = environ.get(ENVVAR_CONFIG_FILE)
    if config_filename is None:
        # Fall back to OS environment
        config_filename = os.environ.get(ENVVAR_CONFIG_FILE)
    if not config_filename:
        raise AssertionError(
            "Neither WSGI nor OS environment provided the required "
            "environment variable {}".format(ENVVAR_CONFIG_FILE))
    return config_filename


# =============================================================================
# Cached instances
# =============================================================================

@cache_region_static.cache_on_arguments(function_key_generator=fkg)
def get_config(config_filename: str) -> CamcopsConfig:
    return CamcopsConfig(config_filename)


# =============================================================================
# Get default config
# =============================================================================

def get_default_config_from_os_env() -> CamcopsConfig:
    return get_config(get_config_filename())
