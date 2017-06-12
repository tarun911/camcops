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

#define DEBUG_STEP_DETAIL

#include "cardinalexpdetthreshold.h"
#include <QGraphicsScene>
#include <QPushButton>
#include <QTimer>
#include "common/uiconst.h"
#include "db/ancillaryfunc.h"
#include "db/dbtransaction.h"
#include "lib/ccrandom.h"
#include "lib/convert.h"
#include "lib/graphicsfunc.h"
#include "maths/mathfunc.h"
#include "questionnairelib/questionnaire.h"
#include "questionnairelib/questionnairefunc.h"
#include "questionnairelib/qulineeditdouble.h"
#include "questionnairelib/qulineeditinteger.h"
#include "questionnairelib/qumcq.h"
#include "questionnairelib/qupage.h"
#include "questionnairelib/qutext.h"
#include "tasklib/taskregistrar.h"
#include "taskxtra/cardinalexpdetcommon.h"
#include "taskxtra/cardinalexpdetthresholdtrial.h"
using cardinalexpdetcommon::AUDITORY_BACKGROUND;
using cardinalexpdetcommon::AUDITORY_CUES;
using cardinalexpdetcommon::AUDITORY_TARGETS;
using cardinalexpdetcommon::VISUAL_BACKGROUND;
using cardinalexpdetcommon::VISUAL_CUES;
using cardinalexpdetcommon::VISUAL_TARGETS;
using cardinalexpdetcommon::MODALITY_AUDITORY;
using cardinalexpdetcommon::MODALITY_VISUAL;
using cardinalexpdetcommon::TX_CONFIG_VISUAL_TARGET_DURATION_S;
using cardinalexpdetcommon::urlFromStem;
using ccrandom::coin;
using ccrandom::randomRealIncUpper;
using convert::msFromSec;
using graphicsfunc::ButtonAndProxy;
using graphicsfunc::makeTextButton;
using mathfunc::mean;


// ============================================================================
// Constants
// ============================================================================

const QString CardinalExpDetThreshold::CARDINALEXPDETTHRESHOLD_TABLENAME(
        "cardinal_expdetthreshold");

// Fieldnames: config
const QString FN_MODALITY("modality");
const QString FN_TARGET_NUMBER("target_number");
const QString FN_BACKGROUND_FILENAME("background_filename");
const QString FN_TARGET_FILENAME("target_filename");
const QString FN_VISUAL_TARGET_DURATION_S("visual_target_duration_s");
const QString FN_BACKGROUND_INTENSITY("background_intensity");
const QString FN_START_INTENSITY_MIN("start_intensity_min");
const QString FN_START_INTENSITY_MAX("start_intensity_max");
const QString FN_INITIAL_LARGE_INTENSITY_STEP("initial_large_intensity_step");
const QString FN_MAIN_SMALL_INTENSITY_STEP("main_small_intensity_step");
const QString FN_NUM_TRIALS_IN_MAIN_SEQUENCE("num_trials_in_main_sequence");
const QString FN_P_CATCH_TRIAL("p_catch_trial");
const QString FN_PROMPT("prompt");
const QString FN_ITI_S("iti_s");
// Fieldnames: results
const QString FN_FINISHED("finished");
const QString FN_INTERCEPT("intercept");
const QString FN_SLOPE("slope");
const QString FN_K("k");
const QString FN_THETA("theta");

// Text for user
const QString TX_CONFIG_TITLE("Configure ExpDetThreshold task");
const QString TX_CONFIG_MAIN_INSTRUCTIONS_1(
        "Set your device’s brightness and volume BEFORE running this task, "
        "and DO NOT ALTER THEM in between runs or before completing the main "
        "Expectation–Detection task. Also, try to keep the lighting and "
        "background noise constant throughout.");
const QString TX_CONFIG_MAIN_INSTRUCTIONS_2(
        "Before you run the Expectation–Detection task for a given subject, "
        "please run this task FOUR times to determine the subject’s threshold "
        "for each of two auditory stimuli (tone, voice) and each of two "
        "auditory stimuli (circle, word).");
const QString TX_CONFIG_MAIN_INSTRUCTIONS_3(
        "Then, make a note of the 75% (“x75”) threshold intensities for each "
        "stimulus, and start the Expectation–Detection task (which only needs "
        "to be run once). It will ask you for these four intensities.");
