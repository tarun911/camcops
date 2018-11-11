#!/usr/bin/env python

"""
camcops_server/cc_modules/cc_taskindex.py

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

**Server-side task index.**

Note in particular that if you, as a developer, change the ``is_complete()``
criteria for a task, you should cause the server index to be rebuilt (because
it caches ``is_complete()`` information).

"""

import logging
from typing import List, Optional, Type, TYPE_CHECKING

from cardinal_pythonlib.logs import BraceStyleAdapter
from cardinal_pythonlib.reprfunc import simple_repr
from pendulum import DateTime as Pendulum
import pyramid.httpexceptions as exc
from sqlalchemy.orm import relationship, Session as SqlASession
from sqlalchemy.sql.expression import and_, join, select
from sqlalchemy.sql.schema import Column, ForeignKey, Table
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, DateTime, Integer

from .cc_client_api_core import fail_user_error
from .cc_constants import ERA_NOW
from .cc_idnumdef import IdNumDefinition
from .cc_patient import Patient
from .cc_patientidnum import PatientIdNum
from .cc_sqla_coltypes import (
    EraColType,
    isotzdatetime_to_utcdatetime,
    PendulumDateTimeAsIsoTextColType,
    TableNameColType,
)
from .cc_sqlalchemy import Base
from .cc_task import tablename_to_task_class_dict, Task
from .cc_user import User

if TYPE_CHECKING:
    from .cc_request import CamcopsRequest


log = BraceStyleAdapter(logging.getLogger(__name__))


# =============================================================================
# Helper functions
# =============================================================================

