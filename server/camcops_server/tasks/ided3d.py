#!/usr/bin/env python

"""
camcops_server/tasks/ided3d.py

===============================================================================

    Copyright (C) 2012-2019 Rudolf Cardinal (rudolf@pobox.com).

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

from typing import Any, List

import cardinal_pythonlib.rnc_web as ws
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Boolean, Float, Integer, Text

from camcops_server.cc_modules.cc_constants import CssClass
from camcops_server.cc_modules.cc_db import (
    ancillary_relationship,
    GenericTabletRecordMixin,
)
from camcops_server.cc_modules.cc_html import (
    answer,
    get_yes_no_none,
    identity,
    tr,
    tr_qa,
)
from camcops_server.cc_modules.cc_request import CamcopsRequest
from camcops_server.cc_modules.cc_sqla_coltypes import (
    BIT_CHECKER,
    CamcopsColumn,
    PendulumDateTimeAsIsoTextColType,
)
from camcops_server.cc_modules.cc_sqlalchemy import Base
from camcops_server.cc_modules.cc_task import Task, TaskHasPatientMixin


def a(x: Any) -> str:
    """Answer formatting for this task."""
    return answer(x, formatter_answer=identity, default="")


# =============================================================================
# IDED3D
# =============================================================================

class IDED3DTrial(GenericTabletRecordMixin, Base):
    __tablename__ = "ided3d_trials"

    ided3d_id = Column(
        "ided3d_id", Integer,
        nullable=False,
        comment="FK to ided3d"
    )
    trial = Column(
        "trial", Integer,
        nullable=False,
        comment="Trial number (1-based)"
    )
    stage = Column(
        "stage", Integer,
        comment="Stage number (1-based)"
    )

    # Locations
    correct_location = Column(
        "correct_location", Integer,
        comment="Location of correct stimulus "
                "(0 top, 1 right, 2 bottom, 3 left)"
    )
    incorrect_location = Column(
        "incorrect_location", Integer,
        comment="Location of incorrect stimulus "
                "(0 top, 1 right, 2 bottom, 3 left)"
    )

    # Stimuli
    correct_shape = Column(
        "correct_shape", Integer,
        comment="Shape# of correct stimulus"
    )
    correct_colour = Column(
        "correct_colour", Text,
        comment="HTML colour of correct stimulus"
    )
    correct_number = Column(
        "correct_number", Integer,
        comment="Number of copies of correct stimulus"
    )
    incorrect_shape = Column(
        "incorrect_shape", Integer,
        comment="Shape# of incorrect stimulus"
    )
    incorrect_colour = Column(
        "incorrect_colour", Text,
        comment="HTML colour of incorrect stimulus"
    )
    incorrect_number = Column(
        "incorrect_number", Integer,
        comment="Number of copies of incorrect stimulus"
    )

    # Trial
    trial_start_time = Column(
        "trial_start_time", PendulumDateTimeAsIsoTextColType,
        comment="Trial start time / stimuli presented at (ISO-8601)"
    )

    # Response
    responded = CamcopsColumn(
        "responded", Boolean,
        permitted_value_checker=BIT_CHECKER,
        comment="Did the subject respond?"
    )
    response_time = Column(
        "response_time", PendulumDateTimeAsIsoTextColType,
        comment="Time of response (ISO-8601)"
    )
    response_latency_ms = Column(
        "response_latency_ms", Integer,
        comment="Response latency (ms)"
    )
    correct = CamcopsColumn(
        "correct", Boolean,
        permitted_value_checker=BIT_CHECKER,
        comment="Response was correct"
    )
    incorrect = CamcopsColumn(
        "incorrect", Boolean,
        permitted_value_checker=BIT_CHECKER,
        comment="Response was incorrect"
    )

    @classmethod
    def get_html_table_header(cls) -> str:
        return """
            <table class="{CssClass.EXTRADETAIL}">
                <tr>
                    <th>Trial#</th>
                    <th>Stage#</th>
                    <th>Correct location</th>
                    <th>Incorrect location</th>
                    <th>Correct shape</th>
                    <th>Correct colour</th>
                    <th>Correct number</th>
                    <th>Incorrect shape</th>
                    <th>Incorrect colour</th>
                    <th>Incorrect number</th>
                    <th>Trial start time</th>
                    <th>Responded?</th>
                    <th>Response time</th>
                    <th>Response latency (ms)</th>
                    <th>Correct?</th>
                    <th>Incorrect?</th>
                </tr>
        """.format(CssClass=CssClass)

    def get_html_table_row(self) -> str:
        return tr(
            a(self.trial),
            a(self.stage),
            a(self.correct_location),
            a(self.incorrect_location),
            a(self.correct_shape),
            a(self.correct_colour),
            a(self.correct_number),
            a(self.incorrect_shape),
            a(self.incorrect_colour),
            a(self.incorrect_number),
            a(self.trial_start_time),
            a(self.responded),
            a(self.response_time),
            a(self.response_latency_ms),
            a(self.correct),
            a(self.incorrect),
        )


class IDED3DStage(GenericTabletRecordMixin, Base):
    __tablename__ = "ided3d_stages"

    ided3d_id = Column(
        "ided3d_id", Integer,
        nullable=False,
        comment="FK to ided3d"
    )
    stage = Column(
        "stage", Integer,
        nullable=False,
        comment="Stage number (1-based)"
    )

    # Config
    stage_name = Column(
        "stage_name", Text,
        comment="Name of the stage (e.g. SD, EDr)"
    )
    relevant_dimension = Column(
        "relevant_dimension", Text,
        comment="Relevant dimension (e.g. shape, colour, number)"
    )
    correct_exemplar = Column(
        "correct_exemplar", Text,
        comment="Correct exemplar (from relevant dimension)"
    )
    incorrect_exemplar = Column(
        "incorrect_exemplar", Text,
        comment="Incorrect exemplar (from relevant dimension)"
    )
    correct_stimulus_shapes = Column(
        "correct_stimulus_shapes", Text,
        comment="Possible shapes for correct stimulus "
                "(CSV list of shape numbers)"
    )
    correct_stimulus_colours = Column(
        "correct_stimulus_colours", Text,
        comment="Possible colours for correct stimulus "
                "(CSV list of HTML colours)"
    )
    correct_stimulus_numbers = Column(
        "correct_stimulus_numbers", Text,
        comment="Possible numbers for correct stimulus "
                "(CSV list of numbers)"
    )
    incorrect_stimulus_shapes = Column(
        "incorrect_stimulus_shapes", Text,
        comment="Possible shapes for incorrect stimulus "
                "(CSV list of shape numbers)"
    )
    incorrect_stimulus_colours = Column(
        "incorrect_stimulus_colours", Text,
        comment="Possible colours for incorrect stimulus "
                "(CSV list of HTML colours)"
    )
    incorrect_stimulus_numbers = Column(
        "incorrect_stimulus_numbers", Text,
        comment="Possible numbers for incorrect stimulus "
                "(CSV list of numbers)"
    )

    # Results
    first_trial_num = Column(
        "first_trial_num", Integer,
        comment="Number of the first trial of the stage (1-based)"
    )
    n_completed_trials = Column(
        "n_completed_trials", Integer,
        comment="Number of trials completed"
    )
    n_correct = Column(
        "n_correct", Integer,
        comment="Number of trials performed correctly"
    )
    n_incorrect = Column(
        "n_incorrect", Integer,
        comment="Number of trials performed incorrectly"
    )
    stage_passed = CamcopsColumn(
        "stage_passed", Boolean,
        permitted_value_checker=BIT_CHECKER,
        comment="Subject met criterion and passed stage"
    )
    stage_failed = CamcopsColumn(
        "stage_failed", Boolean,
        permitted_value_checker=BIT_CHECKER,
        comment="Subject took too many trials and failed stage"
    )

    @classmethod
    def get_html_table_header(cls) -> str:
        return """
            <table class="{CssClass.EXTRADETAIL}">
                <tr>
                    <th>Stage#</th>
                    <th>Stage name</th>
                    <th>Relevant dimension</th>
                    <th>Correct exemplar</th>
                    <th>Incorrect exemplar</th>
                    <th>Shapes for correct</th>
                    <th>Colours for correct</th>
                    <th>Numbers for correct</th>
                    <th>Shapes for incorrect</th>
                    <th>Colours for incorrect</th>
                    <th>Numbers for incorrect</th>
                    <th>First trial#</th>
                    <th>#completed trials</th>
                    <th>#correct</th>
                    <th>#incorrect</th>
                    <th>Passed?</th>
                    <th>Failed?</th>
                </tr>
        """.format(CssClass=CssClass)

    def get_html_table_row(self) -> str:
        return tr(
            a(self.stage),
            a(self.stage_name),
            a(self.relevant_dimension),
            a(self.correct_exemplar),
            a(self.incorrect_exemplar),
            a(self.correct_stimulus_shapes),
            a(self.correct_stimulus_colours),
            a(self.correct_stimulus_numbers),
            a(self.incorrect_stimulus_shapes),
            a(self.incorrect_stimulus_colours),
            a(self.incorrect_stimulus_numbers),
            a(self.first_trial_num),
            a(self.n_completed_trials),
            a(self.n_correct),
            a(self.n_incorrect),
            a(self.stage_passed),
            a(self.stage_failed),
        )


class IDED3D(TaskHasPatientMixin, Task):
    """
    Server implementation of the ID/ED-3D task.
    """
    __tablename__ = "ided3d"
    shortname = "ID/ED-3D"
    longname = "Three-dimensional ID/ED task"

    # Config
    last_stage = Column(
        "last_stage", Integer,
        comment="Last stage to offer (1 [SD] - 8 [EDR])"
    )
    max_trials_per_stage = Column(
        "max_trials_per_stage", Integer,
        comment="Maximum number of trials allowed per stage before "
                "the task aborts"
    )
    progress_criterion_x = Column(
        "progress_criterion_x", Integer,
        comment='Criterion to proceed to next stage: X correct out of'
                ' the last Y trials, where this is X'
    )
    progress_criterion_y = Column(
        "progress_criterion_y", Integer,
        comment='Criterion to proceed to next stage: X correct out of'
                ' the last Y trials, where this is Y'
    )
    min_number = Column(
        "min_number", Integer,
        comment="Minimum number of stimulus element to use"
    )
    max_number = Column(
        "max_number", Integer,
        comment="Maximum number of stimulus element to use"
    )
    pause_after_beep_ms = Column(
        "pause_after_beep_ms", Integer,
        comment="Time to continue visual feedback after auditory "
                "feedback finished (ms)"
    )
    iti_ms = Column(
        "iti_ms", Integer,
        comment="Intertrial interval (ms)"
    )
    counterbalance_dimensions = Column(
        "counterbalance_dimensions", Integer,
        comment="Dimensional counterbalancing condition (0-5)"
    )
    volume = Column(
        "volume", Float,
        comment="Sound volume (0.0-1.0)"
    )
    offer_abort = CamcopsColumn(
        "offer_abort", Boolean,
        permitted_value_checker=BIT_CHECKER,
        comment="Offer an abort button?"
    )
    debug_display_stimuli_only = CamcopsColumn(
        "debug_display_stimuli_only", Boolean,
        permitted_value_checker=BIT_CHECKER,
        comment="DEBUG: show stimuli only, don't run task"
    )

    # Intrinsic config
    shape_definitions_svg = Column(
        "shape_definitions_svg", Text,
        comment="JSON-encoded version of shape definition"
                " array in SVG format (with arbitrary scale of -60 to"
                " +60 in both X and Y dimensions)"
    )
    colour_definitions_rgb = Column(  # v2.0.0
        "colour_definitions_rgb", Text,
        comment="JSON-encoded version of colour RGB definitions"
    )

    # Results
    aborted = Column(
        "aborted", Integer,
        comment="Was the task aborted? (0 no, 1 yes)"
    )
    finished = Column(
        "finished", Integer,
        comment="Was the task finished? (0 no, 1 yes)"
    )
    last_trial_completed = Column(
        "last_trial_completed", Integer,
        comment="Number of last trial completed"
    )

    # Relationships
    trials = ancillary_relationship(
        parent_class_name="IDED3D",
        ancillary_class_name="IDED3DTrial",
        ancillary_fk_to_parent_attr_name="ided3d_id",
        ancillary_order_by_attr_name="trial"
    )  # type: List[IDED3DTrial]
    stages = ancillary_relationship(
        parent_class_name="IDED3D",
        ancillary_class_name="IDED3DStage",
        ancillary_fk_to_parent_attr_name="ided3d_id",
        ancillary_order_by_attr_name="stage"
    )  # type: List[IDED3DStage]

    def is_complete(self) -> bool:
        return bool(self.debug_display_stimuli_only) or bool(self.finished)

    def get_stage_html(self) -> str:
        html = IDED3DStage.get_html_table_header()
        # noinspection PyTypeChecker
        for s in self.stages:
            html += s.get_html_table_row()
        html += """</table>"""
        return html

    def get_trial_html(self) -> str:
        html = IDED3DTrial.get_html_table_header()
        # noinspection PyTypeChecker
        for t in self.trials:
            html += t.get_html_table_row()
        html += """</table>"""
        return html

    def get_task_html(self, req: CamcopsRequest) -> str:
        h = """
            <div class="{CssClass.SUMMARY}">
                <table class="{CssClass.SUMMARY}">
                    {tr_is_complete}
                </table>
            </div>
            <div class="{CssClass.EXPLANATION}">
                1. Simple discrimination (SD), and 2. reversal (SDr);
                3. compound discrimination (CD), and 4. reversal (CDr);
                5. intradimensional shift (ID), and 6. reversal (IDr);
                7. extradimensional shift (ED), and 8. reversal (EDr).
            </div>
            <table class="{CssClass.TASKCONFIG}">
                <tr>
                    <th width="50%">Configuration variable</th>
                    <th width="50%">Value</th>
                </tr>
        """.format(
            CssClass=CssClass,
            tr_is_complete=self.get_is_complete_tr(req),
        )
        h += tr_qa(self.wxstring(req, "last_stage"), self.last_stage)
        h += tr_qa(self.wxstring(req, "max_trials_per_stage"),
                   self.max_trials_per_stage)
        h += tr_qa(self.wxstring(req, "progress_criterion_x"),
                   self.progress_criterion_x)
        h += tr_qa(self.wxstring(req, "progress_criterion_y"),
                   self.progress_criterion_y)
        h += tr_qa(self.wxstring(req, "min_number"), self.min_number)
        h += tr_qa(self.wxstring(req, "max_number"), self.max_number)
        h += tr_qa(self.wxstring(req, "pause_after_beep_ms"),
                   self.pause_after_beep_ms)
        h += tr_qa(self.wxstring(req, "iti_ms"), self.iti_ms)
        h += tr_qa(
            self.wxstring(req, "counterbalance_dimensions") + "<sup>[1]</sup>",
            self.counterbalance_dimensions)
        h += tr_qa(req.wappstring("volume_0_to_1"), self.volume)
        h += tr_qa(self.wxstring(req, "offer_abort"), self.offer_abort)
        h += tr_qa(self.wxstring(req, "debug_display_stimuli_only"),
                   self.debug_display_stimuli_only)
        h += tr_qa("Shapes (as a JSON-encoded array of SVG "
                   "definitions; X and Y range both –60 to +60)",
                   ws.webify(self.shape_definitions_svg))
        h += """
            </table>
            <table class="{CssClass.TASKDETAIL}">
                <tr><th width="50%">Measure</th><th width="50%">Value</th></tr>
        """.format(CssClass=CssClass)
        h += tr_qa("Aborted?", get_yes_no_none(req, self.aborted))
        h += tr_qa("Finished?", get_yes_no_none(req, self.finished))
        h += tr_qa("Last trial completed", self.last_trial_completed)
        h += (
            """
                </table>
                <div>Stage specifications and results:</div>
            """ +
            self.get_stage_html() +
            "<div>Trial-by-trial results:</div>" +
            self.get_trial_html() +
            """
                <div class="{CssClass.FOOTNOTES}">
                    [1] Counterbalancing of dimensions is as follows, with
                    notation X/Y indicating that X is the first relevant
                    dimension (for stages SD–IDr) and Y is the second relevant
                    dimension (for stages ED–EDr).
                    0: shape/colour.
                    1: colour/number.
                    2: number/shape.
                    3: shape/number.
                    4: colour/shape.
                    5: number/colour.
                </div>
            """.format(CssClass=CssClass)
        )
        return h
