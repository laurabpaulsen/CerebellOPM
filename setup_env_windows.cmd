@echo off
set scriptDir=%~dp0
set scriptDir=%scriptDir:~0,-1%
winget install -e --id Python.Python.3.11
python3 -m venv "%scriptDir%\env"

call "%scriptDir%\env\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install psychopy --no-deps
pip install -r "%scriptDir%\requirements.txt"