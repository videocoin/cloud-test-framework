import email
import poplib
import quopri
import re
import requests

from consts import input_values

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

def get_items_from_email(test_email, subject, body_regex, test_email_password = None):
    """
    Remember to enable POP server stuff on the test email being used
    """
    if test_email.split('@')[1] == 'gmail.com':
        pop_server = 'pop.gmail.com'
    else:
        raise ValueError('Invalid email format or POP server not supported')

    if test_email_password == None:
        # TODO: Should support different emails without needing to provide test_email_password
        test_email_password = input_values.VALID_EMAIL_PASSWORD

    pop_conn = poplib.POP3_SSL(pop_server)
    pop_conn.user(test_email)
    pop_conn.pass_(test_email_password)

    support_email = input_values.SUPPORT_EMAIL
    support_subject = input_values.PASSWORD_RECOVERY_SUBJECT
    
    # List of email is given in chronological ascending order
    email_count = len(pop_conn.list()[1])
    while email_count > 0:
        raw_email = b"\n".join(pop_conn.retr(email_count)[1])
        parsed_email = email.message_from_bytes(raw_email)

        email_from = parsed_email['From']
        parsed_email_from = re.match(r'^.* <(.+)>$', email_from).group(1)
        subject = parsed_email['Subject']
        
        if parsed_email_from == support_email and subject == support_subject:
            body = parsed_email.get_payload()
            # Read more about quoted-printable encodings here:
            # https://stackoverflow.com/questions/15621510/how-to-understand-the-equal-sign-symbol-in-imap-email-text
            # https://docs.python.org/3.7/library/quopri.html
            decoded_body = quopri.decodestring(str(body[1]))

            # Having trouble with decoding using utf-8, have to use ISO-8859-1
            # https://stackoverflow.com/questions/23772144/python-unicodedecodeerror-utf8-codec-cant-decode-byte-0xc0-in-position-0-i
            password_reset_email = decoded_body.decode('ISO-8859-1')
            break
            
        email_count -= 1

    # bad regex, fix later
    reset_password_url = re.search(body_regex, password_reset_email).group(1)
    redirect_url = requests.get(reset_password_url).url
    # TODO: Get all items after 0th index and put them in list
    result = re.search(r'token=(.*)', redirect_url).group(1)

    pop_conn.quit()
    return result
