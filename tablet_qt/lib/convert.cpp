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

#include "convert.h"
#include <QBuffer>
#include <QByteArray>
#include <QChar>
#include <QDate>
#include <QDateTime>
#include <QDebug>
#include <QImage>
#include <QRegularExpression>
#include <QtMath>
#include <QUrl>
#include "lib/datetimefunc.h"
#include "lib/uifunc.h"

const QChar COMMA = ',';
const QChar SQUOTE = '\'';  // single quote

const QString RECORD_RE_STR("^([\\S]+?):\\s*([\\s\\S]*)");
// double-backslashes for C++ escaping
// \s whitespace, \S non-whitespace
// ? makes the + lazy, not greedy
// ... thus: (lazy-non-whitespace) : whitespace (anything)
const QRegularExpression RECORD_RE(RECORD_RE_STR);


QString Convert::escapeNewlines(QString raw)
{
    // Raw string literal, from C++ 11 (note the parentheses):
    // http://en.cppreference.com/w/cpp/language/string_literal
    raw.replace(R"(\)", R"(\\)");
    raw.replace("\n", R"(\n)");
    raw.replace("\r", R"(\r)");
    return raw;
}


QString Convert::unescapeNewlines(QString escaped)
{
    if (escaped.isEmpty()) {
        return escaped;
    }
    QString result;
    bool in_escape = false;
    int n = escaped.length();
    for (int i = 0; i < n; ++i) {
        QChar c = escaped.at(i);
        if (in_escape) {
            // Can't use switch statement with a QChar
            if (c == 'r') {
                result += "\r";
            } else if (c == 'n') {
                result += "\n";
            } else {
                result += c;
            }
            in_escape = false;
        } else {
            if (c == SQUOTE) {
                in_escape = true;
            } else {
                result += c;
            }
        }
    }
    return result;
}


QString Convert::sqlQuoteString(QString raw)
{
    // In: my name's Bob
    // Out: 'my name''s Bob'
    raw.replace("'", "''");
    return QString("'%1'").arg(raw);
}


QString Convert::sqlDequoteString(const QString& quoted)
{
    // In: 'my name''s Bob'
    // Out: my name's Bob

    // Strip off outside quotes:
    int n = quoted.length();
    if (n < 2 || quoted.at(0) != SQUOTE || quoted.at(n - 1) != SQUOTE) {
        // Wrong format
        return QString();
    }
    QString raw = quoted.mid(1, n - 2);
    // De-escape quotes:
    raw.replace("''", "'");
    return raw;
}


QString Convert::blobToQuotedBase64(const QByteArray& blob)
{
    // Returns in the format: 64'...'
    return QString("64'%1'").arg(QString(blob.toBase64()));
}


QByteArray Convert::quotedBase64ToBlob(const QString& quoted)
{
    // Reverses blobToQuotedBase64()
    int n = quoted.length();
    if (n < 4 || !quoted.startsWith("64'") || !quoted.endsWith(SQUOTE)) {
        // Wrong format
        return QByteArray();
    }
    QString b64data = quoted.mid(3, n - 4);
    return QByteArray::fromBase64(b64data.toLocal8Bit());
}


QString Convert::padHexTwo(const QString& input)
{
    return input.length() == 1 ? QString("0") + input : input;
}


QString Convert::blobToQuotedHex(const QByteArray& blob)
{
    // Returns in the format: X'01FF76A8'
    // Since Qt is magic:
    return QString("X'%1'").arg(QString(blob.toHex()));
}


QByteArray Convert::quotedHexToBlob(const QString& hex)
{
    // Reverses blobToQuotedHex()
    int n = hex.length();
    if (n < 3 || !hex.startsWith("X'") || !hex.endsWith(SQUOTE)) {
        // Wrong format
        return QByteArray();
    }
    QString hexdata = hex.mid(2, n - 3);
    return QByteArray::fromHex(hexdata.toLocal8Bit());
}


