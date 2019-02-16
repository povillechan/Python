call cmd /c start python ..\Site\HegreHunter\Photos.py -p 2
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\HegreHunter\Photos.py -p 3 -t 50
