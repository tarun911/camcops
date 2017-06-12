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

/*

[1] https://github.com/wepe/MachineLearning/tree/master/logistic%20regression/use_cpp_and_eigen
    ... gives WRONG ANSWERS
[2] https://en.wikipedia.org/wiki/Cross_entropy#Cross-entropy_error_function_and_logistic_regression
[3] https://eigen.tuxfamily.org/dox/group__QuickRefPage.html#title2
[4] https://stackoverflow.com/questions/19824293/regularized-logistic-regression-code-in-matlab
[5] http://www.cs.cmu.edu/~ggordon/IRLS-example/
[6] https://stats.stackexchange.com/questions/166958/multinomial-logistic-loss-vs-cross-entropy-vs-square-error
[7] http://eli.thegreenplace.net/2016/logistic-regression/
[8] http://blog.smellthedata.com/2009/06/python-logistic-regression-with-l2.html
[9] https://github.com/PatWie/CppNumericalSolvers
[10] https://bwlewis.github.io/GLM/  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    - Best algorithmic introduction to GLMs
[11] https://en.wikipedia.org/wiki/Generalized_linear_model#Model_components
[12] http://web.as.uky.edu/statistics/users/pbreheny/760/S13/notes/2-19.pdf

-------------------------------------------------------------------------------
First, a general linear model
-------------------------------------------------------------------------------
- Cardinal & Aitken 2006, p379 onwards.

Matrix notation: as per standard:
    - define matrix(nrows, ncols)
    - address element as m(row, col)

For a single dependent variable:
    n   number of observations
    k   number of predictors (including intercept)

    Y   dependent variable(s), vector (n * 1)
    X   design matrix (predictors), matrix (n * k)
    b   coefficients/parameters, vector (k * 1)
    e   error, vector (n * 1)
        ... expected to be normally distributed: e ~ N(mean, SD)

Then a general linear model is

    Y = Xb + e

... for which we solve for b.

A generalized linear model extends this with a link function [11]:
    eta = Xb                        // linear predictor
    E(Y) = mu = invlink(eta)

i.e.

    Y = invlink(Xb + e)             // or Y = invlink(Xb) + e?  In any case, Y_predicted = invlink(Xb)
    link(Y) = Xb + e
    g(Y) = Xb + e                   // the link function is called g()

... so in Wikipedia notation,

    Xb = g(mu) = g(Y)

For logistic regression, then:

    Y = logistic(Xb + e)            // logistic is the INVERSE link function
    logit(Y) = Xb + e               // logit (= inverse logistic) is the link fn

*/

#include "glm.h"
#include <algorithm>
#include <QDebug>
#include "maths/eigenfunc.h"
#include "maths/mathfunc.h"
#include "maths/statsfunc.h"
using namespace Eigen;

// Eigen's cross() requires specific dimensions, that must be known at
// compile-time, or you get THIS_METHOD_IS_ONLY_FOR_VECTORS_OF_A_SPECIFIC_SIZE.
// - https://stackoverflow.com/questions/43283444/row-wise-cross-product-eigen
// - http://eigen.tuxfamily.org/bz/show_bug.cgi?id=1037
// A more general cross-product (after R's ?crossprod) is t(x) %*% y.
// However, this doesn't work as a template because Eigen produces objects of
// intermediate type, like Eigen::Product<...>, so let's just use the
// preprocessor, being careful with brackets:
#define CROSSPROD(x, y) ((x).matrix().transpose() * (y).matrix())

// Also helpful to have an svd() macro to match R's.
#define svd(x) ((x).jacobiSvd(ComputeThinU | ComputeThinV))


// ============================================================================
// Constructor
// ============================================================================

Glm::Glm(LinkFunctionFamily link_fn_family,
         SolveMethod solve_method,
         int max_iterations,
         double tolerance,
         RankDeficiencyMethod rank_deficiency_method) :
    m_link_fn_family(link_fn_family),
    m_solve_method(solve_method),
    m_max_iterations(max_iterations),
    m_tolerance(tolerance),
    m_rank_deficiency_method(rank_deficiency_method)
{
    reset();
}


// ============================================================================
// Internals
// ============================================================================

void Glm::reset()
{
    m_dependent_variable = VectorXd();
    m_predictors = MatrixXd();
    m_p_weights = nullptr;

    m_fitted = false;
    m_converged = false;
    m_n_iterations = 0;
    m_calculation_errors.clear();
    m_coefficients = VectorXd();
}


void Glm::warnReturningGarbage() const
{
    QString not_fitted("Not fitted! Returning garbage.");
    qWarning() << not_fitted;
    addError(not_fitted);
}


