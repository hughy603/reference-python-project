@echo off
REM Script to open the project in VSCode with WSL
REM Put this file in the root of your project on Windows

echo Opening project in VSCode with WSL...

REM Get the current directory
set CURRENT_DIR=%~dp0
set PROJECT_DIR=%CURRENT_DIR%..

REM Change to the project directory
cd %PROJECT_DIR%

REM Open VSCode with WSL
wsl code -n .
