import bcrypt
from flask import session
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker, joinedload
from contextlib import contextmanager

from .tabledef import engine, Room, User, Reservation, ScreenType, AudioSystem


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
    return sessionmaker(bind=engine)()


def get_all_screen_types():
    with session_scope() as s:
        screen_types = s.query(ScreenType).all()
        return screen_types


def get_all_audio_systems():
    with session_scope() as s:
        audio_systems = s.query(AudioSystem).all()
        return audio_systems


def get_all_rooms(search_query, screen_type_id, audio_system_id):
    with session_scope() as s:
        query = s.query(Room)

        if search_query:
            query = query.filter(or_(
                Room.name.ilike(f'%{search_query}%'),
                Room.description.ilike(f'%{search_query}%'),
            ))
        if screen_type_id:
            query = query.filter(Room.screen_type_id == screen_type_id)
        if audio_system_id:
            query = query.filter(Room.audio_system_id == audio_system_id)

        rooms = query.options(
            joinedload(Room.screen_type),
            joinedload(Room.audio_system)
        ).all()
        return rooms


def get_room(room_id):
    with session_scope() as s:
        room = s.query(Room).options(
            joinedload(Room.screen_type),
            joinedload(Room.audio_system)
        ).filter(Room.id == room_id).first()
        return room


def get_reservation(reservation_id):
    with session_scope() as s:
        reservation = s.query(Reservation).filter(Reservation.id == reservation_id).first()
        return reservation


def cancel_reservation(reservation_id):
    with session_scope() as s:
        reservation = s.query(Reservation).filter(Reservation.id == reservation_id).first()

        if reservation is None:
            return

        s.delete(reservation)
        s.commit()


def get_user_reservations(username):
    with session_scope() as s:
        user = s.query(User).filter(
            User.username.in_([username])
        ).first()

        if not user:
            return

        reservations = s.query(Reservation).options(joinedload(Reservation.room)).filter_by(user_id=user.id).all()

        return reservations


def get_reservations_between(room_id, start_time, end_time):
    with session_scope() as s:
        conflicting_reservations = s.query(Reservation).filter(
            Reservation.room_id == room_id,
            Reservation.start_time <= end_time,
            Reservation.end_time >= start_time
        ).all()
        return conflicting_reservations


def get_user():
    username = session.get('username')
    with session_scope() as s:
        user = s.query(User).filter(
            User.username.in_([username])
        ).first()
        return user


def add_user(username, password, email):
    with session_scope() as s:
        user = User(
            username=username,
            password=password.decode('utf8'),
            email=email,
        )
        s.add(user)
        s.commit()


def modify_user_data(**kwargs):
    username = session['username']
    with session_scope() as s:
        user = s.query(User).filter(
            User.username.in_([username])
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
        user = s.query(User).filter(
            User.username.in_([username])).first()
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
        return s.query(User).filter(User.username.in_([username])).first()
