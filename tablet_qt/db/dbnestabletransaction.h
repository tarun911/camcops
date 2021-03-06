/*
    Copyright (C) 2012-2019 Rudolf Cardinal (rudolf@pobox.com).

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

#pragma once
#include <QString>
class DatabaseManager;


class DbNestableTransaction
{
    // https://www.sqlite.org/lang_savepoint.html
public:
    DbNestableTransaction(DatabaseManager& db);
    ~DbNestableTransaction();
    void fail();
    void succeed();
protected:
    DatabaseManager& m_db;
    bool m_fail;
    QString m_name;

    static int s_count;  // used for savepoint name; continuously increments
    static int s_level;  // current depth within savepoint stack
};
