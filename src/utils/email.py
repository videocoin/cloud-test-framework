import os
import sendgrid
import jinja2
import time
from datetime import datetime

from src.utils.utils import get_domain_link


def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    result = ''
    if h:
        result += '%d:' % h
    if m:
        result += '%02d:' % m
    if m:
        result += '%02d' % s
    else:
        result += '%02ds' % s
    return result


def get_report_html(passed, failed, skipped, error, cluster):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tpl_path = os.path.join(base_dir, '../templates/report.html')

    path, filename = os.path.split(tpl_path)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    )
    env.filters['format_time'] = format_time
    html = env.get_template(filename).render({
        'now': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'execution_time': format_time(time.time() - time.time()),
        'cluster': cluster,
        'domain': get_domain_link(cluster),

        'passed': passed,
        'results': passed + failed + error,

        'total_count': len(passed) + len(failed) + len(error),
        'has_errors': failed or error,
        'success_count': len(passed),
    })
    return html


def send_report(report_html, sendgrid_key, report_emails):
    sg = sendgrid.SendGridAPIClient(sendgrid_key)

    data = {
        "content": [
            {
                "type": "text/html",
                "value": report_html
            }
        ],
        "from": {
            "email": "cs@liveplanet.net",
            "name": "Videocoin Integration tests"
        },
        "headers": {},
        'personalizations': [
            {
                'to': [{'email': x} for x in report_emails.split(',')],
                'subject': 'Videocoin integration tests'
            }
        ],
    }
    response = sg.client.mail.send.post(request_body=data)
