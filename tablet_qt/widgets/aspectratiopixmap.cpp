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

// #define DEBUG_LAYOUT
// #define DEBUG_CLICK_TIMING

#include "aspectratiopixmap.h"
#include <QDebug>
#include <QMouseEvent>
#include <QPainter>
#include <QResizeEvent>
#include "common/gui_defines.h"
#include "common/uiconst.h"
#include "lib/sizehelpers.h"


AspectRatioPixmap::AspectRatioPixmap(QPixmap* pixmap, QWidget* parent) :
    QWidget(parent)
{
    setSizePolicy(sizehelpers::maximumFixedHFWPolicy());
    if (pixmap) {
        setPixmap(*pixmap);
    }
}


void AspectRatioPixmap::setPixmap(const QPixmap& pixmap)
{
#ifdef DEBUG_LAYOUT
    qDebug() << Q_FUNC_INFO;
#endif
    m_pixmap = pixmap;
    updateGeometry();  // maximum size may have changed
}


bool AspectRatioPixmap::hasHeightForWidth() const
{
    return true;
}


int AspectRatioPixmap::heightForWidth(int width) const
{
#ifdef DEBUG_CLICK_TIMING
    qDebug() << Q_FUNC_INFO;
#endif
    // Step 1: calculate an answer that's right for our image's aspect ratio
    int h = m_pixmap.isNull()
            ? 0  // a bit arbitrary! width()? 0? 1?
            : ((qreal)m_pixmap.height() * width) / m_pixmap.width();

    // Step 2: never give an answer that is greater than our maximum height,
    // or the framework may allocate too much space for it (and then display
    // us at our correct maximum size, but with giant gaps in the layout).
    h = qMin(h, m_pixmap.height());  // height() is 0 for a null pixmap anyway; see qpixmap.cpp

#ifdef DEBUG_LAYOUT
    qDebug() << Q_FUNC_INFO << "width" << width << "-> height" << h;
#endif
    return h;
}


QSize AspectRatioPixmap::sizeHint() const
{
#ifdef DEBUG_CLICK_TIMING
    qDebug() << Q_FUNC_INFO;
#endif
    QSize hint = m_pixmap.size();
    // hint.rheight() = -1;
#ifdef DEBUG_LAYOUT
    qDebug() << Q_FUNC_INFO << "pixmap size" << m_pixmap.size()
             << "size hint" << hint;
#endif
    return hint;

    // PROBLEM with AspectRatioPixmap
    // If you have a 1920 x 1080 pixmap, then if you don't override sizeHint
    // you get something like a 640x380 default size. If you want the pixmap
    // to expand horizontally, you need to give a sizeHint.
    // However, if you give a sizeHint that's 1920 x 1080, the layout may
    // reduce the horizontal direction, but won't reduce the vertical
    // direction. Then, the *actual* image size is appropriately reduced
    // vertically by the resizeEvent() code, so you get a pixmap with
    // big top-and-bottom borders, because the displayed size is less than
    // the sizeHint.

    // Can you just return a width hint?
    // Well, you can, and that give the opposite problem - a right-hand border
    // with an image that's insufficiently sized.

    // This gets better if you enforce a size policy with
    // setHeightForWidth(true) set.

    // The problem may now be in VerticalScrollArea, having its vertical size
    // too large; not sure.
}


QSize AspectRatioPixmap::minimumSizeHint() const
{
    return QSize(0, 0);
}


void AspectRatioPixmap::mousePressEvent(QMouseEvent* event)
{
#ifdef DEBUG_CLICK_TIMING
    qDebug() << Q_FUNC_INFO;
#endif
    Q_UNUSED(event);
    emit clicked();
}


void AspectRatioPixmap::clear()
{
    // qDebug() << Q_FUNC_INFO;
    // If you set (1) a giant pixmap and then (2) a null pixmap, you can have
    // your size remain at the giant size.
    QPixmap blank(1, 1);
    blank.fill(uiconst::TRANSPARENT);
    setPixmap(blank);
}


void AspectRatioPixmap::paintEvent(QPaintEvent* event)
{
    Q_UNUSED(event);

    QPainter painter(this);
    QRect cr = contentsRect();
    if (cr.size() != m_pixmap.size()) {
        // Scale
        QSize displaysize = m_pixmap.size();
        displaysize.scale(cr.size(), Qt::KeepAspectRatio);
        QRect dest_active_rect = QRect(cr.topLeft(), displaysize);
        QRect source_all_image(QPoint(0, 0), m_pixmap.size());
#ifdef DEBUG_LAYOUT
        qDebug().nospace()
                << Q_FUNC_INFO
                << " - Asked to draw to contentsRect() of size " << cr.size()
                << "; drawing to size " << displaysize;
#endif
        painter.drawPixmap(dest_active_rect, m_pixmap, source_all_image);

        // Optimizations are possible: we don't have to draw all of it...
        // http://blog.qt.io/blog/2006/05/13/fast-transformed-pixmapimage-drawing/
        // ... but I haven't implemented those optimizations.
        // See also CanvasWidget.
    } else {
        // No need to scale
        painter.drawPixmap(cr.left(), cr.top(), m_pixmap);
    }
}