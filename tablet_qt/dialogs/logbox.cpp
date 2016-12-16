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

#include "logbox.h"
#include <QApplication>
#include <QDebug>
#include <QHBoxLayout>
#include <QPlainTextEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include "lib/uifunc.h"

const int MIN_WIDTH = 600;
const int MIN_HEIGHT = 600;


LogBox::LogBox(QWidget* parent, const QString& title, bool offer_cancel,
               bool offer_ok_at_end, int maximum_block_count) :
    QDialog(parent),
    m_editor(nullptr),
    m_ok(nullptr),
    m_cancel(nullptr),
    m_ack_fail(nullptr)
{
    // qDebug() << Q_FUNC_INFO;
    setWindowTitle(title);
    setMinimumWidth(MIN_WIDTH);
    setMinimumHeight(MIN_HEIGHT);

    QVBoxLayout* mainlayout = new QVBoxLayout();
    setLayout(mainlayout);

    m_editor = new QPlainTextEdit();
    // QPlainTextEdit better than QTextEdit because it supports
    // maximumBlockCount while still allowing HTML (via appendHtml,
    // not insertHtml).
    m_editor->setReadOnly(true);
    m_editor->setLineWrapMode(QPlainTextEdit::NoWrap);
    m_editor->setMaximumBlockCount(maximum_block_count);
    mainlayout->addWidget(m_editor);

    QHBoxLayout* buttonlayout = new QHBoxLayout();
    QPushButton* copybutton = new QPushButton(tr("Copy"));
    buttonlayout->addWidget(copybutton);
    connect(copybutton, &QPushButton::clicked, this, &LogBox::copyClicked);

    if (offer_cancel) {
        m_cancel = new QPushButton(tr("Cancel"));
        buttonlayout->addWidget(m_cancel);
        connect(m_cancel, &QPushButton::clicked, this, &LogBox::reject);
    }

    buttonlayout->addStretch();
    // Don't have cancel button on the right (user might hit it thinking
    // it's the OK button, based on shared location).

    if (offer_ok_at_end) {
        m_ok = new QPushButton(tr("OK"));
        buttonlayout->addWidget(m_ok);
        connect(m_ok, &QPushButton::clicked, this, &LogBox::okClicked);
        m_ok->hide();
    }

    m_ack_fail = new QPushButton(tr("Acknowledge failure"));
    buttonlayout->addWidget(m_ack_fail);
    connect(m_ack_fail, &QPushButton::clicked, this, &LogBox::okClicked);
    m_ack_fail->hide();

    mainlayout->addLayout(buttonlayout);
}


LogBox::~LogBox()
{
    if (m_wait_cursor_on) {
        QApplication::restoreOverrideCursor();
    }
}


void LogBox::open()
{
    // qDebug() << Q_FUNC_INFO;
    QApplication::setOverrideCursor(Qt::WaitCursor);
    m_wait_cursor_on = true;
    QDialog::open();
}


void LogBox::statusMessage(const QString& msg, bool as_html)
{
    if (!m_editor) {
        return;
    }
    if (as_html) {
        m_editor->appendHtml(msg);
    } else {
        m_editor->appendPlainText(msg);
    }
}


void LogBox::finish(bool success)
{
    // qDebug() << Q_FUNC_INFO;
    // If we're waiting for the user to press OK (so they can look at the log,
    // enable the OK button and await the accepted() signal via that button).
    // Otherwise, accept() now. Either way, restore the cursor.
    QApplication::restoreOverrideCursor();
    m_wait_cursor_on = false;
    if (m_cancel) {
        m_cancel->hide();
    }
    if (success && m_ok) {
        m_ok->show();  // and await the accepted() signal via the button
    } else if (!success) {
        m_ack_fail->show();  // and await the accepted() signal via the button
    } else {
        // success, but caller didn't want an OK button
        accept();  // will emit accepted()
    }
}


void LogBox::okClicked()
{
    // qDebug() << Q_FUNC_INFO;
    accept();
    hide();  // hide explicitly, as we may be called using open() not exec()
}


void LogBox::copyClicked()
{
    m_editor->selectAll();
    m_editor->copy();
    m_editor->moveCursor(QTextCursor::End);
    UiFunc::scrollToEnd(m_editor.data());
}