const QString TX_CONFIG_INSTRUCTIONS_1("Choose a modality:");
const QString TX_AUDITORY("Auditory");
const QString TX_VISUAL("Visual");
const QString TX_CONFIG_INSTRUCTIONS_2("Choose a target stimulus:");
const QString TX_AUDITORY_TARGET_0("tone (auditory target 0)");
const QString TX_AUDITORY_TARGET_0_SHORT("tone");
const QString TX_AUDITORY_TARGET_1("voice (auditory target 1)");
const QString TX_AUDITORY_TARGET_1_SHORT("voice");
const QString TX_VISUAL_TARGET_0("circle (visual target 0)");
const QString TX_VISUAL_TARGET_0_SHORT("circle");
const QString TX_VISUAL_TARGET_1("word (visual target 1)");
const QString TX_VISUAL_TARGET_1_SHORT("word");
const QString TX_CONFIG_INFO(
        "Intensities and probabilities are in the range 0–1.");
const QString TX_CONFIG_START_INTENSITY_MIN(
        "Minimum starting intensity (e.g. 0.9)");
const QString TX_CONFIG_START_INTENSITY_MAX(
        "Maximum starting intensity (e.g. 1.0)");
const QString TX_CONFIG_INITIAL_LARGE_INTENSITY_STEP(
        "Initial, large, intensity step (e.g. 0.1)");
const QString TX_CONFIG_MAIN_SMALL_INTENSITY_STEP(
        "Main, small, intensity step (e.g. 0.01)");
const QString TX_CONFIG_NUM_TRIALS_IN_MAIN_SEQUENCE(
        "Number of trials in the main test sequence (e.g. 14)");
const QString TX_CONFIG_P_CATCH_TRIAL(
        "Probability of a catch trial (e.g. 0.2)");
const QString TX_CONFIG_BACKGROUND_INTENSITY(
        "Background intensity (usually 1.0)");
const QString TX_CONFIG_ITI_S("Intertrial interval (s) (e.g. 0.2)");
const QString TX_DETECTION_Q_VISUAL("Did you see a");
const QString TX_DETECTION_Q_AUDITORY("Did you hear a");
const QString TX_START_PROMPT("When you’re ready, touch here to start.");

// Defaults
const qreal DEFAULT_VISUAL_TARGET_DURATION_S = 1.0;
const qreal DEFAULT_BACKGROUND_INTENSITY = 1.0;
const qreal DEFAULT_START_INTENSITY_MIN = 0.9;
const qreal DEFAULT_START_INTENSITY_MAX = 1.0;
const qreal DEFAULT_INITIAL_LARGE_INTENSITY_STEP = 0.1;
const qreal DEFAULT_MAIN_SMALL_INTENSITY_STEP = 0.01;
const int DEFAULT_NUM_TRIALS_IN_MAIN_SEQUENCE = 14;
const qreal DEFAULT_P_CATCH_TRIAL = 0.2;
const qreal DEFAULT_ITI_S = 0.2;

// Tags
const QString TAG_P2("p2");
const QString TAG_P3("p3");
const QString TAG_AUDITORY("a");
const QString TAG_VISUAL("v");
const QString TAG_WARNING_MIN_MAX("mm");

// Other
const int DP = 3;

// Graphics
const qreal SCENE_WIDTH = 1000;
const qreal SCENE_HEIGHT = 750;  // 4:3 aspect ratio
const QRectF SCENE_RECT(0, 0, SCENE_WIDTH, SCENE_HEIGHT);
const QColor SCENE_BACKGROUND("black");  // try: "salmon"
const int BORDER_WIDTH_PX = 3;
const QColor BUTTON_BACKGROUND("blue");
const QColor TEXT_COLOUR("white");
const QColor BUTTON_PRESSED_BACKGROUND("olive");
const QColor ABORT_BUTTON_BACKGROUND("darkred");
const qreal TEXT_SIZE_PX = 20;  // will be scaled
const int BUTTON_RADIUS = 5;
const int PADDING = 5;
const Qt::Alignment BUTTON_TEXT_ALIGN = Qt::AlignCenter;
const Qt::Alignment TEXT_ALIGN = Qt::AlignCenter;
const QColor EDGE_COLOUR("white");


// ============================================================================
// Factory method
// ============================================================================

void initializeCardinalExpDetThreshold(TaskFactory& factory)
{
    static TaskRegistrar<CardinalExpDetThreshold> registered(factory);
}


// ============================================================================
// CardinalExpectationDetection
// ============================================================================

