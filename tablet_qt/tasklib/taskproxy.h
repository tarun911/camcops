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

#pragma once
#include <QSqlDatabase>
#include "common/dbconstants.h"
#include "task.h"

class TaskFactory;


// For TaskFactory:
// ===========================================================================
// Base "descriptor" class, so we can do more things with the class as an
// entity than just instantiate one.
// ===========================================================================

class TaskProxy
{
public:
    TaskProxy(TaskFactory& factory);  // Registers itself with the factory.
    // We do want to create instances...
    virtual TaskPtr create(CamcopsApp& app,
                           const QSqlDatabase& db,
                           int load_pk = DbConst::NONEXISTENT_PK) const = 0;
    virtual TaskPtrList fetch(CamcopsApp& app,
                              const QSqlDatabase& db,
                              int patient_id = DbConst::NONEXISTENT_PK) const = 0;
protected:
    virtual TaskPtrList fetchWhere(CamcopsApp& app,
                                   const QSqlDatabase& db,
                                   const WhereConditions& where) const = 0;
};
