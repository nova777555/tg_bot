@echo off

call %~dp0\venv\scripts\activate

cd %~dp0

set TOKEN=5608055502:AAEByAda4oILCXC9-RCjkWMUqRFZLTMclfI

python bot_main.py

pause