CardinalExpDetThreshold::CardinalExpDetThreshold(
        CamcopsApp& app, const QSqlDatabase& db, int load_pk) :
    Task(app, db, CARDINALEXPDETTHRESHOLD_TABLENAME, false, false, false)  // ... anon, clin, resp
{
    // Config
    addField(FN_MODALITY, QVariant::Int);
    addField(FN_TARGET_NUMBER, QVariant::Int);
    addField(FN_BACKGROUND_FILENAME, QVariant::String);  // set automatically
    addField(FN_TARGET_FILENAME, QVariant::String);  // set automatically
    addField(FN_VISUAL_TARGET_DURATION_S, QVariant::Double);
    addField(FN_BACKGROUND_INTENSITY, QVariant::Double);
    addField(FN_START_INTENSITY_MIN, QVariant::Double);
    addField(FN_START_INTENSITY_MAX, QVariant::Double);
    addField(FN_INITIAL_LARGE_INTENSITY_STEP, QVariant::Double);
    addField(FN_MAIN_SMALL_INTENSITY_STEP, QVariant::Double);
    addField(FN_NUM_TRIALS_IN_MAIN_SEQUENCE, QVariant::Int);
    addField(FN_P_CATCH_TRIAL, QVariant::Double);
    addField(FN_PROMPT, QVariant::String);
    addField(FN_ITI_S, QVariant::Double);
    // Results
    addField(FN_FINISHED, QVariant::Bool);
    addField(FN_INTERCEPT, QVariant::Double);
    addField(FN_SLOPE, QVariant::Double);
    addField(FN_K, QVariant::Double);
    addField(FN_THETA, QVariant::Double);

    load(load_pk);

    if (load_pk == dbconst::NONEXISTENT_PK) {
        // Default values:
        setValue(FN_VISUAL_TARGET_DURATION_S, DEFAULT_VISUAL_TARGET_DURATION_S);
        setValue(FN_BACKGROUND_INTENSITY, DEFAULT_BACKGROUND_INTENSITY);
        setValue(FN_START_INTENSITY_MIN, DEFAULT_START_INTENSITY_MIN);
        setValue(FN_START_INTENSITY_MAX, DEFAULT_START_INTENSITY_MAX);
        setValue(FN_INITIAL_LARGE_INTENSITY_STEP, DEFAULT_INITIAL_LARGE_INTENSITY_STEP);
        setValue(FN_MAIN_SMALL_INTENSITY_STEP, DEFAULT_MAIN_SMALL_INTENSITY_STEP);
        setValue(FN_NUM_TRIALS_IN_MAIN_SEQUENCE, DEFAULT_NUM_TRIALS_IN_MAIN_SEQUENCE);
        setValue(FN_P_CATCH_TRIAL, DEFAULT_P_CATCH_TRIAL);
        setValue(FN_ITI_S, DEFAULT_ITI_S);
    }

    // Internal data
    m_player_background = QSharedPointer<QMediaPlayer>(new QMediaPlayer(),
                                                       &QObject::deleteLater);
    connect(m_player_background.data(), &QMediaPlayer::mediaStatusChanged,
            this, &CardinalExpDetThreshold::mediaStatusChangedBackground);
    m_player_target = QSharedPointer<QMediaPlayer>(new QMediaPlayer(),
                                                   &QObject::deleteLater);

    m_timer = QSharedPointer<QTimer>(new QTimer());
    m_timer->setSingleShot(true);

    m_current_trial = -1;
    m_current_trial_ignoring_catch_trials = -1;
    m_trial_last_y_b4_first_n = -1;
}


CardinalExpDetThreshold::~CardinalExpDetThreshold()
{
    // Necessary: for rationale, see QuAudioPlayer::~QuAudioPlayer()
    if (m_player_background) {
        m_player_background->stop();
    }
    if (m_player_target) {
        m_player_target->stop();
    }
}


// ============================================================================
// Class info
// ============================================================================

QString CardinalExpDetThreshold::shortname() const
{
    return "Cardinal_ExpDetThreshold";
}


QString CardinalExpDetThreshold::longname() const
{
    return tr("Cardinal RN — ExpDet-Threshold task");
}


QString CardinalExpDetThreshold::menusubtitle() const
{
    return tr("Rapid assessment of auditory/visual thresholds "
              "(for expectation–detection task)");
}


// ============================================================================
// Ancillary management
// ============================================================================

void CardinalExpDetThreshold::loadAllAncillary(int pk)
{
    OrderBy order_by{{CardinalExpDetThresholdTrial::FN_TRIAL, true}};
    ancillaryfunc::loadAncillary<CardinalExpDetThresholdTrial,
                                 CardinalExpDetThresholdTrialPtr>(
                m_trials, m_app, m_db,
                CardinalExpDetThresholdTrial::FN_FK_TO_TASK, order_by, pk);
}


QVector<DatabaseObjectPtr> CardinalExpDetThreshold::getAncillarySpecimens() const
{
    return QVector<DatabaseObjectPtr>{
        CardinalExpDetThresholdTrialPtr(new CardinalExpDetThresholdTrial(m_app, m_db)),
    };
}


QVector<DatabaseObjectPtr> CardinalExpDetThreshold::getAllAncillary() const
{
    QVector<DatabaseObjectPtr> ancillaries;
    for (auto trial : m_trials) {
        ancillaries.append(trial);
    }
    return ancillaries;
}


