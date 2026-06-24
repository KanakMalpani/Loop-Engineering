@echo off
setlocal
cd /d "%~dp0.."
python scripts\validate_loop_library.py
exit /b %ERRORLEVEL%
