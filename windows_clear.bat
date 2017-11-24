@echo off

REM 
del *.log
del *.blacklist

REM This style of folder delete supports wildcards
FOR /D /R %%X IN ("phase_1_faces") DO RD /S /Q "%%X"

cls

echo clean finished.
echo.
echo You can now close this window and execute windows_run.bat
echo.

pause