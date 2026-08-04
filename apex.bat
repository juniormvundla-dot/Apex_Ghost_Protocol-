@echo off
setlocal
:: Resolve the current script directory
set "SCRIPTPATH=%~dp0"

:: Launch main.py with passed arguments using the virtual environment python
"%SCRIPTPATH%.venv\Scripts\python.exe" "%SCRIPTPATH%main.py" %*
endlocal
