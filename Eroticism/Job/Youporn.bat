python ..\Site\Youporn\Models.py -p 4

call cmd /c start python ..\Site\Youporn\Models.py -p 2 -l 50

ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\Youporn\Models.py -p 3 -t 50

