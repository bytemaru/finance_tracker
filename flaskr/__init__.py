import os

import celery

from celery import Celery, Task
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from celery import shared_task

import redis
import logging
import hashlib
import re
from datetime import datetime


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask, include=['flaskr.write_header_data'])
    celery_app.autodiscover_tasks(packages=['flaskr'])
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        CELERY_BROKER_URL='amqp://guest:guest@localhost:5672/',
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

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

            task = write_header_data.delay(filename, save_path)  # trigger background job

        # GET
        return render_template('upload.html', message=message)

    return app


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

header = {"filename": "", "upload_date": "", "statement_date": "", "statement_time": "", "bank": "", "branch": "",
          "account": "", "from_date": "", "to_date": "", "hash": ""}


def fill_dates(text: str):
    date_match = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", text)
    if date_match:
        day, mon_str, year = date_match.groups()
        mon_str = mon_str.capitalize()
        dt = datetime.strptime(f"{day} {mon_str} {year}", "%d %B %Y")
        header["statement_date"] = dt.date().isoformat()
        header["upload_date"] = datetime.today().date().isoformat()


def fill_times(text: str):
    time_match = re.search(r"(\d{2}:\d{2}:\d{2})", text)
    if time_match:
        header["statement_time"] = time_match.group(1)


def fill_banks(text: str):
    bank_match = re.search(r"(Bank \d{2})", text)
    if bank_match:
        bank_match = re.search(r"(\d{2})", bank_match.group(1))
        header["bank"] = bank_match.group(1)


def fill_branches(text: str):
    branch_match = re.search(r"(Branch \d{4})", text)
    if branch_match:
        branch_match = re.search(r"(\d{4})", branch_match.group(1))
        header["branch"] = branch_match.group(1)


def fill_accounts(text: str):
    account_match = re.search(r"(Account \d{7}-\d{2})", text)
    if account_match:
        account_match = re.search(r"(\d{7}-\d{2})", account_match.group(1))
        header["account"] = account_match.group(1)


def fill_periods(text: str):
    period_match = re.search(r"(From date \d{8})", text)
    if period_match:
        period_match = re.search(r"(\d{8})", period_match.group(1))
        dt = datetime.strptime(period_match.group(1), "%Y%m%d")
        header["from_date"] = dt.date().isoformat()
    end_period_match = re.search(r"(To date \d{8})", text)
    if end_period_match:
        end_period_match = re.search(r"(\d{8})", end_period_match.group(1))
        dt = datetime.strptime(end_period_match.group(1), "%Y%m%d")
        header["to_date"] = dt.date().isoformat()


def fill_hash():
    to_convert = header["statement_date"] + header["statement_time"] + header["bank"] + header["branch"] + header[
        "account"] + header["from_date"] + header["to_date"]
    blob = to_convert.encode("utf-8")
    header["hash"] = hashlib.md5(blob).hexdigest()


@shared_task(name="flaskr.write_header_data",ignore_result=False)
def write_header_data(filename: str, filepath: str):
    logger.info('Fetching metadata of the file %s', filename)
    header["filename"] = filename
    csvfile = open(filepath, 'r').readlines()
    open(str(filename + "_header") + '.txt', 'w+').writelines(csvfile[0:6])
    with open(filename + '_header.txt') as file:
        for line in file:
            fill_dates(line)
            fill_times(line)
            fill_banks(line)
            fill_branches(line)
            fill_accounts(line)
            fill_periods(line)
            fill_hash()
    logger.info('Metadata = %s', header)
    logger.info('Checking duplicate loads')
    if r.exists(header['hash']):
        logger.info('Ooopsies!... Seems like the exact same file has been loaded already to %s', filepath)
    elif header['hash'] != "":
        logger.info('Not a duplicate!')
        r.set(header['hash'], filepath)

    return header
