#!/usr/bin/env python
# camcops_server/cc_modules/cc_tracker.py

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

from typing import Any, Dict

from cardinal_pythonlib.pdf import get_pdf_from_html

from .cc_constants import PDF_ENGINE, WKHTMLTOPDF_OPTIONS
from .cc_request import CamcopsRequest


def pdf_from_html(req: CamcopsRequest,
                  html: str,
                  header_html: str = None,
                  footer_html: str = None,
                  extra_wkhtmltopdf_options: Dict[str, Any] = None):
    extra_wkhtmltopdf_options = extra_wkhtmltopdf_options or {}  # type: Dict[str, Any]  # noqa
    wkhtmltopdf_options = dict(WKHTMLTOPDF_OPTIONS,
                               **extra_wkhtmltopdf_options)
    cfg = req.config
    return get_pdf_from_html(html,
                             header_html=header_html,
                             footer_html=footer_html,
                             processor=PDF_ENGINE,
                             wkhtmltopdf_filename=cfg.WKHTMLTOPDF_FILENAME,
                             wkhtmltopdf_options=wkhtmltopdf_options)