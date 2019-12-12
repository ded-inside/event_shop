from flask import url_for, request
from flask_admin import AdminIndexView
from flask_admin.contrib import sqla
from flask_login import current_user
from werkzeug.utils import redirect

from app import login
from app import app


class MicroBlogModelView(AdminIndexView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == "Admin"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("index"))
