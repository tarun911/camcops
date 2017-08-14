#!/usr/bin/env python
# camcops_server/tasks/npiq.py

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

from typing import List

from sqlalchemy.sql.sqltypes import Integer

from ..cc_modules.cc_constants import DATA_COLLECTION_UNLESS_UPGRADED_DIV, PV
from ..cc_modules.cc_ctvinfo import CTV_INCOMPLETE, CtvInfo
from ..cc_modules.cc_db import repeat_fieldspec
from ..cc_modules.cc_html import answer, get_yes_no_unknown, tr
from ..cc_modules.cc_summaryelement import SummaryElement
from ..cc_modules.cc_task import Task


# =============================================================================
# NPI-Q
# =============================================================================

ENDORSED = "endorsed"
SEVERITY = "severity"
DISTRESS = "distress"


class NpiQ(Task):
    tablename = "npiq"
    shortname = "NPI-Q"
    longname = "Neuropsychiatric Inventory Questionnaire"
    has_respondent = True

    NQUESTIONS = 12
    QUESTION_SNIPPETS = [
        "delusions",  # 1
        "hallucinations",
        "agitation/aggression",
        "depression/dysphoria",
        "anxiety",  # 5
        "elation/euphoria",
        "apathy/indifference",
        "disinhibition",
        "irritability/lability",
        "motor disturbance",  # 10
        "night-time behaviour",
        "appetite/eating",
    ]
    fieldspecs = repeat_fieldspec(
        ENDORSED, 1, NQUESTIONS, cctype="BOOL", pv=PV.BIT,
        comment_fmt="Q{n}, {s}, endorsed?",
        comment_strings=QUESTION_SNIPPETS
    ) + repeat_fieldspec(
        SEVERITY, 1, NQUESTIONS, pv=list(range(1, 3 + 1)),
        comment_fmt="Q{n}, {s}, severity (1-3), if endorsed",
        comment_strings=QUESTION_SNIPPETS
    ) + repeat_fieldspec(
        DISTRESS, 1, NQUESTIONS, pv=list(range(0, 5 + 1)),
        comment_fmt="Q{n}, {s}, distress (0-5), if endorsed",
        comment_strings=QUESTION_SNIPPETS
    )

    ENDORSED_FIELDS = [ENDORSED + str(n) for n in range(1, NQUESTIONS + 1)]

    def get_summaries(self, req: CamcopsRequest) -> List[SummaryElement]:
        return [
            self.is_complete_summary_field(),
            SummaryElement(name="n_endorsed", coltype=Integer(),
                           value=self.n_endorsed(),
                           comment="Number endorsed (/ 12)"),
            SummaryElement(name="severity_score", coltype=Integer(),
                           value=self.severity_score(),
                           comment="Severity score (/ 36)"),
            SummaryElement(name="distress_score", coltype=Integer(),
                           value=self.distress_score(),
                           comment="Distress score (/ 60)"),
        ]

    def get_clinical_text(self, req: CamcopsRequest) -> List[CtvInfo]:
        if not self.is_complete():
            return CTV_INCOMPLETE
        return [CtvInfo(
            content=(
                "Endorsed: {e}/12; severity {s}/36; distress {d}/60".format(
                    e=self.n_endorsed(),
                    s=self.severity_score(),
                    d=self.distress_score(),
                )
            )
        )]

    def q_endorsed(self, q: int) -> bool:
        return bool(getattr(self, ENDORSED + str(q)))

    def n_endorsed(self) -> int:
        return self.count_booleans(self.ENDORSED_FIELDS)

    def severity_score(self) -> int:
        total = 0
        for q in range(1, self.NQUESTIONS + 1):
            if self.q_endorsed(q):
                s = getattr(self, SEVERITY + str(q))
                if s is not None:
                    total += s
        return total

    def distress_score(self) -> int:
        total = 0
        for q in range(1, self.NQUESTIONS + 1):
            if self.q_endorsed(q):
                d = getattr(self, DISTRESS + str(q))
                if d is not None:
                    total += d
        return total

    def q_complete(self, q: int) -> bool:
        qstr = str(q)
        endorsed = getattr(self, ENDORSED + qstr)
        if endorsed is None:
            return False
        if not endorsed:
            return True
        if getattr(self, SEVERITY + qstr) is None:
            return False
        if getattr(self, DISTRESS + qstr) is None:
            return False
        return True

    def is_complete(self) -> bool:
        return (
            self.field_contents_valid() and
            self.is_respondent_complete() and
            all(self.q_complete(q) for q in range(1, self.NQUESTIONS + 1))
        )

    def get_task_html(self, req: CamcopsRequest) -> str:
        h = """
            <div class="summary">
                <table class="summary">
                    {complete_tr}
                    <tr>
                        <td>Endorsed</td>
                        <td>{e} / 12</td>
                    </td>
                    <tr>
                        <td>Severity score</td>
                        <td>{s} / 36</td>
                    </td>
                    <tr>
                        <td>Distress score</td>
                        <td>{d} / 60</td>
                    </td>
                </table>
            </div>
            <table class="taskdetail">
                <tr>
                    <th width="40%">Question</th>
                    <th width="20%">Endorsed</th>
                    <th width="20%">Severity (patient)</th>
                    <th width="20%">Distress (carer)</th>
                </tr>
        """.format(
            complete_tr=self.get_is_complete_tr(),
            e=self.n_endorsed(),
            s=self.severity_score(),
            d=self.distress_score(),
        )
        for q in range(1, self.NQUESTIONS + 1):
            qstr = str(q)
            e = getattr(self, ENDORSED + qstr)
            s = getattr(self, SEVERITY + qstr)
            d = getattr(self, DISTRESS + qstr)
            qtext = "<b>{}:</b> {}".format(
                self.wxstring(req, "t" + qstr),
                self.wxstring(req, "q" + qstr),
            )
            etext = get_yes_no_unknown(e)
            if e:
                stext = self.wxstring(req, "severity_{}".format(s), s,
                                      provide_default_if_none=False)
                dtext = self.wxstring(req, "distress_{}".format(d), d,
                                      provide_default_if_none=False)
            else:
                stext = ""
                dtext = ""
            h += tr(qtext, answer(etext), answer(stext), answer(dtext))
        h += """
            </table>
        """ + DATA_COLLECTION_UNLESS_UPGRADED_DIV
        return h
