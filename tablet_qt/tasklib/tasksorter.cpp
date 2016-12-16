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

#include "tasklib/task.h"
#include "tasksorter.h"


TaskSorter::TaskSorter()
{
    // could use this to implement specific sorting methods; see
    // https://forum.qt.io/topic/4877/sorting-a-qlist-with-a-comparator/4
}


bool TaskSorter::operator()(const TaskPtr& left, const TaskPtr& right) const
{
    // Implements: LEFT < RIGHT ?
    // Sort by date/time (descending), then taskname (ascending)
    QDateTime l_when = left->valueDateTime(
        DbConst::CREATION_TIMESTAMP_FIELDNAME);
    QDateTime r_when = right->valueDateTime(
        DbConst::CREATION_TIMESTAMP_FIELDNAME);
    if (l_when != r_when) {
        return l_when > r_when;  // descending
    } else {
        QString l_name = left->shortname();
        QString r_name = right->shortname();
        return l_name < r_name; // ascending
    }
}
