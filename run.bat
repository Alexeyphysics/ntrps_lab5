@echo off
chcp 65001 > nul
echo ====================================================
echo Zapusk prilozheniya: Analiticheskaya sistema otzyvov
echo Razrabotchik: Kondratenko A.S. (gr. M_PIN_RIS_2607)
echo ====================================================

if not exist venv_win\Scripts\activate.bat (
    echo [INFO] Sozdanie virtualnogo okruzheniya dlya Windows...
    python -m venv venv_win
    call venv_win\Scripts\activate.bat
    echo [INFO] Ustanovka bibliotek v Windows (PySide6, pandas, etc)...
    python -m pip install --upgrade pip
    pip install PySide6 pandas matplotlib seaborn nltk pymorphy3 requests beautifulsoup4
) else (
    call venv_win\Scripts\activate.bat
)

echo [INFO] Zapusk graficheskogo interfeysa...
python main.py
pause
