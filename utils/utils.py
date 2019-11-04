import email
import poplib
import quopri
import re
import requests

def get_raw_request(method, url, body={}):
    req = requests.Request(method, url, data=body)
    prepared = req.prepare()

    def pretty_print_POST(req):
        """
        Taken from https://stackoverflow.com/questions/20658572/python-requests-print-entire-http-request-raw
        ---
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in 
        this function because it is programmed to be pretty 
        printed and may differ from the actual request.
        """
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

    pretty_print_POST(prepared)

def get_items_from_email(test_email, test_email_password, support_subject, *body_regex):
    """
    Remember to enable POP server stuff on the test email being used
    """
    if test_email.split('@')[1] == 'gmail.com':
        pop_server = 'pop.gmail.com'
    else:
        raise ValueError('Invalid email format or POP server not supported')

    pop_conn = poplib.POP3_SSL(pop_server)
    pop_conn.user(test_email)
    pop_conn.pass_(test_email_password)

    support_email = 'support@videocoin.network'
    
    # List of email is given in chronological ascending order
    email_count = len(pop_conn.list()[1])

    while email_count > 0:
        raw_email = b"\n".join(pop_conn.retr(email_count)[1])
        parsed_email = email.message_from_bytes(raw_email)
        email_from = parsed_email['From']
        parsed_email_from = re.match(r'^.* <(.+)>$', email_from).group(1)
        subject = parsed_email['Subject']

        email_body_str = None
        if parsed_email_from == support_email and subject == support_subject:
            # pdb.set_trace()
            body = parsed_email.get_payload()
            # Read more about quoted-printable encodings here:
            # https://stackoverflow.com/questions/15621510/how-to-understand-the-equal-sign-symbol-in-imap-email-text
            # https://docs.python.org/3.7/library/quopri.html
            email_body_bytes = quopri.decodestring(str(body[1]))

            # Having trouble with decoding using utf-8, have to use ISO-8859-1
            # https://stackoverflow.com/questions/23772144/python-unicodedecodeerror-utf8-codec-cant-decode-byte-0xc0-in-position-0-i
            email_body_str = email_body_bytes.decode('ISO-8859-1')
            break
        email_count -= 1

    if email_count == 0:
        raise IndexError('Email cannot be found')

    regex_result = []
    for regex in body_regex:
        regex_result.append(re.search(regex, email_body_str).group(1))
    pop_conn.quit()
    return regex_result[0] if len(regex_result) == 1 else regex_result
