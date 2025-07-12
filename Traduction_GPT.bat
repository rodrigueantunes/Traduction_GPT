@echo off
set "script=%~dp0Traduction_GPT.py"
"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -Command "Start-Process python.exe '%script%' -Verb RunAs"
