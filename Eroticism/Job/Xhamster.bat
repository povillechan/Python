python ..\Site\Xhamster\models.py -p 4
call cmd /c start python ..\Site\Xhamster\models.py -p 1
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\Xhamster\models.py -p 2 -t 50 -l 50
ping -n 60 127.0.0.1>nul
call cmd /c start python ..\Site\Xhamster\models.py -p 3 -t 50

