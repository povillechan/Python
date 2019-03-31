python ..\Site\BabeImpact\Photos.py -p 4
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\BabeImpact\Photos.py -p 2 -t 100
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\BabeImpact\Photos.py -p 3 -t 100
