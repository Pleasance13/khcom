@echo off
title Build Kingdom Hearts: Chain of Memories
cd /d "%~dp0"

set "PATH=C:\msys64\ucrt64\bin;C:\msys64\usr\bin;%PATH%"

echo(
echo === Regenerating build configuration ===
"C:\Python314\python.exe" -m pip install PyYAML
"C:\Python314\python.exe" configure.py
if errorlevel 1 goto failed

echo(
echo === Fixing Windows paths ===
"C:\Python314\python.exe" -c "from pathlib import Path; p=Path('build.ninja'); s=p.read_text(encoding='utf-8'); p.write_text(s.replace('include\\','include/'), encoding='utf-8', newline='')"
if errorlevel 1 goto failed

echo(
echo === Building ROM ===
"C:\msys64\usr\bin\ninja.exe"
if errorlevel 1 goto failed

echo(
echo === BUILD SUCCEEDED ===
echo Your ROM is at build\us\com_us.gba
goto finish

:failed
echo(
echo === BUILD FAILED ===
echo Read the error above before closing this window.

:finish
echo(
pause
