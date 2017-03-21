/*
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
*/

#include "auditc.h"
#include "audit.h"  // for AUDIT_TABLENAME
#include "lib/mathfunc.h"
#include "lib/stringfunc.h"
#include "questionnairelib/namevaluepair.h"
#include "questionnairelib/questionnaire.h"
#include "questionnairelib/qumcq.h"
#include "questionnairelib/qutext.h"
#include "tasklib/taskfactory.h"
using mathfunc::anyNull;
using mathfunc::noneNull;
using mathfunc::sumInt;
using mathfunc::totalScorePhrase;
using stringfunc::strseq;

const int FIRST_Q = 1;
const int N_QUESTIONS = 3;
const int MAX_SCORE = N_QUESTIONS * 4;
const QString QPREFIX("q");

const QString TABLENAME("audit_c");


void initializeAuditC(TaskFactory& factory)
{
    static TaskRegistrar<AuditC> registered(factory);
}


AuditC::AuditC(CamcopsApp& app, const QSqlDatabase& db, int load_pk) :
    Task(app, db, TABLENAME, false, false, false)  // ... anon, clin, resp
{
    addFields(strseq(QPREFIX, FIRST_Q, N_QUESTIONS), QVariant::Int);

    load(load_pk);  // MUST ALWAYS CALL from derived Task constructor.
}


// ============================================================================
// Class info
// ============================================================================

QString AuditC::shortname() const
{
    return "AUDIT-C";
}


QString AuditC::longname() const
{
    return tr("Alcohol Use Disorders Identification Test");
}


QString AuditC::menusubtitle() const
{
    return tr("3-item consumption subset of the AUDIT; "
              "clinician-administered screening test.");
}


QString AuditC::xstringTaskname() const
{
    return AUDIT_TABLENAME;  // shares strings with AUDIT
}


// ============================================================================
// Instance info
// ============================================================================

bool AuditC::isComplete() const
{
    return noneNull(values(strseq(QPREFIX, FIRST_Q, N_QUESTIONS)));
}


QStringList AuditC::summary() const
{
    return QStringList{totalScorePhrase(totalScore(), MAX_SCORE)};
}


QStringList AuditC::detail() const
{
    QStringList lines = fieldSummaries("q", "_s", " ",
                                       QPREFIX, FIRST_Q, N_QUESTIONS);
    lines.append("");
    lines += summary();
    return lines;
}


OpenableWidget* AuditC::editor(bool read_only)
{
    NameValueOptions options1{
        {xstring("q1_option0"), 0},
        {xstring("q1_option1"), 1},
        {xstring("q1_option2"), 2},
        {xstring("q1_option3"), 3},
        {xstring("q1_option4"), 4},
    };
    NameValueOptions options2{
        {xstring("c_q2_option0"), 0},  // NB different from AUDIT
        {xstring("q2_option1"), 1},
        {xstring("q2_option2"), 2},
        {xstring("q2_option3"), 3},
        {xstring("q2_option4"), 4},
    };
    NameValueOptions options3{
        {xstring("q3to8_option0"), 0},
        {xstring("q3to8_option1"), 1},
        {xstring("q3to8_option2"), 2},
        {xstring("q3to8_option3"), 3},
        {xstring("q3to8_option4"), 4},
    };
    QString qprefix = xstring("c_qprefix");

    QuPagePtr page1((new QuPage{
        new QuText(xstring("instructions_1")),
        // no "instructions_2"
        new QuText(xstring("instructions_3")),
        new QuText(xstring("instructions_4")),
        new QuText(xstring("instructions_5")),
    })->setType(QuPage::PageType::Clinician)->setTitle(shortname()));

    QuPagePtr page2((new QuPage{
        (new QuText(xstring("c_q1_question")))->setBold(),
        new QuText(xstring("c_instruction")),
        new QuMcq(fieldRef("q1"), options1),
    })->setType(QuPage::PageType::Clinician)->setTitle(qprefix + " 1"));

    QuPagePtr page3((new QuPage{
        (new QuText(xstring("c_q2_question")))->setBold(),
        new QuMcq(fieldRef("q2"), options2),
    })->setType(QuPage::PageType::Clinician)->setTitle(qprefix + " 2"));

    QuPagePtr page4((new QuPage{
        (new QuText(xstring("c_q3_question")))->setBold(),
        new QuMcq(fieldRef("q3"), options3),
    })->setType(QuPage::PageType::Clinician)->setTitle(qprefix + " 3"));

    Questionnaire* questionnaire = new Questionnaire(
                m_app, {page1, page2, page3, page4});
    questionnaire->setReadOnly(read_only);
    return questionnaire;
}


// ============================================================================
// Task-specific calculations
// ============================================================================

int AuditC::totalScore() const
{
    return sumInt(values(strseq(QPREFIX, FIRST_Q, N_QUESTIONS)));
}