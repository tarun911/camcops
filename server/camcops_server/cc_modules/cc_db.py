#!/usr/bin/env python

"""
camcops_server/cc_modules/cc_db.py

===============================================================================

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

===============================================================================

**Common database code, e.g. mixins for tables that are uploaded from the
client.**

"""

from collections import OrderedDict
import logging
from typing import (Any, Dict, Generator, List, Optional, Set, Tuple, Type,
                    TYPE_CHECKING, TypeVar, Union)

from cardinal_pythonlib.logs import BraceStyleAdapter
from cardinal_pythonlib.sqlalchemy.orm_inspect import gen_columns
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm import Session as SqlASession
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Integer

from camcops_server.cc_modules.cc_constants import ERA_NOW
from camcops_server.cc_modules.cc_sqla_coltypes import (
    CamcopsColumn,
    EraColType,
    gen_ancillary_relationships,
    gen_camcops_blob_columns,
    PendulumDateTimeAsIsoTextColType,
    PermittedValueChecker,
    RelationshipInfo,
    SemanticVersionColType,
)
from camcops_server.cc_modules.cc_simpleobjects import TaskExportOptions
from camcops_server.cc_modules.cc_tsv import TsvPage
from camcops_server.cc_modules.cc_version import CAMCOPS_SERVER_VERSION
from camcops_server.cc_modules.cc_xml import (
    make_xml_branches_from_blobs,
    make_xml_branches_from_columns,
    make_xml_branches_from_summaries,
    XML_COMMENT_STORED,
    XML_COMMENT_CALCULATED,
    XmlElement,
)

if TYPE_CHECKING:
    from camcops_server.cc_modules.cc_blob import Blob
    from camcops_server.cc_modules.cc_request import CamcopsRequest
    from camcops_server.cc_modules.cc_summaryelement import SummaryElement

log = BraceStyleAdapter(logging.getLogger(__name__))

T = TypeVar('T')

# Database fieldname constants. Do not change. Used here and in client_api.py
FN_PK = "_pk"
FN_DEVICE_ID = "_device_id"
FN_ERA = "_era"
FN_CURRENT = "_current"
FN_WHEN_ADDED_EXACT = "_when_added_exact"
FN_WHEN_ADDED_BATCH_UTC = "_when_added_batch_utc"
FN_ADDING_USER_ID = "_adding_user_id"
FN_WHEN_REMOVED_EXACT = "_when_removed_exact"
FN_WHEN_REMOVED_BATCH_UTC = "_when_removed_batch_utc"
FN_REMOVING_USER_ID = "_removing_user_id"
FN_PRESERVING_USER_ID = "_preserving_user_id"
FN_FORCIBLY_PRESERVED = "_forcibly_preserved"
FN_PREDECESSOR_PK = "_predecessor_pk"
FN_SUCCESSOR_PK = "_successor_pk"
FN_MANUALLY_ERASED = "_manually_erased"
FN_MANUALLY_ERASED_AT = "_manually_erased_at"
FN_MANUALLY_ERASING_USER_ID = "_manually_erasing_user_id"
FN_CAMCOPS_VERSION = "_camcops_version"
FN_ADDITION_PENDING = "_addition_pending"
FN_REMOVAL_PENDING = "_removal_pending"
FN_GROUP_ID = "_group_id"


# =============================================================================
# Base classes implementing common fields
# =============================================================================

