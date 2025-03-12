@echo off
REM Test Lambda functions locally without Docker or admin rights
REM This batch file runs the test_lambda_local.py script with the hello_world example

echo Testing Lambda function locally without Docker...
echo.

REM Get the directory of this batch file
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..\..

REM Run the Lambda test script
python "%PROJECT_ROOT%\scripts\test_lambda_local.py" ^
  --file "%SCRIPT_DIR%hello_world.py" ^
  --handler "lambda_handler" ^
  --event "%SCRIPT_DIR%test_event.json" ^
  --verbose

echo.
echo Test complete!
pause