void Glm::addInfo(const QString &msg) const
{
    m_info.append(msg);
}


void Glm::addError(const QString &msg) const
{
    m_calculation_errors.append(msg);
}


// ============================================================================
// Fit method
// ============================================================================

void Glm::fit(const MatrixXd& predictors,
              const VectorXd& depvar,
              VectorXd* p_weights)
{
    reset();

    // Set up data
    m_predictors = predictors;
    m_dependent_variable = depvar;
    m_p_weights = p_weights;

    // Validate input
    bool ok = true;
    const int n_predictors = nPredictors();
    const int n_observations = nObservations();
    addInfo(QString("Number of observations: %1").arg(n_observations));
    addInfo(QString("Number of predictors: %1").arg(n_predictors));
    if (m_predictors.rows() != n_observations) {  // n
        addError(QString(
                "Mismatch: 'predictors' has %1 rows but 'dependent_variable' "
                "has %2 rows; should match (and be: number of observations)!"
            ).arg(m_predictors.rows()).arg(n_observations));
        ok = false;
    }
    if (m_p_weights && m_p_weights->rows() != n_predictors) {
        addError(QString(
                "Mismatch: '*p_weights' has %1 rows but 'predictors' "
                "has %2 columns; should match (and be: number of predictors)!"
            ).arg(m_p_weights->rows()).arg(n_predictors));
        ok = false;
    }

    // Perform fit
    if (ok) {
        switch (m_solve_method) {
        case SolveMethod::IRLS:
            fitIRLS();
            break;
        case SolveMethod::IRLS_SVD_Newton:
            fitIRLSSVDNewton();
            break;
        default:
            addError("Unknown solve method!");
            break;
        }
    }

    // Report any errors
    if (!m_calculation_errors.isEmpty()) {
        qWarning() << "Errors occurred during GLM fit:";
        for (auto error : m_calculation_errors) {
            qWarning() << "-" << error;
        }
    }
}


// ============================================================================
// Re-retrieve config
// ============================================================================

LinkFunctionFamily Glm::getLinkFunctionFamily() const
{
    return m_link_fn_family;
}


Glm::SolveMethod Glm::getSolveMethod() const
{
    return m_solve_method;
}


int Glm::getMaxIterations() const
{
    return m_max_iterations;
}


double Glm::getTolerance() const
{
    return m_tolerance;
}


Glm::RankDeficiencyMethod Glm::getRankDeficiencyMethod() const
{
    return m_rank_deficiency_method;
}


// ============================================================================
// Re-retrieve input
// ============================================================================

VectorXd Glm::getDependentVariable() const
{
    return m_dependent_variable;
}


MatrixXd Glm::getPredictors() const
{
    return m_predictors;
}


Eigen::VectorXd* Glm::getWeightsPointer() const
{
    return m_p_weights;
}


int Glm::nObservations() const
{
    return m_dependent_variable.rows();
}


int Glm::nPredictors() const
{
    return m_predictors.cols();
}


// ============================================================================
// Get output
// ============================================================================

bool Glm::fitted() const
{
    return m_fitted;
}


bool Glm::converged() const
{
    return m_converged;
}


int Glm::nIterations() const
{
    return m_n_iterations;
}


VectorXd Glm::coefficients() const
{
    return m_coefficients;
}


VectorXd Glm::predict() const
{
    return predict(m_predictors);
}


QStringList Glm::calculationErrors() const
{
    return m_calculation_errors;
}


QStringList Glm::getInfo() const
{
    return m_info;
}


VectorXd Glm::residuals() const
{
    if (!m_fitted) {
        warnReturningGarbage();
        return VectorXd();
    }
    return predict() - m_dependent_variable;
}


Eigen::ArrayXXd Glm::predictEta(const Eigen::MatrixXd& predictors) const
{
    if (!m_fitted) {
        warnReturningGarbage();
        return VectorXd();
    }
    return (predictors * m_coefficients).array();
}


Eigen::ArrayXXd Glm::predictEta() const
{
    return predictEta(m_predictors);
}


VectorXd Glm::predict(const MatrixXd& predictors) const
{
    // As per: Y_predicted = invlink(Xb)
    if (!m_fitted) {
        warnReturningGarbage();
        return VectorXd();
    }
    const ArrayXXd eta = predictEta(predictors);
    const ArrayXXd predicted = eta.unaryExpr(m_link_fn_family.inv_link_fn);
    return predicted.matrix();
}


// ============================================================================
// The interesting parts
// ============================================================================

