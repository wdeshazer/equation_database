@ECHO OFF
setlocal
set PYTHONPATH=%PYTHONPATH%;%1
python %2
endlocal