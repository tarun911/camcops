#!/usr/bin/env python3
# mds_updrs.py

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

from ..cc_modules.cc_constants import DATA_COLLECTION_ONLY_DIV, PV
from ..cc_modules.cc_html import tr_qa
from ..cc_modules.cc_task import Task


# =============================================================================
# MDS-UPDRS (crippled)
# =============================================================================

class MdsUpdrs(Task):
    main_cmt = " (0 normal, 1 slight, 2 mild, 3 moderate, 4 severe)"
    main_pv = list(range(0, 4 + 1))
    informant_cmt = " (0 patient, 1 caregiver, 2 both)"
    informant_pv = list(range(0, 2 + 1))
    yn_cmt = " (0 no, 1 yes)"
    on_off_cmt = " (0 off, 1 on)"
    hy_pv = list(range(0, 5 + 1))

    tablename = "mds_updrs"
    shortname = "MDS-UPDRS"
    longname = (
        "Movement Disorder Society-Sponsored Revision of the Unified "
        "Parkinson’s Disease Rating Scale (data collection only)")
    fieldspecs = [
        # Part I
        dict(name="q1a", cctype="INT", pv=informant_pv,
             comment="Part I: informant for Q1.1-1.6" + informant_cmt),
        dict(name="q1_1", cctype="INT", pv=main_pv,
             comment="Part I, Q1.1 " + main_cmt),
        dict(name="q1_2", cctype="INT", pv=main_pv,
             comment="Part I, Q1.2 " + main_cmt),
        dict(name="q1_3", cctype="INT", pv=main_pv,
             comment="Part I, Q1.3 " + main_cmt),
        dict(name="q1_4", cctype="INT", pv=main_pv,
             comment="Part I, Q1.4 " + main_cmt),
        dict(name="q1_5", cctype="INT", pv=main_pv,
             comment="Part I, Q1.5 " + main_cmt),
        dict(name="q1_6", cctype="INT", pv=main_pv,
             comment="Part I, Q1.6 " + main_cmt),
        dict(name="q1_6a", cctype="INT", pv=informant_pv,
             comment="Part I, Q1.6a: informant for Q1.7-1.13" + informant_cmt),
        dict(name="q1_7", cctype="INT", pv=main_pv,
             comment="Part I, Q1.7 " + main_cmt),
        dict(name="q1_8", cctype="INT", pv=main_pv,
             comment="Part I, Q1.8 " + main_cmt),
        dict(name="q1_9", cctype="INT", pv=main_pv,
             comment="Part I, Q1.9 " + main_cmt),
        dict(name="q1_10", cctype="INT", pv=main_pv,
             comment="Part I, Q1.10 " + main_cmt),
        dict(name="q1_11", cctype="INT", pv=main_pv,
             comment="Part I, Q1.11 " + main_cmt),
        dict(name="q1_12", cctype="INT", cpv=main_pv,
             comment="Part I, Q1.12 " + main_cmt),
        dict(name="q1_13", cctype="INT", pv=main_pv,
             comment="Part I, Q1.13 " + main_cmt),
        # Part II
        dict(name="q2_1", cctype="INT", pv=main_pv,
             comment="Part II, Q2.1 " + main_cmt),
        dict(name="q2_2", cctype="INT", pv=main_pv,
             comment="Part II, Q2.2 " + main_cmt),
        dict(name="q2_3", cctype="INT", pv=main_pv,
             comment="Part II, Q2.3 " + main_cmt),
        dict(name="q2_4", cctype="INT", pv=main_pv,
             comment="Part II, Q2.4 " + main_cmt),
        dict(name="q2_5", cctype="INT", pv=main_pv,
             comment="Part II, Q2.5 " + main_cmt),
        dict(name="q2_6", cctype="INT", pv=main_pv,
             comment="Part II, Q2.6 " + main_cmt),
        dict(name="q2_7", cctype="INT", pv=main_pv,
             comment="Part II, Q2.7 " + main_cmt),
        dict(name="q2_8", cctype="INT", pv=main_pv,
             comment="Part II, Q2.8 " + main_cmt),
        dict(name="q2_9", cctype="INT", pv=main_pv,
             comment="Part II, Q2.9 " + main_cmt),
        dict(name="q2_10", cctype="INT", pv=main_pv,
             comment="Part II, Q2.10 " + main_cmt),
        dict(name="q2_11", cctype="INT", pv=main_pv,
             comment="Part II, Q2.11 " + main_cmt),
        dict(name="q2_12", cctype="INT", pv=main_pv,
             comment="Part II, Q2.12 " + main_cmt),
        dict(name="q2_13", cctype="INT", pv=main_pv,
             comment="Part II, Q2.13 " + main_cmt),
        # Part III
        dict(name="q3a", cctype="BOOL", pv=PV.BIT,
             comment="Part III, Q3a (medication) " + yn_cmt),
        dict(name="q3b", cctype="BOOL", pv=PV.BIT,
             comment="Part III, Q3b (clinical state) " + on_off_cmt),
        dict(name="q3c", cctype="BOOL", pv=PV.BIT,
             comment="Part III, Q3c (levodopa) " + yn_cmt),
        dict(name="q3c1", cctype="FLOAT",
             comment="Part III, Q3c.1 (minutes since last dose)"),
        dict(name="q3_1", cctype="INT", pv=main_pv,
             comment="Part III, Q3.1 " + main_cmt),
        dict(name="q3_2", cctype="INT", pv=main_pv,
             comment="Part III, Q3.2 " + main_cmt),
        dict(name="q3_3a", cctype="INT", pv=main_pv,
             comment="Part III, Q3.3a " + main_cmt),
        dict(name="q3_3b", cctype="INT", pv=main_pv,
             comment="Part III, Q3.3b " + main_cmt),
        dict(name="q3_3c", cctype="INT", pv=main_pv,
             comment="Part III, Q3.3c " + main_cmt),
        dict(name="q3_3d", cctype="INT", pv=main_pv,
             comment="Part III, Q3.3d " + main_cmt),
        dict(name="q3_3e", cctype="INT", pv=main_pv,
             comment="Part III, Q3.3e " + main_cmt),
        dict(name="q3_4a", cctype="INT", pv=main_pv,
             comment="Part III, Q3.4a " + main_cmt),
        dict(name="q3_4b", cctype="INT", pv=main_pv,
             comment="Part III, Q3.4b " + main_cmt),
        dict(name="q3_5a", cctype="INT", pv=main_pv,
             comment="Part III, Q3.5a " + main_cmt),
        dict(name="q3_5b", cctype="INT", pv=main_pv,
             comment="Part III, Q3.5b " + main_cmt),
        dict(name="q3_6a", cctype="INT", pv=main_pv,
             comment="Part III, Q3.6a " + main_cmt),
        dict(name="q3_6b", cctype="INT", pv=main_pv,
             comment="Part III, Q3.6b " + main_cmt),
        dict(name="q3_7a", cctype="INT", pv=main_pv,
             comment="Part III, Q3.7a " + main_cmt),
        dict(name="q3_7b", cctype="INT", pv=main_pv,
             comment="Part III, Q3.7b " + main_cmt),
        dict(name="q3_8a", cctype="INT", pv=main_pv,
             comment="Part III, Q3.8a " + main_cmt),
        dict(name="q3_8b", cctype="INT", pv=main_pv,
             comment="Part III, Q3.8b " + main_cmt),
        dict(name="q3_9", cctype="INT", pv=main_pv,
             comment="Part III, Q3.9 " + main_cmt),
        dict(name="q3_10", cctype="INT", pv=main_pv,
             comment="Part III, Q3.10 " + main_cmt),
        dict(name="q3_11", cctype="INT", pv=main_pv,
             comment="Part III, Q3.11 " + main_cmt),
        dict(name="q3_12", cctype="INT", pv=main_pv,
             comment="Part III, Q3.12 " + main_cmt),
        dict(name="q3_13", cctype="INT", pv=main_pv,
             comment="Part III, Q3.13 " + main_cmt),
        dict(name="q3_14", cctype="INT", pv=main_pv,
             comment="Part III, Q3.14 " + main_cmt),
        dict(name="q3_15a", cctype="INT", pv=main_pv,
             comment="Part III, Q3.15a " + main_cmt),
        dict(name="q3_15b", cctype="INT", pv=main_pv,
             comment="Part III, Q3.15b " + main_cmt),
        dict(name="q3_16a", cctype="INT", pv=main_pv,
             comment="Part III, Q3.16a " + main_cmt),
        dict(name="q3_16b", cctype="INT", pv=main_pv,
             comment="Part III, Q3.16b " + main_cmt),
        dict(name="q3_17a", cctype="INT", pv=main_pv,
             comment="Part III, Q3.17a " + main_cmt),
        dict(name="q3_17b", cctype="INT", pv=main_pv,
             comment="Part III, Q3.17b " + main_cmt),
        dict(name="q3_17c", cctype="INT", pv=main_pv,
             comment="Part III, Q3.17c " + main_cmt),
        dict(name="q3_17d", cctype="INT", pv=main_pv,
             comment="Part III, Q3.17d " + main_cmt),
        dict(name="q3_17e", cctype="INT", pv=main_pv,
             comment="Part III, Q3.17e " + main_cmt),
        dict(name="q3_18", cctype="INT", pv=main_pv,
             comment="Part III, Q3.18 " + main_cmt),
        dict(name="q3_dyskinesia_present", cctype="BOOL", pv=PV.BIT,
             comment="Part III, q3_dyskinesia_present " + yn_cmt),
        dict(name="q3_dyskinesia_interfered", cctype="BOOL", pv=PV.BIT,
             comment="Part III, q3_dyskinesia_interfered " + yn_cmt),
        dict(name="q3_hy_stage", cctype="INT", pv=hy_pv,
             comment="Part III, q3_hy_stage (0-5)"),
        # Part IV
        dict(name="q4_1", cctype="INT", pv=main_pv,
             comment="Part IV, Q4.1 " + main_cmt),
        dict(name="q4_2", cctype="INT", pv=main_pv,
             comment="Part IV, Q4.2 " + main_cmt),
        dict(name="q4_3", cctype="INT", pv=main_pv,
             comment="Part IV, Q4.3 " + main_cmt),
        dict(name="q4_4", cctype="INT", pv=main_pv,
             comment="Part IV, Q4.4 " + main_cmt),
        dict(name="q4_5", cctype="INT", pv=main_pv,
             comment="Part IV, Q4.5 " + main_cmt),
        dict(name="q4_6", cctype="INT", pv=main_pv,
             comment="Part IV, Q4.6 " + main_cmt),
    ]

    TASK_FIELDS = [x["name"] for x in fieldspecs]
    TASK_FIELDS_EXCEPT_3C1 = [x for x in TASK_FIELDS if x != "q3c1"]

    def is_complete(self) -> bool:
        return (
            self.field_contents_valid() and
            self.are_all_fields_complete(self.TASK_FIELDS_EXCEPT_3C1) and
            (self.q3c1 is not None or not self.q3c)
        )

    def get_task_html(self) -> str:
        h = """
            <div class="summary">
                <table class="summary">
        """ + self.get_is_complete_tr() + """
                </table>
            </div>
            <table class="taskdetail">
                <tr>
                    <th width="70%">Question</th>
                    <th width="30%">Answer</th>
                </tr>
        """
        for fs in self.fieldspecs:
            question = fs["comment"]
            fieldname = fs["name"]
            value = getattr(self, fieldname)
            h += tr_qa(question, value)
        h += """
            </table>
        """ + DATA_COLLECTION_ONLY_DIV
        return h