void Glm::fitIRLS()
{
    addInfo("Fitting GLM using iteratively reweighted least squares (IRLS) "
            "estimation");
    // https://bwlewis.github.io/GLM/

    // Renaming:
    // Everyone uses a different notation!
    // Translation table:
    //      Thing   Conventional notation       https://bwlewis.github.io/GLM/
    //      ------------------------------------------------------------------
    //      depvar      Y                               b
    //      predictors  X                               A
    //      coeffs      b                               x
    const MatrixXd& A = m_predictors;   // n,k
    const ArrayXXd& b = m_dependent_variable.array();  // n,1
    const LinkFunctionFamily& family = m_link_fn_family;
    const int n_predictors = nPredictors();
    using statsfunc::svdSolve;

    VectorXd x = VectorXd::Zero(n_predictors);  // k,1
    VectorXd xold = VectorXd::Zero(n_predictors);  // k,1
    for (m_n_iterations = 1;
            m_n_iterations <= m_max_iterations;
            ++m_n_iterations) {
        // Note also, for debugging, that you can inspect matrices, but not
        // arrays, in the Qt debugger.
        const ArrayXXd eta = (A   * x).array();
                           // n,k * k,1  -> n,1
        const ArrayXXd g = eta.unaryExpr(family.inv_link_fn);  // apply invlink to eta -> n,1
        const ArrayXXd gprime = eta.unaryExpr(family.derivative_inv_link_fn).array();  // -> n,1
        const ArrayXXd gprime_squared = gprime.square();  // -> n,1
        const VectorXd z = (eta + (b - g) / gprime).matrix();  // n,1
        const ArrayXXd var_g = family.variance_fn(g);
        const MatrixXd W = (gprime_squared / var_g).matrix().asDiagonal();  // n,n
        xold = x;

        // Now the tricky bit.
        // The source has:
        //      Let x[j+1] = (A_T W A)^−1 A_T W z
        // In R, it uses:
        //      x = solve(crossprod(A,W*A), crossprod(A,W*z), tol=2*.Machine$double.eps)
        // R says "solve" solves "a %*% x = b" for x
        // ... i.e.
        //              a * x = b
        //              a_INV * a * x = a_INV * b
        //              x = a_INV * b
        // Therefore, we translate to:
        //      "A" = A_T W A = A.cross(W * A) ?
        //      "b" = A_T W z = A.cross(W * z) ?
        // ... yes, except that we can't use Eigen's "cross" like that; see
        //     instead the preprocessor macro CROSSPROD to create some
        //     shorthand while still allowing compiler optimization for Eigen
        //     code.
        // In Eigen, we solve Ax = b using
        //      x = A.jacobiSvd(options).solve(b)
        // So we end up with:

        x = svdSolve(CROSSPROD(A,     W   * A),
                            // n,k ; (n,n * n,k) -> n,k        --> k,k
                     CROSSPROD(A,     W   * z));
                            // n,k ; (n,n * n,1) -> n,1        --> k,1
        // -> k,1

        double euclidean_norm_of_change = (x - xold).norm();
        // = sqrt(sum of squared values of (x - xold))
        if (euclidean_norm_of_change < m_tolerance) {
            m_converged = true;
            break;
        }
    }

    m_fitted = true;
    m_coefficients = x;  // k,1
}


