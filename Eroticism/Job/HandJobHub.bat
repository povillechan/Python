call cmd /c start python ..\Site\HandJobHub\videos.py -p 4

call cmd /c start python ..\Site\HandJobHub\videos.py -p 1
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\HandJobHub\videos.py -p 2 -l 10
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\HandJobHub\videos.py -p 3 -t 20
