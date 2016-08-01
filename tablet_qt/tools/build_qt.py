#!/usr/bin/env python3

"""
When is it NECESSARY to compile OpenSSL from source?
    - OpenSSL for Android
      http://doc.qt.io/qt-5/opensslsupport.html
      ... so: necessary.

When is it NECESSARY to compile Qt from source?
    - Static linking of OpenSSL (non-critical)
    - SQLite support (critical)
      http://doc.qt.io/qt-5/sql-driver.html
      ... so: necessary.
"""

# configure: http://doc.qt.io/qt-5/configure-options.html
# sqlite: http://doc.qt.io/qt-5/sql-driver.html
# build for Android: http://wiki.qt.io/Qt5ForAndroidBuilding
# multi-core builds: http://stackoverflow.com/questions/9420825/how-to-compile-on-multiple-cores-using-mingw-inside-qtcreator  # noqa

import argparse
import logging
import os
from os.path import abspath, expanduser, isdir, isfile, join, split
import subprocess
import sys
import urllib.request

log = logging.getLogger(__name__)


def run(args, env=None):
    log.info("Running external command: {}".format(args))
    if env is not None:
        log.info("Using environment: {}".format(env))
    subprocess.check_call(args, env=env)


def replace(filename, text_from, text_to):
    log.info("Amending {} from {} to {}".format(
        filename, repr(text_from), repr(text_to)))
    with open(filename) as infile:
        contents = infile.read()
    contents = contents.replace(text_from, text_to)
    with open(filename, 'w') as outfile:
        outfile.write(contents)


def replace_multiple(filename, replacements):
    with open(filename) as infile:
        contents = infile.read()
    for text_from, text_to in replacements:
        log.info("Amending {} from {} to {}".format(
            filename, repr(text_from), repr(text_to)))
        contents = contents.replace(text_from, text_to)
    with open(filename, 'w') as outfile:
        outfile.write(contents)


def mkdir_p(path):
    log.info("mkdir -p {}".format(path))
    os.makedirs(path, exist_ok=True)


def download_if_not_exists(url, filename):
    if isfile(filename):
        log.info("Already have: {}".format(filename))
        return
    dir, basename = split(abspath(filename))
    mkdir_p(dir)
    log.info("Downloading from {} to {}".format(url, filename))
    urllib.request.urlretrieve(url, filename)


def fetch_qt(args):
    if isdir(args.qt_src_gitdir):
        log.info("Using Qt source in {}".format(args.qt_src_gitdir))
        return
    log.info("Fetching Qt source from {} into {}".format(args.qt_git_url,
                                                         args.qt_src_gitdir))
    os.chdir(args.src_rootdir)
    run(["git", "clone", args.qt_git_url])
    os.chdir(args.qt_src_gitdir)
    run(["perl", "init-repository"])


def fetch_openssl(args):
    download_if_not_exists(args.openssl_src_url, args.openssl_src_fullpath)
    #download_if_not_exists(args.openssl_android_script_url,
    #                       args.openssl_android_script_fullpath)


def get_openssl_android_rootdir_workdir(args, cpu):
    rootdir = join(args.root_dir, "openssl_android_{}_build".format(cpu))
    workdir = join(rootdir, args.openssl_version)
    return rootdir, workdir


def root_path():
    # http://stackoverflow.com/questions/12041525
    return os.path.abspath(os.sep)