void Glm::fitIRLSSVDNewton()
{
    addInfo("Fitting GLM using iteratively reweighted least squares (IRLS) "
            "estimation, SVD (singular value decomposition) Newton variant");
    // https://bwlewis.github.io/GLM/
    // Because of the variability in variable names, for dimensional analysis
    // we'll use nobs, npred.

    // Renaming, as above
    MatrixXd A = m_predictors;  // nobs,npred
    const ArrayXXd& b = m_dependent_variable.array();  // nobs,1
    const LinkFunctionFamily& family = m_link_fn_family;
    const int n_predictors = nPredictors();  // = npred
    const int m = nObservations();  // n (sigh...) = nobs
    const int& n = n_predictors;  // = npred
    const double NA = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();
    using namespace eigenfunc;

    ArrayXd weights(m);  // nobs,1
    // Below, can't use "weights = m_p_weights ? ... : ...", because the
    // resulting template types are not identical. But this works fine:
    if (m_p_weights) {
        weights = m_p_weights->array();
    } else {
        weights = ArrayXd::Ones(m);
    }
    if (weights.rows() != m) {
        addError(QString(
                     "'weights' is of length %1, but should match number of "
                     "observations, %2").arg(weights.rows(), m));
        return;
    }

    // If any weights are zero, set corresponding A row to zero
    for (int i = 0; i < m; ++i) {
        if (weights(i) == 0) {
            A.row(i).setConstant(0);
        }
    }

    JacobiSVD<MatrixXd> S = svd(A);
    // In R, the "d" part of an SVD is the vector of singular values; "u" is
    // the matrix of left singular values vectors; "v" is the matrix of right
    // singular values vectors. The original here used S$d.
    // In Eigen, singular values are given by singularValues(), and are always
    // in descending order (I presume they're also in descending order in R!).
    // https://eigen.tuxfamily.org/dox/classEigen_1_1SVDBase.html
    ArrayXd S_d = S.singularValues().array();
    if (S_d.size() == 0) {
        // Before we address d(0)... check it exists!
        addError("Singular values: empty!");
        return;
    }
    IndexArray select_pred_indices = indexSeq(0, n_predictors - 1);
    ArrayXb tiny_singular_values = S_d / S_d(0) < m_tolerance;
    int k = tiny_singular_values.cast<int>().sum();  // number of tiny singular values; ntiny
    if (k > 0) {
        addInfo("Numerically rank-deficient model matrix");
        switch (m_rank_deficiency_method) {
        case RankDeficiencyMethod::SelectColumns:
            addInfo("RankDeficiencyMethod::SelectColumns");
            select_pred_indices = svdsubsel(A, n - k);
            S = svd(subsetByColumnIndex(A, select_pred_indices));
            S_d = S.singularValues().array();  // Since we change S, rewrite S_d
            break;
        case RankDeficiencyMethod::MinimumNorm:
            addInfo("RankDeficiencyMethod::MinimiumNorm");
            // Dealt with at the end; see below
            break;
        case RankDeficiencyMethod::Error:
            addError("Near rank-deficient model matrix");
            return;
        default:
            addError("Unknown rank deficiency method!");
            return;
        }
    }

    ArrayXd t = ArrayXd::Zero(m);  // nobs,1  // NB confusing name choice, cf. R's t() for transpose
    MatrixXd s = VectorXd::Zero(select_pred_indices.size());  // npred_unless_subselected,1
    MatrixXd s_old = s;  // npred_unless_subselected,1
    ArrayXb select_pred_bool = selectBoolFromIndices(select_pred_indices, n_predictors);
    ArrayXb good = weights > 0;  // nobs,1
    double two_epsilon = 2.0 * std::numeric_limits<double>::epsilon();

    for (m_n_iterations = 1;
            m_n_iterations <= m_max_iterations;
            ++m_n_iterations) {
        const ArrayXd t_good = subsetByElementBoolean(t, good);  // nobs_where_good,1
        const ArrayXd b_good = subsetByElementBoolean(b, good);  // nobs_where_good,1
        const ArrayXd weights_good = subsetByElementBoolean(weights, good);  // nobs_where_good,1

        const ArrayXd g = t_good.unaryExpr(family.inv_link_fn);  // nobs_where_good,1

        const ArrayXd varg = family.variance_fn(g);  // nobs_where_good,1
        if (varg.isNaN().any()) {
            // As per original...
            addError("NAs in variance of the inverse link function");
            return;
        }
        // But also (RNC):
        if (varg.isInf().any()) {
            // As per original...
            addError("Infinities in variance of the inverse link function");
            return;
        }
        if ((varg == 0).any()) {
            addError("Zero value in variance of the inverse link function");
            return;
        }

        const ArrayXd gprime = t_good.unaryExpr(family.derivative_inv_link_fn);  // nobs_where_good,1
        if (gprime.isNaN().any()) {
            // As per original...
            addError("NAs in the inverse link function derivative");
            return;
        }
        // But also (RNC):
        if (gprime.isInf().any()) {
            // As per original...
            addError("Infinities in the inverse link function derivative");
            return;
        }

        ArrayXd z = ArrayXd::Zero(m);  // nobs,1
        ArrayXd W = ArrayXd::Zero(m);  // nobs,1
        ArrayXd to_z_good = t_good + (b_good - g) / gprime;  // nobs_where_ngood,1
        assignByBooleanSequentially(z, good, to_z_good);
        ArrayXd W_new_good = weights_good * (gprime.square() / varg);  // nobs_where_ngood,1
        assignByBooleanSequentially(W, good, W_new_good);
        good = W > two_epsilon;
        // --------------------------------------------------------------------
        // NB good changes here; cached versions invalidated
        // --------------------------------------------------------------------
        int n_good = good.cast<int>().sum();
        if (n_good < m) {
            addInfo("Warning: tiny weights encountered");
        }
        s_old = s;

        const MatrixXd S_u = S.matrixU();  // nobs,npred
        const ArrayXXd S_u_good = subsetByRowBoolean(S_u, good);  // nobs_where_ngood,npred
        // Note that mat[boolvec] gives a 1-d result, whereas
        // mat[boolvec,] gives a 2-d result.
        const ArrayXd W_good = subsetByElementBoolean(W, good);  // nobs_where_ngood,1
        const ArrayXd z_good = subsetByElementBoolean(z, good);  // nobs_where_ngood,1
        // Now, about W_good * S_u_good, where S_u_good is e.g. 20x2:
        // In R, if W_good is 20x1, you get a "non-conformable arrays" error,
        // but if W_good is a 20-length vector, it works, applying it across
        // all columns of S_u_good.
        // Let's create a new multiplication function:
        MatrixXd tmp_matrix_to_chol = CROSSPROD(
                    S_u_good,  // nobs_where_ngood,npred
                    multiply(W_good, S_u_good)  // nobs_where_ngood,npred
        );  // npred,npred
        MatrixXd C = chol(tmp_matrix_to_chol);  // npred,npred
        MatrixXd tmp_matrix_rhs = CROSSPROD(
                    S_u_good,  // nobs_where_ngood,npred
                    W_good * z_good  // nobs_where_ngood,1
        );  // npred,1
        s = forwardsolve(C.transpose(), tmp_matrix_rhs);  // npred,1
        s = backsolve(C, s);  // npred,1

        t = ArrayXd::Zero(m);  // nobs,1
        MatrixXd t_new_good = S_u_good.matrix() * s;  // nobs_where_ngood,1
        assignByBooleanSequentially(t, good, t_new_good);  // nobs,1

        // Converged?
        double euclidean_norm_of_change = (s - s_old).matrix().norm();
        // = sqrt(sum of squared values of (s - s_old))
        if (euclidean_norm_of_change < m_tolerance) {
            m_converged = true;
            break;
        }
    }

    VectorXd& x = m_coefficients;
    x = VectorXd(n).setConstant(NA);
    if (m_rank_deficiency_method == RankDeficiencyMethod::MinimumNorm) {
        S_d = tiny_singular_values.select(Inf, S_d);
    }

    const ArrayXd t_good = subsetByElementBoolean(t, good);  // nobs_where_good,1
    const MatrixXd S_u = S.matrixU();  // nobs,npred
    const MatrixXd S_u_good = subsetByRowBoolean(S_u, good);  // nobs_where_good,npred
    const MatrixXd S_v = S.matrixV();
    const MatrixXd x_possible = S_v * ((1 / S_d) * CROSSPROD(
                                           S_u_good,
                                           t_good).array()).matrix();  // npred,1
    x = select_pred_bool.select(x_possible, x);
}


