; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!
;
; RNC: looks like InnoSetup uses many similar variables names and that's why the
; convention is to use "My" as a prefix for the Innosetup preprocessor (ISPP) add-on.
;
; For simultaneous 32/64-bit use, see
; https://stackoverflow.com/questions/4833831/inno-setup-32bit-and-64bit-in-one

; =============================================================================
; VERSION-DEPENDENT VALUES
; =============================================================================

#define CamcopsClientVersion "2.3.1"

#define OpenSSLVersion "1.1.0g"
#define OpenSSLMajorVersionUnderscores "1_1"

; =============================================================================
; VALUES DEPENDING ON THE DEVELOPER'S BUILD ENVIRONMENT
; =============================================================================

#define CamcopsSourceDir GetEnv("CAMCOPS_SOURCE_DIR")
#if CamcopsSourceDir == ""
    #error "Must define environment variable CAMCOPS_SOURCE_DIR; e.g. D:\dev\camcops"
#endif

#define CamcopsQtBaseDir GetEnv("CAMCOPS_QT_BASE_DIR")
#if CamcopsQtBaseDir == ""
    #error "Must define environment variable CAMCOPS_QT_BASE_DIR; e.g. D:\dev\qt_local_build"
#endif

#define VisualStudioRedistRoot GetEnv("CAMCOPS_VISUAL_STUDIO_REDIST_ROOT")
#if VisualStudioRedistRoot == ""
    #error "Must define environment variable CAMCOPS_VISUAL_STUDIO_REDIST_ROOT; e.g. C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Redist\MSVC\14.14.26405"
#endif

; =============================================================================
; Constants
; =============================================================================

#define CamcopsAppName "CamCOPS"
#define CamcopsAppNameLowerCase "camcops"
#define CamcopsPublisher "Rudolf Cardinal"
#define CamcopsURL "http://www.camcops.org/"

; =============================================================================
; Derived variables
; =============================================================================

; It looks like ISPP can't do a #define involving an existing #define...
; ... but you can define macros and compositions.
; So this fails: #define MyAppExeName "{#CamcopsAppNameLowerCase}.exe"
; But this works: #define MyAppExeName CamcopsAppNameLowerCase + ".exe"

#define MyAppExeName CamcopsAppNameLowerCase + ".exe"
#define InstallableOutputDir CamcopsSourceDir + "\distributables"
#define SrcTabletDir CamcopsSourceDir + "\tablet_qt"
; Note that the next two lines presuppose that you have used the suggested name
; for the Qt kits.
#define SrcBuild32Dir CamcopsSourceDir + "\build-camcops-Custom_Windows_x86_32-Release\release"
#define SrcBuild64Dir CamcopsSourceDir + "\build-camcops-Custom_Windows_x86_64-Release\release"
#define SrcExe32 SrcBuild32Dir + "\" + CamcopsAppNameLowerCase + ".exe"
#define SrcExe64 SrcBuild64Dir + "\" + CamcopsAppNameLowerCase + ".exe"
#define LibCrypto32 CamcopsQtBaseDir + "\openssl_windows_x86_32_build\openssl-" + OpenSSLVersion + "\libcrypto-" + OpenSSLMajorVersionUnderscores + ".dll"
#define LibCrypto64 CamcopsQtBaseDir + "\openssl_windows_x86_64_build\openssl-" + OpenSSLVersion + "\libcrypto-" + OpenSSLMajorVersionUnderscores + "-x64.dll"
#define LibSSL32 CamcopsQtBaseDir + "\openssl_windows_x86_32_build\openssl-" + OpenSSLVersion + "\libssl-" + OpenSSLMajorVersionUnderscores + ".dll"
#define LibSSL64 CamcopsQtBaseDir + "\openssl_windows_x86_64_build\openssl-" + OpenSSLVersion + "\libssl-" + OpenSSLMajorVersionUnderscores + "-x64.dll"
#define IconName CamcopsAppNameLowerCase + ".ico"
#define SrcIconFilename SrcTabletDir + "\windows\" + IconName
#define VCRedist32Name "vcredist_x86.exe"
#define VCRedist64Name "vcredist_x64.exe"
#define SrcVCRedist32 VisualStudioRedistRoot + "\" + VCRedist32Name
#define SrcVCRedist64 VisualStudioRedistRoot + "\" + VCRedist64Name

