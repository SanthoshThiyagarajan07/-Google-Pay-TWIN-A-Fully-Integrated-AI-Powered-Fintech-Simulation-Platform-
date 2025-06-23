@echo off
echo Fixing st.experimental_rerun issues...

REM Use PowerShell to replace experimental_rerun with rerun in all Python files
powershell -Command "Get-ChildItem -Path . -Filter '*.py' | ForEach-Object { (Get-Content $_.FullName) -replace 'st\.experimental_rerun\(\)', 'st.rerun()' | Set-Content $_.FullName }"

echo Done! All st.experimental_rerun() calls have been replaced with st.rerun()
pause