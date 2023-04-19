import requests

from tabledef import Base, Room, AudioSystem, ScreenType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# create an engine to connect to your database
engine = create_engine('sqlite:///main.db')

# create the tables if they don't exist
Base.metadata.create_all(engine)

# create a session factory bound to the engine
Session = sessionmaker(bind=engine)

# create a session object
session = Session()


def get_image():
    url = 'https://api.unsplash.com/photos/random?client_id=56zIfiZZ7c92vvQjPGIdkrHW7bMUv0arU8w6RghW6kc&query=cinema-room'
    response = requests.get(url)
    data = response.json()
    image_url = data['urls']['regular']
    return image_url


if __name__ == '__main__':
    screen_type1 = ScreenType(name='IMAX')
    screen_type2 = ScreenType(name='3D')
    session.add_all([screen_type1, screen_type2])
    session.commit()

    audio_system1 = AudioSystem(name='Dolby Atmos')
    audio_system2 = AudioSystem(name='THX')
    session.add_all([audio_system1, audio_system2])
    session.commit()

    cinema_room1 = Room(
        name='Room 1',
        image_url=get_image(),
        number_of_seats=120,
        screen_type_id=1,
        audio_system_id=1,
        price_per_hour=50,
        description='Large room with the latest IMAX screen and Dolby Atmos sound system. Perfect for action and adventure movies.'
    )

    cinema_room2 = Room(
        name='Room 2',
        image_url=get_image(),
        number_of_seats=80,
        screen_type_id=2,
        audio_system_id=2,
        price_per_hour=40,
        description='Medium-sized room with a 3D screen and THX-certified sound system. Great for family-friendly movies and animated films.'
    )

    cinema_room3 = Room(
        name='Room 3',
        image_url=get_image(),
        number_of_seats=60,
        screen_type_id=1,
        audio_system_id=2,
        price_per_hour=30,
        description='Small room with an IMAX screen and THX-certified sound system. Ideal for intimate movie screenings and film festivals.'
    )

    cinema_room4 = Room(
        name='Room 4',
        image_url=get_image(),
        number_of_seats=100,
        screen_type_id=2,
        audio_system_id=1,
        price_per_hour=45,
        description='Medium-sized room with a 3D screen and the latest Dolby Atmos sound system. Perfect for horror and thriller movies.'
    )

    cinema_room5 = Room(
        name='Room 5',
        image_url=get_image(),
        number_of_seats=150,
        screen_type_id=1,
        audio_system_id=2,
        price_per_hour=60,
        description='Large room with the latest IMAX screen and THX-certified sound system. Ideal for epic movies and action-packed blockbusters.'
    )

    cinema_room6 = Room(
        name='Room 6',
        image_url=get_image(),
        number_of_seats=90,
        screen_type_id=2,
        audio_system_id=1,
        price_per_hour=35,
        description='Medium-sized room with a 3D screen and the latest Dolby Atmos sound system. Great for sci-fi and fantasy movies.'
    )

    cinema_room7 = Room(
        name='Room 7',
        image_url=get_image(),
        number_of_seats=70,
        screen_type_id=1,
        audio_system_id=2,
        price_per_hour=25,
        description='Small room with an IMAX screen and THX-certified sound system. Perfect for documentaries and indie films.'
    )

    cinema_room8 = Room(
        name='Room 8',
        image_url=get_image(),
        number_of_seats=110,
        screen_type_id=2,
        audio_system_id=1,
        price_per_hour=50,
        description='Medium-sized room with a 3D screen and the latest Dolby Atmos sound system. Ideal for romantic comedies and dramas.'
    )

    session.add(cinema_room1)
    session.add(cinema_room2)
    session.add(cinema_room3)
    session.add(cinema_room4)
    session.add(cinema_room5)
    session.add(cinema_room6)
    session.add(cinema_room7)
    session.add(cinema_room8)

    session.commit()
