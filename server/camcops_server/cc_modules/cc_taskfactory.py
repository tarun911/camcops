#!/usr/bin/env python

"""
camcops_server/cc_modules/cc_taskfactory.py

===============================================================================

    Copyright (C) 2012-2018 Rudolf Cardinal (rudolf@pobox.com).

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

===============================================================================

**Functions to fetch tasks from the database.**

"""

import logging
from typing import Optional, Type, Union

from cardinal_pythonlib.logs import BraceStyleAdapter
import pyramid.httpexceptions as exc
from sqlalchemy.orm import Query

# noinspection PyUnresolvedReferences
import camcops_server.cc_modules.cc_all_models  # import side effects (ensure all models registered)  # noqa
from .cc_request import CamcopsRequest
from .cc_task import tablename_to_task_class_dict, Task
from .cc_taskindex import TaskIndexEntry

log = BraceStyleAdapter(logging.getLogger(__name__))


# =============================================================================
# Task query helpers
# =============================================================================

def task_query_restricted_to_permitted_users(
        req: CamcopsRequest,
        q: Query,
        cls: Union[Type[Task], Type[TaskIndexEntry]],
        as_dump: bool) -> Optional[Query]:
    """
    Restricts an SQLAlchemy ORM query to permitted users, for a given
    task class. THIS IS A KEY SECURITY FUNCTION.

    Args:
        req:
            the :class:`camcops_server.cc_modules.cc_request.CamcopsRequest`
        q:
            the SQLAlchemy ORM query
        cls:
            the class of the task type, or the
            :class:`camcops_server.cc_modules.cc_taskindex.TaskIndexEntry`
            class
        as_dump:
            use the "dump" permissions rather than the "view" permissions?

    Returns:
        a filtered query (or the original query, if no filtering was required)

    """
    user = req.user

    if user.superuser:
        return q  # anything goes

    # Implement group security. Simple:
    if as_dump:
        group_ids = user.ids_of_groups_user_may_dump
    else:
        group_ids = user.ids_of_groups_user_may_see

    if not group_ids:
        return None

    # noinspection PyProtectedMember
    if cls is TaskIndexEntry:
        q = q.filter(cls.group_id.in_(group_ids))
    else:  # a kind of Task
        q = q.filter(cls._group_id.in_(group_ids))

    return q


# =============================================================================
# Make a single task given its base table name and server PK
# =============================================================================

def task_factory(req: CamcopsRequest, basetable: str,
                 serverpk: int) -> Optional[Task]:
    """
    Load a task from the database and return it.
    Filters to tasks permitted to the current user.

    Args:
        req: the :class:`camcops_server.cc_modules.cc_request.CamcopsRequest`
        basetable: name of the task's base table
        serverpk: server PK of the task

    Returns:
        the task, or ``None`` if the PK doesn't exist

    Raises:
        :exc:`HTTPBadRequest` if the table doesn't exist

    """
    d = tablename_to_task_class_dict()
    try:
        cls = d[basetable]  # may raise KeyError
    except KeyError:
        raise exc.HTTPBadRequest("No such task table: {!r}".format(basetable))
    dbsession = req.dbsession
    # noinspection PyProtectedMember
    q = dbsession.query(cls).filter(cls._pk == serverpk)
    q = task_query_restricted_to_permitted_users(req, q, cls, as_dump=False)
    return q.first()
