// ResearchSetsMenu.js

/*
    Copyright (C) 2012-2016 Rudolf Cardinal (rudolf@pobox.com).
    Department of Psychiatry, University of Cambridge.
    Funded by the Wellcome Trust.

    This file is part of CamCOPS.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
*/

/*jslint node: true, newcap: true */
"use strict";
/*global L */

module.exports = function ResearchSetsMenu() {

    var MenuWindow = require('menulib/MenuWindow'),
        UICONSTANTS = require('common/UICONSTANTS'),
        data = [
            UICONSTANTS.CHANGE_PATIENT_MENU_LINE,
            {
                maintitle: L('t_set_cpft_affective_1'),
                subtitle: L('s_set_cpft_affective_1'),
                arrowOnRight: true,
                window: 'menu/SetMenu_CPFT_Affective_1'
            },
            {
                maintitle: L('t_set_deakin_1'),
                subtitle: L('s_set_deakin_1'),
                arrowOnRight: true,
                window: 'menu/SetMenu_Deakin_1'
            },
            {
                maintitle: L('t_set_obrien_1'),
                subtitle: L('s_set_obrien_1'),
                arrowOnRight: true,
                window: 'menu/SetMenu_OBrien_1'
            }
        ],
        self = new MenuWindow({
            title: L('menutitle_sets_research'),
            icon: UICONSTANTS.ICON_MENU_SETS_RESEARCH,
            data: data
        });

    return self;
};
