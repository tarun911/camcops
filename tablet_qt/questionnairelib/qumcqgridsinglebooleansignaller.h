/*
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
*/

#pragma once
#include <QObject>

// This should be a private (nested) class of QuMCQGrid, but you can't nest
// Q_OBJECT classes ("Error: Meta object features not supported for nested
// classes").

class FieldRef;
class QuMcqGridSingleBoolean;


class QuMcqGridSingleBooleanSignaller : public QObject {
    Q_OBJECT
public:
    QuMcqGridSingleBooleanSignaller(QuMcqGridSingleBoolean* recipient,
                                    int question_index);
public slots:
    void mcqFieldValueOrMandatoryChanged(const FieldRef* fieldref);
    void booleanFieldValueOrMandatoryChanged(const FieldRef* fieldref);
protected:
    QuMcqGridSingleBoolean* m_recipient;
    int m_question_index;
};
