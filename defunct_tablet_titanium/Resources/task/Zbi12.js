// Zbi12.js

/*
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
*/

/*jslint node: true, newcap: true, nomen: true, plusplus: true, unparam: true */
"use strict";
/*global L */

var DBCONSTANTS = require('common/DBCONSTANTS'),
    dbcommon = require('lib/dbcommon'),
    taskcommon = require('lib/taskcommon'),
    lang = require('lib/lang'),
    tablename = "zbi12",
    fieldlist = dbcommon.standardTaskFields(),
    nquestions = 12;

fieldlist.push.apply(fieldlist, dbcommon.RESPONDENT_FIELDSPECS);
dbcommon.appendRepeatedFieldDef(fieldlist, "q", 1, nquestions,
                                DBCONSTANTS.TYPE_INTEGER);

// CREATE THE TABLE

dbcommon.createTable(tablename, fieldlist);

// TASK

function Zbi12(patient_id) {
    taskcommon.BaseTask.call(this, patient_id); // call base constructor
}

lang.inheritPrototype(Zbi12, taskcommon.BaseTask);
lang.extendPrototype(Zbi12, {

    // KEY DATABASE FIELDS (USED BY DatabaseObject)

    _objecttype: Zbi12,
    _tablename: tablename,
    _fieldlist: fieldlist,

    // TASK CLASS FIELD OVERRIDES (USED BY BaseTask)

    _extrastringTaskname: "zbi12",
    isTaskCrippled: function () {
        return !this.extraStringsPresent();
    },

    // EXTRA STRINGS

    get_questions: function () {
        var arr = [],
            i;
        for (i = 1; i <= nquestions; ++i) {
            arr.push(this.XSTRING("q" + i, "Q" + i));
        }
        return arr;
    },

    // OTHER

    // Standard task functions
    isComplete: function () {
        return (
            this.isRespondentComplete() &&
            taskcommon.isCompleteByPrefix(this, "q", 1, nquestions)
        );
    },

    getSummary: function () {
        return (this.respondent_relationship || "") + this.isCompleteSuffix();
    },

    getDetail: function () {
        return this.getSummary();
    },

    edit: function (readOnly) {
        var self = this,
            KeyValuePair = require('lib/KeyValuePair'),
            Questionnaire = require('questionnaire/Questionnaire'),
            elements,
            pages,
            questionnaire;

        elements = [
            this.getRespondentQuestionnaireBlock(true),
            {
                type: "QuestionText",
                bold: true,
                text: this.XSTRING('instruction')
            },
            {
                type: "QuestionMCQGrid",
                options: [
                    new KeyValuePair(L('zbi_a0'), 0),
                    new KeyValuePair(L('zbi_a1'), 1),
                    new KeyValuePair(L('zbi_a2'), 2),
                    new KeyValuePair(L('zbi_a3'), 3),
                    new KeyValuePair(L('zbi_a4'), 4)
                ],
                questions: this.get_questions(),
                fields: taskcommon.stringArrayFromSequence("q", 1, nquestions),
                optionsWidthTogether: '65%'
            }
        ];

        pages = [
            {
                title: L('t_zbi12'),
                clinician: false,
                elements: elements
            }
        ];

        questionnaire = new Questionnaire({
            readOnly: readOnly,
            pages: pages,
            callbackThis: self,
            fnGetFieldValue: self.defaultGetFieldValueFn,
            fnSetField: self.defaultSetFieldFn,
            fnFinished: self.defaultFinishedFn
        });

        questionnaire.open();
    }

});

module.exports = Zbi12;
