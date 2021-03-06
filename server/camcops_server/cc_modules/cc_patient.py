#!/usr/bin/env python

"""
camcops_server/cc_modules/cc_patient.py

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

**Patients.**

"""

import logging
from typing import Generator, List, Optional, Set, Tuple, TYPE_CHECKING, Union

from cardinal_pythonlib.classes import classproperty
from cardinal_pythonlib.datetimefunc import (
    coerce_to_pendulum_date,
    format_datetime,
    get_age,
    PotentialDatetimeType,
)
from cardinal_pythonlib.logs import BraceStyleAdapter
import cardinal_pythonlib.rnc_web as ws
import hl7
import pendulum
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session as SqlASession
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.expression import and_, ClauseElement, select
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.selectable import SelectBase
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.sqltypes import Integer, UnicodeText

from camcops_server.cc_modules.cc_audit import audit
from camcops_server.cc_modules.cc_constants import (
    DateFormat,
    ERA_NOW,
    FP_ID_DESC,
    FP_ID_SHORT_DESC,
    FP_ID_NUM,
    TSV_PATIENT_FIELD_PREFIX,
)
from camcops_server.cc_modules.cc_db import GenericTabletRecordMixin
from camcops_server.cc_modules.cc_hl7 import make_pid_segment
from camcops_server.cc_modules.cc_html import answer
from camcops_server.cc_modules.cc_simpleobjects import (
    BarePatientInfo,
    HL7PatientIdentifier,
)
from camcops_server.cc_modules.cc_patientidnum import PatientIdNum
from camcops_server.cc_modules.cc_report import Report
from camcops_server.cc_modules.cc_simpleobjects import (
    IdNumReference,
    TaskExportOptions,
)
from camcops_server.cc_modules.cc_specialnote import SpecialNote
from camcops_server.cc_modules.cc_sqla_coltypes import (
    CamcopsColumn,
    PatientNameColType,
    SexColType,
)
from camcops_server.cc_modules.cc_sqlalchemy import Base
from camcops_server.cc_modules.cc_tsv import TsvPage
from camcops_server.cc_modules.cc_unittest import DemoDatabaseTestCase
from camcops_server.cc_modules.cc_version import CAMCOPS_SERVER_VERSION_STRING
from camcops_server.cc_modules.cc_xml import (
    XML_COMMENT_SPECIAL_NOTES,
    XmlElement,
)

if TYPE_CHECKING:
    from camcops_server.cc_modules.cc_exportrecipient import ExportRecipient
    from camcops_server.cc_modules.cc_group import Group
    from camcops_server.cc_modules.cc_policy import TokenizedPolicy
    from camcops_server.cc_modules.cc_request import CamcopsRequest

log = BraceStyleAdapter(logging.getLogger(__name__))


# =============================================================================
# Patient class
# =============================================================================