eigenfunc::IndexArray Glm::svdsubsel(const MatrixXd& A, int k)
{
    // As per http://bwlewis.github.io/GLM/svdss.html
    // Input:
    //      A: m*p matrix, m >= p
    //      k: number of output columns, k <= p
    // Returns a column array containing the COLUMN INDICES of the columns of A
    // that *estimates* the k most linearly independent columns of A.
    //
    // Note the differences from the original relating to Eigen being 0-based
    // versus R being 1-based in its indexing.

    using namespace eigenfunc;

    // Input validation as per requirements above:
    Q_ASSERT(A.rows() >= A.cols());
    // ... we will force k, as below

    int index_k = k - 1;
    if (index_k < 0 || index_k >= A.cols()) {
        index_k = A.cols() - 1;
    }
    JacobiSVD<MatrixXd> S = svd(scale(A, false, true));
    ArrayXd d = svd(A).singularValues().array();
    double epsilon = std::numeric_limits<double>::epsilon();
    IndexArray small_sv_indices = which(d < 2.0 * epsilon);
    if (small_sv_indices.size() > 0) {
        Index n = small_sv_indices(0);  // index of first small singular value
        if (index_k >= n) {
            index_k = n - 1;
            addInfo("k was reduced to match the rank of A");
        }
    }
    MatrixXd subsetted = subsetByColumnIndex(S.matrixV(), indexSeq(0, index_k)).transpose();  // k,?
    // The original uses qr(..., LAPACK=TRUE), and R's ?qr says "Using
    // LAPACK... uses column pivoting..." so the Eigen equivalent is probably:
    ColPivHouseholderQR<MatrixXd> Q = subsetted.colPivHouseholderQr();
    // Then, the original uses Q$pivot, which is a list of column indices in
    // R. Thanks to
    // https://stackoverflow.com/questions/26385561/how-to-get-matrix-pivot-index-in-c-eigen
    // we have:

    ArrayXi column_indices_int = Q.colsPermutation().indices();
    IndexArray column_indices = column_indices_int.cast<Index>();
    sort(column_indices);
    return column_indices;
}