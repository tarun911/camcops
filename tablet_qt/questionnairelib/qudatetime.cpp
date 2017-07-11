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

#include "qudatetime.h"
#include <QCalendarWidget>
#include <QDateTimeEdit>
#include <QFont>
#include <QHBoxLayout>
#include "lib/uifunc.h"
#include "questionnairelib/questionnaire.h"
#include "widgets/imagebutton.h"
#include "widgets/spacer.h"

// http://doc.qt.io/qt-5/qdatetime.html#toString
const QString DEFAULT_DATETIME_FORMAT("dd MMM yyyy HH:mm");
const QString DEFAULT_DATE_FORMAT("dd MMM yyyy");
const QString DEFAULT_TIME_FORMAT("HH:mm");
// const QDate PSEUDONULL_DATE(1752, 9, 14);  // 14 Sep 1752 is usual minimum (Gregorian calendar)
const QDate PSEUDONULL_DATE(2000, 1, 1);  // ... but 1752 is a long way away from now...
const QTime PSEUDONULL_TIME(0, 0, 0, 0);
const QDateTime PSEUDONULL_DATETIME(PSEUDONULL_DATE, PSEUDONULL_TIME);


QuDateTime::QuDateTime(FieldRefPtr fieldref) :
    m_fieldref(fieldref),
    m_mode(Mode::DefaultDateTime),
    m_offer_now_button(false),
    m_offer_null_button(false),
    m_editor(nullptr),
    m_calendar_widget(nullptr)
{
    Q_ASSERT(m_fieldref);
    connect(m_fieldref.data(), &FieldRef::valueChanged,
            this, &QuDateTime::fieldValueChanged);
    connect(m_fieldref.data(), &FieldRef::mandatoryChanged,
            this, &QuDateTime::fieldValueChanged);
}


QuDateTime* QuDateTime::setMode(QuDateTime::Mode mode)
{
    m_mode = mode;
    return this;
}


QuDateTime* QuDateTime::setCustomFormat(const QString& format)
{
    m_custom_format = format;
    return this;
}


QuDateTime* QuDateTime::setOfferNowButton(bool offer_now_button)
{
    m_offer_now_button = offer_now_button;
    return this;
}


QuDateTime* QuDateTime::setOfferNullButton(bool offer_null_button)
{
    m_offer_null_button = offer_null_button;
    return this;
}


void QuDateTime::setFromField()
{
    fieldValueChanged(m_fieldref.data(), nullptr);
}


FieldRefPtrList QuDateTime::fieldrefs() const
{
    return FieldRefPtrList{m_fieldref};
}


