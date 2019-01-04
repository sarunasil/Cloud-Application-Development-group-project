### prerequisites
if you dont want all packages to be installed globally you need `virtual env`
`pip install -r requirements.txt`

## to run server locally:
rename configExample.py to config.py
change <PASSWORD> in URL to our password (ask for it)
  
in terminal (on Windows):  `set FLASK_APP=main.py`

in terminal (on Linux):  `export FLASK_APP=main.py`


finally: `flask run`