// ============================================================================
// Instance info
// ============================================================================

bool CardinalExpDetThreshold::isComplete() const
{
    return valueBool(FN_FINISHED);
}


QStringList CardinalExpDetThreshold::summary() const
{
    return QStringList{
        QString("Target: <b>%1</b>").arg(getTargetName()),
        QString("x75 = <b>%1</b>").arg(convert::prettyValue(x75(), DP)),
    };
}


QStringList CardinalExpDetThreshold::detail() const
{
    QStringList lines = completenessInfo() + recordSummaryLines();
    lines.append("\n");
    lines.append("Trials:");
    for (CardinalExpDetThresholdTrialPtr trial : m_trials) {
        lines.append(trial->recordSummaryCSVString());
    }
    return lines;
}


OpenableWidget* CardinalExpDetThreshold::editor(bool read_only)
{
    // ------------------------------------------------------------------------
    // OK to edit?
    // ------------------------------------------------------------------------
    if (read_only) {
        qWarning() << "Task not editable! Shouldn't have got here.";
        return nullptr;
    }

    // ------------------------------------------------------------------------
    // Configure the task using a Questionnaire
    // ------------------------------------------------------------------------

    NameValueOptions modality_options{
        {TX_AUDITORY, MODALITY_AUDITORY},
        {TX_VISUAL, MODALITY_VISUAL},
    };
    NameValueOptions target_options_auditory{
        {TX_AUDITORY_TARGET_0, 0},
        {TX_AUDITORY_TARGET_1, 1},
    };
    NameValueOptions target_options_visual{
        {TX_VISUAL_TARGET_0, 0},
        {TX_VISUAL_TARGET_1, 1},
    };

    // const int no_max = std::numeric_limits<int>::max();
    const QString warning_min_max(tr(
            "WARNING: cannot proceed: must satisfy "
            "min start intensity <= max start intensity"));

    auto text = [](const QString& t) -> QuElement* {
        return new QuText(t);
    };
    auto boldtext = [](const QString& t) -> QuElement* {
        return (new QuText(t))->setBold(true);
    };
    auto mcq = [this](const QString& fieldname,
                      const NameValueOptions& options) -> QuElement* {
        return new QuMcq(fieldRef(fieldname), options);
    };

    QuPagePtr page1((new QuPage{
        boldtext(TX_CONFIG_MAIN_INSTRUCTIONS_1),
        text(TX_CONFIG_MAIN_INSTRUCTIONS_2),
        text(TX_CONFIG_MAIN_INSTRUCTIONS_3),
        boldtext(TX_CONFIG_INSTRUCTIONS_1),
        mcq(FN_MODALITY, modality_options),
    })->setTitle(TX_CONFIG_TITLE + " (1)"));

    QuPagePtr page2((new QuPage{
        boldtext(TX_CONFIG_INSTRUCTIONS_2),
        mcq(FN_TARGET_NUMBER, target_options_auditory)->addTag(TAG_AUDITORY),
        mcq(FN_TARGET_NUMBER, target_options_visual)->addTag(TAG_VISUAL),
    })->setTitle(TX_CONFIG_TITLE + " (2)")->addTag(TAG_P2));

    const qreal zero = 0.0;
    const qreal one = 1.0;

    QuPagePtr page3((new QuPage{
        text(TX_CONFIG_INFO),
        questionnairefunc::defaultGridRawPointer({
            {TX_CONFIG_VISUAL_TARGET_DURATION_S,
             new QuLineEditDouble(fieldRef(FN_VISUAL_TARGET_DURATION_S), 0.1, 10.0)},
            {TX_CONFIG_BACKGROUND_INTENSITY,
             new QuLineEditDouble(fieldRef(FN_BACKGROUND_INTENSITY), zero, one)},
            {TX_CONFIG_START_INTENSITY_MIN,
             new QuLineEditDouble(fieldRef(FN_START_INTENSITY_MIN), zero, one)},
            {TX_CONFIG_START_INTENSITY_MAX,
             new QuLineEditDouble(fieldRef(FN_START_INTENSITY_MAX), zero, one)},
            {TX_CONFIG_INITIAL_LARGE_INTENSITY_STEP,
             new QuLineEditDouble(fieldRef(FN_INITIAL_LARGE_INTENSITY_STEP), zero, one)},
            {TX_CONFIG_MAIN_SMALL_INTENSITY_STEP,
             new QuLineEditDouble(fieldRef(FN_MAIN_SMALL_INTENSITY_STEP), zero, one)},
            {TX_CONFIG_NUM_TRIALS_IN_MAIN_SEQUENCE,
             new QuLineEditInteger(fieldRef(FN_NUM_TRIALS_IN_MAIN_SEQUENCE), 0, 100)},
            {TX_CONFIG_P_CATCH_TRIAL,
             new QuLineEditDouble(fieldRef(FN_P_CATCH_TRIAL), zero, one)},
            {TX_CONFIG_ITI_S,
             new QuLineEditDouble(fieldRef(FN_ITI_S), zero, 100.0)},
        }),
        (new QuText(warning_min_max))
                        ->setWarning(true)
                        ->addTag(TAG_WARNING_MIN_MAX),
    })->setTitle(TX_CONFIG_TITLE + " (3)")->addTag(TAG_P3));

    m_questionnaire = new Questionnaire(m_app, {page1, page2, page3});
    m_questionnaire->setType(QuPage::PageType::Clinician);
    m_questionnaire->setReadOnly(read_only);
    m_questionnaire->setWithinChain(true);  // fast forward button, not stop

    connect(fieldRef(FN_START_INTENSITY_MIN).data(), &FieldRef::valueChanged,
            this, &CardinalExpDetThreshold::validateQuestionnaire);
    connect(fieldRef(FN_START_INTENSITY_MAX).data(), &FieldRef::valueChanged,
            this, &CardinalExpDetThreshold::validateQuestionnaire);

    connect(m_questionnaire.data(), &Questionnaire::cancelled,
            this, &CardinalExpDetThreshold::abort);
    connect(m_questionnaire.data(), &Questionnaire::completed,
            this, &CardinalExpDetThreshold::startTask);
    // Because our main m_widget isn't itself a questionnaire, we need to hook
    // up these, too:
    questionnairefunc::connectQuestionnaireToTask(m_questionnaire.data(), this);

    validateQuestionnaire();

    // ------------------------------------------------------------------------
    // If the config questionnaire is successful, we'll launch the main task;
    // prepare this too.
    // ------------------------------------------------------------------------

    m_scene = new QGraphicsScene(SCENE_RECT);
    m_scene->setBackgroundBrush(QBrush(SCENE_BACKGROUND)); // *** not working
    m_graphics_widget = makeGraphicsWidget(m_scene, SCENE_BACKGROUND,
                                           true, true);
    connect(m_graphics_widget.data(), &OpenableWidget::aborting,
            this, &CardinalExpDetThreshold::abort);

    m_widget = new OpenableWidget();

    // We start off by seeing the questionnaire:
    m_widget->setWidgetAsOnlyContents(m_questionnaire, 0, false, false);

    return m_widget;
}