class Patient(GenericTabletRecordMixin, Base):
    """
    Class representing a patient.
    """
    __tablename__ = "patient"

    id = Column(
        "id", Integer,
        nullable=False,
        comment="Primary key (patient ID) on the source tablet device"
        # client PK
    )
    forename = CamcopsColumn(
        "forename", PatientNameColType,
        index=True,
        identifies_patient=True, cris_include=True,
        comment="Forename"
    )
    surname = CamcopsColumn(
        "surname", PatientNameColType,
        index=True,
        identifies_patient=True, cris_include=True,
        comment="Surname"
    )
    dob = CamcopsColumn(
        "dob", sqltypes.Date,  # verified: merge_db handles this correctly
        index=True,
        identifies_patient=True, cris_include=True,
        comment="Date of birth"
        # ... e.g. "2013-02-04"
    )
    sex = CamcopsColumn(
        "sex", SexColType,
        index=True,
        cris_include=True,
        comment="Sex (M, F, X)"
    )
    address = CamcopsColumn(
        "address", UnicodeText,
        identifies_patient=True,
        comment="Address"
    )
    gp = Column(
        "gp", UnicodeText,
        comment="General practitioner (GP)"
    )
    other = CamcopsColumn(
        "other", UnicodeText,
        identifies_patient=True,
        comment="Other details"
    )
    idnums = relationship(
        # http://docs.sqlalchemy.org/en/latest/orm/join_conditions.html#relationship-custom-foreign
        # http://docs.sqlalchemy.org/en/latest/orm/relationship_api.html#sqlalchemy.orm.relationship  # noqa
        # http://docs.sqlalchemy.org/en/latest/orm/join_conditions.html#relationship-primaryjoin  # noqa
        "PatientIdNum",
        primaryjoin=(
            "and_("
            " remote(PatientIdNum.patient_id) == foreign(Patient.id), "
            " remote(PatientIdNum._device_id) == foreign(Patient._device_id), "
            " remote(PatientIdNum._era) == foreign(Patient._era), "
            " remote(PatientIdNum._current) == True "
            ")"
        ),
        uselist=True,
        viewonly=True,
        # Not profiled - any benefit unclear # lazy="joined"
    )  # type: List[PatientIdNum]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # THE FOLLOWING ARE DEFUNCT, AND THE SERVER WORKS AROUND OLD TABLETS IN
    # THE UPLOAD API.
    #
    # idnum1 = Column("idnum1", BigInteger, comment="ID number 1")
    # idnum2 = Column("idnum2", BigInteger, comment="ID number 2")
    # idnum3 = Column("idnum3", BigInteger, comment="ID number 3")
    # idnum4 = Column("idnum4", BigInteger, comment="ID number 4")
    # idnum5 = Column("idnum5", BigInteger, comment="ID number 5")
    # idnum6 = Column("idnum6", BigInteger, comment="ID number 6")
    # idnum7 = Column("idnum7", BigInteger, comment="ID number 7")
    # idnum8 = Column("idnum8", BigInteger, comment="ID number 8")
    #
    # iddesc1 = Column("iddesc1", IdDescriptorColType, comment="ID description 1")  # noqa
    # iddesc2 = Column("iddesc2", IdDescriptorColType, comment="ID description 2")  # noqa
    # iddesc3 = Column("iddesc3", IdDescriptorColType, comment="ID description 3")  # noqa
    # iddesc4 = Column("iddesc4", IdDescriptorColType, comment="ID description 4")  # noqa
    # iddesc5 = Column("iddesc5", IdDescriptorColType, comment="ID description 5")  # noqa
    # iddesc6 = Column("iddesc6", IdDescriptorColType, comment="ID description 6")  # noqa
    # iddesc7 = Column("iddesc7", IdDescriptorColType, comment="ID description 7")  # noqa
    # iddesc8 = Column("iddesc8", IdDescriptorColType, comment="ID description 8")  # noqa
    #
    # idshortdesc1 = Column("idshortdesc1", IdDescriptorColType, comment="ID short description 1")  # noqa
    # idshortdesc2 = Column("idshortdesc2", IdDescriptorColType, comment="ID short description 2")  # noqa
    # idshortdesc3 = Column("idshortdesc3", IdDescriptorColType, comment="ID short description 3")  # noqa
    # idshortdesc4 = Column("idshortdesc4", IdDescriptorColType, comment="ID short description 4")  # noqa
    # idshortdesc5 = Column("idshortdesc5", IdDescriptorColType, comment="ID short description 5")  # noqa
    # idshortdesc6 = Column("idshortdesc6", IdDescriptorColType, comment="ID short description 6")  # noqa
    # idshortdesc7 = Column("idshortdesc7", IdDescriptorColType, comment="ID short description 7")  # noqa
    # idshortdesc8 = Column("idshortdesc8", IdDescriptorColType, comment="ID short description 8")  # noqa
    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Relationships

    # noinspection PyMethodParameters
    @declared_attr
    def special_notes(cls) -> RelationshipProperty:
        """
        Relationship to all :class:`SpecialNote` objects associated with this
        patient.
        """
        # The SpecialNote also allows a link to patients, not just tasks,
        # like this:
        return relationship(
            SpecialNote,
            primaryjoin=(
                "and_("
                " remote(SpecialNote.basetable) == literal({repr_patient_tablename}), "  # noqa
                " remote(SpecialNote.task_id) == foreign(Patient.id), "
                " remote(SpecialNote.device_id) == foreign(Patient._device_id), "  # noqa
                " remote(SpecialNote.era) == foreign(Patient._era) "
                ")".format(
                    repr_patient_tablename=repr(cls.__tablename__),
                )
            ),
            uselist=True,
            order_by="SpecialNote.note_at",
            viewonly=True,  # for now!
        )

    @classmethod
    def get_patients_by_idnum(cls,
                              dbsession: SqlASession,
                              which_idnum: int,
                              idnum_value: int,
                              group_id: int = None,
                              current_only: bool = True) -> List['Patient']:
        """
        Get all patients matching the specified ID number.

        Args:
            dbsession: a :class:`sqlalchemy.orm.session.Session`
            which_idnum: which ID number type?
            idnum_value: actual value of the ID number
            group_id: optional group ID to restrict to
            current_only: restrict to ``_current`` patients?

        Returns:
            list of all matching patients

        """
        if not which_idnum or which_idnum < 1:
            return []
        if idnum_value is None:
            return []
        q = dbsession.query(cls).join(cls.idnums)
        # ... the join pre-restricts to current ID numbers
        # http://docs.sqlalchemy.org/en/latest/orm/join_conditions.html#using-custom-operators-in-join-conditions  # noqa
        q = q.filter(PatientIdNum.which_idnum == which_idnum)
        q = q.filter(PatientIdNum.idnum_value == idnum_value)
        if group_id is not None:
            q = q.filter(Patient._group_id == group_id)
        if current_only:
            q = q.filter(cls._current == True)  # nopep8
        patients = q.all()  # type: List[Patient]
        return patients

    @classmethod
    def get_patient_by_pk(cls, dbsession: SqlASession,
                          server_pk: int) -> Optional["Patient"]:
        """
        Fetch a patient by the server PK.
        """
        return dbsession.query(cls).filter(cls._pk == server_pk).first()

    def __str__(self) -> str:
        return "{sf} ({sex}, {dob}, {ids})".format(
            sf=self.get_surname_forename_upper(),
            sex=self.sex,
            dob=self.get_dob_str(),
            ids=", ".join(str(i) for i in self.get_idnum_objects()),
        )

    def get_idnum_objects(self) -> List[PatientIdNum]:
        """
        Returns all :class:`PatientIdNum` objects for the patient.

        These are SQLAlchemy ORM objects.
        """
        return self.idnums  # type: List[PatientIdNum]

    def get_idnum_references(self) -> List[IdNumReference]:
        """
        Returns all
        :class:`camcops_server.cc_modules.cc_simpleobjects.IdNumReference`
        objects for the patient.

        These are simple which_idnum/idnum_value pairs.
        """
        idnums = self.idnums  # type: List[PatientIdNum]
        return [x.get_idnum_reference() for x in idnums
                if x.is_superficially_valid()]

    def get_idnum_raw_values_only(self) -> List[int]:
        """
        Get all plain ID number values (ignoring which ID number type they
        represent) for the patient.
        """
        idnums = self.idnums  # type: List[PatientIdNum]
        return [x.idnum_value for x in idnums if x.is_superficially_valid()]

    def get_xml_root(self, req: "CamcopsRequest",
                     options: TaskExportOptions = None) -> XmlElement:
        """
        Get root of XML tree, as an
        :class:`camcops_server.cc_modules.cc_xml.XmlElement`.

        Args:
            req: a :class:`camcops_server.cc_modules.cc_request.CamcopsRequest`
            options: a :class:`camcops_server.cc_modules.cc_simpleobjects.TaskExportOptions`
        """  # noqa
        # No point in skipping old ID columns (1-8) now; they're gone.
        branches = self._get_xml_branches(req, options=options)
        # Now add new-style IDs:
        pidnum_branches = []  # type: List[XmlElement]
        pidnum_options = TaskExportOptions(xml_include_plain_columns=True,
                                           xml_with_header_comments=False)
        for pidnum in self.idnums:  # type: PatientIdNum
            pidnum_branches.append(pidnum._get_xml_root(
                req, options=pidnum_options))
        branches.append(XmlElement(
            name="idnums",
            value=pidnum_branches
        ))
        # Special notes
        branches.append(XML_COMMENT_SPECIAL_NOTES)
        special_notes = self.special_notes  # type: List[SpecialNote]
        for sn in special_notes:
            branches.append(sn.get_xml_root())
        return XmlElement(name=self.__tablename__, value=branches)

    def get_tsv_page(self, req: "CamcopsRequest") -> TsvPage:
        """
        Get a :class:`camcops_server.cc_modules.cc_tsv.TsvPage` for the
        patient.
        """
        # 1. Our core fields.
        page = self._get_core_tsv_page(
            req, heading_prefix=TSV_PATIENT_FIELD_PREFIX)
        # 2. ID number details
        #    We can't just iterate through the ID numbers; we have to iterate
        #    through all possible ID numbers.
        for iddef in req.idnum_definitions:
            n = iddef.which_idnum
            nstr = str(n)
            shortdesc = iddef.short_description
            longdesc = iddef.description
            idnum_value = next(
                (idnum.idnum_value for idnum in self.idnums
                 if idnum.which_idnum == n and idnum.is_superficially_valid()),
                None)
            page.add_or_set_value(
                heading=TSV_PATIENT_FIELD_PREFIX + FP_ID_NUM + nstr,
                value=idnum_value)
            page.add_or_set_value(
                heading=TSV_PATIENT_FIELD_PREFIX + FP_ID_DESC + nstr,
                value=longdesc)
            page.add_or_set_value(
                heading=(TSV_PATIENT_FIELD_PREFIX + FP_ID_SHORT_DESC +
                         nstr),
                value=shortdesc)
        return page

    def get_bare_ptinfo(self) -> BarePatientInfo:
        """
        Get basic identifying information, as a
        :class:`camcops_server.cc_modules.cc_simpleobjects.BarePatientInfo`
        object.
        """
        return BarePatientInfo(
            forename=self.forename,
            surname=self.surname,
            sex=self.sex,
            dob=self.dob,
            address=self.address,
            gp=self.gp,
            other=self.other,
            idnum_definitions=self.get_idnum_references()
        )

    @property
    def group(self) -> Optional["Group"]:
        """
        Returns the :class:`camcops_server.cc_modules.cc_group.Group` to which
        this patient's record belongs.
        """
        return self._group

    def satisfies_upload_id_policy(self) -> bool:
        """
        Does the patient satisfy the uploading ID policy?
        """
        group = self._group  # type: Optional[Group]
        if not group:
            return False
        return self.satisfies_id_policy(group.tokenized_upload_policy())

    def satisfies_finalize_id_policy(self) -> bool:
        """
        Does the patient satisfy the finalizing ID policy?
        """
        group = self._group  # type: Optional[Group]
        if not group:
            return False
        return self.satisfies_id_policy(group.tokenized_finalize_policy())

    def satisfies_id_policy(self, policy: "TokenizedPolicy") -> bool:
        """
        Does the patient satisfy a particular ID policy?
        """
        return policy.satisfies_id_policy(self.get_bare_ptinfo())

    def get_surname(self) -> str:
        """
        Get surname (in upper case) or "".
        """
        return self.surname.upper() if self.surname else ""

    def get_forename(self) -> str:
        """
        Get forename (in upper case) or "".
        """
        return self.forename.upper() if self.forename else ""

    def get_surname_forename_upper(self) -> str:
        """
        Get "SURNAME, FORENAME" in HTML-safe format, using "(UNKNOWN)" for
        missing details.
        """
        s = self.surname.upper() if self.surname else "(UNKNOWN)"
        f = self.forename.upper() if self.surname else "(UNKNOWN)"
        return ws.webify(s + ", " + f)

    def get_dob_html(self, longform: bool) -> str:
        """
        HTML fragment for date of birth.
        """
        if longform:
            return "<br>Date of birth: {}".format(
                answer(format_datetime(
                    self.dob, DateFormat.LONG_DATE, default=None)))
        return "DOB: {}.".format(format_datetime(
            self.dob, DateFormat.SHORT_DATE))

    def get_age(self, req: "CamcopsRequest",
                default: str = "") -> Union[int, str]:
        """
        Age (in whole years) today, or default.
        """
        now = req.now
        return self.get_age_at(now, default=default)

    def get_dob(self) -> Optional[pendulum.Date]:
        """
        Date of birth, as a a timezone-naive date.
        """
        dob = self.dob
        if not dob:
            return None
        return coerce_to_pendulum_date(dob)

    def get_dob_str(self) -> Optional[str]:
        """
        Date of birth, as a string.
        """
        dob_dt = self.get_dob()
        if dob_dt is None:
            return None
        return format_datetime(dob_dt, DateFormat.SHORT_DATE)

    def get_age_at(self,
                   when: PotentialDatetimeType,
                   default: str = "") -> Union[int, str]:
        """
        Age (in whole years) at a particular date, or default.
        """
        return get_age(self.dob, when, default=default)

    def is_female(self) -> bool:
        """
        Is sex 'F'?
        """
        return self.sex == "F"

    def is_male(self) -> bool:
        """
        Is sex 'M'?
        """
        return self.sex == "M"

    def get_sex(self) -> str:
        """
        Return sex or "".
        """
        return self.sex or ""

    def get_sex_verbose(self, default: str = "sex unknown") -> str:
        """
        Returns HTML-safe version of sex, or default.
        """
        return default if not self.sex else ws.webify(self.sex)

    def get_address(self) -> Optional[str]:
        """
        Returns address (NOT necessarily web-safe).
        """
        address = self.address  # type: Optional[str]
        return address or ""

    def get_hl7_pid_segment(self,
                            req: "CamcopsRequest",
                            recipient: "ExportRecipient") -> hl7.Segment:
        """
        Get HL7 patient identifier (PID) segment.

        Args:
            req:
                a :class:`camcops_server.cc_modules.cc_request.CamcopsRequest`
            recipient:
                a :class:`camcops_server.cc_modules.cc_exportrecipient.ExportRecipient`

        Returns:
            a :class:`hl7.Segment` object
        """  # noqa
        # Put the primary one first:
        patient_id_tuple_list = [
            HL7PatientIdentifier(
                id=str(self.get_idnum_value(recipient.primary_idnum)),
                id_type=recipient.get_hl7_id_type(
                    req,
                    recipient.primary_idnum),
                assigning_authority=recipient.get_hl7_id_aa(
                    req,
                    recipient.primary_idnum)
            )
        ]
        # Then the rest:
        for idobj in self.idnums:
            which_idnum = idobj.which_idnum
            if which_idnum == recipient.primary_idnum:
                continue
            idnum_value = idobj.idnum_value
            if idnum_value is None:
                continue
            patient_id_tuple_list.append(
                HL7PatientIdentifier(
                    id=str(idnum_value),
                    id_type=recipient.get_hl7_id_type(req, which_idnum),
                    assigning_authority=recipient.get_hl7_id_aa(
                        req, which_idnum)
                )
            )
        return make_pid_segment(
            forename=self.get_surname(),
            surname=self.get_forename(),
            dob=self.get_dob(),
            sex=self.get_sex(),
            address=self.get_address(),
            patient_id_list=patient_id_tuple_list,
        )

    def get_idnum_object(self, which_idnum: int) -> Optional[PatientIdNum]:
        """
        Gets the PatientIdNum object for a specified which_idnum, or None.
        """
        idnums = self.idnums  # type: List[PatientIdNum]
        for x in idnums:
            if x.which_idnum == which_idnum:
                return x
        return None

    def has_idnum_type(self, which_idnum: int) -> bool:
        """
        Does the patient have an ID number of the specified type?
        """
        return self.get_idnum_object(which_idnum) is not None

    def get_idnum_value(self, which_idnum: int) -> Optional[int]:
        """
        Get value of a specific ID number, if present.
        """
        idobj = self.get_idnum_object(which_idnum)
        return idobj.idnum_value if idobj else None

    def set_idnum_value(self, req: "CamcopsRequest",
                        which_idnum: int, idnum_value: int) -> None:
        """
        Sets an ID number value.
        """
        dbsession = req.dbsession
        ccsession = req.camcops_session
        idnums = self.idnums  # type: List[PatientIdNum]
        for idobj in idnums:
            if idobj.which_idnum == which_idnum:
                idobj.idnum_value = idnum_value
                return
        # Otherwise, make a new one:
        newid = PatientIdNum()
        newid.patient_id = self.id
        newid._device_id = self._device_id
        newid._era = self._era
        newid._current = True
        newid._when_added_exact = req.now_era_format
        newid._when_added_batch_utc = req.now_utc
        newid._adding_user_id = ccsession.user_id
        newid._camcops_version = CAMCOPS_SERVER_VERSION_STRING
        dbsession.add(newid)
        self.idnums.append(newid)

    def get_iddesc(self, req: "CamcopsRequest",
                   which_idnum: int) -> Optional[str]:
        """
        Get value of a specific ID description, if present.
        """
        idobj = self.get_idnum_object(which_idnum)
        return idobj.description(req) if idobj else None

    def get_idshortdesc(self, req: "CamcopsRequest",
                        which_idnum: int) -> Optional[str]:
        """
        Get value of a specific ID short description, if present.
        """
        idobj = self.get_idnum_object(which_idnum)
        return idobj.short_description(req) if idobj else None

    def is_preserved(self) -> bool:
        """
        Is the patient record preserved and erased from the tablet?
        """
        return self._pk is not None and self._era != ERA_NOW

    # -------------------------------------------------------------------------
    # Audit
    # -------------------------------------------------------------------------

    def audit(self, req: "CamcopsRequest",
              details: str, from_console: bool = False) -> None:
        """
        Audits an action to this patient.
        """
        audit(req,
              details,
              patient_server_pk=self._pk,
              table=Patient.__tablename__,
              server_pk=self._pk,
              from_console=from_console)

    # -------------------------------------------------------------------------
    # Special notes
    # -------------------------------------------------------------------------

    def apply_special_note(
            self,
            req: "CamcopsRequest",
            note: str,
            audit_msg: str = "Special note applied manually") -> None:
        """
        Manually applies a special note to a patient.
        WRITES TO DATABASE.
        """
        sn = SpecialNote()
        sn.basetable = self.__tablename__
        sn.task_id = self.id  # patient ID, in this case
        sn.device_id = self._device_id
        sn.era = self._era
        sn.note_at = req.now
        sn.user_id = req.user_id
        sn.note = note
        req.dbsession.add(sn)
        self.special_notes.append(sn)
        self.audit(req, audit_msg)
        # HL7 deletion of corresponding tasks is done in camcops_server.py

    # -------------------------------------------------------------------------
    # Deletion
    # -------------------------------------------------------------------------

    def gen_patient_idnums_even_noncurrent(self) -> \
            Generator[PatientIdNum, None, None]:
        """
        Generates all :class:`PatientIdNum` objects, including non-current
        ones.
        """
        seen = set()  # type: Set[PatientIdNum]
        for live_pidnum in self.idnums:
            for lineage_member in live_pidnum.get_lineage():
                if lineage_member in seen:
                    continue
                # noinspection PyTypeChecker
                seen.add(lineage_member)
                yield lineage_member

    def delete_with_dependants(self, req: "CamcopsRequest") -> None:
        """
        Delete the patient with all its dependent objects.
        """
        if self._pk is None:
            return
        for pidnum in self.gen_patient_idnums_even_noncurrent():
            req.dbsession.delete(pidnum)
        super().delete_with_dependants(req)

    # -------------------------------------------------------------------------
    # Editing
    # -------------------------------------------------------------------------

    @property
    def is_editable(self) -> bool:
        """
        Is the patient finalized (no longer available to be edited on the
        client device), and therefore editable on the server?
        """
        if self._era == ERA_NOW:
            # Not finalized; no editing on server
            return False
        return True

    def user_may_edit(self, req: "CamcopsRequest") -> bool:
        """
        Does the current user have permission to edit this patient?
        """
        return req.user.may_administer_group(self._group_id)


