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

#include "linkfunctionfamily.h"
#include "maths/statsfunc.h"


LinkFunctionFamily::LinkFunctionFamily(
        std::function<double(double)> link_fn,
        std::function<double(double)> inv_link_fn,
        std::function<double(double)> derivative_inv_link_fn,
        std::function<Eigen::ArrayXXd(const Eigen::ArrayXXd&)> variance_fn) :
    link_fn(link_fn),
    inv_link_fn(inv_link_fn),
    derivative_inv_link_fn(derivative_inv_link_fn),
    variance_fn(variance_fn)
{
}


// Disambiguating overloaded functions:
// - https://stackoverflow.com/questions/10111042/wrap-overloaded-function-via-stdfunction

const LinkFunctionFamily LINK_FN_FAMILY_LOGIT(
        statsfunc::logit,  // link
        statsfunc::logistic,  // inverse link
        statsfunc::derivativeOfLogistic,  // derivative of inverse link
        statsfunc::binomialVariance  // variance function
);


const LinkFunctionFamily LINK_FN_FAMILY_IDENTITY(
        statsfunc::identity,  // link
        statsfunc::identity,  // inverse link
        static_cast<double (&)(double)>(statsfunc::one),  // derivative of inverse link (y = x => y' = 1)
        static_cast<Eigen::ArrayXXd (&)(const Eigen::ArrayXXd&)>(statsfunc::one)  // variance function
            // ... ?assumes normality; variance is independent of the mean
            // ... https://en.wikipedia.org/wiki/Variance_function#Example_.E2.80.93_normal
);

// For link function families, see also:
// - https://stats.stackexchange.com/questions/212430/what-are-the-error-distribution-and-link-functions-of-a-model-family-in-r
// - https://en.wikipedia.org/wiki/Generalized_linear_model#Link_function
// - R: ?family