QPointer<QWidget> QuDateTime::makeWidget(Questionnaire* questionnaire)
{
    bool read_only = questionnaire->readOnly();

    QPointer<QWidget> widget = new QWidget();
    widget->setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
    QHBoxLayout* layout = new QHBoxLayout();
    layout->setContentsMargins(uiconst::NO_MARGINS);
    widget->setLayout(layout);

    QString format;
    bool use_calendar = true;
    switch (m_mode) {
    case DefaultDateTime:
        format = DEFAULT_DATETIME_FORMAT;
        break;
    case DefaultDate:
        format = DEFAULT_DATE_FORMAT;
        break;
    case DefaultTime:
        format = DEFAULT_TIME_FORMAT;
        use_calendar = false;
        break;
    case CustomDateTime:
    case CustomDate:
        format = m_custom_format;
        break;
    case CustomTime:
        format = m_custom_format;
        use_calendar = false;
        break;
    }

    m_editor = new QDateTimeEdit();
    m_editor->setDisplayFormat(format);

    m_editor->setCalendarPopup(use_calendar);
    /*
    TO THINK ABOUT: QuDateTime time picker
    - Qt only supplies a date (calendar) popup.
      You can explore its features using the "calendarwidget" demo.
    - It is possible to write ones to do times as well.
    - http://doc.qt.io/qt-5/qdatetimeedit.html#using-a-pop-up-calendar-widget
    - http://doc.qt.io/qt-5/qtwidgets-widgets-calendarwidget-example.html
    - https://forum.qt.io/topic/71670/qdatetimeedit-with-date-and-time-picker/6
    - Looking at the various bits of source:

        void QDateTimeEditPrivate::initCalendarPopup(QCalendarWidget *cw)
        {
            Q_Q(QDateTimeEdit);
            if (!monthCalendar) {
                monthCalendar = new QCalendarPopup(q, cw);
                monthCalendar->setObjectName(QLatin1String("qt_datetimedit_calendar"));
                QObject::connect(monthCalendar, SIGNAL(newDateSelected(QDate)), q, SLOT(setDate(QDate)));
                QObject::connect(monthCalendar, SIGNAL(hidingCalendar(QDate)), q, SLOT(setDate(QDate)));
                QObject::connect(monthCalendar, SIGNAL(activated(QDate)), q, SLOT(setDate(QDate)));
                QObject::connect(monthCalendar, SIGNAL(activated(QDate)), monthCalendar, SLOT(close()));
                QObject::connect(monthCalendar, SIGNAL(resetButton()), q, SLOT(_q_resetButton()));
            } else if (cw) {
                monthCalendar->setCalendarWidget(cw);
            }
            syncCalendarWidget();
        }

    - Alternatively, for dates: alter the stylesheet to make the
      QCalendarWidget big enough to use on tablets.

    */
    if (use_calendar) {
        // Editor does NOT take ownership, so we should:
        // http://doc.qt.io/qt-5/qdatetimeedit.html#setCalendarWidget
        m_calendar_widget = QSharedPointer<QCalendarWidget>(new QCalendarWidget());
        // QFont font;
        // font.setBold(true);  // works!
        // font.setPixelSize(60);  // Does NOT work!
        // m_calendar_widget->setFont(font);
        m_editor->setCalendarWidget(m_calendar_widget.data());
    }

    m_editor->setEnabled(!read_only);
    m_editor->setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Expanding);
    // Fixed horizontal keeps the drop-down button close to the text.
    // Expanding vertical makes the drop-down button and spin buttons a
    // reasonable size (not too small).
    m_editor->setMinimumHeight(uiconst::MIN_SPINBOX_HEIGHT);
    // Also, the QDateTimeEdit *is* a QAbstractSpinBox, so:
    m_editor->setButtonSymbols(uiconst::SPINBOX_SYMBOLS);
    if (!read_only) {
        connect(m_editor.data(), &QDateTimeEdit::dateTimeChanged,
                this, &QuDateTime::widgetValueChanged);
    }
    layout->addWidget(m_editor);

    if (m_offer_now_button) {
        QAbstractButton* now_button = new ImageButton(uiconst::CBS_TIME_NOW);
        now_button->setEnabled(!read_only);
        if (!read_only) {
            connect(now_button, &QAbstractButton::clicked,
                    this, &QuDateTime::setToNow);
        }
        layout->addWidget(now_button);
    }

    if (m_offer_null_button) {
        QAbstractButton* null_button = new ImageButton(uiconst::CBS_DELETE);
        null_button->setEnabled(!read_only);
        if (!read_only) {
            connect(null_button, &QAbstractButton::clicked,
                    this, &QuDateTime::setToNull);
        }
        layout->addWidget(null_button);
    }

    layout->addStretch();

    setFromField();
    return widget;
}


// It will show a NULL as yellow, but as soon as you edit the field,
// it un-NULLs it irreversibly. (You could use e.g. 14 Sep 1752 00:00 as a
// pseudo-NULL that you can enter, but that doesn't work when you want to
// enter midnight deliberately, and starting with 1752 just looks odd.)

void QuDateTime::widgetValueChanged(const QDateTime& datetime)
{
    setField(datetime, false);
}


void QuDateTime::setField(const QDateTime& datetime, bool reset_this_widget)
{
    QVariant newvalue = datetime;
    switch (m_mode) {
    case DefaultDateTime:
    case CustomDateTime:
        newvalue.convert(QVariant::DateTime);
        break;
    case DefaultDate:
    case CustomDate:
        newvalue.convert(QVariant::Date);
        break;
    case DefaultTime:
    case CustomTime:
        newvalue.convert(QVariant::Time);
        break;
    }
    bool changed = m_fieldref->setValue(newvalue, reset_this_widget ? nullptr : this);
    if (changed) {
        emit elementValueChanged();
    }
}


void QuDateTime::setToNow()
{
    setField(QDateTime::currentDateTime(), true);
}


void QuDateTime::setToNull()
{
    setField(QDateTime(), true);
}


void QuDateTime::fieldValueChanged(const FieldRef* fieldref,
                                   const QObject* originator)
{
    if (!m_editor) {
        return;
    }
    // Missing?
    uifunc::setPropertyMissing(m_editor, fieldref->missingInput());
    if (originator != this) {
        // Value
        QDateTime display_value = fieldref->valueDateTime();
        if (!display_value.isValid()) {
            display_value = PSEUDONULL_DATETIME;
            // because QDateTimeEdit::setDateTime() will ignore invalid values
        }
        const QSignalBlocker blocker(m_editor);
        m_editor->setDateTime(display_value);
        // NULL will be shown as the pseudonull value.
        // The yellow marker will disappear when that value is edited.
    }
}