# =============================================================================
# Validate candidate patient info for upload
# =============================================================================

def is_candidate_patient_valid(ptinfo: BarePatientInfo,
                               group: "Group",
                               finalizing: bool) -> Tuple[bool, str]:
    """
    Is the specified patient acceptable to upload into this group?
    
    Checks:
    
    - group upload or finalize policy
    
    .. todo:: is_candidate_patient_valid: check against predefined patients, if
       the group wants

    Args:
        ptinfo:
            a :class:`camcops_server.cc_modules.cc_simpleobjects.BarePatientInfo`
            representing the patient info to check
        group:
            the :class:`camcops_server.cc_modules.cc_group.Group` into which
            this patient will be uploaded, if allowed
        finalizing:
            finalizing, rather than uploading?

    Returns:
        tuple: valid, reason

    """  # noqa
    if not group:
        return False, "Nonexistent group"

    if finalizing:
        if not group.tokenized_finalize_policy().satisfies_id_policy(ptinfo):
            return False, "Fails finalizing ID policy"
    else:
        if not group.tokenized_upload_policy().satisfies_id_policy(ptinfo):
            return False, "Fails upload ID policy"

    # *** add checks against prevalidated patients here

    return True, ""


# =============================================================================
# Reports
# =============================================================================

class DistinctPatientReport(Report):
    """
    Report to show distinct patients.
    """

    # noinspection PyMethodParameters
    @classproperty
    def report_id(cls) -> str:
        return "patient_distinct"

    # noinspection PyMethodParameters
    @classproperty
    def title(cls) -> str:
        return ("(Server) Patients, distinct by name, sex, DOB, all ID "
                "numbers")

    # noinspection PyMethodParameters
    @classproperty
    def superuser_only(cls) -> bool:
        return False

    # noinspection PyProtectedMember
    def get_query(self, req: "CamcopsRequest") -> SelectBase:
        select_fields = [
            Patient.surname.label("surname"),
            Patient.forename.label("forename"),
            Patient.dob.label("dob"),
            Patient.sex.label("sex"),
        ]
        # noinspection PyUnresolvedReferences
        select_from = Patient.__table__
        wheres = [Patient._current == True]  # type: List[ClauseElement]  # nopep8
        if not req.user.superuser:
            # Restrict to accessible groups
            group_ids = req.user.ids_of_groups_user_may_report_on
            wheres.append(Patient._group_id.in_(group_ids))
        for iddef in req.idnum_definitions:
            n = iddef.which_idnum
            desc = iddef.short_description
            # noinspection PyUnresolvedReferences
            aliased_table = PatientIdNum.__table__.alias("i{}".format(n))
            select_fields.append(aliased_table.c.idnum_value.label(desc))
            select_from = select_from.outerjoin(aliased_table, and_(
                aliased_table.c.patient_id == Patient.id,
                aliased_table.c._device_id == Patient._device_id,
                aliased_table.c._era == Patient._era,
                # Note: the following are part of the JOIN, not the WHERE:
                # (or failure to match a row will wipe out the Patient from the
                # OUTER JOIN):
                aliased_table.c._current == True,
                aliased_table.c.which_idnum == n,
            ))  # nopep8
        order_by = [
            Patient.surname,
            Patient.forename,
            Patient.dob,
            Patient.sex,
        ]
        query = (
            select(select_fields)
            .select_from(select_from)
            .where(and_(*wheres))
            .order_by(*order_by)
            .distinct()
        )
        return query


