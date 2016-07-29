#!/usr/bin/env python3
# lunsers.py

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

from ..cc_modules.cc_db import repeat_fieldspec
from ..cc_modules.cc_string import WSTRING
from ..cc_modules.cc_task import get_from_dict, Task


# =============================================================================
# LUNSERS
# =============================================================================

class Lunsers(Task):
    NQUESTIONS = 51
    list_epse = [19, 29, 34, 37, 40, 43, 48]
    list_anticholinergic = [6, 10, 32, 38, 51]
    list_allergic = [1, 35, 47, 49]
    list_miscellaneous = [5, 22, 39, 44]
    list_psychic = [2, 4, 9, 14, 18, 21, 23, 26, 31, 41]
    list_otherautonomic = [15, 16, 20, 27, 36]
    list_hormonal_female = [7, 13, 17, 24, 46, 50]
    list_hormonal_male = [7, 17, 24, 46]
    list_redherrings = [3, 8, 11, 12, 25, 28, 30, 33, 42, 45]

    tablename = "lunsers"
    shortname = "LUNSERS"
    longname = "Liverpool University Neuroleptic Side Effect Rating Scale"
    fieldspecs = repeat_fieldspec("q", 1, NQUESTIONS)

    def get_trackers(self):
        return [
            {
                "value": self.total_score(),
                "plot_label": "LUNSERS total score",
                "axis_label": "Total score (out of {})".format(
                    self.max_score()),
                "axis_min": -0.5,
                "axis_max": 0.5 + self.max_score(),
            }
        ]

    def get_summaries(self):
        return [
            self.is_complete_summary_field(),
            dict(name="total", cctype="INT",
                 value=self.total_score(), comment="Total score"),
        ]

    @staticmethod
    def get_fieldlist(group):
        return ["q" + str(q) for q in group]

    def get_relevant_fieldlist(self):
        qnums = range(1, self.NQUESTIONS + 1)
        if not self.is_female():
            qnums.remove(13)
            qnums.remove(50)
        return ["q" + str(q) for q in qnums]

    def is_complete(self):
        return self.are_all_fields_complete(self.get_relevant_fieldlist())

    def total_score(self):
        return self.sum_fields(self.get_relevant_fieldlist())

    def group_score(self, qnums):
        return self.sum_fields(self.get_fieldlist(qnums))

    @staticmethod
    def get_subheading(subtitle, score, max_score):
        return """
            <tr class="subheading">
                <td>{}</td><td><i><b>{}</b> / {}</i></td>
            </tr>
        """.format(
            subtitle,
            score,
            max_score
        )

    def get_row(self, q, answer_dict):
        return """<tr><td>{}</td><td><b>{}</b></td></tr>""".format(
            "Q" + str(q) + " — " + WSTRING("lunsers_q" + str(q)),
            get_from_dict(answer_dict, getattr(self, "q" + str(q)))
        )

    def get_group_html(self, qnums, subtitle, answer_dict):
        h = self.get_subheading(
            subtitle,
            self.group_score(qnums),
            len(qnums) * 4
        )
        for q in qnums:
            h += self.get_row(q, answer_dict)
        return h

    def max_score(self):
        return 204 if self.is_female() else 196

    def get_task_html(self):
        score = self.total_score()

        answer_dict = {None: "?"}
        for option in range(0, 5):
            answer_dict[option] = WSTRING("lunsers_option" + str(option))
        h = """
            <div class="summary">
                <table class="summary">
                    {}
                    <tr><td>{}</td><td><b>{}</b> / {}</td></tr>
                </table>
            </div>
            <div class="explanation">
                Ratings pertain to the past month.
            </div>
            <table class="taskdetail">
                <tr>
                    <th width="70%">Question</th>
                    <th width="30%">Answer</th>
                </tr>
        """.format(
            self.get_is_complete_tr(),
            WSTRING("total_score"), score, self.max_score()
        )
        h += self.get_group_html(self.list_epse,
                                 WSTRING("lunsers_group_epse"),
                                 answer_dict)
        h += self.get_group_html(self.list_anticholinergic,
                                 WSTRING("lunsers_group_anticholinergic"),
                                 answer_dict)
        h += self.get_group_html(self.list_allergic,
                                 WSTRING("lunsers_group_allergic"),
                                 answer_dict)
        h += self.get_group_html(self.list_miscellaneous,
                                 WSTRING("lunsers_group_miscellaneous"),
                                 answer_dict)
        h += self.get_group_html(self.list_psychic,
                                 WSTRING("lunsers_group_psychic"),
                                 answer_dict)
        h += self.get_group_html(self.list_otherautonomic,
                                 WSTRING("lunsers_group_otherautonomic"),
                                 answer_dict)
        if self.is_female():
            h += self.get_group_html(self.list_hormonal_female,
                                     WSTRING("lunsers_group_hormonal") + " (" +
                                     WSTRING("female") + ")",
                                     answer_dict)
        else:
            h += self.get_group_html(self.list_hormonal_male,
                                     WSTRING("lunsers_group_hormonal") + " (" +
                                     WSTRING("male") + ")",
                                     answer_dict)
        h += self.get_group_html(self.list_redherrings,
                                 WSTRING("lunsers_group_redherrings"),
                                 answer_dict)
        h += """
            </table>
        """
        return h
