import os

from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return redirect(url_for('upload'))

    @app.route('/upload', methods=('GET', 'POST'))
    def upload():
        message = 0
        if request.method == 'POST':
            uploaded_file = request.files.get('file')

            filename = secure_filename(uploaded_file.filename)
            save_path = os.path.join(app.instance_path, filename)
            uploaded_file.save(save_path)
            message = f'File "{filename}" saved in {save_path}'

        # GET
        return render_template('upload.html', message=message)


    return app