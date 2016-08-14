#pragma once
#include <QWidget>
#include "common/camcopsapp.h"
#include "menulib/menuitem.h"

class QListWidget;
class QListWidgetItem;
class QVBoxLayout;
class MenuHeader;


class MenuWindow : public QWidget
{
    Q_OBJECT

public:
    MenuWindow(CamcopsApp& app, const QString& title,
               const QString& icon = "", bool top = false);
    ~MenuWindow();
    void buildMenu();  // call after m_items is set up
    QString title() const;
    QString subtitle() const;
    QString icon() const;

signals:
    void taskSelectionChanged(Task* p_task);

public Q_SLOTS:
    void backClicked();
    void menuItemClicked(QListWidgetItem* item);
    void lockStateChanged(LockState lockstate);

protected:
    CamcopsApp& m_app;
    QString m_title;
    QString m_subtitle;
    QString m_icon;
    bool m_top;
    bool m_offer_add_task;
    QVector<MenuItem> m_items;
    QVBoxLayout* m_mainlayout;
    MenuHeader* m_p_header;
    QListWidget* m_p_listwidget;
};
