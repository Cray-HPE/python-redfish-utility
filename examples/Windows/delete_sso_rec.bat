::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description: This a sample batch script to delete an HPE SIM    ::
::        Single Sign-On (SSO) server record by index.             ::

:: NOTE:  You will need to replace the values inside the quotation ::
::        marks with values that are appropriate for your          ::
::        environment.                                             ::

::        You can determine the record index using                 ::
::        Get_SSO_Settings.bat. As you remove records, the index of::
::        subsequent entries is reduced.                           ::

::        Modification of SSO settings requires Configure iLO      ::
::        privilege.                                               ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - All versions                                 ::


@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest singlesignon deleterecord "6"
ilorest logout
goto :exit
:remote
ilorest singlesignon deleterecord "6" --url=%1 --user %2 --password %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: delete_sso_rec.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  delete_sso_rec.bat

:exit