QString Convert::toSqlLiteral(const QVariant& value)
{
    if (value.isNull()) {
        return "NULL";
    }
    switch (value.type()) {
    // Integer types
    case QVariant::Int:
        return QString("%1").arg(value.toInt());
    case QVariant::UInt:
        return QString("%1").arg(value.toUInt());
    case QVariant::LongLong:
        return QString("%1").arg(value.toLongLong());
    case QVariant::ULongLong:
        return QString("%1").arg(value.toULongLong());

    // Boolean
    case QVariant::Bool:
        return QString("%1").arg(value.toInt());  // boolean to integer

    // Floating-point:
    case QVariant::Double:
        return QString("%1").arg(value.toDouble());

    // String
    case QVariant::String:
    case QVariant::Char:
        return sqlQuoteString(escapeNewlines(value.toString()));

    // Dates, times
    case QVariant::Date:
        return value.toDate().toString("'yyyy-MM-dd'");
    case QVariant::Time:
        return value.toTime().toString("'HH:mm:ss'");
    case QVariant::DateTime:
        return QString("'%1'").arg(DateTime::datetimeToIsoMs(value.toDateTime()));

    // BLOB types
    case QVariant::ByteArray:
        // Base 64 is more efficient for network transmission than hex.
        return blobToQuotedBase64(value.toByteArray());

    default:
        UiFunc::stopApp("Convert::toSqlLiteral: Unknown field type: " +
                        value.type());
        // We'll never get here, but to stop compilers complaining:
        return "NULL";
    }
}


QVariant Convert::fromSqlLiteral(const QString& literal)
{
    if (literal.isEmpty() ||
            literal.compare("NULL", Qt::CaseInsensitive) == 0) {
        // NULL
        return QVariant();
    }

    int n = literal.length();

    if (n >= 4 && literal.startsWith("64'") && literal.endsWith(SQUOTE)) {
        // Base 64-encoded BLOB
        // Waste of time doing a more sophisticated (e.g. regex) check. If it
        // passes this test, it's *claiming* to be a base-64 BLOB, and we're
        // not going to decode it as anything else, even if it's duff.
        return quotedBase64ToBlob(literal);
    }

    if (n >= 3 && literal.startsWith("X'") && literal.endsWith(SQUOTE)) {
        // Hex-encoded BLOB
        return quotedHexToBlob(literal);
    }

    if (n >= 2 && literal.startsWith(SQUOTE) && literal.endsWith(SQUOTE)) {
        // String, date, or time... we will let autoconversion take care of
        // dates/times given as sensible string literals.
        return unescapeNewlines(sqlDequoteString(literal));
    }

    // Numeric
    if (literal.contains(".")) {
        return literal.toDouble();
    }

    return literal.toInt();
}


QList<QVariant> Convert::csvSqlLiteralsToValues(const QString& csv)
{
    // In: 34, NULL, 'a string''s test, with commas', X'0FB2AA', 64'c3VyZS4='
    // Out: split by commas, dealing with quotes appropriately
    QList<QVariant> values;
    int n = csv.length();
    bool in_quotes = false;
    int startpos = 0;
    int pos = 0;
    while (pos < n) {
        QChar at_pos = csv.at(pos);
        if (!in_quotes) {
            if (at_pos == COMMA) {
                // end of chunk
                QString chunk = csv.mid(startpos, pos - startpos).trimmed();
                // ... will not include csv[pos]
                startpos = pos + 1;  // one beyond the comma

                // ------------------------------------------------------------
                // SQL literal processing here: more memory-efficient (e.g.
                // with BLOBs) to process here rather than returning large
                // string intermediates unnecessarily to a calling function
                // that does the next step.
                // ------------------------------------------------------------
                values.append(fromSqlLiteral(chunk));

            } else if (at_pos == SQUOTE) {
                // start of quote
                in_quotes = true;
            }

        } else {
            if (at_pos == SQUOTE && pos < n - 1 && csv.at(pos + 1) == SQUOTE) {
                // double quote, '', is an escaped quote, not end of quote
                pos += 1;  // skip one more than we otherwise would
            } else if (at_pos == SQUOTE) {
                // end of quote
                in_quotes = false;
            }
        }

        pos += 1;
    }
    // Last chunk
    QString chunk = csv.mid(startpos, n - startpos).trimmed();
    // ------------------------------------------------------------------------
    // More SQL literal processing here
    // ------------------------------------------------------------------------
    values.append(fromSqlLiteral(chunk));
    return values;
}


QString Convert::valuesToCsvSqlLiterals(const QList<QVariant>& values)
{
    QStringList literals;
    for (auto value : values) {
        literals.append(toSqlLiteral(value));
    }
    return literals.join(',');
}


QByteArray Convert::imageToByteArray(const QImage& image,
                                     const char* format)
{
    // I thought passing a QImage to a QVariant-accepting function would lead
    // to autoconversion via
    //     http://doc.qt.io/qt-5/qimage.html#operator-QVariant
    // ... but it doesn't.
    // So: http://stackoverflow.com/questions/27343576
    QByteArray arr;
    QBuffer buffer(&arr);
    buffer.open(QIODevice::WriteOnly);
    image.save(&buffer, format);
    return arr;
}


