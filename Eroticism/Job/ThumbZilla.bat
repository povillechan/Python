python ..\Site\ThumbZilla\Models.py -p 4
python ..\Site\ThumbZilla\Videos.py -p 4

call cmd /c start python ..\Site\ThumbZilla\Models.py -p 2 -l 20
call cmd /c start python ..\Site\ThumbZilla\Videos.py -p 2 -l 20

ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\ThumbZilla\Models.py -p 3 -t 20
call cmd /c start python ..\Site\ThumbZilla\Videos.py -p 3 -t 20