// ============================================================================
// Config questionnaire internals
// ============================================================================

void CardinalExpDetThreshold::validateQuestionnaire()
{
    if (!m_questionnaire) {
        return;
    }

    // 1. Validation
    QVector<QuPage*> pages = m_questionnaire->getPages(false, TAG_P3);
    Q_ASSERT(pages.size() == 1);
    QuPage* page3 = pages.at(0);
    bool duff_minmax = valueDouble(FN_START_INTENSITY_MAX) <
            valueDouble(FN_START_INTENSITY_MIN);
    m_questionnaire->setVisibleByTag(TAG_WARNING_MIN_MAX, duff_minmax,
                                     false, TAG_P3);
    page3->blockProgress(duff_minmax);

    // 2. Choice of target
    bool auditory = isAuditory();
    m_questionnaire->setVisibleByTag(TAG_AUDITORY, auditory, false, TAG_P2);
    m_questionnaire->setVisibleByTag(TAG_VISUAL, !auditory, false, TAG_P2);
}


// ============================================================================
// Connection macros
// ============================================================================

// MUST USE Qt::QueuedConnection - see comments in clearScene()
#define CONNECT_BUTTON(b, funcname) \
    connect(b.button, &QPushButton::clicked, \
            this, &CardinalExpDetThreshold::funcname, \
            Qt::QueuedConnection)
// To use a Qt::ConnectionType parameter with a functor, we need a context
// See http://doc.qt.io/qt-5/qobject.html#connect-5
// That's the reason for the extra "this":
#define CONNECT_BUTTON_PARAM(b, funcname, param) \
    connect(b.button, &QPushButton::clicked, \
            this, std::bind(&CardinalExpDetThreshold::funcname, this, param), \
            Qt::QueuedConnection)
// For debugging:
#define CONNECT_SVG_CLICKED(svg, funcname) \
    connect(svg.widget, &SvgWidgetClickable::clicked, \
            this, &CardinalExpDetThreshold::funcname, \
            Qt::QueuedConnection)
    // ... svg is an SvgItemAndRenderer
    // ... use "pressed" not "clicked" for rapid response detection.


// ============================================================================
// Calculation/assistance functions for main task
// ============================================================================

