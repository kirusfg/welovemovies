from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Local
DATABASE_URI = 'sqlite:///main.db'

Base = declarative_base()


def db_connect():
    return create_engine(DATABASE_URI)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    password = Column(String(512))
    email = Column(String(50))

    reservations = relationship('Reservation', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username


class ScreenType(Base):
    __tablename__ = 'screen_types'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    rooms = relationship('Room', backref='screen_type')

    def __repr__(self):
        return '<Screen %s>' % self.name


class AudioSystem(Base):
    __tablename__ = 'audio_systems'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    rooms = relationship('Room', backref='audio_system')

    def __repr__(self):
        return '<Audio System %s>' % self.name


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    number_of_seats = Column(Integer, nullable=False)
    screen_type_id = Column(Integer, ForeignKey('screen_types.id'), nullable=False)
    audio_system_id = Column(Integer, ForeignKey('audio_systems.id'), nullable=False)
    price_per_hour = Column(Float, nullable=False)
    description = Column(String)

    reservations = relationship('Reservation', backref='room')

    def __repr__(self):
        return '<Room %d - "%s" (%d seats, %s screen, %s audio) - $%f/hr>' % (
            self.id,
            self.name,
            self.number_of_seats,
            self.screen_type,
            self.audio_system,
            self.price_per_hour,
        )


class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


engine = db_connect()
Base.metadata.create_all(engine)
