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
class Field;


class FieldCreationPlan {
public:
    QString name;
    const Field* intended_field = nullptr;
    bool exists_in_db = false;
    QString existing_type;
    bool existing_not_null = false;
    bool add = false;
    bool drop = false;
    bool change = false;
public:
    friend QDebug operator<<(QDebug debug, const FieldCreationPlan& plan);
};