QString CardinalExpDetThreshold::getDescriptiveModality() const
{
    QVariant modality = value(FN_MODALITY);
    // can't use external constants in a switch statement
    if (modality.isNull()) {
        return textconst::UNKNOWN;
    } else if (modality.toInt() == MODALITY_AUDITORY) {
        return TX_AUDITORY;
    } else if (modality.toInt() == MODALITY_VISUAL) {
        return TX_VISUAL;
    }
    return textconst::UNKNOWN;
}


QString CardinalExpDetThreshold::getTargetName() const
{
    QVariant modality = value(FN_MODALITY);
    QVariant target_number = value(FN_TARGET_NUMBER);
    if (modality.isNull() || target_number.isNull()) {
        return textconst::UNKNOWN;
    }
    if (modality.toInt() == MODALITY_AUDITORY) {
        switch (target_number.toInt()) {
        case 0:
            return TX_AUDITORY_TARGET_0;
        case 1:
            return TX_AUDITORY_TARGET_1;
        }
    } else if (modality.toInt() == MODALITY_VISUAL) {
        switch (target_number.toInt()) {
        case 0:
            return TX_VISUAL_TARGET_0;
        case 1:
            return TX_VISUAL_TARGET_1;
        }
    }
    return textconst::UNKNOWN;
}


QVariant CardinalExpDetThreshold::x(qreal p) const
{
    if (valueIsNull(FN_INTERCEPT) || valueIsNull(FN_SLOPE)) {
        return QVariant();
    }
    qreal intercept = valueDouble(FN_INTERCEPT);
    qreal slope = valueDouble(FN_SLOPE);
    return mathfunc::logisticFindXWhereP(p, slope, intercept);
}


QVariant CardinalExpDetThreshold::x75() const
{
    return x(0.75);
}


bool CardinalExpDetThreshold::haveWeJustReset() const
{
    int last_trial = m_current_trial - 1;
    if (last_trial < 0 || last_trial >= m_trials.size()) {
        return false;
    }
    return m_trials.at(last_trial)->wasCaughtOutReset();
}


bool CardinalExpDetThreshold::inInitialStepPhase() const
{
    return m_trial_last_y_b4_first_n < 0;
}


bool CardinalExpDetThreshold::lastTrialWasFirstNo() const
{
    if (m_trial_last_y_b4_first_n < 0 || m_current_trial < 0) {
        return false;
    }
    return (
        m_trials.at(m_current_trial)->trialNumIgnoringCatchTrials() ==
            m_trials.at(m_trial_last_y_b4_first_n)->trialNumIgnoringCatchTrials()
                + 2
    );
}


int CardinalExpDetThreshold::getNBackNonCatchTrialIndex(int n, int start_index) const
{
    Q_ASSERT(start_index >= 0 && start_index < m_trials.size());
    int target = m_trials.at(start_index)->trialNumIgnoringCatchTrials() - n;
    for (int i = 0; i < m_trials.size(); ++i) {
        const CardinalExpDetThresholdTrialPtr& t = m_trials.at(i);
        if (t->targetPresented() && t->trialNumIgnoringCatchTrials() == target) {
            return i;
        }
    }
    return -1;
}


qreal CardinalExpDetThreshold::getIntensity() const
{
    Q_ASSERT(m_current_trial >= 0 && m_current_trial < m_trials.size());
    const qreal fail = -1.0;
    const CardinalExpDetThresholdTrialPtr& t = m_trials.at(m_current_trial);
    if (!t->targetPresented()) {
        return fail;
    }
    if (t->trialNum() == 0 || haveWeJustReset()) {
        // First trial, or we've just reset
        return randomRealIncUpper(valueDouble(FN_START_INTENSITY_MIN),
                                  valueDouble(FN_START_INTENSITY_MAX));
    }
    int one_back = getNBackNonCatchTrialIndex(1, m_current_trial);
    Q_ASSERT(one_back >= 0);
    const CardinalExpDetThresholdTrialPtr& prev = m_trials.at(one_back);
    if (inInitialStepPhase()) {
        return prev->intensity() - valueDouble(FN_INITIAL_LARGE_INTENSITY_STEP);
    }
    if (lastTrialWasFirstNo()) {
        int two_back = getNBackNonCatchTrialIndex(2, m_current_trial);
        Q_ASSERT(two_back >= 0);
        const CardinalExpDetThresholdTrialPtr& tb = m_trials.at(two_back);
        return mean(prev->intensity(), tb->intensity());
    }
    if (prev->yes()) {
        // In main phase. Detected stimulus last time; make it harder
        return prev->intensity() - valueDouble(FN_MAIN_SMALL_INTENSITY_STEP);
    }
    // In main phase. Didn't detect stimulus last time; make it easier
    return prev->intensity() + valueDouble(FN_MAIN_SMALL_INTENSITY_STEP);
}


