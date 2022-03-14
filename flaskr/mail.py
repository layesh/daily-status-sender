import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler


def send_daily_status():
    username = 'layesh@nilavo.com'
    app_password = 'fvcwvieyguihatvf'
    to = ['layesh@nilavo.com']
    cc = ['layesh@nilavo.com']
    bcc = []
    subject = 'Daily Status: ' + datetime.today().strftime('%b %d, %Y')
    body = 'This is the body!'

    send_email(username, app_password, to, cc, bcc, subject, body)
    print("Scheduler is alive!")


scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(send_daily_status, 'interval', minutes=1)
scheduler.start()


@app.route('/')
def index():
    username = 'layesh@nilavo.com'
    app_password = 'fvcwvieyguihatvf'
    to = ['layesh@nilavo.com']
    cc = ['layesh@nilavo.com']
    bcc = []
    subject = 'Daily Status: ' + datetime.today().strftime('%b %d, %Y')
    body = 'This is the body!'

    send_email(username, app_password, to, cc, bcc, subject, body)
    return 'Hello World!'


def send_email(username, password, to, cc, bcc, subject, body):
    message = """From: %s\nTo: %s\nCC: %s\nSubject: %s\n\n%s
    """ % (username, ", ".join(to), ", ".join(cc), subject, body)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = ', '.join(to)
    msg['Cc'] = ', '.join(cc)
    msg['Bcc'] = ', '.join(bcc)

    text = "Bhaia,\n\nThe following tasks have been done by today.\n\nTransit\n\nVersion: 1.2.0014.0001\n\n   Refactoring " \
           "session destroy codes when password is changed. (Task ID: 157379) (Complete).\n\nTasks to-do:\n\n   Issues " \
           "related to coping/moving large number of files/folder containing large number of files(e.g 12000) in " \
           "my files page. (Task ID: 157721).\n\n-Layesh"
    html = """\
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