def task_factory_unfiltered(dbsession: SqlASession,
                            basetable: str,
                            serverpk: int) -> Optional[Task]:
    """
    Load a task from the database and return it.
    No permission filtering is performed. (Used by
    :class:`camcops_server.cc_modules.cc_taskindex.TaskIndexEntry`.)

    Args:
        dbsession: SQLAlchemy database session
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
    # noinspection PyProtectedMember
    q = dbsession.query(cls).filter(cls._pk == serverpk)
    return q.first()


# =============================================================================
# IdNumIndexEntry
# =============================================================================

class PatientIdNumIndexEntry(Base):
    """
    Represents a server index entry for a
    :class:`camcops_server.cc_modules.cc_patientidnum.PatientIdNum`.

    - Only current ID numbers are indexed.
    """
    __tablename__ = "_idnum_index"

    idnum_pk = Column(
        "idnum_pk", Integer,
        primary_key=True, index=True,
        comment="Server primary key of the PatientIdNum "
                "(and of the PatientIdNumIndexEntry)"
    )
    patient_pk = Column(
        "patient_pk", Integer, ForeignKey(Patient._pk),
        index=True,
        comment="Server primary key of the Patient"
    )
    which_idnum = Column(
        "which_idnum", Integer, ForeignKey(IdNumDefinition.which_idnum),
        nullable=False,
        index=True,
        comment="Which of the server's ID numbers is this?"
    )
    idnum_value = Column(
        "idnum_value", BigInteger,
        comment="The value of the ID number"
    )

    # Relationships:
    patient = relationship(Patient)

    def __repr__(self) -> str:
        return simple_repr(self, ["idnum_pk", "patient_pk",
                                  "which_idnum", "idnum_value"])

    # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------

    @classmethod
    def make_from_idnum(cls, idnum: PatientIdNum) -> "PatientIdNumIndexEntry":
        """
        Returns an ID index entry for the specified
        :class:`camcops_server.cc_modules.cc_patientidnum.PatientIdNum`. The
        returned index requires inserting into a database session.
        """
        assert idnum._current, "Only index current PatientIdNum objects"
        index = cls()
        index.idnum_pk = idnum.get_pk()
        index.patient_pk = idnum.get_patient_server_pk()
        index.which_idnum = idnum.which_idnum
        index.idnum_value = idnum.idnum_value
        return index

    @classmethod
    def index_idnum(cls, idnum: PatientIdNum, session: SqlASession) -> None:
        """
        Indexes an ID number and inserts the index into the database.

        Args:
            idnum: a
                :class:`camcops_server.cc_modules.cc_patientidnum.PatientIdNum`
            session: an SQLAlchemy Session
        """
        index = cls.make_from_idnum(idnum)
        session.add(index)

    # -------------------------------------------------------------------------
    # Regenerate index
    # -------------------------------------------------------------------------

    @classmethod
    def rebuild_index(cls, session: SqlASession) -> None:
        """
        Rebuilds the index entirely. Uses SQLAlchemy Core (not ORM) for speed.

        Args:
            session: an SQLAlchemy Session
        """
        log.info("Rebuilding patient ID number index")
        # noinspection PyUnresolvedReferences
        indextable = PatientIdNumIndexEntry.__table__  # type: Table
        indexcols = indextable.columns
        # noinspection PyUnresolvedReferences
        idnumtable = PatientIdNum.__table__  # type: Table
        idnumcols = idnumtable.columns
        # noinspection PyUnresolvedReferences
        patienttable = Patient.__table__  # type: Table
        patientcols = patienttable.columns

        # Delete all entries
        session.execute(
            indextable.delete()
        )

        # Create new ones
        # noinspection PyProtectedMember,PyPep8
        session.execute(
            indextable.insert().from_select(
                # Target:
                [indexcols.idnum_pk,
                 indexcols.patient_pk,
                 indexcols.which_idnum,
                 indexcols.idnum_value],
                # Source:
                (
                    select([idnumcols._pk,
                            patientcols._pk,
                            idnumcols.which_idnum,
                            idnumcols.idnum_value])
                    .select_from(
                        join(
                            idnumtable,
                            patienttable,
                            and_(
                                idnumcols._device_id == patientcols._device_id,
                                idnumcols._era == patientcols._era,
                                idnumcols.patient_id == patientcols.id,
                            )
                        )
                    )
                    .where(idnumcols._current == True)
                    .where(patientcols._current == True)
                )
            )
        )

    # -------------------------------------------------------------------------
    # Update index at the point of upload from a device
    # -------------------------------------------------------------------------

    @classmethod
    def update_index_for_upload(cls, session: SqlASession,
                                device_id: int) -> None:
        """
        Updates the index for a device's upload.

        - Deletes index entries for records that are on the way out.
        - Creates index entries for records that are on the way in.

        Args:
            session: an SQLAlchemy Session
            device_id:
                ID of the :class:`camcops_server.cc_modules.cc_device.Device`
        """
        # noinspection PyUnresolvedReferences
        indextable = PatientIdNumIndexEntry.__table__  # type: Table
        indexcols = indextable.columns
        # noinspection PyUnresolvedReferences
        idnumtable = PatientIdNum.__table__  # type: Table
        idnumcols = idnumtable.columns
        # noinspection PyUnresolvedReferences
        patienttable = Patient.__table__  # type: Table
        patientcols = patienttable.columns

        # Delete the old
        # noinspection PyProtectedMember
        session.execute(
            indextable.delete()
            # Extra bits:
            .where(
                indextable.c.idnum_pk.in_(
                    idnumtable.select([idnumcols._pk])
                    .where(idnumcols._device_id == device_id)
                    .where(idnumcols._removal_pending == 1)
                )
            )
        )

        # Create the new
        # noinspection PyPep8,PyProtectedMember
        session.execute(
            indextable.insert().from_select(
                # Target:
                [indexcols.idnum_pk,
                 indexcols.patient_pk,
                 indexcols.which_idnum,
                 indexcols.idnum_value],
                # Source:
                (
                    select([idnumcols._pk,
                            patientcols._pk,
                            idnumcols.which_idnum,
                            idnumcols.idnum_value])
                    .select_from(
                        join(
                            idnumtable,
                            patienttable,
                            and_(
                                idnumcols._device_id == patientcols._device_id,
                                idnumcols._era == patientcols._era,
                                idnumcols.patient_id == patientcols.id,
                            )
                        )
                    )
                    .where(idnumcols._current == True)
                    .where(patientcols._current == True)
                    # Extra bits:
                    .where(idnumcols._device_id == device_id)
                    .where(idnumcols._addition_pending == 1)
                )
            )
        )


# =============================================================================
# TaskIndexEntry
# =============================================================================

class TaskIndexEntry(Base):
    """
    Represents a server index entry for a
    :class:`camcops_server.cc_modules.cc_task.Task`.

    - Only current tasks are indexed. This simplifies direct linking to patient
      PKs.
    """
    __tablename__ = "_task_index"

    index_entry_pk = Column(
        "index_entry_pk", Integer,
        primary_key=True, autoincrement=True,
        comment="Arbitrary primary key of this index entry"
    )

    # The next two fields link to our task:
    task_table_name = Column(
        "task_table_name", TableNameColType,
        index=True,
        comment="Table name of the task's base table"
    )
    task_pk = Column(
        "task_pk", Integer,
        index=True,
        comment="Server primary key of the task"
    )
    # We can probably even represent this with an SQLAlchemy ORM relationship.
    # This is polymorphic loading (we'll return objects of different types)
    # based on concrete table inheritance (each type of object -- each task --
    # has its own standalone table).
    # However, there are warnings about the inefficiency of this; see
    # https://docs.sqlalchemy.org/en/latest/orm/inheritance.html#concrete-table-inheritance
    # and we are trying to be efficient. So let's do via task() below.

    # This links to the task's patient, if there is one:
    patient_pk = Column(
        "patient_pk", Integer, ForeignKey(Patient._pk),
        index=True,
        comment="Server primary key of the task"
    )

    # These fields allow us to filter tasks efficiently:
    device_id = Column(
        "device_id", Integer, ForeignKey("_security_devices.id"),
        nullable=False,
        index=True,
        comment="ID of the source tablet device"
    )
    era = Column(
        "era", EraColType, nullable=False,
        index=True,
        comment="Era (_era) field of the source record",
    )
    when_created_utc = Column(
        "when_created_utc", DateTime, nullable=False,
        index=True,
        comment="Date/time this task instance was created (UTC)"
    )
    when_created_iso = Column(
        "when_created_iso", PendulumDateTimeAsIsoTextColType, nullable=False,
        index=True,
        comment="Date/time this task instance was created (ISO 8601)"
    )  # Pendulum on the Python side
    adding_user_id = Column(
        "adding_user_id", Integer, ForeignKey("_security_users.id"),
        comment="ID of user that added this task",
    )
    group_id = Column(
        "group_id", Integer, ForeignKey("_security_groups.id"),
        nullable=False, index=True,
        comment="ID of group to which this task belongs"
    )
    task_is_complete = Column(
        "task_is_complete", Boolean, nullable=False,
        comment="Is the task complete (as judged by the server when the index "
                "entry was created)?"
    )

    # Relationships:
    patient = relationship(Patient)
    _adding_user = relationship(User)

    def __repr__(self) -> str:
        return simple_repr(self, [
            "index_entry_pk", "task_table_name", "task_pk", "patient_pk",
            "device_id", "era", "when_created_utc", "when_created_iso",
            "adding_user_id", "group_id", "task_is_complete",
        ])

    # -------------------------------------------------------------------------
    # Fetch the task
    # -------------------------------------------------------------------------

    @property
    def task(self) -> Optional[Task]:
        """
        Returns:
            the associated :class:`camcops_server.cc_modules.cc_task.Task`, or
            ``None`` if none exists.

        Raises:
            :exc:`HTTPBadRequest` if the table doesn't exist
        """
        dbsession = SqlASession.object_session(self)
        assert dbsession, (
            "TaskIndexEntry.task called on a TaskIndexEntry "
            "that's not yet in a database session")
        return task_factory_unfiltered(
            dbsession, self.task_table_name, self.task_pk)

    # -------------------------------------------------------------------------
    # Other properties mirroring those of Task, for duck typing
    # -------------------------------------------------------------------------

    @property
    def is_anonymous(self) -> bool:
        """
        Is the task anonymous?
        """
        return self.patient_pk is None

    def is_complete(self) -> bool:
        """
        Is the task complete?
        """
        return self.task_is_complete

    @property
    def _current(self) -> bool:
        """
        All task index entries represent complete tasks, so this always returns
        ``True``.
        """
        return True

    @property
    def _pk(self) -> int:
        """
        Return's the task's server PK.
        """
        return self.task_pk

    @property
    def tablename(self) -> str:
        """
        Returns the base table name of the task.
        """
        return self.task_table_name

    @property
    def shortname(self) -> str:
        """
        Returns the task's shortname.
        """
        d = tablename_to_task_class_dict()
        taskclass = d[self.task_table_name]
        return taskclass.shortname

    def is_live_on_tablet(self) -> bool:
        """
        Is the task live on the source device (e.g. tablet)?
        """
        return self.era == ERA_NOW

    @property
    def when_created(self) -> Pendulum:
        """
        Returns the creation date/time as a Pendulum DateTime object.
        """
        return self.when_created_iso

    def any_patient_idnums_invalid(self, req: "CamcopsRequest") -> bool:
        """
        Do we have a patient who has any invalid ID numbers?

        Args:
            req: a :class:`camcops_server.cc_modules.cc_request.CamcopsRequest`
        """
        idnums = self.get_patient_idnum_objects()
        for idnum in idnums:
            if not idnum.is_fully_valid(req):
                return True
        return False

    def get_patient_idnum_objects(self) -> List[PatientIdNum]:
        """
        Gets all :class:`PatientIdNum` objects for the patient.
        """
        return self.patient.get_idnum_objects() if self.patient else []

    # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------

    @classmethod
    def make_from_task(cls, task: Task,
                       ignore_current: bool = False) -> "TaskIndexEntry":
        """
        Returns a task index entry for the specified
        :class:`camcops_server.cc_modules.cc_task.Task`. The
        returned index requires inserting into a database session.

        Args:
            task: a :class:`camcops_server.cc_modules.cc_task.Task`
            ignore_current: ignore the _current flag; used by the upload API
        """
        if not ignore_current:
            assert task._current, "Only index current Task objects"
        index = cls()

        index.task_table_name = task.tablename
        index.task_pk = task.get_pk()

        patient = task.patient
        index.patient_pk = patient.get_pk() if patient else None

        index.device_id = task.get_device_id()
        index.era = task.get_era()
        index.when_created_utc = task.get_creation_datetime_utc()
        index.when_created_iso = task.when_created
        index.adding_user_id = task.get_adding_user_id()
        index.group_id = task.get_group_id()
        index.task_is_complete = task.is_complete()

        return index

    @classmethod
    def index_task(cls, task: Task, session: SqlASession,
                   ignore_current: bool = False) -> None:
        """
        Indexes a task and inserts the index into the database.

        Args:
            task: a :class:`camcops_server.cc_modules.cc_task.Task`
            session: an SQLAlchemy Session
            ignore_current: ignore the _current flag; used by the upload API
        """
        index = cls.make_from_task(task, ignore_current=ignore_current)
        session.add(index)

    # -------------------------------------------------------------------------
    # Regenerate index
    # -------------------------------------------------------------------------

    @classmethod
    def rebuild_index_for_task_type(cls, session: SqlASession,
                                    taskclass: Type[Task],
                                    delete_first: bool = True) -> None:
        """
        Rebuilds the index for a particular task type.

        Args:
            session: an SQLAlchemy Session
            taskclass: a subclass of
                :class:`camcops_server.cc_modules.cc_task.Task`
            delete_first: delete old index entries first? Should always be True
                unless called as part of a master rebuild that deletes
                everything first.
        """
        # noinspection PyUnresolvedReferences
        idxtable = cls.__table__  # type: Table
        idxcols = idxtable.columns
        tasktablename = taskclass.tablename
        log.info("Rebuilding task index for {}".format(tasktablename))
        # Delete all entries for this task
        if delete_first:
            session.execute(
                idxtable.delete()
                .where(idxcols.table_name == tasktablename)
            )
        # Create new entries
        # noinspection PyPep8,PyUnresolvedReferences
        q = (
            session.query(taskclass)
            .filter(taskclass._current == True)
            .order_by(isotzdatetime_to_utcdatetime(taskclass.when_created))
        )
        for task in q:
            cls.index_task(task, session)

    @classmethod
    def rebuild_entire_index(cls, session: SqlASession) -> None:
        """
        Rebuilds the entire index.

        Args:
            session: an SQLAlchemy Session
        """
        log.info("Rebuilding entire task index")
        # noinspection PyUnresolvedReferences
        idxtable = cls.__table__  # type: Table
        # Delete all entries
        session.execute(
            idxtable.delete()
        )
        # Now rebuild:
        for taskclass in Task.all_subclasses_by_tablename():
            cls.rebuild_index_for_task_type(session, taskclass,
                                            delete_first=False)

    # -------------------------------------------------------------------------
    # Update index at the point of upload from a device
    # -------------------------------------------------------------------------

    @classmethod
    def update_index_for_upload(cls, session: SqlASession,
                                device_id: int,
                                tasktablename: str) -> None:
        """
        Updates the index for a device's upload.

        - Deletes index entries for records that are on the way out.
        - Creates index entries for records that are on the way in.

        Args:
            session: an SQLAlchemy Session
            device_id:
                ID of the :class:`camcops_server.cc_modules.cc_device.Device`
            tasktablename: name of the task's base table
        """
        d = tablename_to_task_class_dict()
        try:
            taskclass = d[tasktablename]  # may raise KeyError
        except KeyError:
            fail_user_error("Bug: no such task table: {!r}".format(
                tasktablename))

        # noinspection PyUnresolvedReferences
        idxtable = cls.__table__  # type: Table
        idxcols = idxtable.columns
        # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
        tasktable = taskclass.__table__  # type: Table
        taskcols = tasktable.columns

        # Delete the old:
        # noinspection PyProtectedMember
        session.execute(
            idxtable.delete()
            .where(idxcols.table_name == tasktablename)
            # Extra bits:
            .where(idxcols.device_id == device_id)
            .where(
                idxcols.task_pk.in_(
                    tasktable.select([taskcols._pk])
                    .where(taskcols._device_id == device_id)
                    .where(taskcols._removal_pending == 1)
                )
            )
        )

        # Create the new:
        q = (
            session.query(taskclass)
            .filter(taskclass._device_id == device_id)
            .filter(taskclass._addition_pending == 1)
            .order_by(isotzdatetime_to_utcdatetime(taskclass.when_created))
        )
        for task in q:
            cls.index_task(task, session, ignore_current=True)


def reindex_everything(session: SqlASession) -> None:
    """
    Deletes from and rebuilds all server index tables.

    Args:
        session: an SQLAlchemy Session
    """
    PatientIdNumIndexEntry.rebuild_index(session)
    TaskIndexEntry.rebuild_entire_index(session)
