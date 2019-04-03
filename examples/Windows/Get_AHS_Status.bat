::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to find out if 	   ::
::               AHS is enabled or disabled.                       ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - All versions.                                ::
@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest get AHSEnabled --selector=iLOActiveHealthSystem. -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
ilorest get AHSEnabled --selector=iLOActiveHealthSystem. --url=%1 -u %2 -p %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Get_AHS_Status.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Get_AHS_Status.bat

:exit