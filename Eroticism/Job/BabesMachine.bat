call cmd /c start python ..\Site\BabesMachine\Models.py -p 1

ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\BabesMachine\Models.py -p 2

ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\BabesMachine\Models.py -p 3
