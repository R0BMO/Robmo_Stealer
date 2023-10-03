@echo off

title Robmo Builder

for /f "tokens=1,2 delims= " %%a in ('powershell -Command "Invoke-WebRequest https://www.python.org/ftp/python/ -UseBasicParsing | Select-String -Pattern '3.10.[0-9]{1,2}' -AllMatches | Select-Object -ExpandProperty Matches | Select-Object -ExpandProperty Value | Sort-Object -Descending -Unique | Select-Object -First 1"') do (
    set "PYTHON_VERSION=%%a%%b"
)
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"
set "PYTHON_EXE=python-installer.exe"

curl -L -o %PYTHON_EXE% %PYTHON_URL%

start /wait %PYTHON_EXE% /quiet /passive InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1 Include_doc=0

del %PYTHON_EXE%

python -m pip install --upgrade pip

pip install requests
pip install pystyle
pip install colorama
pip install auto_py_to_exe
pip install pyinstaller
pip install wmi
pip install pyautogui
pip install psutil
pip install pycryptodome
pip install Pillow
pip install pybase64
pip install requests-toolbelt
pip install python-telegram-bot

pause

start /min "" cmd /c exit