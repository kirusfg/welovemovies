# WeLoveMovies

## Install:
```sh
python3 -m venv venv
python3 -m pip install -r requirements.txt
```

## Run:
```sh
python app.py
```

The app is available at `localhost:5000`. Routes are:
```
/
/logout
/signup
/settings
```

## Check the database:
```sh
sqlite3 accounts.db
sqlite> SELECT * FROM user;
```
