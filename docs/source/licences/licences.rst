..  docs/source/misc/licenses.rst

..  Copyright (C) 2012-2019 Rudolf Cardinal (rudolf@pobox.com).
    .
    This file is part of CamCOPS.
    .
    CamCOPS is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    .
    CamCOPS is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    .
    You should have received a copy of the GNU General Public License
    along with CamCOPS. If not, see <http://www.gnu.org/licenses/>.

.. |denovo| replace:: *de novo*

Licences
========

This section gives citations to, and licence details for, software used by
CamCOPS.

.. _licences_camcops:

CamCOPS
-------

Copyright (C) 2012-2019 Rudolf Cardinal (rudolf@pobox.com).

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


.. _licences_other:

.. _licences_qt:

Qt
--

The CamCOPS client (tablet/desktop app) is written using the Qt C++ framework.
See https://www.qt.io/.

Qt is used here under the LGPL. See:

- https://www.qt.io/qt-licensing-terms/

  - note that some parts of Qt are only available under the GPL for open-source
    users: https://www.qt.io/licensing-comparison/

- https://doc.qt.io/qt-5/licenses-used-in-qt.html

- https://www.gnu.org/licenses/lgpl-3.0.en.html

OpenSSL
-------

Qt uses OpenSSL for its cryptography. See https://www.openssl.org/.

