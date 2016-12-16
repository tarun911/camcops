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

// Difficulties with the cache:
// - Particularly in MCQGrid and similar classes, the calculations go off.
// - These problems go away when the cache is disabled.
// - They are not solved by invalidating the cache on *any* event. So we
//   cannot rely on accurate cache invalidation.
// - However, just caching QLabel::heightForWidth() seems to work.
//   That's the LWWW_USE_QLABEL_CACHE setting.
//   I think that is still a fairly expensive thing so caching will help.

// #define DEBUG_LAYOUT
// #define DEBUG_CALCULATIONS
// #define DEBUG_CACHE_USE  // it's used quite a lot!

#include "labelwordwrapwide.h"
#include <QDebug>
#include <QEvent>
#include <QFontMetrics>
#include <QStyle>
#include <QStyleOptionFrame>
#ifdef DEBUG_LAYOUT
#include "common/cssconst.h"
#endif
#include "lib/uifunc.h"

// A QLabel, with setWordWrap(true), has a tendency to expand vertically and
// not use all the available horizontal space.
// ... Ah, no, that's the consequence of adjacent stretch.
// However, there is a sizing bug, fixed by this code:
// - https://bugreports.qt.io/browse/QTBUG-37673
//   ... but fixed in Qt 5.4, apparently, and we have 5.7

// See also:
// - http://stackoverflow.com/questions/13995657/why-does-qlabel-prematurely-wrap
// - http://stackoverflow.com/questions/13994902/how-do-i-get-a-qlabel-to-expand-to-full-width#13994902
// - http://doc.qt.io/qt-5/layout.html#layout-issues
// - http://stackoverflow.com/questions/31535143/how-to-prevent-qlabel-from-unnecessary-word-wrapping
// - http://www.qtcentre.org/threads/62059-QLabel-Word-Wrapping-adds-unnecessary-line-breaks
// - http://stackoverflow.com/questions/14104871/qlabel-cutting-off-text-on-resize

// When you really get stuck:
// - uncomment "#define QLAYOUT_EXTRA_DEBUG" in qlayoutengine.cpp, rebuild Qt


LabelWordWrapWide::LabelWordWrapWide(const QString& text, QWidget* parent) :
    QLabel(text, parent)
{
    commonConstructor();
}


LabelWordWrapWide::LabelWordWrapWide(QWidget* parent) :
    QLabel(parent)
{
    commonConstructor();
}


void LabelWordWrapWide::commonConstructor()
{
    setWordWrap(true);  // will also do setHeightForWidth(true);
    setSizePolicy(UiFunc::maximumFixedHFWPolicy());

    // If the horizontal policy is Preferred (with vertical Minimum), then
    // the text tries to wrap (increasing height) when other things tell it
    // that it can. So Expanding/Minimum is better.
    // However, that does sometimes mean that the widget expands horizontally
    // when you don't want it to.

    // We were using vertical QSizePolicy::Minimum, and in resizeEvent setting
    // setMinimumHeight(); presumably if we use QSizePolicy::Fixed we should
    // use setFixedHeight().

    // Expanding = GrowFlag | ShrinkFlag | ExpandFlag
    // This is better than MinimumExpanding, because it is possible to squeeze
    // a label right down and still be OK.

    // Maximum = ShrinkFlag

#ifdef DEBUG_LAYOUT
    setObjectName(CssConst::DEBUG_RED);
#endif
}


bool LabelWordWrapWide::hasHeightForWidth() const
{
    return true;
}


int LabelWordWrapWide::heightForWidth(int width) const
{
    QSize extra = extraSizeForCssOrLayout();
    int text_width = width - extra.width();
    int text_height = qlabelHeightForWidth(text_width);
    int height = text_height + extra.height();
#ifdef DEBUG_CALCULATIONS
    qDebug() << Q_FUNC_INFO << "width" << width << "-> height" << height;
#endif
    return height;
}


int LabelWordWrapWide::qlabelHeightForWidth(int width) const
{
#ifdef LWWW_USE_QLABEL_CACHE
    if (m_cached_qlabel_height_for_width.contains(width)) {
#ifdef DEBUG_CACHE_USE
        qDebug() << Q_FUNC_INFO << "using cache";
#endif
        return m_cached_qlabel_height_for_width[width];
    }
#endif
    int height = QLabel::heightForWidth(width);
#ifdef LWWW_USE_QLABEL_CACHE
    m_cached_qlabel_height_for_width[width] = height;
#endif
    return height;
}


void LabelWordWrapWide::resizeEvent(QResizeEvent* event)
{
    QLabel::resizeEvent(event);
    forceHeight();
}


