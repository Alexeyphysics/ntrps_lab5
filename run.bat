@echo off
chcp 65001 > nul
echo ====================================================
echo Zapusk prilozheniya: Analiticheskaya sistema otzyvov
echo Razrabotchik: Kondratenko A.S. (gr. M_PIN_RIS_2607)
echo ====================================================

if exist venv_win\Scripts\activate.bat goto ACTIVATE

echo [INFO] Sozdanie virtualnogo okruzheniya venv_win...
python -m venv venv_win
call venv_win\Scripts\activate.bat

echo [INFO] Ustanovka neobkhodimykh bibliotek...
python -m pip install --upgrade pip
pip install PySide6 pandas matplotlib seaborn nltk pymorphy3 requests beautifulsoup4
goto RUN

:ACTIVATE
call venv_win\Scripts\activate.bat

:RUN
echo [INFO] Zapusk graficheskogo interfeysa...
python main.py
pause
