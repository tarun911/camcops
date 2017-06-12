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

#include "ccrandom.h"

namespace ccrandom {


std::random_device rd;
std::mt19937 rng(rd());


bool coin(qreal p)
{
    std::bernoulli_distribution dist(p);
    return dist(rng);
}


int randomInt(int minimum, int maximum)
{
    // [minimum, maximum] -- i.e. inclusive
    std::uniform_int_distribution<int> dist(minimum, maximum);
    return dist(rng);
}


qreal randomRealExcUpper(qreal minimum, qreal maximum)
{
    // [minimum, maximum) -- i.e. includes lower but not upper bound
    // http://en.cppreference.com/w/cpp/numeric/random/uniform_real_distribution
    std::uniform_real_distribution<qreal> dist(minimum, maximum);
    return dist(rng);
}


qreal randomRealIncUpper(qreal minimum, qreal maximum)
{
    // [minimum, maximum] -- i.e. inclusive
    // http://en.cppreference.com/w/cpp/numeric/random/uniform_real_distribution
    qreal adjusted_max = std::nextafter(maximum, std::numeric_limits<qreal>::max());
    std::uniform_real_distribution<qreal> dist(minimum, adjusted_max);
    return dist(rng);
}


}  // namespace ccrandom