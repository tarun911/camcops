#!/usr/bin/env python
# camcops_server/cc_modules/cc_plot.py

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

# =============================================================================
# Basic imports
# =============================================================================

import atexit
import logging
import os
import shutil
import tempfile

from cardinal_pythonlib.logs import BraceStyleAdapter
import cardinal_pythonlib.plot as rnc_plot

log = BraceStyleAdapter(logging.getLogger(__name__))


# =============================================================================
# Import matplotlib
# =============================================================================

# We need to use os.environ, since per-request stuff won't be initialized yet.
# That goes for anything that affects imports (to avoid the complexity of
# delayed imports).
if 'MPLCONFIGDIR' in os.environ:
    # 1+2. Use a writable static directory (speeds pyplot loads hugely).
    MPLCONFIGDIR = os.environ['MPLCONFIGDIR']
else:
    # 1. Make a temporary directory (must be a directory per process, I'm sure)
    MPLCONFIGDIR = tempfile.mkdtemp()
    # 2. Ensure temporary directory is removed when this process exits.
    atexit.register(lambda: shutil.rmtree(MPLCONFIGDIR, ignore_errors=True))

# 3. Tell matplotlib about this directory prior to importing it
#    http://matplotlib.org/faq/environment_variables_faq.html
os.environ["MPLCONFIGDIR"] = MPLCONFIGDIR

# 4. Another nasty matplotlib hack
#    matplotlib.font_manager reads os.environ.get('HOME') directly, and
#    searches ~/.fonts for fonts. That's fine unless a user is calling with
#    sudo -u USER, leaving $HOME as it was but removing the permissions - then
#    matplotlib crashes out with e.g.
#       PermissionError: [Errno 13] Permission denied: '/home/rudolf/.fonts/SABOI___.TTF'  # noqa
#    Note that an empty string won't help either, since the check is
#    "is not None".
#    You can't assign None to an os.environ member; see
#    http://stackoverflow.com/questions/3575165; do this:
if 'HOME' in os.environ:
    del os.environ['HOME']

# 5. Import matplotlib
log.info("Importing matplotlib (can be slow) (MPLCONFIGDIR={})...",
         MPLCONFIGDIR)
import matplotlib  # noqa

# 6. Set the backend
matplotlib.use("Agg")  # also the default backend
# ... http://matplotlib.org/faq/usage_faq.html#what-is-a-backend
# ... http://matplotlib.org/faq/howto_faq.html
# matplotlib.use("cairo") # cairo backend corrupts some SVG figures

# Load this once so we can tell the user we're importing it and it's slow
import matplotlib.pyplot  # noqa
log.info("... finished importing matplotlib")

# THEN DO e.g. # import matplotlib.pyplot as plt


# =============================================================================
# Functions to configure matplotlib
# =============================================================================

def set_matplotlib_fontsize(fontsize: float) -> None:
    """Sets the font size for matplotlib."""
    rnc_plot.set_matplotlib_fontsize(matplotlib, fontsize)


def ccplot_do_nothing() -> None:
    """Call to justify an import, as seen by pyflakes, whereas the real
    justification is to configure matplotlib at first import."""
    pass