This product includes software developed by the OpenSSL Project for use in the
OpenSSL Toolkit (http://www.openssl.org/).

.. code-block:: none

    License issues

    The OpenSSL toolkit stays under a dual license, i.e. both the conditions of
    the OpenSSL License and the original SSLeay license apply to the toolkit.
    See below for the actual license texts. Actually both licenses are
    BSD-style Open Source licenses. In case of any license issues related to
    OpenSSL please contact openssl-core@openssl.org.

OpenSSL License
~~~~~~~~~~~~~~~

.. code-block:: none

    /* ====================================================================
    * Copyright (c) 1998-2016 The OpenSSL Project.  All rights reserved.
    *
    * Redistribution and use in source and binary forms, with or without
    * modification, are permitted provided that the following conditions
    * are met:
    *
    * 1. Redistributions of source code must retain the above copyright
    *    notice, this list of conditions and the following disclaimer.
    *
    * 2. Redistributions in binary form must reproduce the above copyright
    *    notice, this list of conditions and the following disclaimer in
    *    the documentation and/or other materials provided with the
    *    distribution.
    *
    * 3. All advertising materials mentioning features or use of this
    *    software must display the following acknowledgment:
    *    "This product includes software developed by the OpenSSL Project
    *    for use in the OpenSSL Toolkit. (http://www.openssl.org/)"
    *
    * 4. The names "OpenSSL Toolkit" and "OpenSSL Project" must not be used to
    *    endorse or promote products derived from this software without
    *    prior written permission. For written permission, please contact
    *    openssl-core@openssl.org.
    *
    * 5. Products derived from this software may not be called "OpenSSL"
    *    nor may "OpenSSL" appear in their names without prior written
    *    permission of the OpenSSL Project.
    *
    * 6. Redistributions of any form whatsoever must retain the following
    *    acknowledgment:
    *    "This product includes software developed by the OpenSSL Project
    *    for use in the OpenSSL Toolkit (http://www.openssl.org/)"
    *
    * THIS SOFTWARE IS PROVIDED BY THE OpenSSL PROJECT ``AS IS'' AND ANY
    * EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE OpenSSL PROJECT OR
    * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
    * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
    * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
    * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
    * OF THE POSSIBILITY OF SUCH DAMAGE.
    * ====================================================================
    *
    * This product includes cryptographic software written by Eric Young
    * (eay@cryptsoft.com).  This product includes software written by Tim
    * Hudson (tjh@cryptsoft.com).
    *
    */

Original SSLeay License
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    /* Copyright (C) 1995-1998 Eric Young (eay@cryptsoft.com)
    * All rights reserved.
    *
    * This package is an SSL implementation written
    * by Eric Young (eay@cryptsoft.com).
    * The implementation was written so as to conform with Netscapes SSL.
    *
    * This library is free for commercial and non-commercial use as long as
    * the following conditions are aheared to.  The following conditions
    * apply to all code found in this distribution, be it the RC4, RSA,
    * lhash, DES, etc., code; not just the SSL code.  The SSL documentation
    * included with this distribution is covered by the same copyright terms
    * except that the holder is Tim Hudson (tjh@cryptsoft.com).
    *
    * Copyright remains Eric Young's, and as such any Copyright notices in
    * the code are not to be removed.
    * If this package is used in a product, Eric Young should be given attribution
    * as the author of the parts of the library used.
    * This can be in the form of a textual message at program startup or
    * in documentation (online or textual) provided with the package.
    *
    * Redistribution and use in source and binary forms, with or without
    * modification, are permitted provided that the following conditions
    * are met:
    * 1. Redistributions of source code must retain the copyright
    *    notice, this list of conditions and the following disclaimer.
    * 2. Redistributions in binary form must reproduce the above copyright
    *    notice, this list of conditions and the following disclaimer in the
    *    documentation and/or other materials provided with the distribution.
    * 3. All advertising materials mentioning features or use of this software
    *    must display the following acknowledgement:
    *    "This product includes cryptographic software written by
    *     Eric Young (eay@cryptsoft.com)"
    *    The word 'cryptographic' can be left out if the rouines from the library
    *    being used are not cryptographic related :-).
    * 4. If you include any Windows specific code (or a derivative thereof) from
    *    the apps directory (application code) you must include an acknowledgement:
    *    "This product includes software written by Tim Hudson (tjh@cryptsoft.com)"
    *
    * THIS SOFTWARE IS PROVIDED BY ERIC YOUNG ``AS IS'' AND
    * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
    * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
    * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
    * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
    * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
    * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
    * SUCH DAMAGE.
    *
    * The licence and distribution terms for any publically available version or
    * derivative of this code cannot be changed.  i.e. this code cannot simply be
    * copied and put under another distribution licence
    * [including the GNU Public Licence.]
    */

SQLCipher
---------

CamCOPS uses SQLCipher for encrypted SQLite databases. See
https://www.zetetic.net/sqlcipher/.

.. code-block:: none

    Copyright (c) 2016, ZETETIC LLC
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
          notice, this list of conditions and the following disclaimer in the
          documentation and/or other materials provided with the distribution.
        * Neither the name of the ZETETIC LLC nor the
          names of its contributors may be used to endorse or promote products
          derived from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY ZETETIC LLC ''AS IS'' AND ANY
    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL ZETETIC LLC BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

..
    Boost
    -----
..
    See http://www.boost.org//
..
    Licensed under the Boost Software License, version 1.0:
    http://www.boost.org/LICENSE_1_0.txt
..
    .. code-block:: none
..
        Boost Software License - Version 1.0 - August 17th, 2003
..
        Permission is hereby granted, free of charge, to any person or
        organization obtaining a copy of the software and accompanying
        documentation covered by this license (the "Software") to use,
        reproduce, display, distribute, execute, and transmit the Software, and
        to prepare derivative works of the Software, and to permit
        third-parties to whom the Software is furnished to do so, all subject
        to the following:
..
        The copyright notices in the Software and this entire statement,
        including the above license grant, this restriction and the following
        disclaimer, must be included in all copies of the Software, in whole or
        in part, and all derivative works of the Software, unless such copies
        or derivative works are solely in the form of machine-executable object
        code generated by a source language processor.
..
        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
        OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
        MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND
        NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR ANYONE
        DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES OR OTHER LIABILITY,
        WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
        CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.


..
    Armadillo
    ---------
..
    See http://arma.sourceforge.net/.
..
    Sanderson C, Curtin R (2016). **Armadillo: a template-based C++ library for
    linear algebra.** *Journal of Open Source Software* 1: 26.
    http://arma.sourceforge.net/armadillo_joss_2016.pdf;
    http://dx.doi.org/10.21105/joss.00026
..
    Licensed under the Apache License 2.0:
    https://opensource.org/licenses/Apache-2.0
..
    .. code-block:: none
..
        Apache License
        Version 2.0, January 2004
        http://www.apache.org/licenses/
..
        TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
..
        1. Definitions.
..
        "License" shall mean the terms and conditions for use, reproduction, and
        distribution as defined by Sections 1 through 9 of this document.
..
        "Licensor" shall mean the copyright owner or entity authorized by the
        copyright owner that is granting the License.
..
        "Legal Entity" shall mean the union of the acting entity and all other
        entities that control, are controlled by, or are under common control with
        that entity. For the purposes of this definition, "control" means (i) the
        power, direct or indirect, to cause the direction or management of such
        entity, whether by contract or otherwise, or (ii) ownership of fifty
        percent (50%) or more of the outstanding shares, or (iii) beneficial
        ownership of such entity.
..
        "You" (or "Your") shall mean an individual or Legal Entity exercising
        permissions granted by this License.
..
        "Source" form shall mean the preferred form for making modifications,
        including but not limited to software source code, documentation source,
        and configuration files.
..
        "Object" form shall mean any form resulting from mechanical transformation
        or translation of a Source form, including but not limited to compiled
        object code, generated documentation, and conversions to other media types.
..
        "Work" shall mean the work of authorship, whether in Source or Object form,
        made available under the License, as indicated by a copyright notice that
        is included in or attached to the work (an example is provided in the
        Appendix below).
..
        "Derivative Works" shall mean any work, whether in Source or Object form,
        that is based on (or derived from) the Work and for which the editorial
        revisions, annotations, elaborations, or other modifications represent, as
        a whole, an original work of authorship. For the purposes of this License,
        Derivative Works shall not include works that remain separable from, or
        merely link (or bind by name) to the interfaces of, the Work and Derivative
        Works thereof.
..
        "Contribution" shall mean any work of authorship, including the original
        version of the Work and any modifications or additions to that Work or
        Derivative Works thereof, that is intentionally submitted to Licensor for
        inclusion in the Work by the copyright owner or by an individual or Legal
        Entity authorized to submit on behalf of the copyright owner. For the
        purposes of this definition, "submitted" means any form of electronic,
        verbal, or written communication sent to the Licensor or its
        representatives, including but not limited to communication on electronic
        mailing lists, source code control systems, and issue tracking systems that
        are managed by, or on behalf of, the Licensor for the purpose of discussing
        and improving the Work, but excluding communication that is conspicuously
        marked or otherwise designated in writing by the copyright owner as "Not a
        Contribution."
..
        "Contributor" shall mean Licensor and any individual or Legal Entity on
        behalf of whom a Contribution has been received by Licensor and
        subsequently incorporated within the Work.
..
        2. Grant of Copyright License.
..
        Subject to the terms and conditions of this License, each Contributor
        hereby grants to You a perpetual, worldwide, non-exclusive, no-charge,
        royalty-free, irrevocable copyright license to reproduce, prepare
        Derivative Works of, publicly display, publicly perform, sublicense, and
        distribute the Work and such Derivative Works in Source or Object form.
..
        3. Grant of Patent License.
..
        Subject to the terms and conditions of this License, each Contributor
        hereby grants to You a perpetual, worldwide, non-exclusive, no-charge,
        royalty-free, irrevocable (except as stated in this section) patent license
        to make, have made, use, offer to sell, sell, import, and otherwise
        transfer the Work, where such license applies only to those patent claims
        licensable by such Contributor that are necessarily infringed by their
        Contribution(s) alone or by combination of their Contribution(s) with the
        Work to which such Contribution(s) was submitted. If You institute patent
        litigation against any entity (including a cross-claim or counterclaim in a
        lawsuit) alleging that the Work or a Contribution incorporated within the
        Work constitutes direct or contributory patent infringement, then any
        patent licenses granted to You under this License for that Work shall
        terminate as of the date such litigation is filed.
..
        4. Redistribution.
..
        You may reproduce and distribute copies of the Work or Derivative Works
        thereof in any medium, with or without modifications, and in Source or
        Object form, provided that You meet the following conditions:
..
        You must give any other recipients of the Work or Derivative Works a copy
        of this License; and You must cause any modified files to carry prominent
        notices stating that You changed the files; and You must retain, in the
        Source form of any Derivative Works that You distribute, all copyright,
        patent, trademark, and attribution notices from the Source form of the
        Work, excluding those notices that do not pertain to any part of the
        Derivative Works; and If the Work includes a "NOTICE" text file as part of
        its distribution, then any Derivative Works that You distribute must
        include a readable copy of the attribution notices contained within such
        NOTICE file, excluding those notices that do not pertain to any part of the
        Derivative Works, in at least one of the following places: within a NOTICE
        text file distributed as part of the Derivative Works; within the Source
        form or documentation, if provided along with the Derivative Works; or,
        within a display generated by the Derivative Works, if and wherever such
        third-party notices normally appear. The contents of the NOTICE file are
        for informational purposes only and do not modify the License. You may add
        Your own attribution notices within Derivative Works that You distribute,
        alongside or as an addendum to the NOTICE text from the Work, provided that
        such additional attribution notices cannot be construed as modifying the
        License. You may add Your own copyright statement to Your modifications and
        may provide additional or different license terms and conditions for use,
        reproduction, or distribution of Your modifications, or for any such
        Derivative Works as a whole, provided Your use, reproduction, and
        distribution of the Work otherwise complies with the conditions stated in
        this License.
..
        5. Submission of Contributions.
..
        Unless You explicitly state otherwise, any Contribution intentionally
        submitted for inclusion in the Work by You to the Licensor shall be under
        the terms and conditions of this License, without any additional terms or
        conditions. Notwithstanding the above, nothing herein shall supersede or
        modify the terms of any separate license agreement you may have executed
        with Licensor regarding such Contributions.
..
        6. Trademarks.
..
        This License does not grant permission to use the trade names, trademarks,
        service marks, or product names of the Licensor, except as required for
        reasonable and customary use in describing the origin of the Work and
        reproducing the content of the NOTICE file.
..
        7. Disclaimer of Warranty.
..
        Unless required by applicable law or agreed to in writing, Licensor
        provides the Work (and each Contributor provides its Contributions) on an
        "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
        or implied, including, without limitation, any warranties or conditions of
        TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR
        PURPOSE. You are solely responsible for determining the appropriateness of
        using or redistributing the Work and assume any risks associated with Your
        exercise of permissions under this License.
..
        8. Limitation of Liability.
..
        In no event and under no legal theory, whether in tort (including
        negligence), contract, or otherwise, unless required by applicable law
        (such as deliberate and grossly negligent acts) or agreed to in writing,
        shall any Contributor be liable to You for damages, including any direct,
        indirect, special, incidental, or consequential damages of any character
        arising as a result of this License or out of the use or inability to use
        the Work (including but not limited to damages for loss of goodwill, work
        stoppage, computer failure or malfunction, or any and all other commercial
        damages or losses), even if such Contributor has been advised of the
        possibility of such damages.
..
        9. Accepting Warranty or Additional Liability.
..
        While redistributing the Work or Derivative Works thereof, You may choose
        to offer, and charge a fee for, acceptance of support, warranty, indemnity,
        or other liability obligations and/or rights consistent with this License.
        However, in accepting such obligations, You may act only on Your own behalf
        and on Your sole responsibility, not on behalf of any other Contributor,
        and only if You agree to indemnify, defend, and hold each Contributor
        harmless for any liability incurred by, or claims asserted against, such
        Contributor by reason of your accepting any such warranty or additional
        liability.
..
        END OF TERMS AND CONDITIONS


..  MLPACK: UNUSED

..
    MLPACK
    ------
..
    See http://www.mlpack.org/.
..
    Curtin RR, Cline JR, Slagle NP, March WB, Ram P, Mehta NA, Gray AG (2013).
    MLPACK: A Scalable C++ Machine Learning Library.** Journal of Machine
    Learning Research* 14: 801–805.
..
    Licensed under the 3-Clause BSD License:
    https://opensource.org/licenses/BSD-3-Clause
..
    See specifically: https://github.com/mlpack/mlpack/blob/master/LICENSE.txt
..
    .. code-block:: none
..
        mlpack is provided without any warranty of fitness for any purpose.
        You can redistribute the library and/or modify it under the terms of
        the 3-clause BSD license.  The text of the 3-clause BSD license is
        contained below.
..
        mlpack contains some reproductions of the source code of Armadillo,
        which is licensed under the Mozilla Public License v2.0 (MPL2).  This
        code is found in src/mlpack/core/arma_extend/ and more details on the
        licensing are available there.
..
        mlpack also contains some reproductions of the source code of Boost,
        which is licensed under the Boost Software License, version 1.0.  This
        code is found in src/mlpack/core/boost_backport/ and more details on
        the licensing are available there.
..
        ----
        Copyright (c) 2007-2016, mlpack contributors (see COPYRIGHT.txt)
        All rights reserved.
..
        Redistribution and use of mlpack in source and binary forms, with or
        without modification, are permitted provided that the following
        conditions are met:
..
        1. Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.
..
        2. Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution.
..
        3. Neither the name of the copyright holder nor the names of its
        contributors may be used to endorse or promote products derived from
        this software without specific prior written permission.
..
        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
        IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
        TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
        PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
        HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
        SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
        LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
        DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
        THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
        (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Eigen
-----

The CamCOPS client uses Eigen for matrix algebra (e.g. for implementing
generalized linear models). See http://eigen.tuxfamily.org.

- Guennebaud G, Jacob B, et al. (2010). Eigen v3. http://eigen.tuxfamily.org

- Eigen is free software licensed under the Mozilla Public License (MPL) v2.0
  (https://www.mozilla.org/en-US/MPL/2.0/); see
  http://eigen.tuxfamily.org/index.php?title=Main_Page#License.


FloatingPoint
-------------

The CamCOPS client uses Google's FloatingPoint class for “nearly equal”
testing. This is from the Google C++ Testing Framework.

See:

- https://stackoverflow.com/questions/17333/what-is-the-most-effective-way-for-float-and-double-comparison
- https://raw.githubusercontent.com/google/googletest/master/googletest/include/gtest/internal/gtest-internal.h
- https://raw.githubusercontent.com/google/googletest/master/googletest/include/gtest/internal/gtest-port.h

.. code-block:: none

    // Copyright 2005, Google Inc.
    // All rights reserved.
    //
    // Redistribution and use in source and binary forms, with or without
    // modification, are permitted provided that the following conditions are
    // met:
    //
    //     * Redistributions of source code must retain the above copyright
    // notice, this list of conditions and the following disclaimer.
    //     * Redistributions in binary form must reproduce the above
    // copyright notice, this list of conditions and the following disclaimer
    // in the documentation and/or other materials provided with the
    // distribution.
    //     * Neither the name of Google Inc. nor the names of its
    // contributors may be used to endorse or promote products derived from
    // this software without specific prior written permission.
    //
    // THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    // "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    // LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    // A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    // OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    // SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    // LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    // DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    // THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    // (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    // OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    //
    // Authors: wan@google.com (Zhanyong Wan), eefacm@gmail.com (Sean Mcafee)
    //
    // The Google C++ Testing Framework (Google Test)


Sounds
------

For sounds relating to specific tasks, see each task’s information file. For
the CamCOPS general sounds:

- Sound test 1 (bach_brandenburg_3_3.mp3):

  - excerpt from Bach JS, *Brandenburg
    Concerto No. 3, third movement (Allegro)*, by the Advent Chamber Orchestra,
    from
    `<http://freemusicarchive.org/music/Advent_Chamber_Orchestra/Selections_from_the_2005-2006_Season/>`_;

  - licensed under the EFF Open Audio License
    (https://commons.wikimedia.org/wiki/EFF_OAL), reported by the source site
    as equivalent to CC-BY-SA-2.0
    (https://creativecommons.org/licenses/by-sa/3.0/us/).

- Sound test 2 (mozart_laudate.mp3):

  - excerpt from Mozart WA, *Vesperae solennes
    de confessore* (K.339), fifth movement, *Laudate Dominum*, by the Advent
    Chamber Orchester, from
    `<http://freemusicarchive.org/music/Advent_Chamber_Orchestra/Selections_from_the_December_2006_Concert/Advent_Chamber_Orchestra_-_11_-_Mozart_-_Laudate_Dominum>`_;

  - licensed under the EFF Open Audio License
    (https://commons.wikimedia.org/wiki/EFF_OAL), reported by the source site
    as equivalent to CC-BY-SA-2.0
    (https://creativecommons.org/licenses/by-sa/3.0/us/).

- Other sounds generated |denovo| in Audacity (http://www.audacityteam.org/).

Images
------

For images relating to specific tasks, see each task’s information file. For
the CamCOPS general images:

..  Something about URLs makes Sphinx go wrong with e.g.
    WARNING: Block quote ends without a blank line; unexpected unindent.
    The practical answer seems to be to stop word-wrapping the lines in the
    table that complain.
..  More generally, sometimes URLs with underscores in generate errors about
    "bad target name" or similar. Try replacing http://dodgy_url with
    `<http://dodgy_url>`_

=============================== ===============================================
File                            Source
=============================== ===============================================
addiction.png	                Cigarette symbol from
                                https://openclipart.org/detail/23552/cigarette-symbol
                                (public domain, as per https://openclipart.org/share).
                                Glass from
                                https://commons.wikimedia.org/wiki/File:Wheat_beer_glass_silhouette.svg
                                (by BenFrantzDale~commonswiki, CC-SA-3.0).
                                Rest |denovo|.
add.png	                        |denovo|
affective.png	                Modified from
                                https://commons.wikimedia.org/wiki/File:Drama-icon.svg
                                (by User:Booyabazooka; GFDL).
alltasks.png	                |denovo|
anonymous.png	                |denovo|
back.png	                    |denovo|
branch-closed.png	            |denovo|
branch-end.png	                |denovo|
branch-more.png	                |denovo|
branch-open.png	                |denovo|
camcops.png	                    Brain from `<http://www.public-domain-photos.com/free-cliparts/people/bodypart/brain_jon_phillips_01-4366.htm>`_ (public domain). Rest |denovo|.
camera.png	                    |denovo|
cancel.png	                    |denovo|
catatonia.png	                After Cardinal RN, Everitt BJ. Neural systems
                                of motivation. Encyclopedia of Behavioral
                                Neuroscience, Elsevier/Academic Press, Oxford.
chain.png	                    |denovo|
check_disabled.png	            |denovo|
check_false_black.png	        |denovo|
check_false_red.png	            |denovo|
check_true_black.png	        |denovo|
check_true_red.png	            |denovo|
check_unselected.png	        |denovo|
check_unselected_required.png	|denovo|
choose_page.png	                |denovo|
choose_patient.png	            |denovo|
clinical.png	                |denovo|
cognitive.png	                |denovo|
delete.png	                    Pencil modified from http://www.clker.com/clipart-pencil-28.html> (public domain, as per http://www.clker.com/disclaimer.html). Rest |denovo|.
edit.png	                    Pencil modified from http://www.clker.com/clipart-pencil-28.html (public domain, as per http://www.clker.com/disclaimer.html). Rest |denovo|.
executive.png	                Built using chess icons
                                https://commons.wikimedia.org/wiki/File:Chess_qdt45.svg,
                                https://commons.wikimedia.org/wiki/File:Chess_rlt45.svg,
                                and
                                https://commons.wikimedia.org/wiki/File:Chess_ndt45.svg
                                (by en:User:Cburnett; GFDL, BSD, and GPL).
fast_forward.png	            |denovo|
field_incomplete_mandatory.png	|denovo|
field_incomplete_optional.png	|denovo|
field_problem.png	            |denovo|
finishflag.png	                Modified from
                                http://www.clker.com/clipart-finish-flags.html
                                (public domain, as per
                                http://www.clker.com/disclaimer.html).
finish.png	                    |denovo|
global.png	                    From https://commons.wikimedia.org/wiki/File:Globe_Atlantic.svg (by the US Government; public domain).
hasChild.png	                |denovo|
hasParent.png	                |denovo|
info.png	                    Modified from https://en.wikipedia.org/wiki/File:Info_icon_002.svg (by Amada44; unrestricted use).
locked.png	                    Modified from https://commons.wikimedia.org/wiki/File:Ambox_padlock_gray.svg (by User:HuBoro; public domain).
magnify.png	                    Modified from https://commons.wikimedia.org/wiki/File:Magnifying_glass_icon.svg (by Derferman; public domain).
next.png	                    |denovo|
ok.png	                        |denovo|
patient_summary.png	            |denovo|
personality.png	                Prism/rainbow from
                                https://commons.wikimedia.org/wiki/File:Prism-rainbow-black.svg
                                (by Suidroot; CC-SA-3.0). “Children crossing”
                                from
                                http://www.clker.com/clipart-children-crossing.html
                                (public domain, as per
                                http://www.clker.com/disclaimer.html).
privileged.png	                |denovo|
psychosis.png	                |denovo|
radio_disabled.png	            |denovo|
radio_selected.png	            |denovo|
radio_unselected.png	        |denovo|
radio_unselected_required.png	|denovo|
read_only.png	                Pencil modified from
                                http://www.clker.com/clipart-pencil-28.html
                                (public domain, as per
                                http://www.clker.com/disclaimer.html). Rest
                                |denovo|.
reload.png	                    |denovo|
research.png	                Mortarboard from
                                https://en.wikipedia.org/wiki/File:French_university_icon.svg
                                [CC-SA-3.0, by Λua∫Wise (Operibus anteire)].
                                Test tube from
                                http://www.clker.com/clipart-26081.html (public
                                domain, as per
                                http://www.clker.com/disclaimer.html).
rotate_anticlockwise.png	    |denovo|
rotate_clockwise.png	        |denovo|
sets_clinical.png	            |denovo|
sets_research.png	            Mortarboard from https://en.wikipedia.org/wiki/File:French_university_icon.svg [CC-SA-3.0, by Λua∫Wise (Operibus anteire)]. Rest |denovo|.
settings.png	                Modified from
                                https://www.clker.com/clipart-gear-grey.html
                                (public domain, as per
                                http://www.clker.com/disclaimer.html).
spanner.png	                    |denovo|
speaker_playing.png	            |denovo|
speaker.png	                    |denovo|
stop.png	                    |denovo|
time_now.png	                |denovo|
treeview.png	                |denovo|
unlocked.png	                Modified from
                                https://commons.wikimedia.org/wiki/File:Ambox_padlock_gray.svg
                                (by User:HuBoro; public domain).
upload.png	                    Globe from https://openclipart.org/download/121609/1298353280.svg (public domain, as per https://openclipart.org/share). Server from https://commons.wikimedia.org/wiki/File:Server-database-mysql.svg, in turn from https://commons.wikimedia.org/wiki/File:Drive-harddisk.svg (by Sasa Stefanovic; public domain).
vline.png	                    |denovo|
warning.png	                    |denovo|
whisker.png	                    |denovo|
zoom.png	                    Modified from https://commons.wikimedia.org/wiki/File:Magnifying_glass_icon.svg (by Derferman; public domain).
=============================== ===============================================
