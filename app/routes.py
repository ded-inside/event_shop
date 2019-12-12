from flask_login import login_user, current_user, login_required

from app import app, ALLOWED_EXTENSIONS
from flask import request, flash, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
import os

from app.forms import LoginForm, RegisterForm, UserEditForm
from app.models import *


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        return redirect(url_for('index'))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u:
            form.username.data = ""
            flash("Username is alredy taken!")
            return render_template("register.html", form=form)
        if form.password1.data != form.password2.data:
            flash("Passwords aren't equal!")
            return render_template("register.html", form=form)
        u = User(username=form.username.data,
                 first_name=form.first_name.data,
                 last_name=form.last_name.data,
                 email=form.email.data
                 )
        u.set_password(form.password1.data)
        db.session.add(u)
        db.session.commit()
        return redirect(url_for("user_page", username=u.username))
    return render_template("register.html", form=form)


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    print(app.config['UPLOAD_FOLDER'], filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)



@app.route("/edit/user", methods=["GET", "POST"])
@login_required
def user_edit():
    form = UserEditForm()
    if form.validate_on_submit():
        if form.first_name.data:
            current_user.first_name = form.first_name.data
        if form.last_name.data:
            current_user.last_name = form.last_name.data
        if form.profile_picture.data:
            if allowed_file(form.profile_picture.data.filename):

                image_data = request.files[form.profile_picture.name].read()
                filename = secure_filename(form.profile_picture.data.filename)
                open(os.path.join(app.config['UPLOAD_FOLDER'], form.profile_picture.data.filename), 'wb').write(image_data)
                current_user.profile_pic_filename = filename
                db.session.commit()
                return redirect(url_for('user_page',
                                        username=current_user.username))


    return render_template("edit_user.html", form=form)


def add_event():
    pass


@app.route("/user/<username>")
def user_page(username: str):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', active='prof')


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/', endpoint='index_clr')
@app.route("/index")
def index():
    users = User.query.all()
    return render_template("index.html", active='main', users=users)


@app.route('/dbg/profile')
def dbg_profile():
	user = {'username': 'Alice'
	}
	return render_template('profile.html', user=user)
