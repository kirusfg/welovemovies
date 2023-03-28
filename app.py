import os
import json

from scripts import forms
from scripts import helpers
from flask import Flask, redirect, url_for, render_template, request, session


app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route('/', methods=['GET', 'POST'])
def login():
    """
    The login route.
    If the user is not logged in, and the HTML method
    was POST, this method will validate the POST form (check if the
    fields are not missing and if they are not too short), and then log in the
    new user if everything is ok.
    """
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if helpers.credentials_are_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both username and password are required'})
        return render_template('login.html', form=form)
    user = helpers.get_user()
    return render_template('home.html', user=user)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    The signup route.
    If the user is not logged in, and the HTML method
    was POST, this method will validate the POST form (check if the
    fields are not missing and if they are not too short, check if the username
    was not already taken), then create and log in the new user if everything
    is ok.
    """
    if not session.get('logged_in'):
        form = forms.SignupForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'Both username and password are required'})
        return render_template('login.html', form=form)
    return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    The settings route.
    Allows the user to change their settings: email and password.
    """
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.modify_user_data(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host="0.0.0.0")
