#pragma once
#include "common/camcopsapp.h"
#include "menulib/menuwindow.h"


class SingleTaskMenu : public MenuWindow
{
    Q_OBJECT
public:
    SingleTaskMenu(const QString& tablename, CamcopsApp& app);
};