; =============================================================================
[Setup]
; =============================================================================
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{29B3F489-C33C-4915-A3DB-DEA9F53E2E79}
AppName={#CamcopsAppName}
AppVersion={#CamcopsClientVersion}
AppVerName={#CamcopsAppName} {#CamcopsClientVersion}
AppPublisher={#CamcopsPublisher}
AppPublisherURL={#CamcopsURL}
AppSupportURL={#CamcopsURL}
AppUpdatesURL={#CamcopsURL}
Compression=lzma
DefaultDirName={pf}\{#CamcopsAppName}
DefaultGroupName={#CamcopsAppName}
DisableProgramGroupPage=yes
LicenseFile={#CamcopsSourceDir}\LICENSE.txt
OutputDir={#InstallableOutputDir}
OutputBaseFilename={#CamcopsAppNameLowerCase}_{#CamcopsClientVersion}_windows
SetupIconFile={#SrcIconFilename}
SolidCompression=yes
UninstallDisplayIcon={app}\{#IconName}

; "ArchitecturesInstallIn64BitMode=x64" requests that the install be
; done in "64-bit mode" on x64, meaning it should use the native
; 64-bit Program Files directory and the 64-bit view of the registry.
; On all other architectures it will install in "32-bit mode".
ArchitecturesInstallIn64BitMode=x64
; Note: We don't set ProcessorsAllowed because we want this
; installation to run on all architectures (including Itanium,
; since it's capable of running 32-bit code too).

; =============================================================================
[Languages]
; =============================================================================
Name: "english"; MessagesFile: "compiler:Default.isl"

; =============================================================================
[Tasks]
; =============================================================================
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
; ... use "Flags: unchecked" to disable by default

; =============================================================================
[Files]
; =============================================================================
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

; Main executable.
; Install 64-bit version if running in 64-bit mode (x64; see above), otherwise 32-bit version.
Source: "{#SrcExe32}"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion; Check: not Is64BitInstallMode
Source: "{#SrcExe64}"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion; Check: Is64BitInstallMode

; We need libcrypto and libssl too.
Source: "{#LibCrypto32}"; DestDir: "{app}"; Flags: ignoreversion; Check: not Is64BitInstallMode
Source: "{#LibCrypto64}"; DestDir: "{app}"; Flags: ignoreversion; Check: Is64BitInstallMode
Source: "{#LibSSL32}"; DestDir: "{app}"; Flags: ignoreversion; Check: not Is64BitInstallMode
Source: "{#LibSSL64}"; DestDir: "{app}"; Flags: ignoreversion; Check: Is64BitInstallMode

; We also need VCRUNTIME140.DLL, and presumably the version of the Visual C++ redistributable is the one from our compiler.
Source: "{#SrcVCRedist32}"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: VCRedist32NeedsInstall
Source: "{#SrcVCRedist64}"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: VCRedist64NeedsInstall

; Other files:
Source: "{#SrcIconFilename}"; DestDir: "{app}"; DestName: "{#IconName}"
; Source: "Readme.txt"; DestDir: "{app}"; Flags: isreadme

; =============================================================================
[Icons]
; =============================================================================
; The "[Icons]" section means "shortcuts".
Name: "{commonprograms}\{#CamcopsAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#IconName}"
Name: "{commondesktop}\{#CamcopsAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#IconName}"; Tasks: desktopicon

; =============================================================================
[Run]
; =============================================================================
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(CamcopsAppName, '&', '&&')}}"; \
    Flags: nowait postinstall skipifsilent

; https://stackoverflow.com/questions/24574035/how-to-install-microsoft-vc-redistributables-silently-in-inno-setup
; http://asawicki.info/news_1597_installing_visual_c_redistributable_package_from_command_line.html
Filename: "{tmp}\{#VCRedist32Name}"; \
    Parameters: "/install /passive /norestart"; \
    Check: VCRedist32NeedsInstall; \
    StatusMsg: "Installing Visual C++ 2017 32-bit redistributables..."
Filename: "{tmp}\{#VCRedist64Name}"; \
    Parameters: "/install /passive /norestart"; \
    Check: VCRedist64NeedsInstall; \
    StatusMsg: "Installing Visual C++ 2017 64-bit redistributables..."

// ============================================================================
[Code]
// ============================================================================
// https://stackoverflow.com/questions/11137424/how-to-make-vcredist-x86-reinstall-only-if-not-yet-installed/11172939#11172939
// https://pingfu.net/how-to-detect-which-version-of-visual-c-runtime-is-installed
// https://stackoverflow.com/questions/12206314/detect-if-visual-c-redistributable-for-visual-studio-2012-is-installed
#IFDEF UNICODE
  #DEFINE AW "W"
#ELSE
  #DEFINE AW "A"
#ENDIF
type
  INSTALLSTATE = Longint;
const
  INSTALLSTATE_INVALIDARG = -2;  // An invalid parameter was passed to the function.
  INSTALLSTATE_UNKNOWN = -1;     // The product is neither advertised or installed.
  INSTALLSTATE_ADVERTISED = 1;   // The product is advertised but not installed.
  INSTALLSTATE_ABSENT = 2;       // The product is installed for a different user.
  INSTALLSTATE_DEFAULT = 5;      // The product is installed for the current user.

  // RNC:
  // Visual C++ 2017 Redistributable 14.14.26405.0
  VC_2017_REDIST_14_14_26405_X86_MINIMUM_RUNTIME = '{ec9c2282-a836-48a6-9e41-c2f0bf8d678b}';
  // ... value taken from the installation log
  // ... also from "Add or remove programs" -> "Microsoft Visual C++ 2017 Redistributable
  //     (x86) - 14.14.26405 / 14.14.26405.0" -> "Modify" -> "Show more details".
  // ... NOT SURE IF THIS ONE IS WORKING; problem may be the use of a 64-bit installer
  //     (thus maybe calling a 64-bit msi.dll and getting a different answer??).
  // Worst case is that the redistributable gets installed twice, though.
  VC_2017_REDIST_14_14_26405_X64_MINIMUM_RUNTIME = '{BCA8F863-9BAB-3398-B8E4-E1D0959D0943}';
  // ... value taken from the installation log

function MsiQueryProductState(szProduct: string): INSTALLSTATE; 
  external 'MsiQueryProductState{#AW}@msi.dll stdcall';

function VCVersionInstalled(const ProductID: string): Boolean;
begin
  Result := MsiQueryProductState(ProductID) = INSTALLSTATE_DEFAULT;
end;

function deactivated_InitializeSetup: Boolean;
// When named InitializeSetup, this overrides an Inno Setup built-in function.
// Return False to abort setup, True otherwise.
// Rename it to deactivate.
var
  S: string;
  State: INSTALLSTATE;
begin
  Result := False;
  State := MsiQueryProductState(VC_2017_REDIST_14_14_26405_X86_MINIMUM_RUNTIME);
  // State := MsiQueryProductState(VC_2017_REDIST_14_14_26405_X64_MINIMUM_RUNTIME);
  case State of
    INSTALLSTATE_INVALIDARG: S := 'INSTALLSTATE_INVALIDARG: An invalid parameter was passed to the function.';
    INSTALLSTATE_UNKNOWN: S := 'INSTALLSTATE_UNKNOWN: The product is neither advertised or installed.';
    INSTALLSTATE_ADVERTISED: S := 'INSTALLSTATE_ADVERTISED: The product is advertised but not installed.';
    INSTALLSTATE_ABSENT: S := 'INSTALLSTATE_ABSENT: The product is installed for a different user.';
    INSTALLSTATE_DEFAULT: S := 'INSTALLSTATE_DEFAULT: The product is installed for the current user.';
  else
    S := IntToStr(State) + 'Unexpected result';
  end;
  MsgBox(S, mbInformation, MB_OK);
end;

function VCRedist32NeedsInstall: Boolean;
begin
  Result := (not Is64BitInstallMode) and (not VCVersionInstalled(VC_2017_REDIST_14_14_26405_X86_MINIMUM_RUNTIME));
end;

function VCRedist64NeedsInstall: Boolean;
begin
  Result := Is64BitInstallMode and (not VCVersionInstalled(VC_2017_REDIST_14_14_26405_X64_MINIMUM_RUNTIME));
end;

// https://stackoverflow.com/questions/11187022/inno-script-how-to-make-i-accept-the-agreement-radio-button-on-eula-page-sel
// procedure InitializeWizard;
// begin
//   WizardForm.LicenseAcceptedRadio.Checked := True;
// end;
