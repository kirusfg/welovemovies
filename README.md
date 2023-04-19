# WeLoveMovies

## Install:
```sh
python3 -m venv venv
python3 -m pip install -r requirements.txt
```

## Run:
```sh
python app.py
# or
flask run --debug
```

The app is available at `localhost:5000`. Routes are:
```
/
/login
/logout
/signup
/settings

/rooms
/reservation/<int:room_id>
/cancel/<int:reservation_id>
/my-reservations
```

## Check the database:
The database has following relations:
```
users
- id
- username
- password (hashed)
- email

screen_types
- id
- name
- description (optional)

audio_systems
- id
- name
- description (optional)

rooms
- id
- name
- image_url (optional)
- number_of_seats
- screen_type_id (foreign key referencing screen_types)
- audio_system_id (foreign key referencing audio_systems)
- price_per_hour
- description (optional)

reservations
- id
- user_id (foreign key referencing users)
- room_id (foreign key referencing rooms)
- start_time
- end_time
```

Here are some of the commands you can run to check whether the database
gets updated or not:
```sh
sqlite3 main.db
sqlite> SELECT * FROM users;
sqlite> SELECT * FROM rooms;
sqlite> SELECT * FROM audio_systems;
sqlite> SELECT * FROM reservations;
sqlite> SELECT * FROM reservations WHERE user_id = <some user id>;
```

## Project structure:
The application has the following file structure:
```
scripts/
    data.py  # A python script that fills the database with dummy test data
    forms.py  # Login and signup forms with some data validators
    helpers.py  # Helper functions for working with the database and cryptography
    tabledef.py  # A file that defines how the database will look
static/
templates/
    base.html  # Base template for all other pages
    login.html  # The login page
    my_reservations.html  # Page that shows reservations of the logged in user
    navbar.html  # Navigation bar template
    reservation.html  #  The page for making reservations
    rooms.html  # Page displaying all the rooms available for reservation
    settings.html  # User settings page
app.py  # Main module, which defines the application logic
```

