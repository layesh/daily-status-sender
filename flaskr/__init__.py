import os
from . import db
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from flaskr.db import get_db
import openpyxl

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    def get_mail_text():
        return "Bhaia,\n\nThe following tasks have been done by today.\n\nTransit\n\nVersion: 1.2.0014.0001\n\n   Refactoring " \
               "session destroy codes when password is changed. (Task ID: 157379) (Complete).\n\nTasks to-do:\n\n   Issues " \
               "related to coping/moving large number of files/folder containing large number of files(e.g 12000) in " \
               "my files page. (Task ID: 157721).\n\n-Layesh"

    def get_mail_html():
        return """\
        <html>
          <head></head>
          <body>
            Bhaia,
            <div>
                <br>
            </div>   
            <div>
                The following tasks have been done by today.
            </div>
            <div>
                <br>
            </div>
            <div>
                <b>
                    <u>
                        Transit
                    </u>
                </b>
            </div>
            <div>
                <br>
            </div>
            <div>
                <b>
                    Version: 1.2.0014.0001
                </b>
            </div>
            <div>
                <ul>
                    <li>
                        Refactoring session destroy codes when password is changed. (Task ID: 157379) (Complete).
                    </li>
                </ul>
            </div>
            <div>
                <b>
                    Tasks to-do:
                </b>
            </div>
            <div>
                <ul>
                    <li>
                        Issues related to coping/moving large number of files/folder containing large number of files(e.g 12000) in my files page. (Task ID: 157721).
                    </li>
                </ul>
            </div>
            <div>
                <br>
            </div>
            <div>
                -Layesh
            </div>
          </body>
        </html>
        """

    def send_daily_status():
        username = 'layesh@nilavo.com'
        app_password = 'fvcwvieyguihatvf'
        to = ['layesh@nilavo.com']
        cc = ['layesh@nilavo.com']
        bcc = []
        subject = 'Daily Status: ' + datetime.today().strftime('%b %d, %Y')

        with app.app_context():
            send_email(username, app_password, to, cc, bcc, subject)
        print("Scheduler is alive!")

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(send_daily_status, 'interval', seconds=3)
    scheduler.start()

    def get_database_conn():
        return get_db()

    def get_all_tasks(database):
        return database.execute(
            'SELECT * FROM task'
        ).fetchall()

    def get_last_sent_daily_status_date(database):
        return database.execute(
            'SELECT max(created) FROM daily_status'
        ).fetchone()

    def read_excel_file():
        book = openpyxl.load_workbook(r'D:\My Workshop\tasks.xlsx')
        sheet = book.active
        return sheet.values

    def add_new_task(database, excel_row):
        database.execute(
            "INSERT INTO task (row_id, project_name, version, opt_id, task_status, task_name) values (?, ?, ?, ?, ?, ?)",
            (excel_row[0], excel_row[1], excel_row[2], excel_row[3], excel_row[4], excel_row[5])
        )
        database.commit()

    def get_matched_task_from_db(all_tasks_from_db, excel_row):
        return next((x for x in all_tasks_from_db if excel_row[0] == x['row_id']), None)

    def insert_task_log_and_update_task(database, matched_task_from_db, excel_row):
        database.execute(
            "INSERT INTO task_log (task_id, previous_status, current_status) values (?, ?, ?)",
            (matched_task_from_db['id'], matched_task_from_db['task_status'], excel_row[4])
        )
        database.execute(
            'UPDATE task SET project_name = ?, version = ?, opt_id = ?, task_status = ?, task_name = ?'
            ' WHERE row_id = ?',
            (excel_row[1], excel_row[2], excel_row[3], excel_row[4], excel_row[5], matched_task_from_db['row_id'])
        )
        database.commit()

    def scan_excel_and_generate_task_log(database, all_tasks_from_db, excel_rows):
        # iterate over excel rows
        for excel_row in excel_rows:
            # skip the header row
            if excel_row[0] == 'Row Id':
                continue
            # match will return the matched row from database
            matched_task_from_db = get_matched_task_from_db(all_tasks_from_db, excel_row)

            if matched_task_from_db is None:
                # task is not present in the database
                add_new_task(database, excel_row)
            else:
                # task is present in the database
                if excel_row[4] != matched_task_from_db['task_status']:
                    # status changed in current excel file
                    insert_task_log_and_update_task(database, matched_task_from_db, excel_row)

    def get_change_list():
        database = get_database_conn()
        all_tasks_from_db = get_all_tasks(database)
        print(all_tasks_from_db)
        excel_rows = read_excel_file()
        scan_excel_and_generate_task_log(database, all_tasks_from_db, excel_rows)
        last_sent_daily_status_date = get_last_sent_daily_status_date(database)

        return ""

    @app.route('/')
    def index():
        return get_change_list()

    def send_email(username, password, to, cc, bcc, subject):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = ', '.join(to)
        msg['Cc'] = ', '.join(cc)
        msg['Bcc'] = ', '.join(bcc)

        change_list = get_change_list()

        text = get_mail_text()
        html = get_mail_html()

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(username, password)
            test = msg.as_string()
            server.sendmail(username, to + cc + bcc, msg.as_string())
            server.close()
            print('Successfully sent the mail.')
        except Exception as e:
            print(e)

    return app

    if __name__ == '__main__':
        app.run()
