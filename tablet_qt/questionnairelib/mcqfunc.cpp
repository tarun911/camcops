/*
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

#include "mcqfunc.h"
#include <QDebug>
#include <QString>
#include "common/cssconst.h"
#include "common/uiconstants.h"
#include "db/fieldref.h"
#include "widgets/booleanwidget.h"
#include "widgets/labelwordwrapwide.h"
#include "widgets/verticalline.h"
#include "namevalueoptions.h"

// ============================================================================
// Alignment
// ============================================================================

namespace mcqfunc {

Qt::Alignment question_text_align = Qt::AlignVCenter;
Qt::Alignment question_widget_align = Qt::AlignVCenter;
// don't do right align; disrupts natural reading flow

Qt::Alignment title_text_align = Qt::AlignTop;
Qt::Alignment title_widget_align = Qt::AlignTop;

Qt::Alignment option_text_align = Qt::AlignCenter | Qt::AlignBottom;
Qt::Alignment option_widget_align = Qt::AlignCenter | Qt::AlignBottom;

// If you don't apply a widget alignment, the label widget takes the entire
// cell -- which is fine for the most part (the text alignment does the rest)
// -- but not when you want a *bottom* alignment.

Qt::Alignment response_widget_align = Qt::AlignCenter | Qt::AlignTop;

}  // namespace mcqfunc


// ============================================================================
// Background to part of a QGridLayout
// ============================================================================
/*

- Layouts don't draw.
- They are unresponsive to CSS.
  http://doc.qt.io/qt-5.7/stylesheet-reference.html
- Use setSpacing() and related to set/remove spacing between widgets.
- So one possibility is:
    - setSpacing(0)
    - set background colour of options
    - add some sort of other spacing (e.g. padding) for the actual widgets

- Is another possibility:
    - a grey background as a background?

*/

void mcqfunc::addVerticalLine(GridLayout* grid, int col, int n_rows)
{
    VerticalLine* vline = new VerticalLine(uiconst::MCQGRID_VLINE_WIDTH);
    vline->setObjectName(cssconst::VLINE);
    grid->addWidget(vline, 0, col, n_rows, 1);
}


void mcqfunc::addQuestion(GridLayout* grid, int row,
                          const QString& question)
{
    LabelWordWrapWide* q = new LabelWordWrapWide(question);
    q->setAlignment(question_text_align);
    q->setObjectName(cssconst::QUESTION);
    grid->addWidget(q, row, 0, question_widget_align);
}


void mcqfunc::addTitle(GridLayout* grid, int row, const QString& title)
{
    if (!title.isEmpty()) {
        LabelWordWrapWide* w = new LabelWordWrapWide(title);
        w->setAlignment(title_text_align);
        w->setObjectName(cssconst::TITLE);
        grid->addWidget(w, row, 0, title_widget_align);
    }
}


void mcqfunc::addSubtitle(GridLayout* grid, int row,
                          const QString& subtitle)
{
    if (!subtitle.isEmpty()) {
        LabelWordWrapWide* w = new LabelWordWrapWide(subtitle);
        w->setAlignment(title_text_align);
        w->setObjectName(cssconst::SUBTITLE);
        grid->addWidget(w, row, 0, title_widget_align);
    }
}


void mcqfunc::addOption(GridLayout* grid, int row, int col,
                        const QString& option)
{
    LabelWordWrapWide* w = new LabelWordWrapWide(option);
    w->setAlignment(option_text_align);
    w->setObjectName(cssconst::OPTION);
    grid->addWidget(w, row, col, option_widget_align);
}


void mcqfunc::addOptionBackground(GridLayout* grid, int row,
                                  int firstcol, int ncols)
{
    QWidget* bg = new QWidget();
    bg->setObjectName(cssconst::OPTION_BACKGROUND);
    grid->addWidget(bg, row, firstcol, 1, ncols);
}


void mcqfunc::setResponseWidgets(
        const NameValueOptions& options,
        const QList<QPointer<BooleanWidget>>& question_widgets,
        const FieldRef* fieldref)
{
    if (!fieldref) {
        qWarning() << Q_FUNC_INFO << "Bad fieldref!";
        return;
    }
    QVariant value = fieldref->value();
    bool null = value.isNull();
    int index = options.indexFromValue(value);
    if (!null && index == -1) {
        qWarning() << Q_FUNC_INFO << "- unknown value";
        // But we must PROCEED so that the widgets are shown.
    }
    for (int vi = 0; vi < question_widgets.size(); ++vi) {
        const QPointer<BooleanWidget>& w = question_widgets.at(vi);
        if (!w) {
            qCritical() << Q_FUNC_INFO << "- defunct pointer!";
            continue;
        }
        if (vi == index) {
            w->setState(BooleanWidget::State::True);
        } else if (index == -1) {  // null but not selected
            w->setState(fieldref->mandatory()
                        ? BooleanWidget::State::NullRequired
                        : BooleanWidget::State::Null);
        } else {
            w->setState(BooleanWidget::State::False);
        }
    }
}


void mcqfunc::toggleBooleanField(FieldRef* fieldref, bool allow_unset)
{
    // Used by "clicked" receivers.
    if (!fieldref) {
        qWarning() << Q_FUNC_INFO << "bad pointer! Ignored";
        return;
    }
    QVariant value = fieldref->value();
    QVariant newvalue;
    if (value.isNull()) {  // NULL -> true
        newvalue = true;
    } else if (value.toBool()) {  // true -> false
        newvalue = false;
    } else {  // false -> either NULL or true
        newvalue = allow_unset ? QVariant() : true;
    }
    fieldref->setValue(newvalue);  // Will trigger valueChanged
}
