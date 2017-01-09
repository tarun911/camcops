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

// #define DEBUG_HFW_RESIZE_EVENT

#include "sizehelpers.h"
#include <QLayout>
#include <QLabel>
#include <QPushButton>
#include <QSizePolicy>
#include <QStyle>
#include <QStyleOptionButton>
#include <QStyleOptionFrame>
#include <QWidget>

#ifdef DEBUG_HFW_RESIZE_EVENT
#include <QDebug>
#endif


QSizePolicy sizehelpers::expandingFixedHFWPolicy()
{
    QSizePolicy sp(QSizePolicy::Expanding, QSizePolicy::Fixed);
    sp.setHeightForWidth(true);
    return sp;
}


QSizePolicy sizehelpers::expandingPreferredHFWPolicy()
{
    QSizePolicy sp(QSizePolicy::Expanding, QSizePolicy::Preferred);
    sp.setHeightForWidth(true);
    return sp;
}


QSizePolicy sizehelpers::maximumFixedHFWPolicy()
{
    QSizePolicy sp(QSizePolicy::Maximum, QSizePolicy::Fixed);
    sp.setHeightForWidth(true);
    return sp;
}


QSizePolicy sizehelpers::expandingMaximumHFWPolicy()
{
    QSizePolicy sp(QSizePolicy::Expanding, QSizePolicy::Maximum);
    sp.setHeightForWidth(true);
    return sp;
}


QSizePolicy sizehelpers::expandingExpandingHFWPolicy()
{
    QSizePolicy sp(QSizePolicy::Expanding, QSizePolicy::Expanding);
    sp.setHeightForWidth(true);
    return sp;
}


QSizePolicy sizehelpers::maximumMaximumHFWPolicy()
{
    QSizePolicy sp(QSizePolicy::Maximum, QSizePolicy::Maximum);
    sp.setHeightForWidth(true);
    return sp;
}


QSizePolicy sizehelpers::preferredPreferredHFWPolicy()
{
    QSizePolicy sp(QSizePolicy::Preferred, QSizePolicy::Preferred);
    sp.setHeightForWidth(true);
    return sp;
}


void sizehelpers::resizeEventForHFWParentWidget(QWidget* widget)
{
    // Call from your resizeEvent() processor passing "this" as the parameter
    // if you are a widget that contains (via a layout) height-for-width
    // widgets.
    Q_ASSERT(widget);
    QLayout* lay = widget->layout();
    if (!lay || !lay->hasHeightForWidth()) {
        return;
    }
    int w = widget->width();
    int h = lay->heightForWidth(w);
#ifdef DEBUG_HFW_RESIZE_EVENT
    qDebug() << Q_FUNC_INFO << "w" << w << "-> h" << h;
#endif
    widget->setFixedHeight(h);
    widget->updateGeometry();
}


QSize sizehelpers::contentsMarginsAsSize(const QWidget* widget)
{
    Q_ASSERT(widget);
    QMargins margins = widget->contentsMargins();
    return QSize(margins.left() + margins.right(),
                 margins.top() + margins.bottom());
}


QSize sizehelpers::contentsMarginsAsSize(const QLayout* layout)
{
    Q_ASSERT(layout);
    QMargins margins = layout->contentsMargins();
    return QSize(margins.left() + margins.right(),
                 margins.top() + margins.bottom());
}


QSize sizehelpers::spacingAsSize(const QLayout* layout)
{
    Q_ASSERT(layout);
    int spacing = layout->spacing();
    return QSize(2 * spacing, 2 * spacing);
}


QSize sizehelpers::widgetExtraSizeForCssOrLayout(
        const QWidget* widget,
        const QStyleOption* opt,
        const QSize& child_size,
        bool add_style_element,
        QStyle::ContentsType contents_type)
{
    // See QPushButton::sizeHint()
    Q_ASSERT(widget);
    Q_ASSERT(opt);

    QSize stylesheet_extra_size(0, 0);
    if (add_style_element) {
        QStyle* style = widget->style();
        if (style) {
            QSize temp = style->sizeFromContents(contents_type, opt,
                                                 child_size, widget);
            stylesheet_extra_size = temp - child_size;
        }
    }

    QSize extra_for_layout_margins(0, 0);
    QLayout* layout = widget->layout();
    if (layout) {
        extra_for_layout_margins = contentsMarginsAsSize(layout);
    }
    // I think that if you have a style, that sets the layout margins
    // and so adding the layout margins *as well* makes the widget too big
    // (by double-counting). However, if there's no style, then this is
    // important.
    // Hmpf. No. Doing one or the other improves some things and breaks others!
    // Specifically, QuBoolean in text mode got better (no longer too big)
    // and QuBoolean in image mode with associated text got worse (too small).
    // Both forms of text are ClickableLabelWordWrapWide.

    // size_hint += stylesheet_extra_size + extra_for_layout_margins;

    // Take the maximum?
    QSize total_extra = stylesheet_extra_size
            .expandedTo(extra_for_layout_margins)
            .expandedTo(QSize(0, 0));  // just to ensure it's never negative

#ifdef DEBUG_WIDGET_MARGINS
    qDebug().nospace() << Q_FUNC_INFO
             << "widget " << LayoutDumper::getWidgetDescriptor(widget)
             << "; child_size " << child_size
             << "; stylesheet_extra_size " << stylesheet_extra_size
             << "; extra_for_layout_margins " << extra_for_layout_margins
             << " => total_extra " << total_extra;
#endif
    return total_extra;
}


QSize sizehelpers::pushButtonExtraSizeRequired(const QPushButton* button,
                                               const QStyleOptionButton* opt,
                                               const QSize& child_size)
{
    return widgetExtraSizeForCssOrLayout(button, opt, child_size,
                                         true, QStyle::CT_PushButton);
}


QSize sizehelpers::frameExtraSizeRequired(const QFrame* frame,
                                          const QStyleOptionFrame* opt,
                                          const QSize& child_size)
{
    return widgetExtraSizeForCssOrLayout(frame, opt, child_size,
                                         false, QStyle::CT_PushButton);
    // Is QStyle::CT_PushButton right?
}


QSize sizehelpers::labelExtraSizeRequired(const QLabel* label,
                                          const QStyleOptionFrame* opt,
                                          const QSize& child_size)
{
    return widgetExtraSizeForCssOrLayout(label, opt, child_size,
                                         true, QStyle::CT_PushButton);
    // Is QStyle::CT_PushButton right?
}
