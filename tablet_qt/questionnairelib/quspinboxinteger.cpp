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

#include "quspinboxinteger.h"
#include <QSpinBox>
#include "lib/uifunc.h"
#include "questionnairelib/questionnaire.h"


QuSpinBoxInteger::QuSpinBoxInteger(FieldRefPtr fieldref, int minimum,
                                   int maximum) :
    m_fieldref(fieldref),
    m_minimum(minimum),
    m_maximum(maximum)
{
    Q_ASSERT(m_fieldref);
    connect(m_fieldref.data(), &FieldRef::valueChanged,
            this, &QuSpinBoxInteger::fieldValueChanged);
    connect(m_fieldref.data(), &FieldRef::mandatoryChanged,
            this, &QuSpinBoxInteger::fieldValueChanged);
}


void QuSpinBoxInteger::setFromField()
{
    fieldValueChanged(m_fieldref.data(), nullptr);
    // special; pretend "it didn't come from us" to disable the efficiency
    // check in fieldValueChanged
}


QPointer<QWidget> QuSpinBoxInteger::makeWidget(Questionnaire* questionnaire)
{
    const bool read_only = questionnaire->readOnly();
    m_spinbox = new QSpinBox();
    m_spinbox->setEnabled(!read_only);
    m_spinbox->setRange(m_minimum, m_maximum);
    m_spinbox->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Fixed);
    m_spinbox->setMinimumHeight(uiconst::MIN_SPINBOX_HEIGHT);  // room for spin arrows
    m_spinbox->setButtonSymbols(uiconst::SPINBOX_SYMBOLS);
    m_spinbox->setInputMethodHints(Qt::ImhFormattedNumbersOnly);

    // QSpinBox has two signals named valueChanged, differing only
    // in the parameter they pass (int versus QString&). You get
    // "no matching function for call to ... unresolved overloaded function
    // type..."
    // Disambiguate like this:
    void (QSpinBox::*vc_signal)(int) = &QSpinBox::valueChanged;
    if (!read_only) {
        connect(m_spinbox.data(), vc_signal,
                this, &QuSpinBoxInteger::widgetValueChanged);
    }
    setFromField();
    return QPointer<QWidget>(m_spinbox);
}


FieldRefPtrList QuSpinBoxInteger::fieldrefs() const
{
    return FieldRefPtrList{m_fieldref};
}


void QuSpinBoxInteger::widgetValueChanged(int value)
{
    const bool changed = m_fieldref->setValue(value, this);  // Will trigger valueChanged
    if (changed) {
        emit elementValueChanged();
    }
}


void QuSpinBoxInteger::fieldValueChanged(const FieldRef* fieldref,
                                         const QObject* originator)
{
    if (!m_spinbox) {
        return;
    }
    uifunc::setPropertyMissing(m_spinbox, fieldref->missingInput());
    if (originator != this) {
        const QSignalBlocker blocker(m_spinbox);
        m_spinbox->setValue(fieldref->valueInt());
    }
}