void LabelWordWrapWide::forceHeight()
{
    // We were making what follows conditional on:
    //     QSizePolicy::Policy vsp = sizePolicy().verticalPolicy();
    //     if (wordWrap() && (vsp == QSizePolicy::Minimum ||
    //                       vsp == QSizePolicy::Fixed)) { ...
    // ... but I'm not sure that's necessary.

    // heightForWidth relies on minimumSize to evaulate, so reset it...
    // setMinimumHeight(0);
    // NO - SET FIXED (MAX + MIN), NOT JUST MIN:
    setMinimumHeight(0);
    setMaximumHeight(QWIDGETSIZE_MAX);
    // ... before defining minimum height:

    int w = width();  // will give the label TEXT width, I think
    int h = qMax(0, heightForWidth(w));
    // suspect heightForWidth(w) can give -1 with no text present

    // The heightForWidth() function, in qlabel.cpp,
    // works out (for a text label) a size, using sizeForWidth(),
    // then returns the height of that size.
    //
    // The complex bit is then in QLabelPrivate::sizeForWidth

    QSize size_with_css = QSize(w, h) + extraSizeForCssOrLayout();
    // int final_height = h;
    int final_height = size_with_css.height();

#ifdef DEBUG_CALCULATIONS
    qDebug() << Q_FUNC_INFO << "w" << w << "h" << h
             << "size_with_css" << size_with_css
             << "final_height" << final_height
             << "... text:" << text();
#endif

    setFixedHeight(final_height);
    updateGeometry();
}


// QLabel::sizeHint() produces a golden ratio, which is fine. If you want a
// LabelWordWrapWide to expand horizontally, set its horizontal size policy to
// include the ExpandFlag, and MAKE SURE YOU DON'T SPECIFY A HORIZONTAL
// ALIGNMENT.

// Except... we want to be able to use Maximum, not just Expanding, as a
// horizontal size policy. That means the widget will expand up to its
// sizeHint, but not further. And for that, its sizeHint shouldn't be the
// QLabel-preferred golden ratio, but the maximum possible width (with one
// line).
// (This is particularly important when using the wrapped text as a button;
// you don't want decorated buttons expanding to the width of the screen.)


QSize LabelWordWrapWide::sizeOfTextWithoutWrap() const
{
#ifdef LWWW_USE_UNWRAPPED_CACHE
    if (m_cached_unwrapped_text_size.isValid()) {
#ifdef DEBUG_CACHE_USE
        qDebug() << Q_FUNC_INFO << "using cache";
#endif
        return m_cached_unwrapped_text_size;
    }
#endif

    // Following the logic of QLabel::minimumSizeHint(), and
    // QLabelPrivate::sizeForWidth():

    // HEIGHT: easy

    // int height = heightForWidth(QWIDGETSIZE_MAX);

    // WIDTH: harder?
    // - For the internal Qt macros like Q_D, see qglobal.h:
    //   #define Q_D(Class) Class##Private * const d = d_func()
    //      ... Q_D gives the class a pointer to its private-class member
    //   #define Q_Q(Class) Class * const q = q_func()
    //      ... Q_Q gives the private class a pointer to its public-class member
    // Ah, not that much harder.
    // - http://stackoverflow.com/questions/1337523/measuring-text-width-in-qt
    // Compare:
    // - http://doc.qt.io/qt-5.7/qfontmetrics.html#width
    // - http://doc.qt.io/qt-5.7/qfontmetrics.html#boundingRect
    // - http://stackoverflow.com/questions/37671839/how-to-use-qfontmetrics-boundingrect-to-measure-size-of-multilne-message
    QFontMetrics fm = fontMetrics();
    // don't use fm.width(text()), that's something else (see Qt docs)
    QString t = text();

    QRect br = fm.boundingRect(QRect(0, 0, QWIDGETSIZE_MAX, QWIDGETSIZE_MAX),
                               0,  // definitely not Qt::TextWordWrap
                               t);
    // Right. Potentially some bugs relating to the output of boundingRect
    // being inconsistent. For example, in the same font, with text =
    // "Option C1", the size can come back as (60, 84) on one call and (60, 14)
    // [correct] the next call. I seem not to be alone:
    // - https://bugreports.qt.io/browse/QTBUG-15974
    // - ? https://bugreports.qt.io/browse/QTBUG-51024
    // - http://stackoverflow.com/questions/27336001/qfontmetrics-returns-inaccurate-results
    // QRect br = fm.boundingRect(QRect(0, 0, 0, 0),
    //                            Qt::AlignLeft | Qt::AlignTop,
    //                            t);
    // Ah, no! The boundingRect is correct; it's the height that's not.

    // int width = br.width();
    // QSize text_size(width, height);
    QSize unwrapped_text_size = br.size();

    #ifdef DEBUG_CALCULATIONS
        qDebug() << Q_FUNC_INFO << "->" << unwrapped_text_size
                 << "... text:" << t;
    #endif

#ifdef LWWW_USE_UNWRAPPED_CACHE
    m_cached_unwrapped_text_size = unwrapped_text_size;
#endif
    return unwrapped_text_size;
}


