;**
;* This installer is created to install the binary version of iSpector
;* on a windows system.
;*/

SetCompressor /SOLID /FINAL zlib

!include LogicLib.nsh
!include MUI2.nsh

;----- Definitions of some constants

!define MY_PROGRAM_NAME     "iSpector"
!define MY_ORGANISATION     "Uil_OTS"
!define MY_ICON_DIR         "logo"
!define MY_ICON             "${MY_ICON_DIR}\ispectorlogo.ico"

; Don't update these three variables, this should be done with bump-version.py.
!define MY_VERSION_MAJOR "0"
!define MY_VERSION_MINOR "5"
!define MY_VERSION_MICRO "1"

; Full application name include major and minor versions, in such way
; the versions with different major and minor version can live together.
!define FULL_APP_NAME "${MY_PROGRAM_NAME}-${MY_VERSION_MAJOR}.${MY_VERSION_MINOR}"

; Path to registry where uninstall info is stored.
!define REGISTRY_UN_PATH    "Software\Microsoft\Windows\CurrentVersion\Uninstall\"

;
; ---- These must be defined for the gui to work
;


; uninstaller settings
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; installer settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE   "LICENSE"
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE       "English" 

;
; ------- text strings for the mui
;

; Strings for the welcome page
LangString MUI_TEXT_WELCOME_INFO_TITLE  ${LANG_ENGLISH} "${FULL_APP_NAME}-installer"
LangString MUI_TEXT_WELCOME_INFO_TEXT   ${LANG_ENGLISH} "Welcome by the ${FULL_APP_NAME} installer."

; Strings for the license page
LangString MUI_INNERTEXT_LICENSE_BOTTOM ${LANG_ENGLISH} "Innertext license bottom"
LangString MUI_INNERTEXT_LICENSE_TOP    ${LANG_ENGLISH} "Innertext license top"
LangString MUI_TEXT_LICENSE_TITLE       ${LANG_ENGLISH} "GPL2 license"
LangString MUI_TEXT_LICENSE_SUBTITLE    ${LANG_ENGLISH} "Do you accept the GPL2 license?"

; Strings for install page
LangString MUI_TEXT_INSTALLING_TITLE    ${LANG_ENGLISH} "Installing"
LangString MUI_TEXT_INSTALLING_SUBTITLE ${LANG_ENGLISH} "Installing: ${FULL_APP_NAME}" 

; Strings for installer finish page
LangString MUI_BUTTONTEXT_FINISH        ${LANG_ENGLISH} "close."
LangString MUI_TEXT_FINISH_TITLE        ${LANG_ENGLISH} "The End!"
LangString MUI_TEXT_FINISH_SUBTITLE     ${LANG_ENGLISH} "Finished installing ${FULL_APP_NAME}"
LangString MUI_TEXT_FINISH_INFO_TITLE   ${LANG_ENGLISH} "Installation is finished"
LangString MUI_TEXT_FINISH_INFO_REBOOT  ${LANG_ENGLISH} "No need to reboot."
LangString MUI_TEXT_FINISH_REBOOTNOW    ${LANG_ENGLISH} "No need to reboot"
LangString MUI_TEXT_FINISH_REBOOTLATER  ${LANG_ENGLISH} "No need to reboot"
LangString MUI_TEXT_FINISH_INFO_TEXT    ${LANG_ENGLISH} "${FULL_APP_NAME} is installed, Goodluck!"

LangString MUI_TEXT_ABORT_TITLE         ${LANG_ENGLISH} "Abort"
LangString MUI_TEXT_ABORT_SUBTITLE      ${LANG_ENGLISH} "Aborting (de-)installation."

;
;--- Strings for uninstall -----
;

;strings for the uninstall welcome page
LangString MUI_UNTEXT_WELCOME_INFO_TITLE    ${LANG_ENGLISH} "Uninstall ${FULL_APP_NAME}"
LangString MUI_UNTEXT_WELCOME_INFO_TEXT     ${LANG_ENGLISH} "You are about to uninstall ${FULL_APP_NAME}!"

