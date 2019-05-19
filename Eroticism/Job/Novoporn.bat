
call cmd /c start python ..\Site\novoporn\Photos.py -p 1
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\novoporn\Photos.py -p 2 -t 50
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\novoporn\Photos.py -p 3 -t 50