# noinspection PyAttributeOutsideInit
class GenericTabletRecordMixin(object):
    """
    Mixin for all tables that are uploaded from the client, representing the
    fields that the server adds at the point of upload.

    From the server's perspective, ``_pk`` is the unique primary key.

    However, records are defined also in their tablet context, for which an
    individual tablet (defined by the combination of ``_device_id`` and
    ``_era``) sees its own PK, ``id``.
    """
    __tablename__ = None  # type: str  # sorts out some mixin type checking

    # -------------------------------------------------------------------------
    # On the server side:
    # -------------------------------------------------------------------------

    # Plain columns

    # noinspection PyMethodParameters
    @declared_attr
    def _pk(cls) -> Column:
        return Column(
            FN_PK, Integer,
            primary_key=True, autoincrement=True, index=True,
            comment="(SERVER) Primary key (on the server)"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _device_id(cls) -> Column:
        return Column(
            FN_DEVICE_ID, Integer, ForeignKey("_security_devices.id"),
            nullable=False, index=True,
            comment="(SERVER) ID of the source tablet device"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _era(cls) -> Column:
        return Column(
            FN_ERA, EraColType,
            nullable=False, index=True,
            comment="(SERVER) 'NOW', or when this row was preserved and "
                    "removed from the source device (UTC ISO 8601)",
        )
        # ... note that _era is textual so that plain comparison
        # with "=" always works, i.e. no NULLs -- for USER comparison too, not
        # just in CamCOPS code

    # noinspection PyMethodParameters
    @declared_attr
    def _current(cls) -> Column:
        return Column(
            FN_CURRENT, Boolean,
            nullable=False, index=True,
            comment="(SERVER) Is the row current (1) or not (0)?"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _when_added_exact(cls) -> Column:
        return Column(
            FN_WHEN_ADDED_EXACT, PendulumDateTimeAsIsoTextColType,
            comment="(SERVER) Date/time this row was added (ISO 8601)"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _when_added_batch_utc(cls) -> Column:
        return Column(
            FN_WHEN_ADDED_BATCH_UTC, DateTime,
            comment="(SERVER) Date/time of the upload batch that added this "
                    "row (DATETIME in UTC)"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _adding_user_id(cls) -> Column:
        return Column(
            FN_ADDING_USER_ID, Integer,
            ForeignKey("_security_users.id"),
            comment="(SERVER) ID of user that added this row",
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _when_removed_exact(cls) -> Column:
        return Column(
            FN_WHEN_REMOVED_EXACT, PendulumDateTimeAsIsoTextColType,
            comment="(SERVER) Date/time this row was removed, i.e. made "
                    "not current (ISO 8601)"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _when_removed_batch_utc(cls) -> Column:
        return Column(
            FN_WHEN_REMOVED_BATCH_UTC, DateTime,
            comment="(SERVER) Date/time of the upload batch that removed "
                    "this row (DATETIME in UTC)"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _removing_user_id(cls) -> Column:
        return Column(
            FN_REMOVING_USER_ID, Integer,
            ForeignKey("_security_users.id"),
            comment="(SERVER) ID of user that removed this row"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _preserving_user_id(cls) -> Column:
        return Column(
            FN_PRESERVING_USER_ID, Integer,
            ForeignKey("_security_users.id"),
            comment="(SERVER) ID of user that preserved this row"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _forcibly_preserved(cls) -> Column:
        return Column(
            FN_FORCIBLY_PRESERVED, Boolean, default=False,
            comment="(SERVER) Forcibly preserved by superuser (rather than "
                    "normally preserved by tablet)?"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _predecessor_pk(cls) -> Column:
        return Column(
            FN_PREDECESSOR_PK, Integer,
            comment="(SERVER) PK of predecessor record, prior to modification"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _successor_pk(cls) -> Column:
        return Column(
            FN_SUCCESSOR_PK, Integer,
            comment="(SERVER) PK of successor record  (after modification) "
                    "or NULL (whilst live, or after deletion)"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _manually_erased(cls) -> Column:
        return Column(
            FN_MANUALLY_ERASED, Boolean, default=False,
            comment="(SERVER) Record manually erased (content destroyed)?"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _manually_erased_at(cls) -> Column:
        return Column(
            FN_MANUALLY_ERASED_AT, PendulumDateTimeAsIsoTextColType,
            comment="(SERVER) Date/time of manual erasure (ISO 8601)"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _manually_erasing_user_id(cls) -> Column:
        return Column(
            FN_MANUALLY_ERASING_USER_ID, Integer,
            ForeignKey("_security_users.id"),
            comment="(SERVER) ID of user that erased this row manually"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _camcops_version(cls) -> Column:
        return Column(
            FN_CAMCOPS_VERSION, SemanticVersionColType,
            default=CAMCOPS_SERVER_VERSION,
            comment="(SERVER) CamCOPS version number of the uploading device"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _addition_pending(cls) -> Column:
        return Column(
            FN_ADDITION_PENDING, Boolean, nullable=False, default=False,
            comment="(SERVER) Addition pending?"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _removal_pending(cls) -> Column:
        return Column(
            FN_REMOVAL_PENDING, Boolean, default=False,
            comment="(SERVER) Removal pending?"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _group_id(cls) -> Column:
        return Column(
            FN_GROUP_ID, Integer, ForeignKey("_security_groups.id"),
            nullable=False, index=True,
            comment="(SERVER) ID of group to which this record belongs"
        )

    RESERVED_FIELDS = [  # fields that tablets can't upload
        FN_PK,
        FN_DEVICE_ID,
        FN_ERA,
        FN_CURRENT,
        FN_WHEN_ADDED_EXACT,
        FN_WHEN_ADDED_BATCH_UTC,
        FN_ADDING_USER_ID,
        FN_WHEN_REMOVED_EXACT,
        FN_WHEN_REMOVED_BATCH_UTC,
        FN_REMOVING_USER_ID,
        FN_PRESERVING_USER_ID,
        FN_FORCIBLY_PRESERVED,
        FN_PREDECESSOR_PK,
        FN_SUCCESSOR_PK,
        FN_MANUALLY_ERASED,
        FN_MANUALLY_ERASED_AT,
        FN_MANUALLY_ERASING_USER_ID,
        FN_CAMCOPS_VERSION,
        FN_ADDITION_PENDING,
        FN_REMOVAL_PENDING,
        FN_GROUP_ID,
    ]  # but more generally: they start with "_"...
    assert(all(x.startswith("_") for x in RESERVED_FIELDS))

    # -------------------------------------------------------------------------
    # Fields that *all* client tables have:
    # -------------------------------------------------------------------------

    # noinspection PyMethodParameters
    @declared_attr
    def id(cls) -> Column:
        return Column(
            "id", Integer,
            nullable=False, index=True,
            comment="(TASK) Primary key (task ID) on the tablet device"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def when_last_modified(cls) -> Column:
        return Column(
            "when_last_modified", PendulumDateTimeAsIsoTextColType,
            index=True,  # ... as used by database upload script
            comment="(STANDARD) Date/time this row was last modified on the "
                    "source tablet device (ISO 8601)"
        )

    # noinspection PyMethodParameters
    @declared_attr
    def _move_off_tablet(cls) -> Column:
        return Column(
            "_move_off_tablet", Boolean, default=False,
            comment="(SERVER/TABLET) Record-specific preservation pending?"
        )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    # noinspection PyMethodParameters
    @declared_attr
    def _device(cls) -> RelationshipProperty:
        return relationship("Device")

    # noinspection PyMethodParameters
    @declared_attr
    def _adding_user(cls) -> RelationshipProperty:
        return relationship("User", foreign_keys=[cls._adding_user_id])

    # noinspection PyMethodParameters
    @declared_attr
    def _removing_user(cls) -> RelationshipProperty:
        return relationship("User", foreign_keys=[cls._removing_user_id])

    # noinspection PyMethodParameters
    @declared_attr
    def _preserving_user(cls) -> RelationshipProperty:
        return relationship("User", foreign_keys=[cls._preserving_user_id])

    # noinspection PyMethodParameters
    @declared_attr
    def _manually_erasing_user(cls) -> RelationshipProperty:
        return relationship("User",
                            foreign_keys=[cls._manually_erasing_user_id])

    # noinspection PyMethodParameters
    @declared_attr
    def _group(cls) -> RelationshipProperty:
        return relationship("Group",
                            foreign_keys=[cls._group_id])

    # -------------------------------------------------------------------------
    # Fetching attributes
    # -------------------------------------------------------------------------

    def get_pk(self) -> Optional[int]:
        """
        Returns the (server) primary key of this record.
        """
        return self._pk

    def get_era(self) -> Optional[str]:
        """
        Returns the era of this record (a text representation of the date/time
        of the point of record finalization, or ``NOW`` if the record is still
        present on the client device).
        """
        return self._era

    def get_device_id(self) -> Optional[int]:
        """
        Returns the client device ID of this record.
        """
        return self._device_id

    def get_group_id(self) -> Optional[int]:
        """
        Returns the group ID of this record.
        """
        return self._group_id

    # -------------------------------------------------------------------------
    # Autoscanning objects and their relationships
    # -------------------------------------------------------------------------

    def _get_xml_root(self,
                      req: "CamcopsRequest",
                      options: TaskExportOptions) -> XmlElement:
        """
        Called to create an XML root object for records ancillary to Task
        objects. Tasks themselves use a more complex mechanism.

        Args:
            req: a :class:`camcops_server.cc_modules.cc_request.CamcopsRequest`
            options: a :class:`camcops_server.cc_modules.cc_simpleobjects.TaskExportOptions`
        """  # noqa
        # "__tablename__" will make the type checker complain, as we're
        # defining a function for a mixin that assumes it's mixed in to a
        # SQLAlchemy Base-derived class
        # noinspection PyUnresolvedReferences
        return XmlElement(
            name=self.__tablename__,
            value=self._get_xml_branches(req=req, options=options)
        )

    def _get_xml_branches(self,
                          req: "CamcopsRequest",
                          options: TaskExportOptions) -> List[XmlElement]:
        """
        Gets the values of SQLAlchemy columns as XmlElement objects.
        Optionally, find any SQLAlchemy relationships that are relationships
        to Blob objects, and include them too.

        Used by :func:`_get_xml_root` above, but also by Tasks themselves.

        Args:
            req: a :class:`camcops_server.cc_modules.cc_request.CamcopsRequest`
            options: a :class:`camcops_server.cc_modules.cc_simpleobjects.TaskExportOptions`
        """  # noqa
        # log.debug("_get_xml_branches for {!r}", self)
        options = options or TaskExportOptions(xml_include_plain_columns=True,
                                               xml_include_calculated=True,
                                               xml_sort_by_name=True)
        branches = []  # type: List[XmlElement]
        if options.xml_with_header_comments:
            branches.append(XML_COMMENT_STORED)
        if options.xml_include_plain_columns:
            new_branches = make_xml_branches_from_columns(
                self, skip_fields=options.xml_skip_fields)
            if options.xml_sort_by_name:
                new_branches.sort(key=lambda el: el.name)
            branches += new_branches
        if options.include_blobs:
            new_branches = make_xml_branches_from_blobs(
                req, self, skip_fields=options.xml_skip_fields)
            if options.xml_sort_by_name:
                new_branches.sort(key=lambda el: el.name)
            branches += new_branches
        # Calculated
        if options.xml_include_calculated:
            if options.xml_with_header_comments:
                branches.append(XML_COMMENT_CALCULATED)
            branches.extend(make_xml_branches_from_summaries(
                self.get_summaries(req),
                skip_fields=options.xml_skip_fields,
                sort_by_name=options.xml_sort_by_name
            ))
        # log.debug("... branches for {!r}: {!r}", self, branches)
        return branches

    def _get_core_tsv_page(self, req: "CamcopsRequest",
                           heading_prefix: str = "") -> TsvPage:
        """
        Returns a single-row :class:`camcops_server.cc_modules.cc_tsv.TsvPage`,
        like an Excel "sheet", representing this record. (It may be combined
        with others later to produce a multi-row spreadsheet.)
        """
        row = OrderedDict()
        for attrname, column in gen_columns(self):
            row[heading_prefix + attrname] = getattr(self, attrname)
        for s in self.get_summaries(req):
            row[heading_prefix + s.name] = s.value
        return TsvPage(name=self.__tablename__, rows=[row])

    # -------------------------------------------------------------------------
    # Erasing (overwriting data, not deleting the database records)
    # -------------------------------------------------------------------------

    def manually_erase_with_dependants(self, req: "CamcopsRequest") -> None:
        """
        Manually erases a standard record and marks it so erased. Iterates
        through any dependants and does likewise to them.

        The object remains ``_current`` (if it was), as a placeholder, but its
        contents are wiped.

        WRITES TO THE DATABASE.
        """
        if self._manually_erased or self._pk is None or self._era == ERA_NOW:
            # ... _manually_erased: don't do it twice
            # ... _pk: basic sanity check
            # ... _era: don't erase things that are current on the tablet
            return
        # 1. "Erase my dependants"
        for ancillary in self.gen_ancillary_instances_even_noncurrent():
            ancillary.manually_erase_with_dependants(req)
        for blob in self.gen_blobs_even_noncurrent():
            blob.manually_erase_with_dependants(req)
        # 2. "Erase me"
        erasure_attrs = []  # type: List[str]
        for attrname, column in gen_columns(self):
            if attrname.startswith("_"):  # system field
                continue
            if not column.nullable:  # this should cover FKs
                continue
            if column.foreign_keys:  # ... but to be sure...
                continue
            erasure_attrs.append(attrname)
        for attrname in erasure_attrs:
            setattr(self, attrname, None)
        self._current = False
        self._manually_erased = True
        self._manually_erased_at = req.now
        self._manually_erasing_user_id = req.user_id

    def delete_with_dependants(self, req: "CamcopsRequest") -> None:
        """
        Deletes (completely from the database) this record and any
        dependant records.
        """
        if self._pk is None:
            return
        # 1. "Delete my dependants"
        for ancillary in self.gen_ancillary_instances_even_noncurrent():
            ancillary.delete_with_dependants(req)
        for blob in self.gen_blobs_even_noncurrent():
            blob.delete_with_dependants(req)
        # 2. "Delete me"
        dbsession = SqlASession.object_session(self)
        dbsession.delete(self)

    def gen_attrname_ancillary_pairs(self) \
            -> Generator[Tuple[str, "GenericTabletRecordMixin"], None, None]:
        """
        Iterates through and yields all ``_current`` "ancillary" objects
        (typically: records of subtables).

        Yields tuples of ``(attrname, related_record)``.
        """
        for attrname, rel_prop, rel_cls in gen_ancillary_relationships(self):
            if rel_prop.uselist:
                ancillaries = getattr(self, attrname)  # type: List[GenericTabletRecordMixin]  # noqa
            else:
                ancillaries = [getattr(self, attrname)]  # type: List[GenericTabletRecordMixin]  # noqa
            for ancillary in ancillaries:
                if ancillary is None:
                    continue
                yield attrname, ancillary

    def gen_ancillary_instances(self) -> Generator["GenericTabletRecordMixin",
                                                   None, None]:
        """
        Generates all ``_current`` ancillary objects of this object.
        """
        for attrname, ancillary in self.gen_attrname_ancillary_pairs():
            yield ancillary

    def gen_ancillary_instances_even_noncurrent(self) \
            -> Generator["GenericTabletRecordMixin", None, None]:
        """
        Generates all ancillary objects of this object, even non-current
        ones.
        """
        seen = set()  # type: Set[GenericTabletRecordMixin]
        for ancillary in self.gen_ancillary_instances():
            for lineage_member in ancillary.get_lineage():
                if lineage_member in seen:
                    continue
                seen.add(lineage_member)
                yield lineage_member

    def gen_blobs(self) -> Generator["Blob", None, None]:
        """
        Generate all ``_current`` BLOBs owned by this object.
        """
        for id_attrname, column in gen_camcops_blob_columns(self):
            relationship_attr = column.blob_relationship_attr_name
            blob = getattr(self, relationship_attr)
            if blob is None:
                continue
            yield blob

    def gen_blobs_even_noncurrent(self) -> Generator["Blob", None, None]:
        """
        Generates all BLOBs owned by this object, even non-current ones.
        """
        seen = set()  # type: Set["Blob"]
        for blob in self.gen_blobs():
            if blob is None:
                continue
            for lineage_member in blob.get_lineage():
                if lineage_member in seen:
                    continue
                # noinspection PyTypeChecker
                seen.add(lineage_member)
                yield lineage_member

    def get_lineage(self) -> List["GenericTabletRecordMixin"]:
        """
        Returns all records that are part of the same "lineage", that is:

        - of the same class;
        - matching on id/device_id/era;
        - including both current and any historical non-current versions.

        """
        dbsession = SqlASession.object_session(self)
        cls = self.__class__
        q = dbsession.query(cls)\
            .filter(cls.id == self.id)\
            .filter(cls._device_id == self._device_id)\
            .filter(cls._era == self._era)
        return list(q)

    # -------------------------------------------------------------------------
    # History functions for server-side editing
    # -------------------------------------------------------------------------

    def set_predecessor(self, req: "CamcopsRequest",
                        predecessor: "GenericTabletRecordMixin") -> None:
        """
        Used for some unusual server-side manipulations (e.g. editing patient
        details).

        Amends this object so the "self" object replaces the predecessor, so:

        - "self" becomes current and refers back to "predecessor";
        - "predecessor" becomes non-current and refers forward to "self".

        """
        assert predecessor._current
        # We become new and current, and refer to our predecessor
        self._device_id = predecessor._device_id
        self._era = predecessor._era
        self._current = True
        self._when_added_exact = req.now
        self._when_added_batch_utc = req.now_utc
        self._adding_user_id = req.user_id
        if self._era != ERA_NOW:
            self._preserving_user_id = req.user_id
            self._forcibly_preserved = True
        self._predecessor_pk = predecessor._pk
        self._camcops_version = predecessor._camcops_version
        self._group_id = predecessor._group_id
        # Make our predecessor refer to us
        if self._pk is None:
            req.dbsession.add(self)  # ensure we have a PK, part 1
            req.dbsession.flush()  # ensure we have a PK, part 2
        predecessor._set_successor(req, self)

    def _set_successor(self, req: "CamcopsRequest",
                       successor: "GenericTabletRecordMixin") -> None:
        """
        See :func:`set_predecessor` above.
        """
        assert successor._pk is not None
        self._current = False
        self._when_removed_exact = req.now
        self._when_removed_batch_utc = req.now_utc
        self._removing_user_id = req.user_id
        self._successor_pk = successor._pk

    def mark_as_deleted(self, req: "CamcopsRequest") -> None:
        """
        Ends the history chain and marks this record as non-current.
        """
        if self._current:
            self._when_removed_exact = req.now
            self._when_removed_batch_utc = req.now_utc
            self._removing_user_id = req.user_id
            self._current = False

    def create_fresh(self, req: "CamcopsRequest", device_id: int,
                     era: str, group_id: int) -> None:
        """
        Used to create a record from scratch.
        """
        self._device_id = device_id
        self._era = era
        self._group_id = group_id
        self._current = True
        self._when_added_exact = req.now
        self._when_added_batch_utc = req.now_utc
        self._adding_user_id = req.user_id

    # -------------------------------------------------------------------------
    # Override this if you provide summaries
    # -------------------------------------------------------------------------

    # noinspection PyMethodMayBeStatic
    def get_summaries(self, req: "CamcopsRequest") -> List["SummaryElement"]:
        """
        Return a list of :class:`SummaryElement` objects, for this database
        object (not any dependent classes/tables).

        Note that this is implemented on :class:`GenericTabletRecordMixin`,
        not :class:`camcops_server.cc_modules.cc_task.Task`, so that ancillary
        objects can also provide summaries.
        """
        return []  # type: List[SummaryElement]

    def get_summary_names(self, req: "CamcopsRequest") -> List[str]:
        """
        Returns a list of summary field names.
        """
        return [x.name for x in self.get_summaries(req)]


# =============================================================================
# Relationships
# =============================================================================

def ancillary_relationship(
        parent_class_name: str,
        ancillary_class_name: str,
        ancillary_fk_to_parent_attr_name: str,
        ancillary_order_by_attr_name: str = None,
        read_only: bool = True) -> RelationshipProperty:
    """
    Implements a one-to-many relationship, i.e. one parent to many ancillaries.
    """
    parent_pk_attr_name = "id"  # always
    return relationship(
        ancillary_class_name,
        primaryjoin=(
            "and_("
            " remote({a}.{fk}) == foreign({p}.{pk}), "
            " remote({a}._device_id) == foreign({p}._device_id), "
            " remote({a}._era) == foreign({p}._era), "
            " remote({a}._current) == True "
            ")".format(
                a=ancillary_class_name,
                fk=ancillary_fk_to_parent_attr_name,
                p=parent_class_name,
                pk=parent_pk_attr_name,
            )
        ),
        uselist=True,
        order_by="{a}.{f}".format(a=ancillary_class_name,
                                  f=ancillary_order_by_attr_name),
        viewonly=read_only,
        info={
            RelationshipInfo.IS_ANCILLARY: True,
        },
        # ... "info" is a user-defined dictionary; see
        # http://docs.sqlalchemy.org/en/latest/orm/relationship_api.html#sqlalchemy.orm.relationship.params.info  # noqa
        # http://docs.sqlalchemy.org/en/latest/orm/internals.html#MapperProperty.info  # noqa
    )


# =============================================================================
# Field creation assistance
# =============================================================================

# TypeEngineBase = TypeVar('TypeEngineBase', bound=TypeEngine)

def add_multiple_columns(
        cls: Type,
        prefix: str,
        start: int,
        end: int,
        coltype=Integer,
        # this type fails: Union[Type[TypeEngineBase], TypeEngine]
        # ... https://stackoverflow.com/questions/38106227
        # ... https://github.com/python/typing/issues/266
        colkwargs: Dict[str, Any] = None,
        comment_fmt: str = None,
        comment_strings: List[str] = None,
        minimum: Union[int, float] = None,
        maximum: Union[int, float] = None,
        pv: List[Any] = None) -> None:
    """
    Add a sequence of SQLAlchemy columns to a class.

    Called from a metaclass.
    Used to make task creation a bit easier.

    Args:
        cls:
            class to which to add columns
        prefix:
            Fieldname will be ``prefix + str(n)``, where ``n`` is defined as
            below.
        start:
            Start of range.
        end:
            End of range. Thus: ``i`` will range from ``0`` to ``(end -
            start)`` inclusive; ``n`` will range from ``start`` to ``end``
            inclusive.
        coltype:
             SQLAlchemy column type, in either of these formats: (a)
             ``Integer`` (of general type ``Type[TypeEngine]``?); (b)
             ``Integer()`` (of general type ``TypeEngine``).
        colkwargs:
            SQLAlchemy column arguments, as in
            ``Column(name, coltype, **colkwargs)``
        comment_fmt:
            Format string defining field comments. Substitutable
            values are:

            - ``{n}``: field number (from range).
            - ``{s}``: comment_strings[i], or "" if out of range.

        comment_strings:
            see ``comment_fmt``
        minimum:
            minimum permitted value, or ``None``
        maximum:
            maximum permitted value, or ``None``
        pv:
            list of permitted values, or ``None``
    """
    colkwargs = {} if colkwargs is None else colkwargs  # type: Dict[str, Any]
    comment_strings = comment_strings or []
    for n in range(start, end + 1):
        nstr = str(n)
        i = n - start
        colname = prefix + nstr
        if comment_fmt:
            s = ""
            if 0 <= i < len(comment_strings):
                s = comment_strings[i] or ""
            colkwargs["comment"] = comment_fmt.format(n=n, s=s)
        if minimum is not None or maximum is not None or pv is not None:
            colkwargs["permitted_value_checker"] = PermittedValueChecker(
                minimum=minimum,
                maximum=maximum,
                permitted_values=pv
            )
            setattr(cls, colname, CamcopsColumn(colname, coltype, **colkwargs))
        else:
            setattr(cls, colname, Column(colname, coltype, **colkwargs))
