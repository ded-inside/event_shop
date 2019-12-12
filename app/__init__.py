from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

from app import routes, models


def generate_default_state():
    db.drop_all()
    db.create_all()
    db.session.commit()

    u1 = models.User(
        username="user1",
        first_name="fname",
        last_name="lname",
        email="u1@example.com",
    )
    u1.set_password('user1')
    u2 = models.User(
        username="user2",
        first_name="fname2",
        last_name="lname2",
        email="u2@example.com",
    )
    u2.set_password("user2")
    for i in range(100):
        cert = models.Certificate()
        u1.certificates.append(cert)
        db.session.add(cert)

    event = models.Event(
        price=42,
        title="Eventb"
    )
    db.session.add(event)
    u2.events_host.append(event)

    db.session.add(u1)
    db.session.add(u2)

    db.session.commit()

    print(u1)
    print(u2)
    print(event)


generate_default_state()
