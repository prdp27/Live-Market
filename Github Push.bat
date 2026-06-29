@echo off
title Live Market - GitHub Setup & Push

cd /d "D:\prdp\Data Analytics\Live-Market"

echo.
echo ==========================================
echo        Live Market - GitHub Push
echo ==========================================
echo.

REM Check if this is already a Git repository
if exist ".git" (
    echo Git repository found.
) else (
    echo.
    echo No Git repository found.
    echo Initializing...

    git init
    git branch -M main
    git remote add origin https://github.com/prdp27/Live-Market.git
)

echo.
git status

echo.
set /p msg=Enter commit message: 

echo.
git add .

git commit -m "%msg%"

git push -u origin main

echo.
echo ==========================================
echo            Completed
echo ==========================================
pause