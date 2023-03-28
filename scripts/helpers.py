from scripts import tabledef
from flask import session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import bcrypt


@contextmanager
def session_scope():
    s = get_session()
    s.expire_on_commit = False
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()


def get_session():
    return sessionmaker(bind=tabledef.engine)()


def get_user():
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.User).filter(
            tabledef.User.username.in_([username])
        ).first()
        return user


def add_user(username, password, email):
    with session_scope() as s:
        u = tabledef.User(
            username=username,
            password=password.decode('utf8'),
            email=email,
        )
        s.add(u)
        s.commit()


def modify_user_data(**kwargs):
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.User).filter(
            tabledef.User.username.in_([username])
        ).first()
        for arg, val in kwargs.items():
            if val != "":
                setattr(user, arg, val)
        s.commit()


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())


def credentials_are_valid(username, password):
    with session_scope() as s:
        # Get the user from database
        user = s.query(tabledef.User).filter(
            tabledef.User.username.in_([username])).first()
        # If the user exists - return the result of password check
        if user:
            # TODO: sometimes user.password is str, sometimes it is bytes
            if type(user.password) == str:
                return bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8'))
            return bcrypt.checkpw(password.encode('utf8'), user.password)
        # Else - return false, because such user does not exist
        else:
            return False


def username_taken(username):
    with session_scope() as s:
        return s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
