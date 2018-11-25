call cmd /c start python ..\Site\HQSluts\Models.py -p 4
call cmd /c start python ..\Site\HQSluts\Models.py -p 2
ping -n 30 127.0.0.1>nul
call cmd /c start python ..\Site\HQSluts\Models.py -p 