def build_openssl_android(args, cpu):
    rootdir, workdir = get_openssl_android_rootdir_workdir(args, cpu)
    targets = [join(workdir, "libssl.so"),
               join(workdir, "libcrypto.so")]
    if all(isfile(x) for x in targets):
        log.info("OpenSSL: All targets exist already: {}".format(targets))
        return

    # https://wiki.openssl.org/index.php/Android
    # We're not using the Setenv-android.sh script, but replicating its
    # functions.
    android_arch_short = cpu
    android_arch_full = "arch-{}".format(android_arch_short)  # e.g. arch-x86
    if cpu == "x86":
        android_eabi = "{}-{}".format(android_arch_short,
                                      args.toolchain_version)  # e.g. x86-4.9
        # For toolchain version: ls $ANDROID_NDK_ROOT/toolchains
        # ... "-android-arch" and "-android-toolchain-version" get
        # concatenated, I think; for example, this gives the toolchain
        # "x86_64-4.9"
    else:
        # but ARM ones look like "arm-linux-androideabi-4.9"
        android_eabi = "{}-linux-androideabi-{}".format(android_arch_short,
                                                        args.toolchain_version)
    android_sysroot = join(args.android_ndk_root, "platforms",
                           args.android_api, android_arch_full)
    android_toolchain = join(args.android_ndk_root, "toolchains", android_eabi,
                             "prebuilt", args.ndk_host, "bin")

    # http://doc.qt.io/qt-5/opensslsupport.html
    if cpu == "armv5":
        target_os = "android"
    elif cpu == "arm":
        target_os = "android-armv7"
    else:
        target_os = "android-{}".format(cpu)

    # env = os.environ.copy()
    env = {  # clean environment
        'PATH': os.environ['PATH'],
    }
    mkdir_p(rootdir)
    run(["tar", "-xvf", args.openssl_src_fullpath, "-C", rootdir])

    # https://wiki.openssl.org/index.php/Android
    makefile_org = join(workdir, "Makefile.org")
    replace(makefile_org,
            "install: all install_docs install_sw",
            "install: install_docs install_sw")

    os.chdir(workdir)

    # The OpenSSL "config" sh script guesses the OS, then passes details
    # to its "Configure" Perl script.
    # For Android, OpenSSL suggest using their Setenv-android.sh script, then
    # running "config".
    # However, it does seem to be screwing up. Let's try Configure instead.

    common_ssl_config_options = [
        "shared",  # make .so files (needed by Qt sometimes) as well as .a
        "no-ssl2",  # SSL-2 is broken
        "no-ssl3",  # SSL-3 is broken. Is an SSL-3 build required for TLS 1.2?
        # "no-comp",  # disable compression independent of zlib
        "no-hw",  # disable hardware support ("useful on mobile devices")
        "no-engine",  # disable hardware support ("useful on mobile devices")
    ]

    env["ANDROID_API"] = args.android_api
    env["ANDROID_ARCH"] = android_arch_full
    env["ANDROID_DEV"] = join(android_sysroot, "usr")
    env["ANDROID_EABI"] = android_eabi
    env["ANDROID_NDK_ROOT"] = args.android_ndk_root
    env["ANDROID_SDK_ROOT"] = args.android_sdk_root
    env["ANDROID_SYSROOT"] = android_sysroot
    env["ANDROID_TOOLCHAIN"] = android_toolchain
    env["ARCH"] = cpu
    # env["CROSS_COMPILE"] = "i686-linux-android-"
    env["FIPS_SIG"] = ""  # OK to leave blank if not building FIPS
    env["HOSTCC"] = "gcc"
    env["MACHINE"] = "i686"
    env["NDK_SYSROOT"] = android_sysroot
    env["PATH"] = "{}{}{}".format(android_toolchain, os.pathsep, env["PATH"])
    env["RELEASE"] = "2.6.37"  # ??
    env["SYSROOT"] = android_sysroot
    env["SYSTEM"] = target_os  # ... NB "android" means ARMv5

    use_configure = True
    if use_configure:
        # ---------------------------------------------------------------------
        # Configure
        # ---------------------------------------------------------------------
        # http://doc.qt.io/qt-5/opensslsupport.html
        env["ANDROID_DEV"] = join(android_sysroot, "usr")
        if cpu == "x86":
            cc_prefix = "i686"
        else:
            cc_prefix = "arm"
        if cpu == "x86":
            env["CC"] = join(
                android_toolchain,
                "i686-linux-android-gcc-{}".format(args.toolchain_version)
            )
            env["AR"] = join(android_toolchain, "i686-linux-android-gcc-ar")
        else:
            env["CC"] = join(
                android_toolchain,
                "arm-linux-androideabi-gcc-{}".format(args.toolchain_version)
            )
            env["AR"] = join(android_toolchain, "arm-linux-androideabi-gcc-ar")
        configure_args = [
            "shared",
            target_os,
        ] + common_ssl_config_options
        # print(env)
        # sys.exit(1)
        run(["perl", join(workdir, "Configure")] + configure_args, env)

    else:
        # ---------------------------------------------------------------------
        # config
        # ---------------------------------------------------------------------
        # https://wiki.openssl.org/index.php/Android
        # and "If in doubt, on Unix-ish systems use './config'."

        # https://wiki.openssl.org/index.php/Compilation_and_Installation
        config_args = [
            target_os,
        ] + common_ssl_config_options
        run([join(workdir, "config")] + config_args, env)

    # Have to remove version numbers from final library filenames:
    # http://doc.qt.io/qt-5/opensslsupport.html
    makefile = join(workdir, "Makefile")
    replace_multiple(makefile, [
        ('LIBNAME=$$i LIBVERSION=$(SHLIB_MAJOR).$(SHLIB_MINOR)',
            'LIBNAME=$$i'),
        ('LIBCOMPATVERSIONS=";$(SHLIB_VERSION_HISTORY)"', ''),
    ])
    run(["make", "depend"], env)
    run(["make", "build_libs"], env)

    # Testing:
    # - "Have I built for the right architecture?"
    #   http://stackoverflow.com/questions/267941
    #   http://stackoverflow.com/questions/1085137
    #
    #   file libssl.so
    #   objdump -a libssl.so  # or -x, or...
    #   readelf -h libssl.so
    #
    # - Compare to files on the Android emulator:
    #
    #   adb pull /system/lib/libz.so  # system
    #   adb pull /data/data/org.camcops.camcops_tablet_qt/lib/  # ours
    #
    # ... looks OK


