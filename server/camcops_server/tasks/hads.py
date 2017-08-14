#!/usr/bin/env python
# camcops_server/tasks/hads.py

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

import logging
from typing import Any, Dict, List, Tuple, Type

from cardinal_pythonlib.stringfunc import strseq
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.sql.sqltypes import Integer

from ..cc_modules.cc_constants import DATA_COLLECTION_UNLESS_UPGRADED_DIV
from ..cc_modules.cc_ctvinfo import CTV_INCOMPLETE, CtvInfo
from ..cc_modules.cc_db import add_multiple_columns
from ..cc_modules.cc_html import answer, tr_qa
from ..cc_modules.cc_request import CamcopsRequest
from ..cc_modules.cc_sqlalchemy import Base
from ..cc_modules.cc_summaryelement import SummaryElement
from ..cc_modules.cc_task import (
    Task,
    TaskHasPatientMixin,
    TaskHasRespondentMixin,
)
from ..cc_modules.cc_trackerhelpers import TrackerInfo

log = logging.getLogger(__name__)


# =============================================================================
# HADS (crippled unless upgraded locally) - base classes
# =============================================================================

class HadsMetaclass(DeclarativeMeta):
    # noinspection PyInitNewSignature
    def __init__(cls: Type['HadsBase'],
                 name: str,
                 bases: Tuple[Type, ...],
                 classdict: Dict[str, Any]) -> None:
        add_multiple_columns(
            cls, "q", 1, cls.NQUESTIONS,
            minimum=0, maximum=3,
            comment_fmt="Q{n}: {s} (0-3)",
            comment_strings=[
                "tense", "enjoy usual", "apprehensive", "laugh", "worry",
                "cheerful", "relaxed", "slow", "butterflies", "appearance",
                "restless", "anticipate", "panic", "book/TV/radio"
            ]
        )
        super().__init__(name, bases, classdict)


class HadsBase(TaskHasPatientMixin, Task,
               metaclass=HadsMetaclass):
    # This is an abstract class and does not inherit from Base.
    provides_trackers = True

    NQUESTIONS = 14
    ANXIETY_QUESTIONS = [1, 3, 5, 7, 9, 11, 13]
    DEPRESSION_QUESTIONS = [2, 4, 6, 8, 10, 12, 14]
    TASK_FIELDS = strseq("q", 1, NQUESTIONS)
    MAX_ANX_SCORE = 21
    MAX_DEP_SCORE = 21

    def is_complete(self) -> bool:
        return (
            self.field_contents_valid() and
            self.are_all_fields_complete(self.TASK_FIELDS)
        )

    def get_trackers(self, req: CamcopsRequest) -> List[TrackerInfo]:
        return [
            TrackerInfo(
                value=self.anxiety_score(),
                plot_label="HADS anxiety score",
                axis_label="Anxiety score (out of {})".format(
                    self.MAX_ANX_SCORE),
                axis_min=-0.5,
                axis_max=self.MAX_ANX_SCORE + 0.5,
            ),
            TrackerInfo(
                value=self.depression_score(),
                plot_label="HADS depression score",
                axis_label="Depression score (out of {})".format(
                    self.MAX_DEP_SCORE),
                axis_min=-0.5,
                axis_max=self.MAX_DEP_SCORE + 0.5
            ),
        ]

    def get_clinical_text(self, req: CamcopsRequest) -> List[CtvInfo]:
        if not self.is_complete():
            return CTV_INCOMPLETE
        return [CtvInfo(
            content="anxiety score {}/{}, depression score {}/21".format(
                self.anxiety_score(), self.MAX_ANX_SCORE,
                self.depression_score())
        )]

    def get_summaries(self, req: CamcopsRequest) -> List[SummaryElement]:
        return [
            self.is_complete_summary_field(),
            SummaryElement(
                name="anxiety", coltype=Integer(),
                value=self.anxiety_score(),
                comment="Anxiety score (/{})".format(self.MAX_ANX_SCORE)),
            SummaryElement(name="depression", coltype=Integer(),
                           value=self.depression_score(),
                           comment="Depression score (/21)"),
        ]

    def score(self, questions: List[int]) -> int:
        fields = self.fieldnames_from_list("q", questions)
        return self.sum_fields(fields)

    def anxiety_score(self) -> int:
        return self.score(self.ANXIETY_QUESTIONS)

    def depression_score(self) -> int:
        return self.score(self.DEPRESSION_QUESTIONS)

    def get_task_html(self, req: CamcopsRequest) -> str:
        min_score = 0
        max_score = 3
        crippled = not self.extrastrings_exist()
        a = self.anxiety_score()
        d = self.depression_score()
        h = """
            <div class="summary">
                <table class="summary">
                    {is_complete_tr}
                    <tr>
                        <td>{sa}</td><td>{a} / {maxa}</td>
                    </tr>
                    <tr>
                        <td>{sd}</td><td>{d} / 21</td>
                    </tr>
                </table>
            </div>
            <div class="explanation">
                All questions are scored from 0–3
                (0 least symptomatic, 3 most symptomatic).
            </div>
            <table class="taskdetail">
                <tr>
                    <th width="50%">Question</th>
                    <th width="50%">Answer</th>
                </tr>
        """.format(
            is_complete_tr=self.get_is_complete_tr(),
            sa=req.wappstring("hads_anxiety_score"),
            a=answer(a),
            maxa=self.MAX_ANX_SCORE,
            sd=req.wappstring("hads_depression_score"),
            d=answer(d),
        )
        for n in range(1, self.NQUESTIONS + 1):
            if crippled:
                q = "HADS: Q{}".format(n)
            else:
                q = "Q{}. {}".format(
                    n,
                    self.wxstring(req, "q" + str(n) + "_stem")
                )
            if n in self.ANXIETY_QUESTIONS:
                q += " (A)"
            if n in self.DEPRESSION_QUESTIONS:
                q += " (D)"
            v = getattr(self, "q" + str(n))
            if crippled or v is None or v < min_score or v > max_score:
                a = v
            else:
                a = "{}: {}".format(
                    v, self.wxstring(req, "q{}_a{}".format(n, v)))
            h += tr_qa(q, a)
        h += """
            </table>
        """ + DATA_COLLECTION_UNLESS_UPGRADED_DIV
        return h


# =============================================================================
# Hads
# =============================================================================

class Hads(HadsBase, Base):
    __tablename__ = "hads"
    shortname = "HADS"
    longname = "Hospital Anxiety and Depression Scale (data collection only)"


# =============================================================================
# HadsRespondent
# =============================================================================

class HadsRespondent(TaskHasRespondentMixin, HadsBase, Base):
    __tablename__ = "hads_respondent"
    shortname = "HADS-Respondent"
    longname = "Hospital Anxiety and Depression Scale (data collection " \
               "only), non-patient respondent version"
    extrastring_taskname = "hads"
