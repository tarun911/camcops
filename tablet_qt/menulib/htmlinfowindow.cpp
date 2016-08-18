#include "htmlinfowindow.h"
#include <QLabel>
#include <QTextBrowser>
#include <QVBoxLayout>
#include "lib/filefunc.h"
#include "menuheader.h"

// http://doc.qt.io/qt-5/qtextbrowser.html


HtmlInfoWindow::HtmlInfoWindow(CamcopsApp& app, const QString& title,
                               const QString& filename, const QString& icon) :
    m_app(app)
{
    setStyleSheet(textfileContents(CSS_CAMCOPS_MENU));
    setObjectName("menu_window_outer_object");

    // Layouts
    QVBoxLayout* mainlayout = new QVBoxLayout();

    QVBoxLayout* dummy_layout = new QVBoxLayout();
    setLayout(dummy_layout);
    QWidget* dummy_widget = new QWidget();
    dummy_widget->setObjectName("menu_window_background");
    dummy_layout->addWidget(dummy_widget);
    dummy_widget->setLayout(mainlayout);

    // Header
    MenuHeader* header = new MenuHeader(this, m_app, false, title, icon);
    mainlayout->addWidget(header);
    connect(header, &MenuHeader::backClicked,
            &m_app, &CamcopsApp::popScreen);

    // HTML
    if (fileExists(filename)) {
        QString html = textfileContents(filename);
        QTextBrowser* browser = new QTextBrowser();
        browser->setHtml(html);
        browser->setOpenExternalLinks(true);
        mainlayout->addWidget(browser);
        // It manages scrolling itself.
    } else {
        QLabel* label = new QLabel(tr("No such file") + ": " + filename);
        label->setObjectName("warning");
        mainlayout->addWidget(label);
        mainlayout->addStretch();
    }
}
