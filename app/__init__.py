from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from test_config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = r"static/uploads"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import routes, models
