@echo off

REM 
del *.log
del *.blacklist

FOR /D /R %%X IN ("phase_1_pool") DO RD /S /Q "%%X"
FOR /D /R %%X IN ("code\one_ring_virtual_env\Lib\site-packages\one_ring*") DO RD /S /Q "%%X"

REM if [[ "$1" == "all" ]]; then
REM 	echo "'clean all specified. Removing libraries."
REM     rm -r code/one_ring_virtual_env > /dev/null 2>&1;
REM else
REM     echo "'all' is not supplied. NOT removing libraries"
REM fi
REM 

cls

echo clean finished.
