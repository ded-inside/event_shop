from app import app, ALLOWED_EXTENSIONS
from flask import request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os

from app.models import *


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(app.config['UPLOAD_FOLDER'], filename)
    return send_from_directory("../"+app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/user/<username>")
def user_page(username: str):
    user = User.query.filter_by(username=username).first_or_404()
    return f'''
    <html>
    <body>
    <p>{user.full_name()}</p>
    <img src="{user.profile_pic_url()}" alt="Smiley face" height="42" width="42">
    </body>
    </html>
    '''


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

@app.route('/')
@app.route("/index")
def index():
    return "Hello fucking World!"
