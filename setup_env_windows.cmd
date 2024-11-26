@echo off
set scriptDir=%~dp0
set scriptDir=%scriptDir:~0,-1%
winget install -e --id Python.Python.3.11
py -m venv "%scriptDir%\env"

call "%scriptDir%\env\Scripts\activate.bat"
py -m pip install --upgrade pip
pip3 install psychopy --no-deps
pip3 install -r "%scriptDir%\requirements.txt"