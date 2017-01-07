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

#include "pagepickeritem.h"
#include "common/uiconstants.h"


PagePickerItem::PagePickerItem(const QString& text, int page_number,
                               PagePickerItemType type):
    m_text(text),
    m_page_number(page_number),
    m_type(type)
{
}


QString PagePickerItem::text() const
{
    return m_text;
}


int PagePickerItem::pageNumber() const
{
    return m_page_number;
}


PagePickerItem::PagePickerItemType PagePickerItem::type() const
{
    return m_type;
}


bool PagePickerItem::selectable() const
{
    return m_type == PagePickerItemType::CompleteSelectable ||
           m_type == PagePickerItemType::IncompleteSelectable;
}


QString PagePickerItem::iconFilename() const
{
    switch (m_type) {
    case PagePickerItemType::CompleteSelectable:
        return uiconst::CBS_NEXT;
    case PagePickerItemType::IncompleteSelectable:
        return uiconst::ICON_WARNING;
    case PagePickerItemType::BlockedByPrevious:
    default:  // to prevent compiler warning
        return uiconst::ICON_STOP;
    }
}
