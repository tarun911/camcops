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
#include "db/fieldref.h"
#include "questionnairelib/quelement.h"

class QDoubleSpinBox;


class QuSpinBoxDouble : public QuElement
{
    // Offers a text editing box with spinbox controls, for floating-point
    // entry.

    Q_OBJECT
public:
    QuSpinBoxDouble(FieldRefPtr fieldref, double minimum, double maximum,
                    int decimals = 2);
protected:
    void setFromField();
    virtual QPointer<QWidget> makeWidget(Questionnaire* questionnaire) override;
    virtual FieldRefPtrList fieldrefs() const override;
protected slots:
    void widgetValueChanged(double value);
    void widgetValueChangedString(const QString& text);
    void fieldValueChanged(const FieldRef* fieldref,
                           const QObject* originator = nullptr);
protected:
    FieldRefPtr m_fieldref;
    double m_minimum;
    double m_maximum;
    int m_decimals;
    QPointer<QDoubleSpinBox> m_spinbox;
};
