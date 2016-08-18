#!/usr/bin/env python3
# irac.py

"""
    Copyright (C) 2012-2016 Rudolf Cardinal (rudolf@pobox.com).
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

import cardinal_pythonlib.rnc_web as ws

from ..cc_modules.cc_html import tr_qa
from ..cc_modules.cc_string import WSTRING
from ..cc_modules.cc_task import get_from_dict, Task


# =============================================================================
# IRAC
# =============================================================================

class Irac(Task):
    tablename = "irac"
    shortname = "IRAC"
    longname = "Identify and Rate the Aim of the Contact"
    fieldspecs = [
        dict(name="aim", cctype="TEXT",
             comment="Main aim of the contact"),
        dict(name="achieved", cctype="INT", min=0, max=2,
             comment="Was the aim achieved? (0 not, 1 partially, 2 fully)"),
    ]

    TASK_FIELDS = [x["name"] for x in fieldspecs]

    def is_complete(self) -> bool:
        return (self.are_all_fields_complete(self.TASK_FIELDS) and
                self.field_contents_valid())

    def get_achieved_text(self) -> str:
        achieveddict = {
            None: None,
            0: WSTRING("irac_achieved_0"),
            1: WSTRING("irac_achieved_1"),
            2: WSTRING("irac_achieved_2"),
        }
        return get_from_dict(achieveddict, self.achieved)

    def get_task_html(self) -> str:
        if self.achieved is not None:
            achieved = "{}. {}".format(self.achieved,
                                       self.get_achieved_text())
        else:
            achieved = None
        h = """
            <div class="summary">
                <table class="summary">
        """ + self.get_is_complete_tr() + """
                </table>
            </div>
            <table class="taskdetail">
                <tr>
                    <th width="50%">Question</th>
                    <th width="50%">Answer</th>
                </tr>
        """
        h += tr_qa(WSTRING("irac_q_aim"), ws.webify(self.aim))
        h += tr_qa(WSTRING("irac_q_achieved"), achieved)
        h += """
            </table>
        """
        return h