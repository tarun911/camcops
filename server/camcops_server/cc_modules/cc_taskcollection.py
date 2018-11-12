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

**Classes to fetch tasks from the database as efficiently as possible.**

"""

from collections import OrderedDict
from enum import Enum
import logging
from threading import Thread
from typing import Dict, List, Optional, Type, TYPE_CHECKING, Union

from cardinal_pythonlib.logs import BraceStyleAdapter
from cardinal_pythonlib.sort import MINTYPE_SINGLETON, MinType
from pendulum import DateTime as Pendulum
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session as SqlASession
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.expression import and_, or_

# noinspection PyUnresolvedReferences
import camcops_server.cc_modules.cc_all_models  # import side effects (ensure all models registered)  # noqa
from .cc_request import CamcopsRequest
from .cc_task import tablename_to_task_class_dict, Task
from .cc_taskfactory import task_query_restricted_to_permitted_users
from .cc_taskfilter import TaskFilter
from .cc_taskindex import TaskIndexEntry

if TYPE_CHECKING:
    from sqlalchemy.sql.elements import ColumnElement

log = BraceStyleAdapter(logging.getLogger(__name__))


# =============================================================================
# Debugging options
# =============================================================================

DEBUG_QUERY_TIMING = False

if DEBUG_QUERY_TIMING:
    log.warning("Debugging options enabled!")


# =============================================================================
# Sorting helpers
# =============================================================================

def task_when_created_sorter(task: Task) -> Union[Pendulum, MinType]:
    """
    Function to sort tasks by their creation date.
    """
    # For sorting of tasks
    when_created = task.when_created
    return MINTYPE_SINGLETON if when_created is None else when_created


class TaskSortMethod(Enum):
    """
    Enum representing ways to sort tasks.
    """
    NONE = 0
    CREATION_DATE_ASC = 1
    CREATION_DATE_DESC = 2


def sort_tasks_in_place(tasklist: List[Task],
                        sortmethod: TaskSortMethod) -> None:
    """
    Sort a list of tasks, in place, according to ``sortmethod``.

    Args:
        tasklist: the list of tasks
        sortmethod: a :class:`TaskSortMethod` enum
    """
    # Sort?
    if sortmethod == TaskSortMethod.CREATION_DATE_ASC:
        tasklist.sort(key=task_when_created_sorter)
    elif sortmethod == TaskSortMethod.CREATION_DATE_DESC:
        tasklist.sort(key=task_when_created_sorter, reverse=True)


# =============================================================================
# Parallel fetch helper
# =============================================================================
# - Why consider a parallel fetch?
#   Because a typical fetch might involve 27ms per query (as seen by Python;
#   less as seen by MySQL) but about 100 queries, for a not-very-large
#   database.
# - Initially UNSUCCESSFUL: even after tweaking pool_size=0 in create_engine()
#   to get round the SQLAlchemy error "QueuePool limit of size 5 overflow 10
#   reached", in the parallel code, a great many queries are launched, but then
#   something goes wrong and others are started but then block -- for ages --
#   waiting for a spare database connection, or something.
# - Fixed that: I was not explicitly closing the sessions.
# - But then a major conceptual problem: anything to be lazy-loaded (e.g.
#   patient, but also patient ID, special note, BLOB...) will give this sort of
#   error: "DetachedInstanceError: Parent instance <Phq9 at 0x7fe6cce2d278> is
#   not bound to a Session; lazy load operation of attribute 'patient' cannot
#   proceed" -- for obvious reasons. And some of those operations are only
#   required on the final paginated task set, which requires aggregation across
#   all tasks.
#
# HOWEVER, the query time per table drops from ~27ms to 4-8ms if we disable
# eager loading (lazy="joined") of patients from tasks.

class FetchThread(Thread):
    """
    Thread to fetch tasks in parallel.

    CURRENTLY UNUSED.
    """
    def __init__(self,
                 req: CamcopsRequest,
                 task_class: Type[Task],
                 factory: "TaskCollection",
                 **kwargs) -> None:
        self.req = req
        self.task_class = task_class
        self.factory = factory
        self.error = False
        name = task_class.__tablename__
        super().__init__(name=name, target=None, **kwargs)

    def run(self) -> None:
        log.debug("Thread starting")
        dbsession = self.req.get_bare_dbsession()
        # noinspection PyBroadException
        try:
            # noinspection PyProtectedMember
            q = self.factory._make_query(dbsession, self.task_class)
            if q:
                tasks = q.all()  # type: List[Task]
                # https://stackoverflow.com/questions/6319207/are-lists-thread-safe  # noqa
                # https://stackoverflow.com/questions/6953351/thread-safety-in-pythons-dictionary  # noqa
                # http://effbot.org/pyfaq/what-kinds-of-global-value-mutation-are-thread-safe.htm  # noqa
                # noinspection PyProtectedMember
                self.factory._tasks_by_class[self.task_class] = tasks
                log.debug("Thread finishing with results")
            else:
                log.debug("Thread finishing without results")
        except:
            self.error = True
            log.error("Thread error")
        dbsession.close()


# =============================================================================
# Make a set of tasks, deferring work until things are needed
# =============================================================================

class TaskCollection(object):
    """
    Represent a potential or instantiated call to fetch tasks from the
    database.

    The caller may want them in a giant list (e.g. task viewer, CTVs), or split
    by task class (e.g. trackers).
    """
    def __init__(self,
                 req: CamcopsRequest,
                 taskfilter: TaskFilter,
                 as_dump: bool = False,
                 sort_method_by_class: TaskSortMethod = TaskSortMethod.NONE,
                 sort_method_global: TaskSortMethod = TaskSortMethod.NONE,
                 current_only: bool = True,
                 via_index: bool = True) \
            -> None:
        """
        Args:
            req:
                the
                :class:`camcops_server.cc_modules.cc_request.CamcopsRequest`
            taskfilter:
                a :class:`camcops_server.cc_modules.cc_taskfilter.TaskFilter`
                object that contains any restrictions we may want to apply
            as_dump:
                use the "dump" permissions rather than the "view" permissions?
            sort_method_by_class:
                how should we sort tasks within each task class?
            sort_method_global:
                how should we sort tasks overall (across all task types)?
            current_only:
                restrict to ``_current`` tasks only?
            via_index:
                use the server's index (faster)?
        """
        if via_index and not current_only:
            log.warning("Can't use index for non-current tasks")
            via_index = False

        self._req = req
        self._filter = taskfilter
        self._as_dump = as_dump
        self._sort_method_by_class = sort_method_by_class
        self._sort_method_global = sort_method_global
        self._current_only = current_only
        self._via_index = via_index

        self._tasks_by_class = OrderedDict()  # type: Dict[Type[Task], List[Task]]  # noqa
        self._all_tasks = None  # type: List[Task]
        self._all_indexes = None  # type: Union[List[TaskIndexEntry], Query]

        # log.debug("TaskCollection(): taskfilter={!r}", self._filter)

    # =========================================================================
    # Interface to read
    # =========================================================================

    def task_classes(self) -> List[Type[Task]]:
        """
        Return a list of task classes that we want.
        """
        return self._filter.task_classes

    def tasks_for_task_class(self, task_class: Type[Task]) -> List[Task]:
        """
        Returns all appropriate task instances for a specific task type.
        """
        if self._via_index:
            self._ensure_everything_fetched_via_index()
        else:
            self._fetch_task_class(task_class)
        tasklist = self._tasks_by_class.get(task_class, [])
        return tasklist

    @property
    def all_tasks(self) -> List[Task]:
        """
        Returns a list of all appropriate task instances.
        """
        if self._all_tasks is None:
            if self._via_index:
                self._ensure_everything_fetched_via_index()
            else:
                self._fetch_all_tasks_without_index()
        return self._all_tasks

    @property
    def all_tasks_or_indexes_or_query(self) \
            -> Union[List[Task], List[TaskIndexEntry], Query]:
        """
        Returns a list of all appropriate task instances, or index entries, or
        a query returning them.

        - Returning a list of tasks is fine, but the results of this function
          may be paginated (e.g. in the main task view), so the end result may
          be that e.g. 20,000 tasks are fetched and 20 are shown.
        - More efficient is to fetch 20,000 indexes from the single index
          table, and fetch only the 20 tasks we need.
        - More efficient still is to fetch the 20 indexes we need, and then
          their task.
        """
        if not self._via_index:
            return self.all_tasks

        self._build_index_query()  # ensure self._all_indexes is set

        if self._all_tasks is not None:
            # The tasks themselves have been fetched.
            return self._all_tasks

        return self._all_indexes  # indexes or a query to fetch them

    def forget_task_class(self, task_class: Type[Task]) -> None:
        """
        Ditch results for a specific task class (for memory efficiency).
        """
        self._tasks_by_class.pop(task_class, None)
        # https://stackoverflow.com/questions/11277432/how-to-remove-a-key-from-a-python-dictionary  # noqa

    # =========================================================================
    # Internals: fetching Task objects
    # =========================================================================

    def _fetch_all_tasks_without_index(self, parallel: bool = False) -> None:
        """
        Fetch all tasks from the database.
        """

        # AVOID parallel=True; see notes above.
        if DEBUG_QUERY_TIMING:
            start_time = Pendulum.now()

        if parallel:
            # Deprecated parallel fetch
            threads = []  # type: List[FetchThread]
            for task_class in self._filter.task_classes:
                thread = FetchThread(self._req, task_class, self)
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
                if thread.error:
                    raise ValueError("Multithreaded fetch failed")

        else:
            # Fetch all tasks, classwise.
            for task_class in self._filter.task_classes:
                self._fetch_task_class(task_class)

        if DEBUG_QUERY_TIMING:
            end_time = Pendulum.now()
            # noinspection PyUnboundLocalVariable
            time_taken = end_time - start_time
            log.info("_fetch_all_tasks took {}", time_taken)

        # Build our joint task list
        self._all_tasks = []  # type: List[Task]
        for single_task_list in self._tasks_by_class.values():
            self._all_tasks += single_task_list
        sort_tasks_in_place(self._all_tasks, self._sort_method_global)

    def _fetch_task_class(self, task_class: Type[Task]) -> None:
        """
        Fetch tasks from the database for one task type.
        """
        if task_class in self._tasks_by_class:
            return  # already fetched
        q = self._serial_query(task_class)
        if q is None:
            newtasks = []  # type: List[Task]
        else:
            newtasks = q.all()  # type: List[Task]
            # Apply Python-side filters?
            newtasks = self._filter_through_python(newtasks)
            sort_tasks_in_place(newtasks, self._sort_method_by_class)
        self._tasks_by_class[task_class] = newtasks

    def _serial_query(self, task_class: Type[Task]) -> Optional[Query]:
        """
        Make and return an SQLAlchemy ORM query for a specific task class.

        Returns ``None`` if no tasks would match our criteria.
        """
        dbsession = self._req.dbsession
        return self._make_query(dbsession, task_class)

    def _make_query(self, dbsession: SqlASession,
                    task_class: Type[Task]) -> Optional[Query]:
        """
        Make and return an SQLAlchemy ORM query for a specific task class.

        Returns ``None`` if no tasks would match our criteria.
        """
        q = dbsession.query(task_class)

        # Restrict to what the web front end will supply
        # noinspection PyProtectedMember
        if self._current_only:
            # noinspection PyProtectedMember
            q = q.filter(task_class._current == True)  # nopep8

        # Restrict to what is PERMITTED
        q = task_query_restricted_to_permitted_users(
            self._req, q, task_class, as_dump=self._as_dump)

        # Restrict to what is DESIRED
        if q:
            q = self._task_query_restricted_by_filter(q, task_class)

        return q

    def _task_query_restricted_by_filter(self,
                                         q: Query,
                                         cls: Type[Task]) -> Optional[Query]:
        """
        Restricts an SQLAlchemy ORM query for a given task class to those
        tasks that our filter permits.

        THIS IS A KEY SECURITY FUNCTION, since it implements some permissions
        that relate to viewing tasks when unfiltered.

        Args:
            q: the starting SQLAlchemy ORM Query
            cls: the task class

        Returns:
            the original query, a modified query, or ``None`` if no tasks
            would pass the filter

        """
        tf = self._filter  # task filter
        user = self._req.user

        if tf.group_ids:
            permitted_group_ids = tf.group_ids.copy()
        else:
            permitted_group_ids = None  # unrestricted

        if tf.dates_inconsistent():
            return None

        if cls not in tf.task_classes:
            # We don't want this task
            return None

        if not cls.is_anonymous:
            # Not anonymous.
            if not tf.any_specific_patient_filtering():
                # No patient filtering. Permissions depend on user settings.
                if user.may_view_all_patients_when_unfiltered:
                    pass
                elif user.may_view_no_patients_when_unfiltered:
                    # (a) User not permitted to view any patients when
                    # unfiltered, and (b) not filtered to a level that would
                    # reasonably restrict to one or a small number of
                    # patients. Skip the task class.
                    return None
                else:
                    liberal_group_ids = user.group_ids_that_nonsuperuser_may_see_when_unfiltered()  # noqa
                    if not permitted_group_ids:  # was unrestricted
                        permitted_group_ids = liberal_group_ids
                    else:  # was restricted; restrict further
                        permitted_group_ids = [
                            gid for gid in permitted_group_ids
                            if gid in liberal_group_ids
                        ]
                        if not permitted_group_ids:
                            return None  # down to zero; no point continuing

            # Patient filtering
            if tf.any_patient_filtering():
                # q = q.join(Patient) # fails
                q = q.join(cls.patient)  # use explicitly configured relationship  # noqa
                q = tf.filter_query_by_patient(q, via_index=False)

        # Patient-independent filtering

        if tf.device_ids:
            # noinspection PyProtectedMember
            q = q.filter(cls._device_id.in_(tf.device_ids))

        if tf.era:
            # noinspection PyProtectedMember
            q = q.filter(cls._era == tf.era)

        if tf.adding_user_ids:
            # noinspection PyProtectedMember
            q = q.filter(cls._adding_user_id.in_(tf.adding_user_ids))

        if permitted_group_ids:
            # noinspection PyProtectedMember
            q = q.filter(cls._group_id.in_(permitted_group_ids))

        if tf.start_datetime is not None:
            q = q.filter(cls.when_created >= tf.start_datetime)
        if tf.end_datetime is not None:
            q = q.filter(cls.when_created <= tf.end_datetime)

        q = self._filter_query_for_text_contents(q, cls)

        return q

    def _filter_through_python(self, tasks: List[Task]) -> List[Task]:
        """
        Returns those tasks in the list provided that pass any Python-only
        aspects of our filter (those parts not easily calculable via SQL).

        This applies to the "direct" (and not "via index") routes only. With
        the index, we can do everything via SQL.
        """
        assert not self._via_index
        if not self._has_python_parts_to_filter():
            return tasks
        return [
            t for t in tasks
            if self._task_matches_python_parts_of_filter(t)
        ]

    def _has_python_parts_to_filter(self) -> bool:
        """
        Does the filter have aspects to it that require some Python thought,
        not just a database query?

        Only applicable to the direct (not "via index") route.
        """
        assert not self._via_index
        return self._filter.complete_only

    def _task_matches_python_parts_of_filter(self, task: Task) -> bool:
        """
        Does the task pass the Python parts of the filter?

        Only applicable to the direct (not "via index") route.
        """
        assert not self._via_index

        # "Is task complete" filter
        if self._filter.complete_only:
            if not task.is_complete():
                return False

        return True

    # =========================================================================
    # Shared between Task and TaskIndexEntry methods
    # =========================================================================

    def _filter_query_for_text_contents(
            self, q: Query, taskclass: Type[Task]) -> Optional[Query]:
        """
        Returns the query, filtered for the "text contents" filter.

        Args:
            q: the starting SQLAlchemy ORM Query
            taskclass: the task class

        Returns:
            a Query, potentially modified.
        """
        tf = self._filter  # task filter

        if not tf.text_contents:
            return q  # unmodified

        # task must contain ALL the strings in AT LEAST ONE text column
        textcols = taskclass.get_text_filter_columns()
        if not textcols:
            # Text filtering requested, but there are no text columns, so
            # by definition the filter must fail.
            return None
        clauses_over_text_phrases = []  # type: List[ColumnElement]
        # ... each e.g. "col1 LIKE '%paracetamol%' OR col2 LIKE '%paracetamol%'"  # noqa
        for textfilter in tf.text_contents:
            tf_lower = textfilter.lower()
            clauses_over_columns = []  # type: List[ColumnElement]
            # ... each e.g. "col1 LIKE '%paracetamol%'"
            for textcol in textcols:
                # Case-insensitive comparison:
                # https://groups.google.com/forum/#!topic/sqlalchemy/331XoToT4lk
                # https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/StringComparisonFilter  # noqa
                clauses_over_columns.append(
                    func.lower(textcol).contains(tf_lower, autoescape=True)
                )
            clauses_over_text_phrases.append(
                or_(*clauses_over_columns)
            )
        return q.filter(and_(*clauses_over_text_phrases))
        # ... thus, e.g.
        # "(col1 LIKE '%paracetamol%' OR col2 LIKE '%paracetamol%') AND
        #  (col1 LIKE '%overdose%' OR col2 LIKE '%overdose%')

    # =========================================================================
    # Internals: fetching TaskIndexEntry objects
    # =========================================================================

    def _ensure_everything_fetched_via_index(self) -> None:
        """
        Ensure we have all our tasks loaded, using the index.
        """
        self._build_index_query()
        self._fetch_tasks_from_indexes()

    def _build_index_query(self) -> None:
        """
        Creates a Query in :attr:`_all_indexes` that will fetch task indexes.
        If the task filtering requires the tasks to be fetched (i.e. text
        contents), fetch the actual tasks too (and filter them).
        """
        if self._all_indexes is not None:
            return
        self._all_indexes = self._make_index_query()
        if self._filter.text_contents:
            self._fetch_tasks_from_indexes()

    def _fetch_tasks_from_indexes(self) -> None:
        """
        Takes the query that has already been stored in :attr:`_all_indexes`,
        and populate the task attributes, :attr:`_all_tasks` and
        :attr:`_tasks_by_class`.
        """
        if self._all_tasks is not None:
            return
        assert self._all_indexes is not None

        d = tablename_to_task_class_dict()
        dbsession = self._req.dbsession
        self._all_tasks = []  # type: List[Task]

        # Fetch indexes
        if isinstance(self._all_indexes, Query):
            # Query built, but indexes not yet fetched.
            # Replace the query with actual indexes
            self._all_indexes = self._all_indexes.all()  # type: List[TaskIndexEntry]  # noqa
        indexes = self._all_indexes

        # Fetch tasks
        tablenames = set(index.task_table_name for index in indexes)
        for tablename in tablenames:
            # We do this by task class, so we can execute a single query per
            # task type (rather than per task).
            try:
                taskclass = d[tablename]
            except KeyError:
                log.warning("Bad tablename in index: {!r}".format(tablename))
                continue
            tasklist = self._tasks_by_class.setdefault(taskclass, [])
            task_pks = [i.task_pk for i in indexes if i.tablename == tablename]
            qtask = (
                dbsession.query(taskclass)
                .filter(taskclass._pk.in_(task_pks))
            )
            qtask = self._filter_query_for_text_contents(qtask, taskclass)
            tasks = qtask.all()  # type: List[Task]
            for task in tasks:
                tasklist.append(task)
                self._all_tasks.append(task)

        # Sort tasks
        for tasklist in self._tasks_by_class.values():
            sort_tasks_in_place(tasklist, self._sort_method_by_class)
        sort_tasks_in_place(self._all_tasks, self._sort_method_global)

    def _make_index_query(self) -> Optional[Query]:
        """
        Make and return an SQLAlchemy ORM query to retrieve indexes.

        Returns ``None`` if no tasks would match our criteria.
        """
        dbsession = self._req.dbsession
        q = dbsession.query(TaskIndexEntry)

        # Restrict to what the web front end will supply
        assert self._current_only, "_current_only must be true to use index"

        # Restrict to what is PERMITTED
        q = task_query_restricted_to_permitted_users(
            self._req, q, TaskIndexEntry, as_dump=self._as_dump)

        # Restrict to what is DESIRED
        if q:
            q = self._index_query_restricted_by_filter(q)

        return q

    def _index_query_restricted_by_filter(self, q: Query) -> Optional[Query]:
        """
        Counterpart to :func:`_task_query_restricted_by_filter`, but for
        indexes.

        THIS IS A KEY SECURITY FUNCTION, since it implements some permissions
        that relate to viewing tasks when unfiltered.

        Args:
            q: the starting SQLAlchemy ORM Query

        Returns:
            the original query, a modified query, or ``None`` if no tasks
            would pass the filter

        """
        tf = self._filter  # task filter
        user = self._req.user

        if tf.group_ids:
            permitted_group_ids = tf.group_ids.copy()
        else:
            permitted_group_ids = None  # unrestricted

        if tf.dates_inconsistent():
            return None

        if tf.skip_anonymous_tasks():
            # noinspection PyPep8
            q = q.filter(TaskIndexEntry.patient_pk != None)

        if not tf.offers_all_non_anonymous_task_types():
            permitted_task_classes = tf.task_classes
        else:
            permitted_task_classes = None

        if not tf.any_specific_patient_filtering():
            # No patient filtering. Permissions depend on user settings.
            if user.may_view_all_patients_when_unfiltered:
                pass
            elif user.may_view_no_patients_when_unfiltered:
                # (a) User not permitted to view any patients when
                # unfiltered, and (b) not filtered to a level that would
                # reasonably restrict to one or a small number of
                # patients. Restrict to anonymous tasks.
                # noinspection PyPep8
                q = q.filter(TaskIndexEntry.patient_pk == None)
            else:
                liberal_group_ids = user.group_ids_that_nonsuperuser_may_see_when_unfiltered()  # noqa
                if not permitted_group_ids:  # was unrestricted
                    permitted_group_ids = liberal_group_ids
                else:  # was restricted; restrict further
                    permitted_group_ids = [
                        gid for gid in permitted_group_ids
                        if gid in liberal_group_ids
                    ]
                    if not permitted_group_ids:
                        return None  # down to zero; no point continuing

        # Task type filtering

        if permitted_task_classes:
            permitted_task_tablenames = [
                tc.__tablename__ for tc in permitted_task_classes]
            q = q.filter(TaskIndexEntry.task_table_name.in_(
                permitted_task_tablenames
            ))

        # Patient filtering

        if tf.any_patient_filtering():
            q = q.join(TaskIndexEntry.patient)  # use relationship
            q = tf.filter_query_by_patient(q, via_index=True)

        # Patient-independent filtering

        if tf.device_ids:
            # noinspection PyProtectedMember
            q = q.filter(TaskIndexEntry.device_id.in_(tf.device_ids))

        if tf.era:
            # noinspection PyProtectedMember
            q = q.filter(TaskIndexEntry.era == tf.era)

        if tf.adding_user_ids:
            # noinspection PyProtectedMember
            q = q.filter(TaskIndexEntry.adding_user_id.in_(tf.adding_user_ids))

        if permitted_group_ids:
            # noinspection PyProtectedMember
            q = q.filter(TaskIndexEntry.group_id.in_(permitted_group_ids))

        if tf.start_datetime is not None:
            q = q.filter(TaskIndexEntry.when_created_utc >= tf.start_datetime_utc)  # noqa
        if tf.end_datetime is not None:
            q = q.filter(TaskIndexEntry.when_created_utc <= tf.end_datetime_utc)  # noqa

        # tf.text_contents has to be managed on the Python side with indexes

        # But is_complete doesn't:
        if tf.complete_only:
            # noinspection PyPep8
            q = q.filter(TaskIndexEntry.task_is_complete == True)

        # When we use indexes, we embed the global sort criteria in the query.
        if self._sort_method_global == TaskSortMethod.CREATION_DATE_ASC:
            q = q.order_by(TaskIndexEntry.when_created_utc.asc())
        elif self._sort_method_global == TaskSortMethod.CREATION_DATE_DESC:
            q = q.order_by(TaskIndexEntry.when_created_utc.desc())

        return q