QSize LabelWordWrapWide::extraSizeForCssOrLayout() const
{
#ifdef LWWW_USE_STYLE_CACHE
    if (m_cached_extra_for_css_or_layout.isValid()) {
#ifdef DEBUG_CACHE_USE
        qDebug() << Q_FUNC_INFO << "using cache";
#endif
        return m_cached_extra_for_css_or_layout;
    }
#endif
    QSize dummy(0, 0);
    QStyleOptionFrame opt;
    initStyleOption(&opt);  // protected
    QSize extra_for_css_or_layout = UiFunc::labelExtraSizeRequired(
                this, &opt, dummy);
#ifdef LWWW_USE_STYLE_CACHE
    m_cached_extra_for_css_or_layout = extra_for_css_or_layout;
#endif
    return extra_for_css_or_layout;
}


#ifdef LWWW_USE_ANY_CACHE
bool LabelWordWrapWide::event(QEvent* e)
{
    bool result = QLabel::event(e);
    QEvent::Type type = e->type();
    switch (type) {

    // Need cache clearing:
    case QEvent::Type::ContentsRectChange:
    case QEvent::Type::DynamicPropertyChange:
    case QEvent::Type::FontChange:
    case QEvent::Type::Polish:
    case QEvent::Type::PolishRequest:
    case QEvent::Type::Resize:
    case QEvent::Type::StyleChange:
    case QEvent::Type::ScreenChangeInternal:  // undocumented? But see https://git.merproject.org/mer-core/qtbase/commit/49194275e02a9d6373767d6485bd8ebeeb0abba5
#ifdef DEBUG_CALCULATIONS
        qDebug() << Q_FUNC_INFO
                 << "event requiring cache clear... text:" << text();
#endif
        clearCache();
        break;

    default:
#ifdef DEBUG_CALCULATIONS
        qDebug() << Q_FUNC_INFO << "other event:" << type;
#endif
        // clearCache();
        break;
    }
    return result;
}
#endif


QSize LabelWordWrapWide::sizeHint() const
{
    QSize text_size = sizeOfTextWithoutWrap();
    // QSize w_smallest_word_h_unclear = QLabel::minimumSizeHint();
    // text_size.rheight() = heightForWidth(w_smallest_word_h_unclear.width());

    // Needs adjustment for stylesheet?
    // - In the case of a label inside a pushbutton, the owner (the pushbutton)
    //   should do this.
    // - Can a QLabel have its own stylesheet info? Yes:
    //   http://doc.qt.io/qt-5.7/stylesheet-reference.html

    QSize size_hint = text_size + extraSizeForCssOrLayout();
#ifdef DEBUG_CALCULATIONS
    qDebug() << Q_FUNC_INFO
             << "text_size" << text_size
             << "->" << size_hint << "... text:" << text();
#endif
    return size_hint;
}


QSize LabelWordWrapWide::minimumSizeHint() const
{
    QSize w_smallest_word_h_unclear = QLabel::minimumSizeHint();
    QSize unwrapped_size = sizeOfTextWithoutWrap();
    QSize smallest_word = QSize(w_smallest_word_h_unclear.width(),
                                unwrapped_size.height());
    QSize minimum_size_hint = smallest_word + extraSizeForCssOrLayout();
#ifdef DEBUG_CALCULATIONS
    qDebug() << Q_FUNC_INFO
             << "smallest_word" << smallest_word
             << "->" << m_cached_minimum_size_hint
             << "... text:" << text();
#endif
    return minimum_size_hint;
}


void LabelWordWrapWide::setText(const QString& text)
{
#ifdef DEBUG_CALCULATIONS
    qDebug() << Q_FUNC_INFO << text;
#endif
    QLabel::setText(text);
#ifdef LWWW_USE_ANY_CACHE
    clearCache();
#endif
    // forceHeight();
}


#ifdef LWWW_USE_ANY_CACHE
void LabelWordWrapWide::clearCache()
{
#ifdef LWWW_USE_UNWRAPPED_CACHE
    m_cached_unwrapped_text_size = QSize();
#endif
#ifdef LWWW_USE_STYLE_CACHE
    m_cached_extra_for_css_or_layout = QSize();
#endif
#ifdef LWWW_USE_QLABEL_CACHE
    m_cached_qlabel_height_for_width.clear();
#endif
}
#endif
