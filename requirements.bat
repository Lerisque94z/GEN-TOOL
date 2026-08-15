@echo off
title GEN-TOOL - Installation des dependances
color 0C

echo ============================================================
echo     GEN-TOOL — Installation des dependances
echo     Par Lerisque94z
echo ============================================================
echo.

echo [1/5] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas trouve dans le PATH !
    echo.
    echo Essaye avec : py --version
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [ERREUR] Python n'est pas installe.
        echo Telecharge-le sur : https://www.python.org/downloads/
        echo.
        echo N'oublie pas de cocher "Add Python to PATH" pendant l'installation.
        pause
        exit
    ) else (
        echo [OK] Python trouve avec la commande 'py'
        set PYTHON_CMD=py
    )
) else (
    echo [OK] Python trouve !
    set PYTHON_CMD=python
)

echo.
echo [2/5] Mise a jour de pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo.
echo [3/5] Installation des modules...
echo.

echo   -> Installation de requests...
%PYTHON_CMD% -m pip install requests

echo   -> Installation de pillow...
%PYTHON_CMD% -m pip install pillow

echo   -> Installation de pywin32...
%PYTHON_CMD% -m pip install pywin32

echo   -> Installation de pycryptodome...
%PYTHON_CMD% -m pip install pycryptodome

echo   -> Installation de pyinstaller...
%PYTHON_CMD% -m pip install pyinstaller

echo   -> Installation de pynput...
%PYTHON_CMD% -m pip install pynput

echo   -> Installation de scapy...
%PYTHON_CMD% -m pip install scapy

echo.
echo [4/5] Verification des installations...
echo.

%PYTHON_CMD% -c "import requests; print('[OK] requests')" 2>nul || echo "[FAIL] requests"
%PYTHON_CMD% -c "import PIL; print('[OK] pillow')" 2>nul || echo "[FAIL] pillow"
%PYTHON_CMD% -c "import win32crypt; print('[OK] pywin32')" 2>nul || echo "[FAIL] pywin32"
%PYTHON_CMD% -c "import Crypto; print('[OK] pycryptodome')" 2>nul || echo "[FAIL] pycryptodome"
%PYTHON_CMD% -c "import pynput; print('[OK] pynput')" 2>nul || echo "[FAIL] pynput"
%PYTHON_CMD% -c "import scapy; print('[OK] scapy')" 2>nul || echo "[FAIL] scapy"

echo.
echo [5/5] Installation terminee !
echo.
echo ============================================================
echo     Tous les modules sont installes !
echo     Lance le tool : python Gen-Tool.py
echo ============================================================
echo.

pause