bool CardinalExpDetThreshold::wantCatchTrial() const
{
    Q_ASSERT(m_current_trial < m_trials.size());
    if (m_current_trial <= 0) {
        return false;  // never on the first
    }
    if (m_trials.at(m_current_trial - 1)->wasCaughtOutReset()) {
        return false;  // never immediately after a reset
    }
    if (m_current_trial == 1) {
        return true;  // always on the second
    }
    if (m_trials.at(m_current_trial - 2)->wasCaughtOutReset()) {
        return true;  // always on the second of a fresh run
    }
    return coin(valueDouble(FN_P_CATCH_TRIAL));  // otherwise on e.g. 20% of trials
}


bool CardinalExpDetThreshold::isAuditory() const
{
    return valueInt(FN_MODALITY) == MODALITY_AUDITORY;
}


void CardinalExpDetThreshold::clearScene()
{
    m_scene->clear();
}


void CardinalExpDetThreshold::setTimeout(int time_ms, FuncPtr callback)
{
    m_timer->stop();
    m_timer->disconnect();
    connect(m_timer.data(), &QTimer::timeout,
            this, callback,
            Qt::QueuedConnection);
    m_timer->start(time_ms);
}


void CardinalExpDetThreshold::showVisualStimulus(int stimulus, qreal intensity)
{
    Q_UNUSED(stimulus);
    Q_UNUSED(intensity);
    // ***
}


void CardinalExpDetThreshold::reset()
{
    Q_ASSERT(m_current_trial >= 0 && m_current_trial < m_trials.size());
    m_trials.at(m_current_trial)->setCaughtOutReset();
    m_trial_last_y_b4_first_n = -1;
}


void CardinalExpDetThreshold::labelTrialsForAnalysis()
{
    DbTransaction trans(m_db);
    int tnum = 1;
    for (int i = 0; i < m_trials.size(); ++i) {
        const CardinalExpDetThresholdTrialPtr& t = m_trials.at(i);
        QVariant trial_num_in_seq;  // NULL
        if (i >= m_trial_last_y_b4_first_n && t->targetPresented()) {
            trial_num_in_seq = tnum++;
        }
        t->setTrialNumInCalcSeq(trial_num_in_seq);
    }
}


void CardinalExpDetThreshold::calculateFit()
{

}


// ============================================================================
// Main task internals
// ============================================================================

void CardinalExpDetThreshold::startTask()
{
#ifdef DEBUG_STEP_DETAIL
    qDebug() << Q_FUNC_INFO;
#endif
    m_widget->setWidgetAsOnlyContents(m_graphics_widget, 0, false, false);
    editStarted();  // will have been stopped by the end of the questionnaire?

    // Finalize the parameters
    bool auditory = isAuditory();
    if (auditory) {
        setValue(FN_BACKGROUND_FILENAME, AUDITORY_BACKGROUND);
        if (valueInt(FN_TARGET_NUMBER) == 0) {
            setValue(FN_TARGET_FILENAME, AUDITORY_TARGETS.at(0));
            setValue(FN_PROMPT, TX_DETECTION_Q_AUDITORY + " " + TX_AUDITORY_TARGET_0_SHORT + "?");
        } else {
            setValue(FN_TARGET_FILENAME, AUDITORY_TARGETS.at(1));
            setValue(FN_PROMPT, TX_DETECTION_Q_AUDITORY + " " + TX_AUDITORY_TARGET_1_SHORT + "?");
        }
    } else {
        setValue(FN_BACKGROUND_FILENAME, VISUAL_BACKGROUND);
        if (valueInt(FN_TARGET_NUMBER) == 0) {
            setValue(FN_TARGET_FILENAME, VISUAL_TARGETS.at(0));
            setValue(FN_PROMPT, TX_DETECTION_Q_VISUAL + " " + TX_VISUAL_TARGET_0_SHORT + "?");
        } else {
            setValue(FN_TARGET_FILENAME, VISUAL_TARGETS.at(1));
            setValue(FN_PROMPT, TX_DETECTION_Q_VISUAL + " " + TX_VISUAL_TARGET_1_SHORT + "?");
        }
    }

    // Double-check we have a PK before we create trials
    save();

    // Prep the sounds
    if (auditory) {
        m_player_background->setMedia(urlFromStem(
                                valueString(FN_BACKGROUND_FILENAME)));
        m_player_background->setVolume(mathfunc::proportionToIntPercent(
                                valueDouble(FN_BACKGROUND_INTENSITY)));
        m_player_target->setMedia(urlFromStem(
                                valueString(FN_TARGET_FILENAME)));
        // Volume will be set later.
    }

    // Start
#ifdef ARGH  // ***
    ButtonAndProxy start = makeTextButton(
                m_scene,
                QRectF(0.2 * SCENE_WIDTH, 0.6 * SCENE_HEIGHT,
                       0.6 * SCENE_WIDTH, 0.1 * SCENE_HEIGHT),
                BASE_BUTTON_CONFIG,
                TX_START);
    CONNECT_BUTTON(start, nextTrial);
#endif
}


