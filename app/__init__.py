from flask import Flask, redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
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
login.login_view = "login"
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


admin = Admin(app, index_view=MyAdminIndexView(), template_mode="bootstrap3")
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

	ad = models.User(
		username="Admin",
		first_name="Admin",
		last_name="Admin",
		email="Admin@example.com"
	)
	ad.set_password("Admin")
	db.session.add(ad)

	u1 = models.User(
		username="user1",
		first_name="fname",
		last_name="lname",
		email="u1@example.com",
		profile_pic_filename='Png.png',
	)
	u1.set_password('user1')
	u2 = models.User(
		username="user2",
		first_name="fname2",
		last_name="lname2",
		email="u2@example.com",
		profile_pic_filename='make-an-anime-vaporwave-profile-picture.jpg',
	)
	u2.set_password("user2")
	u3 = models.User(
		username="user3",
		first_name="fname3",
		last_name="lname3",
		email="u3@example.com",
		profile_pic_filename='59-598379_anime-png-tumblr-anime-profile-pic-transparent-png.png',
	)
	u3.set_password("user3")
	u4 = models.User(
		username="user4",
		first_name="fname4",
		last_name="lname4",
		email="u4@example.com",
	)
	u4.set_password("user4")
	for i in range(100):
		cert = models.Certificate()
		u1.certificates.append(cert)
		db.session.add(cert)

	event1 = models.Event(
		price=42,
		title="Event1"
	)
	event2 = models.Event(
		price=42,
		title="Event2"
	)

	db.session.add(event1)
	db.session.add(event2)
	u2.events_host.append(event1)
	u2.events_host.append(event2)

	db.session.add(u1)
	db.session.add(u2)
	db.session.add(u3)
	db.session.add(u4)

	db.session.commit()
