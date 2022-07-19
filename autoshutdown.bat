@echo off
:start
%systemroot%\system32\shutdown -f -s -t 150
cls
:yn
set /p word=输入Y取消关机，输入N退出：
if /i "%word%"=="y" %systemroot%\system32\shutdown -a&&goto :eof
if /i "%word%"=="m" %systemroot%\system32\shutdown -a&&goto :min
if /i "%word%"=="r" goto :start
if /i "%word%"=="n" (goto :eof) else (cls&&echo 输入有误,输入R重新关机!&&%systemroot%\system32\shutdown -a&&goto :yn)
:min
set /p word=输入等待关机时间（单位：分钟），F强制关机，R重启：
if /i "%word%"=="0" (%systemroot%\system32\shutdown -f -s -t 30)&&goto :yn
if /i "%word%"=="1" (%systemroot%\system32\shutdown -f -s -t 60)&&goto :yn
if /i "%word%"=="2" (%systemroot%\system32\shutdown -f -s -t 120)&&goto :yn
if /i "%word%"=="3" (%systemroot%\system32\shutdown -f -s -t 180)&&goto :yn
if /i "%word%"=="4" (%systemroot%\system32\shutdown -f -s -t 240)&&goto :yn
if /i "%word%"=="5" (%systemroot%\system32\shutdown -f -s -t 300)&&goto :yn
if /i "%word%"=="6" (%systemroot%\system32\shutdown -f -s -t 360)&&goto :yn
if /i "%word%"=="7" (%systemroot%\system32\shutdown -f -s -t 420)&&goto :yn
if /i "%word%"=="8" (%systemroot%\system32\shutdown -f -s -t 480)&&goto :yn
if /i "%word%"=="9" (%systemroot%\system32\shutdown -f -s -t 540)&&goto :yn
if /i "%word%"=="h" (%systemroot%\system32\shutdown -f -s -t 1800)&&goto :yn
if /i "%word%"=="q" (%systemroot%\system32\shutdown -f -s -t 900)&&goto :yn
if /i "%word%"=="o" (%systemroot%\system32\shutdown -f -s -t 3600)&&goto :yn
if /i "%word%"=="d" (%systemroot%\system32\shutdown -f -s -t 7200)&&goto :yn
if /i "%word%"=="t" (%systemroot%\system32\shutdown -f -s -t 10800)&&goto :yn
if /i "%word%"=="t" (%systemroot%\system32\shutdown -f -s -t 14400)&&goto :yn
if /i "%word%"=="t" (%systemroot%\system32\shutdown -f -s -t 18000)&&goto :yn
if /i "%word%"=="f" (%systemroot%\system32\shutdown -f -s -t 0)&&goto :yn
if /i "%word%"=="r" (%systemroot%\system32\shutdown -f -r -t 10&&goto :yn) else (cls&&echo 输入有误,重新关机!&&goto :start)
rem ****************
rem 另存为xx.bat 0000000