QVariant Convert::imageToVariant(const QImage& image,
                                 const char* format)
{
    return QVariant(imageToByteArray(image, format));
}


QImage Convert::byteArrayToImage(const QByteArray& array, const char* format)
{
    QImage image;
    image.loadFromData(array, format);
    return image;
}


QByteArray Convert::base64ToBytes(const QString& data_b64)
{
    return QByteArray::fromBase64(data_b64.toLocal8Bit());
}


SecureQByteArray Convert::base64ToSecureBytes(const QString& data_b64)
{
    return SecureQByteArray::fromBase64(data_b64.toLocal8Bit());
}


QString Convert::prettyValue(const QVariant& variant, QVariant::Type type)
{
    if (variant.isNull()) {
        return "NULL";
    }
    switch (type) {
    case QVariant::ByteArray:
        return "<binary>";
    case QVariant::String:
        return variant.toString().toHtmlEscaped();
    default:
        return variant.toString();
    }
}


QString Convert::prettyValue(const QVariant& variant)
{
    return prettyValue(variant, variant.type());
}


const QStringList PREFIXES_SHORT_BINARY{"", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi"};
const QStringList PREFIXES_LONG_BINARY{"", "kibi", "mebi", "gibi", "tebi", "peti", "exbi", "zebi", "yobi"};
const QStringList PREFIXES_SHORT_DECIMAL{"", "k", "M", "G", "T", "P", "E", "Z", "Y"};
const QStringList PREFIXES_LONG_DECIMAL{"", "kilo", "mega", "giga", "tera", "peta", "exa", "zetta", "yotta"};


QString Convert::prettySize(double num, bool space, bool binary, bool longform,
                            const QString& suffix)
{
    // http://stackoverflow.com/questions/3758606/how-to-convert-byte-size-into-human-readable-format-in-java
    const QStringList& prefixes = binary
            ? (longform ? PREFIXES_LONG_BINARY : PREFIXES_SHORT_BINARY)
            : (longform ? PREFIXES_LONG_DECIMAL : PREFIXES_SHORT_DECIMAL);
    QString optional_space = space ? " " : "";
    double base = binary ? 1024 : 1000;
    int exponent = (int)(qLn(num) / qLn(base));
    exponent = qBound(0, exponent, prefixes.length() - 1);
    QString prefix = prefixes.at(exponent);
    double converted_num = num / pow(base, exponent);
    int precision = (exponent == 0) ? 0 : 1;  // decimals, for 'f'
    return QString("%1%2%3%4")
            .arg(converted_num, 0, 'f', precision)
            .arg(optional_space)
            .arg(prefix)
            .arg(suffix);
}


QString Convert::prettyPointer(const void* pointer)
{
    // http://stackoverflow.com/questions/8881923/how-to-convert-a-pointer-value-to-qstring
    return QString("0x%1").arg((quintptr)pointer,
                               QT_POINTER_SIZE * 2, 16, QChar('0'));
}


QMap<QString, QString> Convert::getReplyDict(const QByteArray& data)
{
    // For server replies looking like key1:value1\nkey2:value2 ...
    QList<QByteArray> lines = data.split('\n');
    QMap<QString, QString> dict;
    for (auto line : lines) {
        QRegularExpressionMatch match = RECORD_RE.match(line);
        if (match.hasMatch()) {
            QString key = match.captured(1);
            QString value = match.captured(2);
            dict[key] = value;
        }
    }
    return dict;
}


QUrlQuery Convert::getPostDataAsUrlQuery(const QMap<QString, QString>& dict)
{
    // http://stackoverflow.com/questions/2599423/how-can-i-post-data-to-a-url-using-qnetworkaccessmanager

    // We had a difficulty here in that semicolons were not being encoded.
    // This thread describes the problem (not a Qt bug; matches relevant RFC):
    // - https://bugreports.qt.io/browse/QTBUG-50843
    // Note in particular Thiago Maciera's comment that "QUrlQuery manages a
    // list of key-value pairs of *encoded* strings."

    QUrlQuery postdata;
    QMapIterator<QString, QString> it(dict);
    while (it.hasNext()) {
        it.next();
        postdata.addQueryItem(QUrl::toPercentEncoding(it.key()),
                              QUrl::toPercentEncoding(it.value()));
    }
    return postdata;
}
