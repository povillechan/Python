call cmd /c start python ..\Site\RedTube\photos.py -p 1
call cmd /c start python ..\Site\RedTube\photos.py -p 2 -l 100
ping -n 60 127.0.0.1>nul
call cmd /c start python ..\Site\RedTube\photos.py -p 3 -t 100
