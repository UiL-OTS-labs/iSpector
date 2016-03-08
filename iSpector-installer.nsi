;**
;* This installer is created to install the binary version of iSpector
;* on a windows system.
;*/

SetCompressor /SOLID /FINAL lzma

!include LogicLib.nsh
!include MUI2.nsh

;----- Definitions of some constants

!define MY_PROGRAM_NAME     "iSpector"
!define MY_ORGANISATION     "Uil_OTS"
!define MY_ICON_DIR         "logo"
!define MY_ICON             "logo\ispectorlogo.ico"
; Path to registry where uninstall info is stored.
!define REGISTRY_UN_PATH    "Software\Microsoft\Windows\CurrentVersion\Uninstall\"

/****** text strings for the mui ********/

; Strings for the welcome page
LangString MUI_TEXT_WELCOME_INFO_TITLE  ${LANG_ENGLISH} "${MY_PROGRAM_NAME}-installer"
LangString MUI_TEXT_WELCOME_INFO_TEXT   ${LANG_ENGLISH} "Welcome by the ${MY_PROGRAM_NAME} installer."

; Strings for the license page
LangString MUI_INNERTEXT_LICENSE_BOTTOM ${LANG_ENGLISH} "Innertext license bottom"
LangString MUI_INNERTEXT_LICENSE_TOP    ${LANG_ENGLISH} "Innertext license top"
LangString MUI_TEXT_LICENSE_TITLE       ${LANG_ENGLISH} "GPL2 license"
LangString MUI_TEXT_LICENSE_SUBTITLE    ${LANG_ENGLISH} "Do you accept the GPL2 license?"

; Strings for install page
LangString MUI_TEXT_INSTALLING_TITLE    ${LANG_ENGLISH} "Installing"
LangString MUI_TEXT_INSTALLING_SUBTITLE ${LANG_ENGLISH} "Installing: ${MY_PROGRAM_NAME}" 

; Strings for installer finish page
LangString MUI_BUTTONTEXT_FINISH        ${LANG_ENGLISH} "close."
LangString MUI_TEXT_FINISH_TITLE        ${LANG_ENGLISH} "The End!"
LangString MUI_TEXT_FINISH_SUBTITLE     ${LANG_ENGLISH} "Finished installing ${MY_PROGRAM_NAME}"
LangString MUI_TEXT_FINISH_INFO_TITLE   ${LANG_ENGLISH} "Installation is finished"
LangString MUI_TEXT_FINISH_INFO_REBOOT  ${LANG_ENGLISH} "No need to reboot."
LangString MUI_TEXT_FINISH_REBOOTNOW    ${LANG_ENGLISH} "No need to reboot"
LangString MUI_TEXT_FINISH_REBOOTLATER  ${LANG_ENGLISH} "No need to reboot"
LangString MUI_TEXT_FINISH_INFO_TEXT    ${LANG_ENGLISH} "${MY_PROGRAM_NAME} is installed, Goodluck!"

LangString MUI_TEXT_ABORT_TITLE         ${LANG_ENGLISH} "Abort"
LangString MUI_TEXT_ABORT_SUBTITLE      ${LANG_ENGLISH} "Aborting (de-)installation."

;--- Strings for uninstall -----

;strings for the uninstall welcome page
LangString MUI_UNTEXT_WELCOME_INFO_TITLE    ${LANG_ENGLISH} "Uninstall ${MY_PROGRAM_NAME}"
LangString MUI_UNTEXT_WELCOME_INFO_TEXT     ${LANG_ENGLISH} "You are about to uninstall ${MY_PROGRAM_NAME}!"

