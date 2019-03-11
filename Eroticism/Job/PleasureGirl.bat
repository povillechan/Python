call cmd /c python ..\Site\PleasureGirl\Photos.py -p 1
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\PleasureGirl\Photos.py -p 2 -l 100
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\PleasureGirl\Photos.py -p 3 -t 100
