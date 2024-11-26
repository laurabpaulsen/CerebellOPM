@echo off
set scriptDir=%~dp0
set scriptDir=%scriptDir:~0,-1%

python -m venv "%scriptDir%\env"

call "%scriptDir%\env\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install psychopy --no-deps
pip install -r "%scriptDir%\requirements.txt"