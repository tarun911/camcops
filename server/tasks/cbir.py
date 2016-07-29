#!/usr/bin/env python3
# cbir.py

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

from cardinal_pythonlib.rnc_lang import AttrDict
from ..cc_modules.cc_constants import (
    PV,
)
from ..cc_modules.cc_db import repeat_fieldspec
from ..cc_modules.cc_html import (
    answer,
    get_yes_no,
    subheading_spanning_three_columns,
    tr,
    tr_qa,
)
from ..cc_modules.cc_string import WSTRING
from ..cc_modules.cc_task import get_from_dict, Task


# =============================================================================
# CBI-R
# =============================================================================

class CbiR(Task):
    MIN_SCORE = 0
    MAX_SCORE = 4
    QUESTION_SNIPPETS = [
        "memory: poor day to day memory",  # 1
        "memory: asks same questions",
        "memory: loses things",
        "memory: forgets familiar names",
        "memory: forgets names of objects",  # 5
        "memory: poor concentration",
        "memory: forgets day",
        "memory: confused in unusual surroundings",
        "everyday: electrical appliances",
        "everyday: writing",  # 10
        "everyday: using telephone",
        "everyday: making hot drink",
        "everyday: money",
        "self-care: grooming",
        "self-care: dressing",  # 15
        "self-care: feeding",
        "self-care: bathing",
        "behaviour: inappropriate humour",
        "behaviour: temper outbursts",
        "behaviour: uncooperative",  # 20
        "behaviour: socially embarrassing",
        "behaviour: tactless/suggestive",
        "behaviour: impulsive",
        "mood: cries",
        "mood: sad/depressed",  # 25
        "mood: restless/agitated",
        "mood: irritable",
        "beliefs: visual hallucinations",
        "beliefs: auditory hallucinations",
        "beliefs: delusions",  # 30
        "eating: sweet tooth",
        "eating: repetitive",
        "eating: increased appetite",
        "eating: table manners",
        "sleep: disturbed at night",  # 35
        "sleep: daytime sleep increased",
        "stereotypy/motor: rigid/fixed opinions",
        "stereotypy/motor: routines",
        "stereotypy/motor: preoccupied with time",
        "stereotypy/motor:  expression/catchphrase",  # 40
        "motivation: less enthusiasm in usual interests",
        "motivation: no interest in new things",
        "motivation: fails to contact friends/family",
        "motivation: indifferent to family/friend concerns",
        "motivation: reduced affection",  # 45
    ]
    QNUMS_MEMORY = (1, 8)  # tuple: first, last
    QNUMS_EVERYDAY = (9, 13)
    QNUMS_SELF = (14, 17)
    QNUMS_BEHAVIOUR = (18, 23)
    QNUMS_MOOD = (24, 27)
    QNUMS_BELIEFS = (28, 30)
    QNUMS_EATING = (31, 34)
    QNUMS_SLEEP = (35, 36)
    QNUMS_STEREOTYPY = (37, 40)
    QNUMS_MOTIVATION = (41, 45)

    NQUESTIONS = 45

    tablename = "cbir"
    shortname = "CBI-R"
    longname = "Cambridge Behavioural Inventory, Revised"
    fieldspecs = [
        dict(name="confirm_blanks", cctype="INT", pv=PV.BIT,
             comment="Respondent confirmed that blanks are deliberate (N/A) "
                     "(0/NULL no, 1 yes)"),
        dict(name="comments", cctype="TEXT",
             comment="Additional comments"),
    ] + repeat_fieldspec(
        "frequency", 1, NQUESTIONS,
        comment_fmt="Frequency Q{n}, {s} (0-4, higher worse)",
        min=MIN_SCORE, max=MAX_SCORE,
        comment_strings=QUESTION_SNIPPETS
    ) + repeat_fieldspec(
        "distress", 1, NQUESTIONS,
        comment_fmt="Distress Q{n}, {s} (0-4, higher worse)",
        min=MIN_SCORE, max=MAX_SCORE,
        comment_strings=QUESTION_SNIPPETS
    )
    has_respondent = True

    TASK_FIELDS = [x["name"] for x in fieldspecs]

    def get_summaries(self):
        return [
            self.is_complete_summary_field(),
            dict(name="memory_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_MEMORY),
                 comment="Memory/orientation: frequency score (% of max)"),
            dict(name="memory_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_MEMORY),
                 comment="Memory/orientation: distress score (% of max)"),
            dict(name="everyday_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_EVERYDAY),
                 comment="Everyday skills: frequency score (% of max)"),
            dict(name="everyday_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_EVERYDAY),
                 comment="Everyday skills: distress score (% of max)"),
            dict(name="selfcare_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_SELF),
                 comment="Self-care: frequency score (% of max)"),
            dict(name="selfcare_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_SELF),
                 comment="Self-care: distress score (% of max)"),
            dict(name="behaviour_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_BEHAVIOUR),
                 comment="Abnormal behaviour: frequency score (% of max)"),
            dict(name="behaviour_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_BEHAVIOUR),
                 comment="Abnormal behaviour: distress score (% of max)"),
            dict(name="mood_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_MOOD),
                 comment="Mood: frequency score (% of max)"),
            dict(name="mood_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_MOOD),
                 comment="Mood: distress score (% of max)"),
            dict(name="beliefs_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_BELIEFS),
                 comment="Beliefs: frequency score (% of max)"),
            dict(name="beliefs_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_BELIEFS),
                 comment="Beliefs: distress score (% of max)"),
            dict(name="eating_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_EATING),
                 comment="Eating habits: frequency score (% of max)"),
            dict(name="eating_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_EATING),
                 comment="Eating habits: distress score (% of max)"),
            dict(name="sleep_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_SLEEP),
                 comment="Sleep: frequency score (% of max)"),
            dict(name="sleep_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_SLEEP),
                 comment="Sleep: distress score (% of max)"),
            dict(name="stereotypic_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_STEREOTYPY),
                 comment="Stereotypic and motor behaviours: frequency "
                         "score (% of max)"),
            dict(name="stereotypic_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_STEREOTYPY),
                 comment="Stereotypic and motor behaviours: distress "
                         "score (% of max)"),
            dict(name="motivation_frequency_pct", cctype="FLOAT",
                 value=self.frequency_subscore(*self.QNUMS_MOTIVATION),
                 comment="Motivation: frequency score (% of max)"),
            dict(name="motivation_distress_pct", cctype="FLOAT",
                 value=self.distress_subscore(*self.QNUMS_MOTIVATION),
                 comment="Motivation: distress score (% of max)"),
        ]

    def subscore(self, first, last, fieldprefix):
        score = 0
        n = 0
        for q in range(first, last + 1):
            value = getattr(self, fieldprefix + str(q))
            if value is not None:
                score += value / self.MAX_SCORE
                n += 1
        return 100 * score / n if n > 0 else None

    def frequency_subscore(self, first, last):
        return self.subscore(first, last, "frequency")

    def distress_subscore(self, first, last):
        return self.subscore(first, last, "distress")

    def is_complete(self):
        if (not self.field_contents_valid() or
                not self.is_respondent_complete()):
            return False
        if self.confirm_blanks:
            return True
        return self.are_all_fields_complete(self.TASK_FIELDS)

    def get_task_html(self):
        freq_dict = {None: None}
        distress_dict = {None: None}
        for a in range(self.MIN_SCORE, self.MAX_SCORE + 1):
            freq_dict[a] = WSTRING("cbir_f" + str(a))
            distress_dict[a] = WSTRING("cbir_d" + str(a))
        headings = AttrDict({
            "memory": WSTRING("cbir_h_memory"),
            "everyday": WSTRING("cbir_h_everyday"),
            "selfcare": WSTRING("cbir_h_selfcare"),
            "behaviour": WSTRING("cbir_h_abnormalbehaviour"),
            "mood": WSTRING("cbir_h_mood"),
            "beliefs": WSTRING("cbir_h_beliefs"),
            "eating": WSTRING("cbir_h_eating"),
            "sleep": WSTRING("cbir_h_sleep"),
            "motor": WSTRING("cbir_h_stereotypy_motor"),
            "motivation": WSTRING("cbir_h_motivation"),
        })

        def get_question_rows(first, last):
            html = ""
            for q in range(first, last + 1):
                f = getattr(self, "frequency" + str(q))
                d = getattr(self, "distress" + str(q))
                fa = ("{}: {}".format(f, get_from_dict(freq_dict, f))
                      if f is not None else None)
                da = ("{}: {}".format(d, get_from_dict(distress_dict, d))
                      if d is not None else None)
                html += tr(
                    WSTRING("cbir_q" + str(q)),
                    answer(fa),
                    answer(da),
                )
            return html

        h = """
            <div class="summary">
                <table class="summary">
                    {complete_tr}
                </table>
                <table class="summary">
                    <tr>
                        <th>Subscale</th>
                        <th>Frequency (% of max)</th>
                        <th>Distress (% of max)</th>
                    </tr>
                    <tr>
                        <td>{headings.memory}</td>
                        <td>{mem_f}</td>
                        <td>{mem_d}</td>
                    </tr>
                    <tr>
                        <td>{headings.everyday}</td>
                        <td>{everyday_f}</td>
                        <td>{everyday_d}</td>
                    </tr>
                    <tr>
                        <td>{headings.selfcare}</td>
                        <td>{self_f}</td>
                        <td>{self_d}</td>
                    </tr>
                    <tr>
                        <td>{headings.behaviour}</td>
                        <td>{behav_f}</td>
                        <td>{behav_d}</td>
                    </tr>
                    <tr>
                        <td>{headings.mood}</td>
                        <td>{mood_f}</td>
                        <td>{mood_d}</td>
                    </tr>
                    <tr>
                        <td>{headings.beliefs}</td>
                        <td>{beliefs_f}</td>
                        <td>{beliefs_d}</td>
                    </tr>
                    <tr>
                        <td>{headings.eating}</td>
                        <td>{eating_f}</td>
                        <td>{eating_d}</td>
                    </tr>
                    <tr>
                        <td>{headings.sleep}</td>
                        <td>{sleep_f}</td>
                        <td>{sleep_d}</td>
                    </tr>
                    <tr>
                        <td>{headings.motor}</td>
                        <td>{motor_f}</td>
                        <td>{motor_d}</td>
                    </tr>
                    <tr>
                        <td>{headings.motivation}</td>
                        <td>{motivation_f}</td>
                        <td>{motivation_d}</td>
                    </tr>
                </table>
            </div>
            <table class="taskdetail">
                {tr_blanks}
                {tr_comments}
            </table>
            <table class="taskdetail">
                <tr>
                    <th width="50%">Question</th>
                    <th width="25%">Frequency (0–4)</th>
                    <th width="25%">Distress (0–4)</th>
                </tr>
        """.format(
            complete_tr=self.get_is_complete_tr(),
            headings=headings,
            mem_f=answer(self.frequency_subscore(*self.QNUMS_MEMORY)),
            mem_d=answer(self.distress_subscore(*self.QNUMS_MEMORY)),
            everyday_f=answer(self.frequency_subscore(*self.QNUMS_EVERYDAY)),
            everyday_d=answer(self.distress_subscore(*self.QNUMS_EVERYDAY)),
            self_f=answer(self.frequency_subscore(*self.QNUMS_SELF)),
            self_d=answer(self.distress_subscore(*self.QNUMS_SELF)),
            behav_f=answer(self.frequency_subscore(*self.QNUMS_BEHAVIOUR)),
            behav_d=answer(self.distress_subscore(*self.QNUMS_BEHAVIOUR)),
            mood_f=answer(self.frequency_subscore(*self.QNUMS_MOOD)),
            mood_d=answer(self.distress_subscore(*self.QNUMS_MOOD)),
            beliefs_f=answer(self.frequency_subscore(*self.QNUMS_BELIEFS)),
            beliefs_d=answer(self.distress_subscore(*self.QNUMS_BELIEFS)),
            eating_f=answer(self.frequency_subscore(*self.QNUMS_EATING)),
            eating_d=answer(self.distress_subscore(*self.QNUMS_EATING)),
            sleep_f=answer(self.frequency_subscore(*self.QNUMS_SLEEP)),
            sleep_d=answer(self.distress_subscore(*self.QNUMS_SLEEP)),
            motor_f=answer(self.frequency_subscore(*self.QNUMS_STEREOTYPY)),
            motor_d=answer(self.distress_subscore(*self.QNUMS_STEREOTYPY)),
            motivation_f=answer(
                self.frequency_subscore(*self.QNUMS_MOTIVATION)),
            motivation_d=answer(
                self.distress_subscore(*self.QNUMS_MOTIVATION)),
            tr_blanks=tr(
                "Respondent confirmed that blanks are deliberate (N/A)",
                answer(get_yes_no(self.confirm_blanks))),
            tr_comments=tr_qa("Comments",
                              answer(self.comments, default="")),
        )
        h += subheading_spanning_three_columns(headings.memory)
        h += get_question_rows(*self.QNUMS_MEMORY)
        h += subheading_spanning_three_columns(headings.everyday)
        h += get_question_rows(*self.QNUMS_EVERYDAY)
        h += subheading_spanning_three_columns(headings.selfcare)
        h += get_question_rows(*self.QNUMS_SELF)
        h += subheading_spanning_three_columns(headings.behaviour)
        h += get_question_rows(*self.QNUMS_BEHAVIOUR)
        h += subheading_spanning_three_columns(headings.mood)
        h += get_question_rows(*self.QNUMS_MOOD)
        h += subheading_spanning_three_columns(headings.beliefs)
        h += get_question_rows(*self.QNUMS_BELIEFS)
        h += subheading_spanning_three_columns(headings.eating)
        h += get_question_rows(*self.QNUMS_EATING)
        h += subheading_spanning_three_columns(headings.sleep)
        h += get_question_rows(*self.QNUMS_SLEEP)
        h += subheading_spanning_three_columns(headings.motor)
        h += get_question_rows(*self.QNUMS_STEREOTYPY)
        h += subheading_spanning_three_columns(headings.motivation)
        h += get_question_rows(*self.QNUMS_MOTIVATION)
        h += """
            </table>
        """
        return h
