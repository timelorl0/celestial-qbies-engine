@echo off
set JAR=%1
if "%JAR%"=="" set JAR=paper.jar
set JAVA_OPTS=%JAVA_OPTS% -Xms1G -Xmx2G
echo Starting Paper with %JAR%
java %JAVA_OPTS% -jar %JAR% nogui
