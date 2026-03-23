@echo off
setlocal EnableExtensions
pushd "%~dp0"

set "PY=%CD%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" "%CD%\tools\task_runner.py" %*
set "RC=%ERRORLEVEL%"

popd
exit /b %RC%
