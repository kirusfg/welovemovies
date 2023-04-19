import os
import json
import datetime

from scripts import forms
from flask import Flask, redirect, url_for, render_template, request, session, flash

from scripts.helpers import (
    get_all_screen_types,
    get_all_audio_systems,
    get_all_rooms,
    get_room,
    get_reservation,
    cancel_reservation,
    get_reservations_between,
    get_user_reservations,
    get_user,
    add_user,
    modify_user_data,
    hash_password,
    credentials_are_valid,
    username_taken,
    session_scope,
)
from scripts.tabledef import Reservation, User


app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    The login route.
    If the user is not logged in, and the HTML method
    was POST, this method will validate the POST form (check if the
    fields are not missing and if they are not too short), and then log in the
    new user if everything is ok.
    '''
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if credentials_are_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both username and password are required'})
        return render_template('login.html', form=form)

    return redirect(url_for('rooms'))


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    '''
    The signup route.
    If the user is not logged in, and the HTML method
    was POST, this method will validate the POST form (check if the
    fields are not missing and if they are not too short, check if the username
    was not already taken), then create and log in the new user if everything
    is ok.
    '''
    if not session.get('logged_in'):
        form = forms.SignupForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not username_taken(username):
                    add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'Both username and password are required'})
        return render_template('login.html', form=form)
    return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    '''
    The settings route.
    Allows the user to change their settings: email and password.
    '''
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != '':
                password = hash_password(password)
            email = request.form['email']
            modify_user_data(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))


@app.route('/rooms', methods=['GET'])
def rooms():
    '''
    The Rooms route.
    Allows the user to view the rooms currently available for reservation,
    with search and filters included. The rooms listed can also be reserved by
    clicking the corresponding button.

    The route is login-protected.
    '''
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Get all the filters from the request
    search_query = request.args.get('search', '')
    screen_type_id = request.args.get('screen_type', '')
    audio_system_id = request.args.get('audio_system', '')

    # Find all rooms that get past the specified filters
    rooms = get_all_rooms(search_query, screen_type_id, audio_system_id)

    screen_types = get_all_screen_types()
    audio_systems = get_all_audio_systems()

    return render_template(
        'rooms.html',
        rooms=rooms,
        screen_types=screen_types,
        audio_systems=audio_systems,
    )


@app.route('/reservation/<int:room_id>', methods=['GET', 'POST'])
def reservation(room_id):
    '''
    The Reservation route.
    Allows the user make a reservation for the room with its id specified as
    a url parameter.

    The route is login-protected.
    '''
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    room = get_room(room_id)

    if request.method == 'POST':
        date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d')
        start_time = datetime.datetime.strptime(request.form['start_time'], '%H:%M')
        end_time = datetime.datetime.strptime(request.form['end_time'], '%H:%M')

        start_time = date.combine(date, start_time.time())
        end_time = date.combine(date, end_time.time())

        # Check if the room is available during the requested time
        conflicting_reservations = get_reservations_between(room_id, start_time, end_time)

        if conflicting_reservations:
            flash('This room is already reserved for the requested time')
            return redirect(url_for('reservation', room_id=room_id))

        # Create a new reservation for the room
        with session_scope() as s:
            user = s.query(User).filter_by(username=session['username']).first()
            reservation = Reservation(room=room, user=user, start_time=start_time, end_time=end_time)
            s.add(reservation)
            s.commit()

        flash('Reservation successfully created')
        return redirect(url_for('my_reservations'))

    return render_template('reservation.html', room=room)


@app.route('/my-reservations')
def my_reservations():
    '''
    The My Reservations route.
    Allows the user to view their own room reservations. Each reservation's view
    has a Cancel button that makes a cancellation request.

    The route is login-protected.
    '''
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    username = session.get('username')
    reservations = get_user_reservations(username)

    return render_template('my_reservations.html', reservations=reservations, datetime=datetime)


@app.route('/cancel/<int:reservation_id>')
def cancel(reservation_id):
    '''
    The Cancel route.
    Allows the user to cancel one of *their own* reservations. Whether the cancellation
    has succeeded or not, the user is redirected to their Reservations page.

    The route is login-protected.
    '''
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user = get_user()
    if not user:
        return redirect(url_for('login'))

    reservation = get_reservation(reservation_id)
    if not reservation:
        flash('Reservation not found.')
        return redirect(url_for('my_reservations'))

    # A user can only cancel their own reservations!
    if reservation.user_id != user.id:
        flash('You do not have permission to cancel this reservation.')
        return redirect(url_for('my_reservations'))

    cancel_reservation(reservation_id)

    flash('Reservation canceled.')
    return redirect(url_for('my_reservations'))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host='0.0.0.0')
