#pragma once
#include <functional>
#include <QDate>
#include <QDateTime>
#include <QObject>
#include <QSharedPointer>
#include "field.h"
#include "databaseobject.h"

class Blob;
class QImage;


class FieldRef : public QObject
{
    /*

If a FieldRef didn't do signals, one would think:

- Copy these things by value. They're small.
- Don't use references; the owning function is likely to have finished
  and made the reference become invalid.
- Don't bother with pointers; they have pointers within them anyway.
- The only prerequisite is that the things they point to outlast the
  lifetime of this object.

However, it'd be helpful if they could do signals.
- In which case, they should be a QObject.
- In which case, you can't copy them.
- In which case, they should be managed by pointer.
- In which case, they should be managed by a QSharedPointer.

The FieldRef manages various kinds of indirection:
- Field: direct connection to a Field object
- DatabaseObject: connection to a Field object belonging to a DatabaseObject
- DatabaseObjectBlobField: connection to (a) a field in the DatabaseObject that
  stores the PK of a BLOB record, and (b) a record in the BLOB table that
  stores the actual blob, and references back to the table/PK/field of the
  DatabaseObject in question.
- Functions: getter/setter functions, to allow the use e.g. of Questionnaires
  (which use FieldRefs) together with arbitrary C++ objects, e.g. for setting
  StoredVar objects.

    */
    Q_OBJECT
public:
    enum class FieldRefMethod {
        Invalid,
        Field,
        DatabaseObject,
        DatabaseObjectBlobField,
        Functions,
    };
    using GetterFunction = std::function<const QVariant&()>;
    using SetterFunction = std::function<bool(const QVariant&)>;  // returns: changed?
public:
    FieldRef();
    FieldRef(Field* p_field, bool mandatory);
    FieldRef(DatabaseObject* p_dbobject, const QString& fieldname,
             bool mandatory, bool autosave = true, bool blob = false);
    FieldRef(const GetterFunction& getterfunc,
             const SetterFunction& setterfunc,
             bool mandatory);
    bool valid() const;
    void setValue(const QVariant& value, const QObject* originator = nullptr);
    // ... originator is optional and used as a performance hint (see QSlider)
    void setValue(const QImage& image, const QObject* originator = nullptr);
    // ... convenience method for QImage

    QVariant value() const;
    bool valueBool() const;
    int valueInt() const;
    qlonglong valueLongLong() const;
    double valueDouble() const;
    QDateTime valueDateTime() const;
    QDate valueDate() const;
    QString valueString() const;
    QByteArray valueByteArray() const;
    bool isNull() const;

    bool mandatory() const;
    void setMandatory(bool mandatory, const QObject* originator = nullptr);
    // ... originator is optional and used as a performance hint (see QSlider)
    bool complete() const;  // not null?
    bool missingInput() const;  // block progress because (mandatory() && !complete())?
protected:
    void commonConstructor();

signals:
    void valueChanged(const FieldRef* fieldref,
                      const QObject* originator) const;
    void mandatoryChanged(const FieldRef* fieldref,
                          const QObject* originator) const;
    // You should NOT cause a valueChanged() signal to be emitted whilst in a
    // mandatoryChanged() signal, but it's fine to emit mandatoryChanged()
    // signals (typically on other fields) whilst processing valueChanged()
    // signals.

protected:
    FieldRefMethod m_method;
    bool m_mandatory;

    Field* m_p_field;

    DatabaseObject* m_p_dbobject;
    QString m_fieldname;
    bool m_autosave;

    bool m_blob_redirect;
    QSharedPointer<Blob> m_blob;

    GetterFunction m_getterfunc;
    SetterFunction m_setterfunc;
};


using FieldRefPtr = QSharedPointer<FieldRef>;
using FieldRefPtrList = QList<FieldRefPtr>;
