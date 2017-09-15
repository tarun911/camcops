#!/usr/bin/env python
# camcops_server/cc_modules/cc_baseconstants.py

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

Constants required during package creation, which therefore can't rely on
anything except the Python standard library.

By simple extension, also directory/filename definitions within the server
tree.

Also, for visibility, environment variable names.
"""

from os import pardir
from os.path import abspath, dirname, join

# =============================================================================
# Environment variable names
# =============================================================================

ENVVAR_CONFIG_FILE = "CAMCOPS_CONFIG_FILE"

# =============================================================================
# Directories and filenames
# =============================================================================

_this_directory = dirname(abspath(__file__))  # cc_modules
CAMCOPS_SERVER_DIRECTORY = abspath(join(_this_directory, pardir))  # camcops_server  # noqa

ALEMBIC_BASE_DIR = CAMCOPS_SERVER_DIRECTORY
ALEMBIC_CONFIG_FILENAME = join(ALEMBIC_BASE_DIR, 'alembic.ini')

STATIC_ROOT_DIR = join(CAMCOPS_SERVER_DIRECTORY, 'static')
TEMPLATE_DIR = join(CAMCOPS_SERVER_DIRECTORY, 'templates')
TABLET_SOURCE_COPY_DIR = join(CAMCOPS_SERVER_DIRECTORY, "tablet_source_copy")
# ... used by setup.py to copy tablet source files into package

# =============================================================================
# Introspectable extensions
# =============================================================================

INTROSPECTABLE_EXTENSIONS = [".cpp", ".h", ".html", ".js", ".jsx",
                             ".py", ".pl", ".qml", ".xml"]
# ... used by setup.py to determine what to copy
