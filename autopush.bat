@echo off
cd /d "C:\Users\aruru\Desktop\nhhanaro"

git add .
git commit -m "Automated commit on %date% %time%"
git push origin master

exit