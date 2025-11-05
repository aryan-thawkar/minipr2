@echo off
echo Setting COM port permissions...
echo Y| cacls COM7 /G Everyone:F
echo Y| cacls \\.\COM7 /G Everyone:F
echo Resetting COM port...
mode COM7 BAUD=9600 PARITY=n DATA=8 STOP=1 to=off dtr=off rts=off
net use COM7 /delete
echo Done. You can now run the Flask application.