;strings for confirm
LangString MUI_UNTEXT_CONFIRM_TITLE         ${LANG_ENGLISH} "Uninstall ${MY_PROGRAM_NAME}"
LangString MUI_UNTEXT_CONFIRM_SUBTITLE      ${LANG_ENGLISH} "Are you sure to uninstall: ${MY_PROGRAM_NAME}"
LangString MUI_UNTEXT_UNINSTALLING_TITLE    ${LANG_ENGLISH} "Uninstalling"
LangString MUI_UNTEXT_UNINSTALLING_SUBTITLE ${LANG_ENGLISH} "Uninstalling ${MY_PROGRAM_NAME}"
LangString MUI_UNTEXT_FINISH_TITLE          ${LANG_ENGLISH} "Finished uninstalling"
LangString MUI_UNTEXT_FINISH_SUBTITLE       ${LANG_ENGLISH} "Finished uninstalling"
LangString MUI_UNTEXT_ABORT_TITLE           ${LANG_ENGLISH} "Abort uninstallation"
LangString MUI_UNTEXT_ABORT_SUBTITLE        ${LANG_ENGLISH} "Do you want to abort uninstallation."
LangString MUI_UNTEXT_FINISH_INFO_TITLE     ${LANG_ENGLISH} "Uninstallation complete."
LangString MUI_UNTEXT_FINISH_INFO_REBOOT    ${LANG_ENGLISH} "Deinstallation no need to reboot"
LangString MUI_UNTEXT_FINISH_INFO_TEXT      ${LANG_ENGLISH} "${MY_PROGRAM_NAME} is uninstalled bye."



!insertmacro MUI_LANGUAGE       "English" 
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE   "LICENSE"
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH


;----- iSpector is a normal program that doesn't need administrator privilleges

RequestExecutionLevel user

Icon ${MY_ICON}

OutFile "${MY_PROGRAM_NAME}-installer.exe"


InstallDir "$PROGRAMFILES\${MY_ORGANISATION}"


;-------- Install
Section
    SetShellVarContext all
    SetOutPath "$INSTDIR\${MY_PROGRAM_NAME}\"
    File /r ".\dist\iSpector\*"

    ; Create short cut
    CreateDirectory "$SMPROGRAMS\${MY_ORGANISATION}"
    CreateShortCut  "$SMPROGRAMS\${MY_ORGANISATION}\${MY_PROGRAM_NAME}.lnk" \
                    "$INSTDIR\${MY_PROGRAM_NAME}\iSpector.exe"              \
                    ""                                                      \
                    "$INSTDIR\${MY_PROGRAM_NAME}\${MY_ICON}"                \
                    0

    ; Write displayname and uninstall string to registry
    WriteRegStr     HKLM "${REGISTRY_UN_PATH}\${MY_PROGRAM_NAME}" "DisplayName"\
                         "${MY_PROGRAM_NAME} a tool to inspect and extract eye-movement data."
    WriteRegStr     HKLM "${REGISTRY_UN_PATH}\${MY_PROGRAM_NAME}"\
                         "UninstallString" "$INSTDIR\${MY_PROGRAM_NAME}-uninstaller.exe"

    ; create uninstaller
    SetOutPath "$INSTDIR\"
    WriteUninstaller "$INSTDIR\${MY_PROGRAM_NAME}-uninstaller.exe"
SectionEnd

;-------- Uninstall
Section "uninstall"
    SetShellVarContext all
    Delete      "$INSTDIR\${MY_PROGRAM_NAME}-uninstaller.exe"
    ;remove iSpector
    RMDir /r    "$INSTDIR\${MY_PROGRAM_NAME}"
    ;if iSpector was the last file in Uil_OTS map delete that one as well
    RMDir       "$INSTDIR"

    ;Remove uninstallation entry for iSpector from the registry
    DeleteRegKey HKLM "${REGISTRY_UN_PATH}\${MY_PROGRAM_NAME}"
    
    ;Delete short cut and map if empty
    Delete "$SMPROGRAMS\${MY_ORGANISATION}\${MY_PROGRAM_NAME}.lnk"
    RMDir "$SMPROGRAMS\${MY_ORGANISATION}"
SectionEnd