void CardinalExpDetThreshold::nextTrial()
{

}


void CardinalExpDetThreshold::startTrial()
{
    ++m_current_trial;
#ifdef DEBUG_STEP_DETAIL
    qDebug() << Q_FUNC_INFO;
#endif

    // Determine if it's a catch trial (on which no stimulus is presented)
    bool want_catch = wantCatchTrial();
    bool present_target = !want_catch;
    if (!want_catch) {
        ++m_current_trial_ignoring_catch_trials;
    }
    QVariant trial_ignoring_catch_trials = want_catch
            ? QVariant()  // NULL
            : m_current_trial_ignoring_catch_trials;
    qreal intensity = qBound(0.0, getIntensity(), 1.0);
    // intensity is in the range [0, 1]

    // Create trial record
    CardinalExpDetThresholdTrialPtr tp(new CardinalExpDetThresholdTrial(
                                           pkvalueInt(),
                                           m_current_trial,
                                           trial_ignoring_catch_trials,
                                           present_target,
                                           intensity,
                                           m_app,
                                           m_db));
    m_trials.append(tp);
    qDebug() << tp->summary();

#ifdef ARGH  // ***

    // Display stimulus
    bool auditory = isAuditory();
    if (present_target) {
        if (auditory) {
            m_player_target->setVolume(
                        mathfunc::proportionToIntPercent(intensity));
            m_player_background->play();
            m_player_target->play();
        } else {
            // ***
            showVisualStimulus(tp.background_filename, tp.background_intensity);
            showVisualStimulus(tp.target_filename, tr.intensity);
        }
    } else {
        // Catch trial
        if (auditory) {
            m_player_background->play();
        } else {
            // ***
            showVisualStimulus(tp.background_filename, tp.background_intensity);
        }
    }

    // If auditory, the event will be driven by the end of the sound, via
    // mediaStatusChangedBackground().
    // Otherwise:
    if (!auditory) {
        int stimulus_time_ms = msFromSec(
                    valueDouble(FN_VISUAL_TARGET_DURATION_S));
        setTimeout(stimulus_time_ms, &CardinalExpDetThreshold::offerChoice);
    }
#endif
}


void CardinalExpDetThreshold::mediaStatusChangedBackground(
        QMediaPlayer::MediaStatus status)
{
    if (status == QMediaPlayer::EndOfMedia) {
#ifdef DEBUG_STEP_DETAIL
        qDebug() << "Backgroud sound playback finished";
#endif
        m_player_target->stop();  // in case it's still playing
        offerChoice();
    }
}


void CardinalExpDetThreshold::offerChoice()
{
    Q_ASSERT(m_current_trial >= 0 && m_current_trial < m_trials.size());
    CardinalExpDetThresholdTrial& t = *m_trials.at(m_current_trial);

    // ***

    t.recordChoiceTime();
}


void CardinalExpDetThreshold::recordChoice(bool yes)
{
    Q_ASSERT(m_current_trial >= 0 && m_current_trial < m_trials.size());
    CardinalExpDetThresholdTrial& t = *m_trials.at(m_current_trial);
    t.recordResponse(yes);
    if (!t.targetPresented() && yes) {
        // Caught out... reset.
        reset();
    } else if (m_current_trial == 0 && !yes) {
        // No on first trial -- treat as reset
        reset();
    } else if (t.targetPresented() && !yes && m_trial_last_y_b4_first_n < 0) {
        // First no
        m_trial_last_y_b4_first_n = getNBackNonCatchTrialIndex(1, m_current_trial);
        qDebug() << "First no response: m_trial_last_y_b4_first_n ="
                 << m_trial_last_y_b4_first_n;
    }
    clearScene();
    setTimeout(msFromSec(valueDouble(FN_ITI_S)),
               &CardinalExpDetThreshold::nextTrial);
}


void CardinalExpDetThreshold::thanks()
{

}


void CardinalExpDetThreshold::abort()
{
#ifdef DEBUG_STEP_DETAIL
    qDebug() << Q_FUNC_INFO;
#endif
    setValue(FN_FINISHED, false);
    Q_ASSERT(m_widget);
    editFinishedAbort();
    emit m_widget->finished();
}


void CardinalExpDetThreshold::finish()
{
#ifdef DEBUG_STEP_DETAIL
    qDebug() << Q_FUNC_INFO;
#endif
    setValue(FN_FINISHED, true);
    Q_ASSERT(m_widget);
    editFinishedProperly();
    emit m_widget->finished();
}