;strings for confirm
LangString MUI_UNTEXT_CONFIRM_TITLE         ${LANG_ENGLISH} "Uninstall ${FULL_APP_NAME}"
LangString MUI_UNTEXT_CONFIRM_SUBTITLE      ${LANG_ENGLISH} "Are you sure to uninstall: ${FULL_APP_NAME}"
LangString MUI_UNTEXT_UNINSTALLING_TITLE    ${LANG_ENGLISH} "Uninstalling"
LangString MUI_UNTEXT_UNINSTALLING_SUBTITLE ${LANG_ENGLISH} "Uninstalling ${FULL_APP_NAME}"
LangString MUI_UNTEXT_FINISH_TITLE          ${LANG_ENGLISH} "Finished uninstalling"
LangString MUI_UNTEXT_FINISH_SUBTITLE       ${LANG_ENGLISH} "Finished uninstalling"
LangString MUI_UNTEXT_ABORT_TITLE           ${LANG_ENGLISH} "Abort uninstallation"
LangString MUI_UNTEXT_ABORT_SUBTITLE        ${LANG_ENGLISH} "Do you want to abort uninstallation."
LangString MUI_UNTEXT_FINISH_INFO_TITLE     ${LANG_ENGLISH} "Uninstallation complete."
LangString MUI_UNTEXT_FINISH_INFO_REBOOT    ${LANG_ENGLISH} "Deinstallation no need to reboot"
LangString MUI_UNTEXT_FINISH_INFO_TEXT      ${LANG_ENGLISH} "${FULL_APP_NAME} is uninstalled bye."



;----- iSpector is a normal program that doesn't need administrator privilleges
RequestExecutionLevel admin

Icon ${MY_ICON}

; The installer.
OutFile "${FULL_APP_NAME}-installer.exe"

; install standard under program files - uil_ots
InstallDir "$PROGRAMFILES64\${MY_ORGANISATION}"


;-------- Install
Section
    SetShellVarContext all
    SetOutPath "$INSTDIR\${FULL_APP_NAME}\"
    File /r ".\dist\iSpector\*"

    ; Create short cut
    CreateDirectory "$SMPROGRAMS\${MY_ORGANISATION}"
    CreateShortCut  "$SMPROGRAMS\${MY_ORGANISATION}\${FULL_APP_NAME}.lnk"   \
                    "$INSTDIR\${FULL_APP_NAME}\iSpector.exe"                \
                    ""                                                      \
                    "$INSTDIR\${FULL_APP_NAME}\${MY_ICON}"                  \
                    0

    ; Write displayname and uninstall string to registry
    WriteRegStr     HKLM "${REGISTRY_UN_PATH}\${FULL_APP_NAME}" "DisplayName"\
                         "${FULL_APP_NAME} a tool to inspect and extract eye-movement data."
    WriteRegStr     HKLM "${REGISTRY_UN_PATH}\${FULL_APP_NAME}"\
                         "UninstallString" "$INSTDIR\${FULL_APP_NAME}-uninstaller.exe"

    ; create uninstaller
    SetOutPath "$INSTDIR\"
    WriteUninstaller "$INSTDIR\${FULL_APP_NAME}-uninstaller.exe"
SectionEnd

;-------- Uninstall
Section "uninstall"
    SetShellVarContext all
    Delete      "$INSTDIR\${FULL_APP_NAME}-uninstaller.exe"
    ;remove iSpector
    RMDir /r    "$INSTDIR\${FULL_APP_NAME}"
    ;if iSpector was the last file in Uil_OTS map delete that one as well
    RMDir       "$INSTDIR"

    ;Remove uninstallation entry for iSpector from the registry
    DeleteRegKey HKLM "${REGISTRY_UN_PATH}\${FULL_APP_NAME}"
    
    ;Delete short cut and map if empty
    Delete "$SMPROGRAMS\${MY_ORGANISATION}\${FULL_APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\${MY_ORGANISATION}"
SectionEnd