# =============================================================================
# Unit tests
# =============================================================================

class PatientTests(DemoDatabaseTestCase):
    """
    Unit tests.
    """
    def test_patient(self) -> None:
        self.announce("test_patient")
        from camcops_server.cc_modules.cc_group import Group

        req = self.req
        q = self.dbsession.query(Patient)
        p = q.first()  # type: Patient
        assert p, "Missing Patient in demo database!"

        for pidnum in p.get_idnum_objects():
            self.assertIsInstance(pidnum, PatientIdNum)
        for idref in p.get_idnum_references():
            self.assertIsInstance(idref, IdNumReference)
        for idnum in p.get_idnum_raw_values_only():
            self.assertIsInstance(idnum, int)
        self.assertIsInstance(p.get_xml_root(req), XmlElement)
        self.assertIsInstance(p.get_tsv_page(req), TsvPage)
        self.assertIsInstance(p.get_bare_ptinfo(), BarePatientInfo)
        self.assertIsInstanceOrNone(p.group, Group)
        self.assertIsInstance(p.satisfies_upload_id_policy(), bool)
        self.assertIsInstance(p.satisfies_finalize_id_policy(), bool)
        self.assertIsInstance(p.get_surname(), str)
        self.assertIsInstance(p.get_forename(), str)
        self.assertIsInstance(p.get_surname_forename_upper(), str)
        for longform in [True, False]:
            self.assertIsInstance(p.get_dob_html(longform), str)
        age_str_int = p.get_age(req)
        assert isinstance(age_str_int, str) or isinstance(age_str_int, int)
        self.assertIsInstanceOrNone(p.get_dob(), pendulum.Date)
        self.assertIsInstanceOrNone(p.get_dob_str(), str)
        age_at_str_int = p.get_age_at(req.now)
        assert isinstance(age_at_str_int, str) or isinstance(age_at_str_int, int)  # noqa
        self.assertIsInstance(p.is_female(), bool)
        self.assertIsInstance(p.is_male(), bool)
        self.assertIsInstance(p.get_sex(), str)
        self.assertIsInstance(p.get_sex_verbose(), str)
        self.assertIsInstance(p.get_address(), str)
        self.assertIsInstance(p.get_hl7_pid_segment(req, self.recipdef),
                              hl7.Segment)
        self.assertIsInstanceOrNone(p.get_idnum_object(which_idnum=1),
                                    PatientIdNum)
        self.assertIsInstanceOrNone(p.get_idnum_value(which_idnum=1), int)
        self.assertIsInstance(p.get_iddesc(req, which_idnum=1), str)
        self.assertIsInstance(p.get_idshortdesc(req, which_idnum=1), str)
        self.assertIsInstance(p.is_preserved(), bool)
        self.assertIsInstance(p.is_editable, bool)
        self.assertIsInstance(p.user_may_edit(req), bool)
