from flask import Flask, redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

from test_config import Config

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = r"static/uploads"

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
bootstrap = Bootstrap(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import models


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == "Admin"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("index"))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == "Admin"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("index"))


admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Event, db.session))
admin.add_view(ModelView(models.Transaction, db.session))
admin.add_view(ModelView(models.Certificate, db.session))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

from app import routes


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
