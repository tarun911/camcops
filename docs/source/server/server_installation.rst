..  docs/source/server/server_installation.rst

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

.. _server_installation:

Installing CamCOPS on the server
================================

Hardware and operating system requirements
------------------------------------------

The CamCOPS server is cross-platform software written in Python. It’s been
tested primarily under Linux with MySQL.

URLs for CamCOPS source code
----------------------------

- https://github.com/RudolfCardinal/camcops (for source)

.. TODO: https://pypi.io/project/XXX/ (for pip install XXX)

Installing CamCOPS
------------------

See :ref:`Linux flavours <linux_flavours>` for a reminder of some common
differences between Linux operating systems.

Ubuntu installation from Debian package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install CRATE and all its dependencies, download the Debian package and use
gdebi:

.. code-block:: bash

    $ sudo gdebi camcops-VERSION.deb

where :code:`VERSION` is the CamCOPS version you're installing.
(If you don’t have gdebi, install it with :code:`sudo apt-get install gdebi`.)

CamCOPS will now be installed in `/usr/share/camcops`.

You should be able to type ``camcops`` and see something relevant.

CentOS installation from RPM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, to get Centos 6.5 to a basic standard, :ref:`see here
<centos65_prerequisites>`. Then:

.. code-block:: bash

    sudo yum install camcops_VERSION.noarch.rpm

    # Or, for more verbosity and to say yes to everything, use this command instead:
    # sudo yum --assumeyes --verbose --rpmverbosity=debug install camcops_VERSION.noarch.rpm
    # ... but, curiously, yum temporarily swallows the output from the post-install
    #     scripts and only spits it out at the end. This makes it look like the
    #     installation has got stuck (because packages like numpy are very slow
    #     to install); use "watch pstree" or "top" to reassure yourself
    #     that progress is indeed happening.

You should be able to type ``camcops`` and see something relevant.

Windows prerequisites
~~~~~~~~~~~~~~~~~~~~~

- Install Python (see :ref:`Installing Python for Windows
  <windows_install_python>`).

- Install ImageMagick (see :ref:`Installing ImageMagick for Windows
  <windows_install_imagemagick>`).

Generic installation for any OS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Create and activate a Python 3.5+ virtual environment:

    .. code-block:: bash

        export CAMCOPS_VENV=~/dev/camcops_venv
        python3 -m venv $CAMCOPS_VENV
        . $CAMCOPS_VENV/bin/activate

- Install the CamCOPS server package:

    .. code-block:: bash

        pip install camcops-server

.. todo:: sort out MySQL dependencies and/or provide database driver advice

.. todo:: implement Windows service

Installing other prerequisites
------------------------------

For example, you might be running Ubuntu and want to use Apache as your
front-end web server and MySQL as your database:

.. code-block:: bash

    sudo apt-get install apache2 mysql-client mysql-server

See also the :ref:`more detailed MySQL configuration tips <linux_mysql_setup>`.


Specimen installations
======================

Ubuntu 18.04 LTS
----------------

.. todo:: write Ubuntu specimen installation



.. _server_installation_win10_specimen:

Windows 10
----------

- Install Python (see :ref:`Installing Python for Windows
  <windows_install_python>`).

- Install ImageMagick (see :ref:`Installing ImageMagick for Windows
  <windows_install_imagemagick>`).

- Install a database package, create a database, and create an ODBC connection
  to that database.

  - For SQL Server, see :ref:`Creating an SQL Server database
    <windows_create_sql_server_database>`.

- Install the CamCOPS server and a suitable database driver.

  .. code-block:: bat

    REM -----------------------------------------------------------------------
    REM Make and activate a Python virtual environment
    REM (Note that old versions of pip may fail, so upgrade just in case.)
    REM -----------------------------------------------------------------------
    \python36\python.exe -m venv \some_path\camcops_venv
    \some_path\camcops_venv\Scripts\activate.bat
    python -m pip install --upgrade pip

    REM -----------------------------------------------------------------------
    REM Install the CamCOPS server
    REM -----------------------------------------------------------------------
    REM pip install camcops_server
    REM or install from a cloned git repository:
    cd \some_path
    git clone <REPOSITORY_URL>
    cd camcops\server
    pip install -e .

    REM -----------------------------------------------------------------------
    REM Install suitable database drivers
    REM -----------------------------------------------------------------------
    pip install pyodbc

    REM -----------------------------------------------------------------------
    REM Create/edit a default config file
    REM -----------------------------------------------------------------------
    camcops_server demo_camcops_config > \some_path\my_camcops_config.ini

  .. note::

      If you get the error ``ImportError: No module named 'tkinter'``, then you
      probably said no to installing tk/tkinter when installing Python. Run the
      installer again and say yes (e.g. :menuselection:`Python 3.6.7 (64-bit)
      Setup --> Modify --> [✓] tcl/tk and IDLE: Installs tkinter and the IDLE
      development environment --> Next --> Install`).

  .. note::

      If you get the error ``TypeError: descriptor '__subclasses__' of 'type'
      object needs an argument``, using Python 3.5, then this is a Python bug;
      upgrade to Python 3.5.3+ as per
      https://github.com/python/typing/issues/266.

- Edit the configuration file. In particular, as an absolute minimum you must
  set:

  - ``DB_URL``

- Create the database structure:

  .. code-block:: bat

    camcops_server upgrade_db --config \some_path\my_camcops_config.ini

  You should specify this filename as an **absolute** path (Alembic does some
  directory changing that makes relative filenames fail!).

  .. todo:: Current Windows problems: SQL DELETE taking forever during
     ``upgrade_db``. Probably to do with constraints/triggers. Temporary
     workaround: use ``create_db`` instead. (However, the ``reindex`` command
     works fine.)

- Create a superuser

  .. code-block:: bat

    camcops_server make_superuser

- Create a dummy ("snake oil") SSL certificate and key, with some variation on
  this theme:

  .. code-block:: bat

    openssl req ^
        -nodes ^
        -new ^
        -x509 ^
        -keyout dummy_ssl_private_key.key ^
        -out dummy_ssl_certificate.cert ^
        -subj "/C=UK/ST=my_state/L=my_location/O=CamCOPS testing/CN=Forename Surname"

    REM Note that the country code (in this case "UK") must be 2 characters max.

- Launch a test server like this (directly or via a batch file):

  .. code-block:: bat

    @echo off

    set IP_ADDR=127.0.0.1
    set PORT=8088
    set SSL_CERTIFICATE=C:\some_path\dummy_ssl_certificate.cert
    set SSL_KEY=C:\some_path\dummy_ssl_private_key.key
    set CAMCOPS_CONFIG_FILE=C:\some_path\test_camcops_config.ini

    REM Config location will be read directly from environment variable.
    REM Could also specify it with --config.

    camcops_server serve_cherrypy ^
        --host %IP_ADDR% ^
        --port %PORT% ^
        --debug_toolbar ^
        --verbose ^
        --ssl_certificate %SSL_CERTIFICATE% ^
        --ssl_private_key %SSL_KEY%

- Browse to https://127.0.0.1:8088/ to test it.

- Create some ID number definitions, and a group. Ensure you have a user that
  is uploading to that group.

- Install the CamCOPS client. Configure and register it. Test settings:

  - Server address: ``127.0.0.1``
  - Server port: ``8088``
  - Path on server: ``database``
  - Validate HTTPS certificates? ``No``