def build_qt_android(args, cpu, static_openssl=False, verbose=True):
    # For testing a new OpenSSL build, have static_openssl=False, or you have
    # to rebuild Qt every time... extremely slow.

    # Android example at http://wiki.qt.io/Qt5ForAndroidBuilding
    # http://doc.qt.io/qt-5/opensslsupport.html
    # Windows: ?also http://simpleit.us/2010/05/30/enabling-openssl-for-qt-c-on-windows/  # noqa

    opensslrootdir, opensslworkdir = get_openssl_android_rootdir_workdir(
        args, cpu)
    openssl_include_root = join(opensslworkdir, "include")
    openssl_lib_root = opensslworkdir
    if cpu == "x86":
        android_arch_short = cpu
    elif cpu == "arm":
        android_arch_short = "armeabi-v7a"
    else:
        raise ValueError("Unknown cpu: {}".format(cpu))

    builddir = join(args.root_dir, "qt_android_{}_build".format(cpu))
    installdir = join(args.root_dir, "qt_android_{}_install".format(cpu))

    targets = [join(installdir, "bin", "qmake")]
    if all(isfile(x) for x in targets):
        log.info("Qt: All targets exist already: {}".format(targets))
        return installdir

    # env = os.environ.copy()
    env = {  # clean environment
        'PATH': os.environ['PATH'],
    }
    env["OPENSSL_LIBS"] = "-L{} -lssl -lcrypto".format(openssl_lib_root)
    # ... unnecessary? But suggested by Qt.

    log.info("Configuring Android {} build in {}".format(cpu, builddir))
    mkdir_p(builddir)
    mkdir_p(installdir)
    os.chdir(builddir)
    qt_config_args = [
        join(args.qt_src_gitdir, "configure"),
        "-android-sdk", args.android_sdk_root,
        "-android-ndk", args.android_ndk_root,
        "-android-ndk-host", args.ndk_host,
        "-android-arch", android_arch_short,
        "-android-toolchain-version", args.toolchain_version,
        "-I", openssl_include_root,  # OpenSSL
        "-L", openssl_lib_root,  # OpenSSL
        "-opensource", "-confirm-license",
        "-prefix", installdir,
        "-qt-sql-sqlite",  # SQLite
        "-no-warnings-are-errors",
        "-nomake", "tests",
        "-nomake", "examples",
        "-skip", "qttranslations",
        "-skip", "qtwebkit",
        "-skip", "qtserialport",
        "-skip", "qtwebkit-examples",
        "-xplatform", "android-g++",
    ]
    if static_openssl:
        qt_config_args.append("-openssl-linked")  # OpenSSL
    else:
        qt_config_args.append("-openssl")  # OpenSSL
    if verbose:
        qt_config_args.append("-v")  # verbose
    run(qt_config_args)  # The configure step takes a few seconds.

    log.info("Making Qt Android {} build into {}".format(cpu, installdir))
    os.chdir(builddir)
    env["ANDROID_API_VERSION"] = args.android_api
    env["ANDROID_NDK_ROOT"] = args.android_ndk_root
    env["ANDROID_SDK_ROOT"] = args.android_sdk_root
    run(["make"], env)  # The make step takes a few hours.

    # PROBLEM WITH "make install":
    #       mkdir: cannot create directory ‘/libs’: Permission denied
    # ... while processing qttools/src/qtplugininfo/Makefile
    # https://bugreports.qt.io/browse/QTBUG-45095
    # 1. Attempt to fix as follows:
    makefile = join(builddir, "qttools", "src", "qtplugininfo", "Makefile")
    baddir = join("$(INSTALL_ROOT)", "libs", android_arch_short, "")
    gooddir = join(installdir, "libs", android_arch_short, "")
    replace(makefile, " " + baddir, " " + gooddir)

    # 2. Using INSTALL_ROOT: bases the root of a filesystem off installdir
    # env["INSTALL_ROOT"] = installdir
    # http://stackoverflow.com/questions/8360609

    run(["make", "install"], env)
    # ... installs to installdir because of -prefix earlier
    return installdir


