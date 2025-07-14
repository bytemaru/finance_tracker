import redis
import logging
import hashlib
import re
from datetime import datetime

from flask import app, Flask


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
    to_convert = header["statement_date"]+header["statement_time"]+header["bank"] + header["branch"] + header["account"]+header["from_date"]+header["to_date"]
    blob = to_convert.encode("utf-8")
    header["hash"] = hashlib.md5(blob).hexdigest()


@celery.task(name="default.write_header_data", bind=True)
def write_header_data(filename: str, filepath: str):
    logger.info('Fetching metadata of the file %s', filename)
    header["filename"] = filename
    csvfile = open(filepath, 'r').readlines()
    open(str(filename+"_header") + '.txt', 'w+').writelines(csvfile[0:6])
    with open(filename+'_header.txt') as file:
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
