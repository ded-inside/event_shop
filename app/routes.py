from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from werkzeug.datastructures import FileStorage
from werkzeug.urls import url_parse
from wtforms import IntegerField
from wtforms.fields.core import UnboundField
from wtforms.validators import NumberRange

from app import app, ALLOWED_EXTENSIONS
from flask import request, flash, redirect, url_for, send_from_directory, render_template, abort
from werkzeug.utils import secure_filename
import os

from app.forms import LoginForm, RegisterForm, UserEditForm, EventForm, AdminUserEditForm
from app.models import *


# TODO: Admin panel
# 1) All transactions
# 2) All users
# 3) All certs for every user
# 4) All events for every user


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    users_ = User.query.filter(User.username != "Admin").outerjoin(User.events_host).order_by(
        desc(Event.time_edited)).all()
    return render_template("index.html", users=users_, active='main')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin_panel")
@login_required
def admin_panel():
    if current_user.username != "Admin":
        return abort(404)
        # return redirect(url_for("user_page", username=current_user.username))

    users_ = User.query.filter(User.username != "Admin").all()
    trans_ = Transaction.query.all()
    # certs_ = Certificate.query.all()
    certificates_available = Certificate.available().all()
    certificates_unavailable = Certificate.unavailable().all()

    return render_template("admin_panel_index.html", users=users_, trans=trans_,
                           certs={"available": certificates_available,
                                  "unavailable": certificates_unavailable})


@app.route("/admin_panel/user/<username>", methods=["GET", "POST"])
@login_required
def admin_panel_user(username: str):
    if current_user.username != "Admin":
        return abort(404)
        # return redirect(url_for("user_page", username=current_user.username))
    user = User.query.filter(User.username == username).first_or_404()
    form = AdminUserEditForm(request.form)

    certificates_available = Certificate.available().all()
    certificates_unavailable = Certificate.unavailable().all()

    if form.validate_on_submit():
        if form.certs.data > user.balance():
            for i in range(form.certs.data - user.balance()):
                cert = Certificate.available().first()
                if cert is None:
                    db.session.rollback()
                    return render_template("admin_panel_user.html", certs={"available": certificates_available,
                                                                           "unavailable": certificates_unavailable},
                                           form=form, user=user)

                user.certificates.append(cert)

        else:
            for i in range(user.balance() - form.certs.data):
                cert = user.certificates[0]
                user.certificates.remove(cert)

        db.session.commit()

    certificates_available = Certificate.available().all()
    certificates_unavailable = Certificate.unavailable().all()
    return render_template("admin_panel_user.html", certs={"available": certificates_available,
                                                           "unavailable": certificates_unavailable},
                           form=form, user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("login.html", form=form, active='login')


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # u = User.query.filter_by(username=form.username.data).first()
        # if u:
        #     form.username.data = ""
        #     flash("Username is alredy taken!")
        #     return render_template("register.html", form=form)
        # if form.password1.data != form.password2.data:
        #     flash("Passwords aren't equal!")
        #     return render_template("register.html", form=form)
        u = User(username=form.username.data,
                 first_name=form.first_name.data,
                 last_name=form.last_name.data,
                 email=form.email.data
                 )
        u.set_password(form.password1.data)
        db.session.add(u)
        db.session.commit()
        login_user(u)
        return redirect(url_for("user_page", username=u.username))
    return render_template("register.html", form=form, active='register')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/edit/user", methods=["GET", "POST"])
@login_required
def user_edit():
    form = UserEditForm()
    # FileStorage(request)
    if form.validate_on_submit():
        if form.first_name.data:
            current_user.first_name = form.first_name.data
        if form.last_name.data:
            current_user.last_name = form.last_name.data
        if form.about.data:
            current_user.about = form.about.data
        if form.job.data:
            current_user.job = form.job.data

        if form.profile_picture.data:
            if allowed_file(form.profile_picture.data.filename):
                image_data = request.files[form.profile_picture.name].read()
                filename = secure_filename(form.profile_picture.data.filename)

                open(os.path.join(os.getcwd(), "app", app.config['UPLOAD_FOLDER'], form.profile_picture.data.filename),
                     'wb').write(image_data)
                current_user.profile_pic_filename = filename
        db.session.commit()
        return redirect(url_for('user_page',
                                username=current_user.username))

    return render_template("edit_user.html", form=form)


@app.route("/user/<username>")
def user_page(username: str):
    if username == "Admin":
        abort(404)
    user = User.query.filter_by(username=username).options(joinedload("events_host")).first_or_404()
    return render_template("profile.html", user=user, submenu='main',
                           active='profile' if user == current_user else None)


@app.route("/users")
def users():
    _users = User.query.options(joinedload("events_host")).filter(User.username != "Admin").all()
    return render_template("users.html", users=_users)


@app.route("/event/id/<event_id>")
def event_page(event_id: int):
    event = Event.query.get_or_404(event_id)
    return render_template("event.html", event=event)


@app.route('/user/<username>/events')
def events(username: str):
    _user = User.query.filter(User.username == username).first();
    _events = Event.query.filter(Event.seller_id == _user.id);
    return render_template('events.html', events=_events, user=_user, submenu='shedule',
                           active='profile' if _user == current_user else None)


@app.route("/event/add", methods=["GET", "POST"])
@login_required
def event_add():
    form = EventForm(request.form)

    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            about=form.about.data,
            price=form.price.data,
            time_start=form.time_start.data,
            time_end=form.time_end.data,
            time_created=datetime.utcnow(),
            time_edited=datetime.utcnow()
        )
        current_user.events_host.append(event)
        db.session.commit()
        return redirect(url_for("users"))
    return render_template("event_add.html", form=form)


@app.route("/buy/event/<event_id>")
@login_required
def event_buy(event_id: int):
    event = Event.query.get_or_404(event_id)
    seller = event.seller
    buyer: User = current_user
    if event.buyer:
        return redirect(url_for("user_page", username=seller.username))
    if buyer == seller:
        flash("U cant buy your event")
        return redirect(url_for("user_page", username=current_user.username))
    if buyer.balance() < event.price:
        flash("U dont have enough certs")
        return redirect(url_for("user_page", username=current_user.username))

    transaction = Transaction()
    remains = event.price
    cert: Certificate
    for cert in buyer.certificates:
        if remains == 0:
            break
        cert.owner = seller
        transaction.certificates.append(cert)
        remains -= 1
    event.buyer = buyer
    transaction._to = seller
    transaction._from = buyer

    db.session.add(transaction)
    db.session.commit()

    return redirect(url_for('events', username=seller.username))


@app.route("/transactions")
@login_required
def transactions():
    trns_buyer = current_user.transactions_buyer
    trns_seller = current_user.transactions_seller

    return render_template("transactions.html", trns_buyer=trns_buyer, trns_seller=trns_seller, user=current_user, active='profile', submenu='transactions')


@app.route('/dbg/profile')
def dbg_profile():
    return render_template('profile.html')
