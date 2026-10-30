@echo off
cd /d c:\Users\HP\Desktop\Solvex_03\Backend\app
echo === Directories ===
dir /ad /b
echo === Files in root ===
dir /b
echo === Test import ===
python -c "import google; print('google-generativeai version:', __import__('google').__version__)" 2>&1