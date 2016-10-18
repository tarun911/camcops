#include "commonoptions.h"

// ============================================================================
// Database-level constants
// ============================================================================

const QString CommonOptions::NO_CHAR = "N";
const QString CommonOptions::YES_CHAR = "Y";
const int CommonOptions::UNKNOWN_INT = -1;
const int CommonOptions::NO_INT = 0;
const int CommonOptions::YES_INT = 1;
const int CommonOptions::INCORRECT_INT = 0;
const int CommonOptions::CORRECT_INT = 1;


// ============================================================================
// Translatables
// ============================================================================

QString CommonOptions::yes()
{
    return tr("Yes");
}


QString CommonOptions::no()
{
    return tr("No");
}


QString CommonOptions::correct()
{
    return tr("Correct");
}


QString CommonOptions::incorrect()
{
    return tr("Incorrect");
}


QString CommonOptions::false_str()
{
    return tr("False");
}


QString CommonOptions::true_str()
{
    return tr("True");
}


QString CommonOptions::absent()
{
    return tr("Absent");
}


QString CommonOptions::present()
{
    return tr("Present");
}


QString CommonOptions::unknown()
{
    return tr("Unknown");
}


// ============================================================================
// Option sets
// ============================================================================

NameValueOptions CommonOptions::yesNoChar()
{
    return NameValueOptions{
        {yes(), YES_CHAR},
        {no(), NO_CHAR},
    };
}


NameValueOptions CommonOptions::yesNoBoolean()
{
    return NameValueOptions{
        {yes(), true},
        {no(), false},
    };
}


NameValueOptions CommonOptions::yesNoInteger()
{
    return NameValueOptions{
        {yes(), YES_INT},
        {no(), NO_INT},
    };
}


NameValueOptions CommonOptions::noYesChar()
{
    return NameValueOptions{
        {no(), NO_CHAR},
        {yes(), YES_CHAR},
    };
}


NameValueOptions CommonOptions::noYesBoolean()
{
    return NameValueOptions{
        {no(), false},
        {yes(), true},
    };
}


NameValueOptions CommonOptions::noYesInteger()
{
    return NameValueOptions{
        {no(), NO_INT},
        {yes(), YES_INT},
    };
}


NameValueOptions CommonOptions::incorrectCorrectBoolean()
{
    return NameValueOptions{
        {incorrect(), false},
        {correct(), true},
    };
}


NameValueOptions CommonOptions::incorrectCorrectInteger()
{
    return NameValueOptions{
        {incorrect(), INCORRECT_INT},
        {correct(), CORRECT_INT},
    };
}


NameValueOptions CommonOptions::falseTrueBoolean()
{
    return NameValueOptions{
        {false_str(), false},
        {true_str(), true},
    };
}


NameValueOptions CommonOptions::absentPresentBoolean()
{
    return NameValueOptions{
        {absent(), false},
        {present(), true},
    };
}


NameValueOptions CommonOptions::unknownNoYesInteger()
{
    return NameValueOptions{
        {unknown(), UNKNOWN_INT},
        {no(), NO_INT},
        {yes(), YES_INT},
    };
}