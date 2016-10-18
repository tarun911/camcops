#include "extrastring.h"

const QString EXTRASTRINGS_TABLENAME = "extrastrings";
const QString EXTRASTRINGS_TASK_FIELD = "task";
const QString EXTRASTRINGS_NAME_FIELD = "name";
const QString EXTRASTRINGS_VALUE_FIELD = "value";


// Specimen constructor:
ExtraString::ExtraString(const QSqlDatabase& db) :
    DatabaseObject(db, EXTRASTRINGS_TABLENAME)
{
    commonConstructor();
}


// String loading constructor:
ExtraString::ExtraString(const QSqlDatabase& db,
                         const QString& task,
                         const QString& name) :
    DatabaseObject(db, EXTRASTRINGS_TABLENAME)
{
    commonConstructor();
    if (!task.isEmpty() && !name.isEmpty()) {
        // Not a specimen; load, or set defaults and save
        WhereConditions where;
        where[EXTRASTRINGS_TASK_FIELD] = task;
        where[EXTRASTRINGS_NAME_FIELD] = name;
        m_exists = load(where);
    }
}


// String saving constructor:
ExtraString::ExtraString(const QSqlDatabase& db,
                         const QString& task,
                         const QString& name,
                         const QString& value) :
    DatabaseObject(db, EXTRASTRINGS_TABLENAME)
{
    commonConstructor();
    if (!task.isEmpty() && !name.isEmpty()) {
        // Not a specimen; load, or set defaults and save
        WhereConditions where;
        where[EXTRASTRINGS_TASK_FIELD] = task;
        where[EXTRASTRINGS_NAME_FIELD] = name;
        bool success = load(where);
        if (!success) {
            setValue(EXTRASTRINGS_TASK_FIELD, task);
            setValue(EXTRASTRINGS_NAME_FIELD, name);
            setValue(EXTRASTRINGS_VALUE_FIELD, value);
            save();
        }
        m_exists = true;
    }
}


void ExtraString::commonConstructor()
{
    // Define fields
    addField(EXTRASTRINGS_TASK_FIELD, QVariant::String, true, false, false);
    addField(EXTRASTRINGS_NAME_FIELD, QVariant::String, true, false, false);
    addField(EXTRASTRINGS_VALUE_FIELD, QVariant::String, false, false, false);

    m_exists = false;
}


ExtraString::~ExtraString()
{
}


QString ExtraString::value() const
{
    return valueString(EXTRASTRINGS_VALUE_FIELD);
}


bool ExtraString::exists() const
{
    return m_exists;
}


bool ExtraString::anyExist(const QString& task) const
{
    WhereConditions where;
    where[EXTRASTRINGS_TASK_FIELD] = task;
    return DbFunc::count(m_db, EXTRASTRINGS_TABLENAME, where) > 0;
}


void ExtraString::deleteAllExtraStrings()
{
    QString sql = QString("DELETE FROM %1").arg(EXTRASTRINGS_TABLENAME);
    DbFunc::exec(m_db, sql);
}