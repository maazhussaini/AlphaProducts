@echo off

REM Activate the virtual environment
REM Note: Change "venv" to the name of your virtual environment folder
call pyenv\Scripts\activate.bat


cd HRIS_apis
REM Start the Flask application
REM Replace "app.py" with the name of your main Flask application file
python run.py