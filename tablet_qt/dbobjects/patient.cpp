/*
    Copyright (C) 2012-2017 Rudolf Cardinal (rudolf@pobox.com).

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

#include "patient.h"
#include <limits>
#include <QDebug>
#include "core/camcopsapp.h"
#include "common/dbconstants.h"
#include "common/design_defines.h"
#include "db/dbfunc.h"
#include "db/dbnestabletransaction.h"
#include "lib/datetime.h"
#include "lib/idpolicy.h"
#include "lib/uifunc.h"
#include "questionnairelib/commonoptions.h"
#include "questionnairelib/qugridcontainer.h"
#include "questionnairelib/qudatetime.h"
#include "questionnairelib/questionnaire.h"
#include "questionnairelib/quheading.h"
#include "questionnairelib/quimage.h"
#include "questionnairelib/qulineedit.h"
#include "questionnairelib/qulineeditlonglong.h"
#include "questionnairelib/qumcq.h"
#include "questionnairelib/qupage.h"
#include "questionnairelib/qutext.h"
#include "questionnairelib/qutextedit.h"
#include "tasklib/taskfactory.h"
#include "widgets/openablewidget.h"

const QString Patient::TABLENAME("patient");

// Important that these match ID policy names:
const QString FORENAME_FIELD("forename");
const QString SURNAME_FIELD("surname");
const QString DOB_FIELD("dob");
const QString SEX_FIELD("sex");
const QString IDNUM_FIELD_FORMAT("idnum%1");

// Not so important:
const QString ADDRESS_FIELD("address");
const QString GP_FIELD("gp");
const QString OTHER_FIELD("other");

const qint64 MIN_ID_NUM_VALUE = 0;
const qint64 MAX_ID_NUM_VALUE = std::numeric_limits<qint64>::max();

const QString TAG_POLICY_APP_OK("app_ok");
const QString TAG_POLICY_APP_FAIL("app_fail");
const QString TAG_POLICY_UPLOAD_OK("upload_ok");
const QString TAG_POLICY_UPLOAD_FAIL("upload_fail");
const QString TAG_POLICY_FINALIZE_OK("finalize_ok");
const QString TAG_POLICY_FINALIZE_FAIL("finalize_fail");
const QString TAG_IDCLASH_OK("idclash_ok");
const QString TAG_IDCLASH_FAIL("idclash_fail");
const QString TAG_IDCLASH_DETAIL("idclash_detail");


Patient::Patient(CamcopsApp& app, DatabaseManager& db, int load_pk) :
    DatabaseObject(app, db, TABLENAME, dbconst::PK_FIELDNAME, true, false),
    m_questionnaire(nullptr)
{
    // ------------------------------------------------------------------------
    // Define fields
    // ------------------------------------------------------------------------
    addField(FORENAME_FIELD, QVariant::String);
    addField(SURNAME_FIELD, QVariant::String);
    addField(SEX_FIELD, QVariant::String);
    addField(DOB_FIELD, QVariant::Date);
    addField(ADDRESS_FIELD, QVariant::String);
    addField(GP_FIELD, QVariant::String);
    addField(OTHER_FIELD, QVariant::String);
    for (int n = 1; n <= dbconst::NUMBER_OF_IDNUMS; ++n) {
        addField(IDNUM_FIELD_FORMAT.arg(n), QVariant::LongLong);
#ifdef DUPLICATE_ID_DESCRIPTIONS_INTO_PATIENT_TABLE
        // Information for these two comes from the server, and is ONLY stored
        // here at the moment of upload (copied from the CamcopsApp's info).
        addField(dbconst::IDSHORTDESC_FIELD_FORMAT.arg(n), QVariant::String);
        addField(dbconst::IDDESC_FIELD_FORMAT.arg(n), QVariant::String);
#endif
    }

    // ------------------------------------------------------------------------
    // Load from database (or create/save), unless this is a specimen
    // ------------------------------------------------------------------------
    load(load_pk);  // MUST ALWAYS CALL from derived Task constructor.
}


int Patient::id() const
{
    return pkvalueInt();
}


QString Patient::forename() const
{
    const QString forename = valueString(FORENAME_FIELD);
    return forename.isEmpty() ? "?" : forename;
}


QString Patient::surname() const
{
    const QString surname = valueString(SURNAME_FIELD);
    return surname.isEmpty() ? "?" : surname;
}


QString Patient::sex() const
{
    const QString sex = valueString(SEX_FIELD);
    return sex.isEmpty() ? "?" : sex;
}


bool Patient::isFemale() const
{
    return sex() == CommonOptions::SEX_FEMALE;
}


bool Patient::isMale() const
{
    return sex() == CommonOptions::SEX_MALE;
}


QDate Patient::dob() const
{
    return valueDate(DOB_FIELD);
}


QString Patient::dobText() const
{
    return datetime::textDate(value(DOB_FIELD));
}


int Patient::ageYears() const
{
    return datetime::ageYears(value(DOB_FIELD));
}


bool Patient::hasIdnum(int which_idnum) const
{
    return !idnumVariant(which_idnum).isNull();
}


QVariant Patient::idnumVariant(int which_idnum) const
{
    if (!dbconst::isValidWhichIdnum(which_idnum)) {
        return QVariant();
    }
    return value(IDNUM_FIELD_FORMAT.arg(which_idnum));
}


qlonglong Patient::idnumInteger(int which_idnum) const
{
    if (!dbconst::isValidWhichIdnum(which_idnum)) {
        return 0;
    }
    return valueULongLong(IDNUM_FIELD_FORMAT.arg(which_idnum));
}


OpenableWidget* Patient::editor(bool read_only)
{
    QuPagePtr page(new QuPage());
    page->setTitle(tr("Edit patient"));

    QuGridContainer* grid = new QuGridContainer();
    grid->setColumnStretch(0, 1);
    grid->setColumnStretch(1, 2);
    int row = 0;
    const Qt::Alignment align = Qt::AlignRight | Qt::AlignTop;

    grid->addCell(QuGridCell(new QuText(tr("Surname")), row, 0, 1, 1, align));
    grid->addCell(QuGridCell(new QuLineEdit(fieldRef(SURNAME_FIELD, false)),
                             row++, 1));
    grid->addCell(QuGridCell(new QuText(tr("Forename")), row, 0, 1, 1, align));
    grid->addCell(QuGridCell(new QuLineEdit(fieldRef(FORENAME_FIELD, false)),
                             row++, 1));
    grid->addCell(QuGridCell(new QuText(tr("Sex")), row, 0, 1, 1, align));
    grid->addCell(QuGridCell(
        (new QuMcq(fieldRef(SEX_FIELD),  // properly mandatory
                   CommonOptions::sexes()))->setHorizontal(true),
        row++, 1));
    grid->addCell(QuGridCell(new QuText(tr("Date of birth")),
                             row, 0, 1, 1, align));
    grid->addCell(QuGridCell(
        (new QuDateTime(fieldRef(DOB_FIELD,
                                 false)))->setMode(QuDateTime::DefaultDate),
        row++, 1));
    grid->addCell(QuGridCell(new QuText(tr("Address")), row, 0, 1, 1, align));
    grid->addCell(QuGridCell(new QuTextEdit(fieldRef(ADDRESS_FIELD, false)),
                             row++, 1));
    grid->addCell(QuGridCell(new QuText(tr("General practitioner (GP)")), row, 0, 1, 1, align));
    grid->addCell(QuGridCell(new QuTextEdit(fieldRef(GP_FIELD, false)),
                             row++, 1));
    grid->addCell(QuGridCell(new QuText(tr("Other details")), row, 0, 1, 1, align));
    grid->addCell(QuGridCell(new QuTextEdit(fieldRef(OTHER_FIELD, false)),
                             row++, 1));
    for (int n = 1; n <= dbconst::NUMBER_OF_IDNUMS; ++n) {
        QString iddesc = m_app.idDescription(n);
        QString idfield = IDNUM_FIELD_FORMAT.arg(n);
        grid->addCell(QuGridCell(new QuText(iddesc), row, 0, 1, 1, align));
        QuLineEditLongLong* num_editor = new QuLineEditLongLong(
                    fieldRef(idfield, false),
                    MIN_ID_NUM_VALUE,
                    MAX_ID_NUM_VALUE);
        grid->addCell(QuGridCell(num_editor, row++, 1));
    }
    page->addElement(grid);

    page->addElement(new QuHeading(tr("Minimum ID required for app:")));
    page->addElement(new QuText(TABLET_ID_POLICY.pretty()));
    page->addElement((new QuImage(uifunc::iconFilename(uiconst::CBS_OK),
                                  uiconst::ICONSIZE))
                     ->addTag(TAG_POLICY_APP_OK));
    page->addElement((new QuImage(uifunc::iconFilename(uiconst::ICON_STOP),
                                  uiconst::ICONSIZE))
                     ->addTag(TAG_POLICY_APP_FAIL));

    page->addElement(new QuHeading(tr("Minimum ID required for upload to server:")));
    page->addElement(new QuText(m_app.uploadPolicy().pretty()));
    page->addElement((new QuImage(uifunc::iconFilename(uiconst::CBS_OK),
                                  uiconst::ICONSIZE))
                     ->addTag(TAG_POLICY_UPLOAD_OK));
    page->addElement((new QuImage(uifunc::iconFilename(uiconst::ICON_STOP),
                                  uiconst::ICONSIZE))
                     ->addTag(TAG_POLICY_UPLOAD_FAIL));

    page->addElement(new QuHeading(tr("Minimum ID required to finalize on server:")));
    page->addElement(new QuText(m_app.finalizePolicy().pretty()));
    page->addElement((new QuImage(uifunc::iconFilename(uiconst::CBS_OK),
                                  uiconst::ICONSIZE))
                     ->addTag(TAG_POLICY_FINALIZE_OK));
    page->addElement((new QuImage(uifunc::iconFilename(uiconst::ICON_STOP),
                                  uiconst::ICONSIZE))
                     ->addTag(TAG_POLICY_FINALIZE_FAIL));

    page->addElement(new QuHeading(tr("ID numbers must not clash with another patient:")));
    page->addElement((new QuText("?"))->addTag(TAG_IDCLASH_DETAIL));
    page->addElement((new QuImage(uifunc::iconFilename(uiconst::CBS_OK),
                                  uiconst::ICONSIZE))
                     ->addTag(TAG_IDCLASH_OK));
    page->addElement((new QuImage(uifunc::iconFilename(uiconst::ICON_STOP),
                                  uiconst::ICONSIZE))
                     ->addTag(TAG_IDCLASH_FAIL));

    for (const QString& fieldname : policyAttributes().keys()) {
        FieldRefPtr fr = fieldRef(fieldname);
        connect(fr.data(), &FieldRef::valueChanged,
                this, &Patient::updateQuestionnaireIndicators);
    }

    m_questionnaire = new Questionnaire(m_app, {page});
    m_questionnaire->setReadOnly(read_only);
    updateQuestionnaireIndicators();
    return m_questionnaire;
}


bool Patient::hasForename() const
{
    return !valueString(FORENAME_FIELD).isEmpty();
}


bool Patient::hasSurname() const
{
    return !valueString(SURNAME_FIELD).isEmpty();
}


bool Patient::hasDob() const
{
    return !value(DOB_FIELD).isNull();
}


bool Patient::hasSex() const
{
    return !valueString(SEX_FIELD).isEmpty();
}


Patient::AttributesType Patient::policyAttributes() const
{
    AttributesType map;
    map[FORENAME_FIELD] = hasForename();
    map[SURNAME_FIELD] = hasSurname();
    map[DOB_FIELD] = hasDob();
    map[SEX_FIELD] = hasSex();
    for (int n = 1; n <= dbconst::NUMBER_OF_IDNUMS; ++n) {
        map[IDNUM_FIELD_FORMAT.arg(n)] = hasIdnum(n);
    }
    return map;
}


bool Patient::compliesWith(const IdPolicy& policy) const
{
    return policy.complies(policyAttributes());
}


bool Patient::compliesWithUpload() const
{
    return compliesWith(m_app.uploadPolicy());
}


bool Patient::compliesWithFinalize() const
{
    return compliesWith(m_app.finalizePolicy());
}


QString Patient::shortIdnumSummary() const
{
    QStringList details;
    for (int n = 1; n <= dbconst::NUMBER_OF_IDNUMS; ++n) {
        if (hasIdnum(n)) {
            details.append(QString("%1 %2")
                           .arg(m_app.idShortDescription(n))
                           .arg(idnumInteger(n)));
        }
    }
    if (details.isEmpty()) {
        return tr("[No ID numbers]");
    }
    return details.join(", ");
}


void Patient::updateQuestionnaireIndicators(const FieldRef* fieldref,
                                            const QObject* originator)
{
    qDebug() << Q_FUNC_INFO;
    Q_UNUSED(fieldref);
    Q_UNUSED(originator);
    if (!m_questionnaire) {
        return;
    }
    AttributesType attributes = policyAttributes();

    const bool tablet = TABLET_ID_POLICY.complies(attributes);
    m_questionnaire->setVisibleByTag(TAG_POLICY_APP_OK, tablet);
    m_questionnaire->setVisibleByTag(TAG_POLICY_APP_FAIL, !tablet);
    fieldRef(SURNAME_FIELD)->setMandatory(!tablet);
    fieldRef(FORENAME_FIELD)->setMandatory(!tablet);
    fieldRef(SEX_FIELD)->setMandatory(!tablet);
    fieldRef(DOB_FIELD)->setMandatory(!tablet);
    for (int n = 1; n <= dbconst::NUMBER_OF_IDNUMS; ++n) {
        fieldRef(IDNUM_FIELD_FORMAT.arg(n))->setMandatory(!tablet);
    }

    const bool upload = m_app.uploadPolicy().complies(attributes);
    m_questionnaire->setVisibleByTag(TAG_POLICY_UPLOAD_OK, upload);
    m_questionnaire->setVisibleByTag(TAG_POLICY_UPLOAD_FAIL, !upload);

    const bool finalize = m_app.finalizePolicy().complies(attributes);
    m_questionnaire->setVisibleByTag(TAG_POLICY_FINALIZE_OK, finalize);
    m_questionnaire->setVisibleByTag(TAG_POLICY_FINALIZE_FAIL, !finalize);

    bool id_ok = true;
    QStringList clashing_ids;
    for (int n = 1; n <= dbconst::NUMBER_OF_IDNUMS; ++n) {
        if (othersClashOnIdnum(n)) {
            clashing_ids.append(m_app.idShortDescription(n));
            id_ok = false;
        }
    }
    const QString idclash_text = id_ok
            ? "No clashes"
            : ("The following IDs clash: " + clashing_ids.join(", "));
    m_questionnaire->setVisibleByTag(TAG_IDCLASH_OK, id_ok);
    m_questionnaire->setVisibleByTag(TAG_IDCLASH_FAIL, !id_ok);
    QuElement* element = m_questionnaire->getFirstElementByTag(
                TAG_IDCLASH_DETAIL, false);
    QuText* textelement = dynamic_cast<QuText*>(element);
    if (textelement) {
        textelement->setText(idclash_text);
    }
}


bool Patient::othersClashOnIdnum(int which_idnum) const
{
    // Answers the question: do any other patients share the ID number whose
    // *index* (e.g. 0-7) is which_idnum?
    using dbfunc::delimit;
    if (which_idnum < 1 || which_idnum > dbconst::NUMBER_OF_IDNUMS) {
        uifunc::stopApp("Bug: Bad which_idnum to Patient::othersClashOnIdnum");
    }
    const QString id_fieldname = IDNUM_FIELD_FORMAT.arg(which_idnum);
    const QVariant idvar = idnumVariant(which_idnum);
    if (idvar.isNull()) {
        return false;
    }
    const qlonglong idnum = idnumInteger(which_idnum);
    const int patient_pk = id();
    const SqlArgs sqlargs(
        QString("SELECT COUNT(*) FROM %1 WHERE %2 = ? AND %3 <> ?")
            .arg(delimit(TABLENAME),
                 delimit(id_fieldname),
                 delimit(dbconst::PK_FIELDNAME)),
        ArgList{idnum, patient_pk}
    );
    const int c = m_db.fetchInt(sqlargs);
    return c > 0;
}


bool Patient::anyIdClash() const
{
    // With a single SQL statement, answers the question: "Are there any other
    // patients (that is, patients with a different PK) that share any ID
    // numbers with this patient)?"
    using dbfunc::delimit;
    ArgList args;
    QStringList idnum_criteria;
    for (int n = 1; n <= dbconst::NUMBER_OF_IDNUMS; ++n) {
        QVariant idvar = idnumVariant(n);
        if (idvar.isNull()) {
            continue;
        }
        QString id_fieldname = IDNUM_FIELD_FORMAT.arg(n);
        idnum_criteria.append(delimit(id_fieldname) + "=?");
        args.append(idvar);
    }
    if (idnum_criteria.isEmpty()) {  // no IDs that are not NULL
        return false;
    }
    args.append(id());
    const QString sql = QString("SELECT COUNT(*) FROM %1 WHERE (%2) AND %3 <> ?")
            .arg(delimit(TABLENAME),
                 idnum_criteria.join(" OR "),
                 delimit(dbconst::PK_FIELDNAME));
    const SqlArgs sqlargs(sql, args);
    const int c = m_db.fetchInt(sqlargs);
    return c > 0;
}


int Patient::numTasks() const
{
    int n = 0;
    const int patient_id = id();
    if (patient_id == dbconst::NONEXISTENT_PK) {
        return 0;
    }
    TaskFactory* factory = m_app.taskFactory();
    for (auto p_specimen : factory->allSpecimensExceptAnonymous()) {
        n += p_specimen->countForPatient(patient_id);  // copes with anonymous
    }
    return n;
}


void Patient::deleteFromDatabase()
{
    // Delete any associated tasks
    const int patient_id = id();
    if (patient_id == dbconst::NONEXISTENT_PK) {
        return;
    }
    DbNestableTransaction trans(m_db);
    TaskFactory* factory = m_app.taskFactory();
    for (auto p_task : factory->fetchAllForPatient(patient_id)) {
        p_task->deleteFromDatabase();
    }
    // Delete ourself
    DatabaseObject::deleteFromDatabase();
}


bool Patient::matchesForMerge(const Patient* other) const
{
    Q_ASSERT(other);
    auto sameOrOneNull = [this, &other](const QString& fieldname) -> bool {
        QVariant a = value(fieldname);
        QVariant b = other->value(fieldname);
        return a.isNull() || b.isNull() || a == b;
    };
    auto sameOrOneBlank = [this, &other](const QString& fieldname) -> bool {
        QString a = valueString(fieldname);
        QString b = other->valueString(fieldname);
        return a.isEmpty() || b.isEmpty() || a == b;
    };

    if (id() == other->id()) {
        qWarning() << Q_FUNC_INFO << "Asked to compare two patients with the "
                                     "same PK for merge! Bug.";
        return false;
    }
    // All ID numbers must match or be blank:
    for (int n = 1; n <= dbconst::NUMBER_OF_IDNUMS; ++n) {
        QString id_fieldname = IDNUM_FIELD_FORMAT.arg(n);
        if (!sameOrOneNull(id_fieldname)) {
            return false;
        }
    }
    // Forename, surname, DOB, sex must match or be blank:
    return sameOrOneBlank(FORENAME_FIELD) &&
            sameOrOneBlank(SURNAME_FIELD) &&
            sameOrOneNull(DOB_FIELD) &&
            sameOrOneBlank(SEX_FIELD) &&
            sameOrOneBlank(ADDRESS_FIELD) &&
            sameOrOneBlank(GP_FIELD) &&
            sameOrOneBlank(OTHER_FIELD);
}


void Patient::mergeInDetailsAndTakeTasksFrom(const Patient* other)
{
    DbNestableTransaction trans(m_db);

    const int this_pk = id();
    const int other_pk = other->id();

    // Copy information from other to this
    qInfo() << Q_FUNC_INFO << "Copying information from patient" << other_pk
            << "to patient" << this_pk;
    QStringList fields{
        FORENAME_FIELD,
        SURNAME_FIELD,
        DOB_FIELD,
        SEX_FIELD,
        ADDRESS_FIELD,
        GP_FIELD,
        OTHER_FIELD,
    };
    for (int n = 1; n <= dbconst::NUMBER_OF_IDNUMS; ++n) {
        fields.append(IDNUM_FIELD_FORMAT.arg(n));
    }
    for (const QString& fieldname : fields) {
        QVariant this_value = value(fieldname);
        QVariant other_value = other->value(fieldname);
        if (this_value.isNull() || (this_value.toString().isEmpty() &&
                                    !other_value.toString().isEmpty())) {
            setValue(fieldname, other_value);
        }
    }
    save();

    // Move tasks from other to this
    qInfo() << Q_FUNC_INFO << "Moving tasks from patient" << other_pk
            << "to patient" << this_pk;
    TaskFactory* factory = m_app.taskFactory();
    for (TaskPtr p_task : factory->fetchAllForPatient(other_pk)) {
        p_task->moveToPatient(this_pk);
        p_task->save();
    }

    qInfo() << Q_FUNC_INFO << "Move complete";
}


QString Patient::descriptionForMerge() const
{
    return QString("<b>%1</b><br>%2<br>%3").arg(surnameUpperForename(),
                                                ageSexDob(),
                                                shortIdnumSummary());
}


QString Patient::forenameSurname() const
{
    return QString("%1 %2").arg(forename(), surname());
}


QString Patient::surnameUpperForename() const
{
    return QString("%1, %2").arg(surname().toUpper(), forename());
}


QString Patient::sexAgeDob() const
{
    return QString("%1, %2y, DOB %3").arg(sex(),
                                          QString::number(ageYears()),
                                          dobText());
}


QString Patient::ageSexDob() const
{
    // "A 37-year-old woman..."
    return QString("%1, %2y, DOB %3").arg(sex(),
                                          QString::number(ageYears()),
                                          dobText());
}


QString Patient::twoLineDetailString() const
{
    return QString("%1 (%2)\n%3").arg(surnameUpperForename(),
                                      ageSexDob(),
                                      shortIdnumSummary());
}


QString Patient::oneLineHtmlDetailString() const
{
    return QString("<b>%1</b> (%2); %3").arg(surnameUpperForename(),
                                             ageSexDob(),
                                             shortIdnumSummary());
}