def main():
    logging.basicConfig(level=logging.DEBUG)
    user_dir = expanduser("~")

    # CPU/architecture
    default_cpus = [
        "x86",  # for a fast emulator under Linux
        "arm",  # for real Android devices (armeabi-v7a)
    ]

    # Android
    default_android_api_num = 23
    default_root_dir = join(user_dir, "dev", "qt_local_build")
    default_android_sdk = join(user_dir, "dev", "android-sdk-linux")
    default_android_ndk = join(user_dir, "dev", "android-ndk-r11c")
    default_ndk_host = "linux-x86_64"
    default_toolchain_version = "4.9"

    # Qt
    default_qt_src_dirname = "qt5"
    default_qt_git_url = "git://code.qt.io/qt/qt5.git"

    # OpenSSL
    default_openssl_version = "openssl-1.0.2h"
    default_openssl_src_url = (
        "https://www.openssl.org/source/{}.tar.gz".format(
            default_openssl_version))
    #default_openssl_android_script = "Setenv-android.sh"
    #default_openssl_android_script_url = (
    #    "https://wiki.openssl.org/images/7/70/{}".format(
    #        default_openssl_android_script))

    parser = argparse.ArgumentParser(description="Build Qt for CamCOPS")

    parser.add_argument(
        "--cpus", nargs="*", default=default_cpus,
        help="CPUs to build for (default: {})".format(default_cpus))

    # Qt
    parser.add_argument(
        "--root_dir", default=default_root_dir,
        help="Root directory for source and builds (default: {})".format(
            default_root_dir))
    parser.add_argument(
        "--qt_src_dirname", default=default_qt_src_dirname,
        help="Qt source directory (default: {})".format(
            default_qt_src_dirname))
    parser.add_argument(
        "--qt_git_url", default=default_qt_git_url,
        help="Qt Git URL (default: {})".format(default_qt_git_url))

    # Android
    parser.add_argument(
        "--android_api_number", type=int, default=default_android_api_num,
        help="Android API number (default: {})".format(
            default_android_api_num))
    parser.add_argument(
        "--android_sdk_root", default=default_android_sdk,
        help="Android SDK root directory (default: {})".format(
            default_android_sdk))
    parser.add_argument(
        "--android_ndk_root", default=default_android_ndk,
        help="Android NDK root directory (default: {})".format(
            default_android_ndk))
    parser.add_argument(
        "--ndk_host", default=default_ndk_host,
        help="Android NDK host architecture (default: {})".format(
            default_ndk_host))
    parser.add_argument(
        "--toolchain_version", default=default_toolchain_version,
        help="Android toolchain version (default: {})".format(
            default_toolchain_version))

    # OpenSSL
    parser.add_argument(
        "--openssl_version", default=default_openssl_version,
        help="OpenSSL version (default: {})".format(default_openssl_version))
    parser.add_argument(
        "--openssl_src_url", default=default_openssl_src_url,
        help="OpenSSL source URL (default: {})".format(
            default_openssl_src_url))
    #parser.add_argument(
    #    "--openssl_android_script", default=default_openssl_android_script,
    #    help="OpenSSL Android assistance script name (default: {})".format(
    #        default_openssl_android_script))
    #parser.add_argument(
    #    "--openssl_android_script_url",
    #    default=default_openssl_android_script_url,
    #    help="OpenSSL Android assistance script download URL "
    #         "(default: {})".format(default_openssl_android_script_url))

    args = parser.parse_args()

    # Calculated args

    args.src_rootdir = join(args.root_dir, "src")
    args.qt_src_gitdir = join(args.src_rootdir, args.qt_src_dirname)

    args.android_api = "android-{}".format(args.android_api_number)
    # see $ANDROID_SDK_ROOT/platforms/

    args.openssl_tar_dir = join(args.src_rootdir, "openssl")
    args.openssl_src_dir = join(args.src_rootdir, args.openssl_version)
    args.openssl_src_filename = "{}.tar.gz".format(args.openssl_version)
    args.openssl_src_fullpath = join(args.openssl_src_dir,
                                     args.openssl_src_filename)
    #args.openssl_android_script_fullpath = join(args.openssl_src_dir,
    #                                            args.openssl_android_script)

    log.info(args)

    # =========================================================================
    # Fetch
    # =========================================================================
    fetch_qt(args)
    fetch_openssl(args)

    # =========================================================================
    # Build
    # =========================================================================
    installdirs = []
    for cpu in args.cpus:
        log.info("Qt shadow build: Android {} +SQLite +OpenSSL".format(cpu))
        build_openssl_android(args, cpu)
        installdir = build_qt_android(args, cpu)
        installdirs.append(installdir)

    print("""
===============================================================================
Now, in Qt Creator:
===============================================================================
1. Add Qt build
      Tools > Options > Build & Run > Qt Versions > Add
      ... browse to one of: {bindirs}
      ... and select "qmake".
2. Create kit
      Tools > Options > Build & Run > Kits > Add (manual)
      ... Qt version = the one you added in the preceding step
      ... compiler = Android GCC (i686-4.9)
      ... debugger = Android Debugger for GCC (i686-4.9)
Then for your project,
      - click on the "Projects" tab
      - Add Kit > choose the kit you created.
      - Build Settings > Android APK > Details > Additional Libraries > Add
    """.format(
        bindirs=", ".join(join(x, "bin") for x in installdirs)
    ))


if __name__ == '__main__':
    main()