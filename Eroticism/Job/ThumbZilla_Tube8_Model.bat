python ..\Site\ThumbZilla\Models.py -p 4
python ..\Site\Tube8\Models.py -p 4

call cmd /c start python ..\Site\ThumbZilla\Models.py -p 2 -l 50
call cmd /c start python ..\Site\Tube8\Models.py -p 2 -l 50

ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\ThumbZilla\Models.py -p 3 -t 50
call cmd /c start python ..\Site\Tube8\Models.py -p 3 -t 50
